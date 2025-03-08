
from lxml import etree
import os, re, sys, json

from helpers import *
from constants import *


#
# Retitle Specific HELPERS
#

# Gets the sequence and clip index from the given ID of format seq{SIDX}_clip{CIDX}
def id_to_seqclip_pair(clipid: str) -> [int, int]:
	m = re.match(r"seq(\d+)_clip(\d+)", clipid)
	return (int(m[1]), int(m[2]))



# Adjusts the items in the playlist pl so that it matches the updated layout.
#
# pl: The playlist to modify.
# ptree: The root ElementTree containing the entire project.
# projfile: The URL of the project file.
# producer_durs: A dictionary of durations for each producer.
# seq_layout: The layout data for the corresponding sequence.
# seq_idx: The index of the corresponding sequence
# found: The number of entries already in this playlist, minus one.
# base_id: The next free unique numeric ID, minus one.
# num_to_add: The amount of clips to add.
# num_to_delete: The amount of clips to delete. num_to_delete is 0 iff num_to_add is not 0.
#
# Returns the total duration of the new playlist.
def modify_playlist(pl, ptree, projfile: str, producer_durs: dict, seq_layout: list[dict], seq_idx: int, found: int, base_id: int, num_to_add: int, num_to_delete: int) -> float:
	# Track the new length of the sequence.
	this_len = 0.0

	# Check if we need to create any new titles before we modify the playlist.
	next_title_idx = (len(seq_layout) - num_to_add) * 2 - 1
	if (num_to_add > 0):
		# Looks like we need to create some new titles!
		pdb(f"Creating New Titles for Sequence {seq_idx}")

		# Get the folder ID by looking it up from the first entry.
		# This produces a warning which I ignore.
		folder_id = ptree.getroot().find(f"producer[@id='{pl[0].get("producer")}']").find("property[@name='kdenlive:folderid']").text

		# Create and add each producer to the tree & playlist
		for i in range(num_to_add):
			clip_data = seq_layout[found + i + 1]

			# Generate Producer XML
			producer_str = title_to_producer(
				title_obj = clip_data,
				projdir = os.path.dirname(projfile),
				folder_id = folder_id,
				clip_id = (base_id + 1) + i,
				producer_id = found + i + 1,
				seq_id = seq_idx
			)

			# Add the producer to the tree
			ptree.getroot().insert(ptree.getroot().index(ptree.getroot().find(f"producer[@id='seq{seq_idx}_clip{found}']")) + 1, etree.fromstring(producer_str))

			# Also add it to the main_bin entry list.
			main_bin_entry_str = main_bin_entry(
				seq_id = seq_idx,
				pl_id = found + i + 1,
				duration = clip_data["duration_time"]
			)
			main_bin = ptree.getroot().find("playlist[@id='main_bin']")
			main_bin.insert(main_bin.index(main_bin.find(f"entry[@producer='seq{seq_idx}_clip{found}']")) + 1, etree.fromstring(main_bin_entry_str))

			producer_durs[f"seq{seq_idx}_clip{found + i + 1}"] = {
				"out": clip_data["duration_time"],
				"full": clip_data["duration_full"]
			}

			# Insert the producer into the playlist
			# Note that since we know our playlist was found, it has at least one element
			# and therefore the new item is a content clip.

			# Create Entry
			entry_str = playlist_entry(
				seq_id = seq_idx,
				pl_id = found + i + 1,
				unique_id = (base_id + 1) + i,
				duration = clip_data["duration_time"],
				fade_dur = FADE_DURATION
			)

			# Get blank length
			blank_len = CONTENT_GAP
			if ("before_pause" in clip_data["modifiers"]):
				blank_len = clip_data["modifiers"]["before_pause"]

			# Add a new blank and the entry to the playlist.
			pl.insert(next_title_idx + (i * 2), etree.fromstring(playlist_blank(blank_len)))
			pl.insert(next_title_idx + 1 + (i * 2), etree.fromstring(entry_str))

			this_len += blank_len
			this_len += clip_data["duration_full"]

			pdb(f"Added Title {found + 1 + i}")


	# Adjust existing elements of the playlist.
	for i in range(0, next_title_idx, 2):
		durations = producer_durs[pl[i].get("producer")]

		# Adjust Entry
		# Adjust out
		pl[i].set("out", seconds_to_timestamp(durations["out"]))

		# Adjust fades
		# Fade-out filter
		pl[i].find("filter[@in]").set("in", seconds_to_timestamp(durations["out"] - FADE_DURATION))
		pl[i].find("filter[@in]").set("out", seconds_to_timestamp(durations["out"]))
		# Fade-in filter
		pl[i].xpath("filter[not(@in)]")[0].set("out", seconds_to_timestamp(FADE_DURATION))

		this_len += durations["full"]
		if (i > 0):
			# Additionally handle and adjust gap before
			gap_size = CONTENT_GAP
			if ("before_pause" in seq_layout[i // 2]["modifiers"]):
				gap_size = seq_layout[i // 2]["modifiers"]["before_pause"]
			elif (i <= 2):
				gap_size = SECTION_GAP

			pl[i - 1].set("length", seconds_to_timestamp(gap_size))
			this_len += gap_size

	# Delete elements of the playlist to be removed.
	if (num_to_delete > 0):
		for i in range(num_to_delete):
			# Get ID
			rem_id = pl[len(seq_layout) * 2].get("producer")

			# Delete Producer
			rem_prod = ptree.xpath(f"/mlt/producer[@id='{rem_id}']")[0]
			rem_prod.getparent().remove(rem_prod)

			# Delete main_bin entry
			rem_mbe = ptree.xpath(f"/mlt/playlist[@id='main_bin']/entry[@producer='{rem_id}']")[0]
			rem_mbe.getparent().remove(rem_mbe)

			# Delete in playlist
			pl.remove(pl[len(seq_layout) * 2])
			pl.remove(pl[len(seq_layout) * 2 - 1])

	pdb(f"Playlist {pl.get('id')} Regenerated: {this_len}")

	return this_len



# Recalculates the length of the sequence tractor and sets all corresponding values based on that.
#
# seq_trac: The sequence tractor to modify
# baseline_len: The length of the title clip track of the sequence.
#
# Returns the new length of the sequence.
def modify_sequence_tractor(seq_trac, ptree, baseline_len: float) -> float:
	# First, find the longest track length. This is the length of the entire sequence.
	longest_len = baseline_len
	track_ids = seq_trac.xpath("track[position() > 1]/@producer")
	for tid in track_ids:
		track = ptree.xpath(f"/mlt/tractor[@id='{tid}']")[0]
		if ("out" in track.attrib):
			track_dur = timestamp_to_seconds(track.get("out"))
			if (track_dur > longest_len):
				longest_len = track_dur

	longest_len = r3(longest_len)

	# Set this sequence's length everywhere it's used.
	seq_trac.set("out", seconds_to_timestamp(longest_len - 1 / FRAMERATE))
	seq_trac.find("property[@name='kdenlive:duration']").text = seconds_to_timestamp(longest_len)
	seq_trac.find("property[@name='kdenlive:maxduration']").text = str(seconds_to_frames(longest_len))
	seq_trac.find("property[@name='kdenlive:sequenceproperties.zoneout']").text = str(seconds_to_frames(longest_len))

	# Adjust the entry in main_bin.
	main_bin_entry = ptree.xpath(f"/mlt/playlist[@id='main_bin']/entry[@producer='{seq_trac.get("id")}']")[0]
	main_bin_entry.set("out", seconds_to_timestamp(longest_len - 1 / FRAMERATE))

	pdb(f"New Length of Sequence {seq_trac.get("id")} Calculated: {longest_len}\n")

	return longest_len



# Attempts to adjust the title clip tracks inside the given kdenlive project file
# so that they match the layout seen in the given layout.json file.
#
# - projfile: The .kdenlive project document to modify
# - layoutfile: A layout.json file generated by tgen.py.
#
# Returns one of the following error codes based on what happened:
# - 0: OK
# - 1: Failed to read layout.json (layoutfile is invalid)
# - 2: Failed to read project.kdenlive (projfile is invalid)
#
def adjust_titles_in_place(projfile: str, layoutfile: str) -> int:
	# Read layout data into memory if possible
	layout = []
	try:
		with open(layoutfile, "r") as layout_json:
			layout = layout_to_sequences(json.loads(layout_json.read()))
	except:
		return 1

	# Open the project file
	ptree = None
	with open(projfile, "r") as projfile_text:
		# Create an XML Element Tree for the project
		ptree = etree.parse(projfile_text)

	pdb("Getting Title Clip Producers...")

	# First, find all producers of format seq*_clip*. These are title clips whose times
	# we need to adjust.
	tc_producers = ptree.xpath("/mlt/producer[contains(@id, 'seq') and contains(@id, '_clip')]")

	# Additionally get the corresponding <entry> in main_bin.
	tc_entries = ptree.xpath("/mlt/playlist[@id='main_bin']/entry[contains(@producer, 'seq') and contains(@producer, '_clip')]")



	# Keep track of a few values before we go through our producer.
	# The number of clips needed to be deleted per playlist.
	to_delete = {}
	# The number of clips found per playlist.
	found = {}

	# List of sequence IDs and their corresponding duration_full
	producer_durs = {}

	# Go through each producer we found.
	pdb("Modifying Title Clip Producers...")
	for i in range(len(tc_producers)):
		seq_idx, clip_idx = id_to_seqclip_pair(tc_producers[i].get("id"))

		# Check if we have a clip we need to delete
		if (seq_idx >= len(layout) or clip_idx >= len(layout[seq_idx])):
			if not seq_idx in to_delete:
				to_delete[seq_idx] = 1
			else:
				to_delete[seq_idx] += 1
			continue
		else:
			if not seq_idx in found:
				found[seq_idx] = clip_idx
			elif clip_idx > found[seq_idx]:
				found[seq_idx] = clip_idx

		# Operating on a preexisting clip.
		clip_data = layout[seq_idx][clip_idx]

		# Set "out" duration for each
		tc_producers[i].set("out", seconds_to_timestamp(clip_data["duration_time"]))
		# Thanks to the way we do things, our producers are in the same order as the entries
		# in main bin. We can use the same index!
		tc_entries[i].set("out", seconds_to_timestamp(clip_data["duration_time"]))

		# Additionally set a few more properties for the producer.
		# kdenlive:duration_frames
		tc_producers[i].xpath("property[@name='kdenlive:duration_frames']")[0].text = frames_to_timestamp(clip_data["duration_frames"])
		# kdenlive:duration
		tc_producers[i].xpath("property[@name='kdenlive:duration']")[0].text = seconds_to_timestamp(clip_data["duration_full"])
		# length
		tc_producers[i].xpath("property[@name='length']")[0].text = str(clip_data["duration_frames"])

		# Record Duration
		producer_durs[tc_producers[i].get("id")] = {
			"out": clip_data["duration_time"],
			"full": clip_data["duration_full"]
		}

	# Tally number of clips per sequence we need to add
	to_add = {}
	for i in range(len(layout)):
		# Check if layout has sequence not found
		if not i in found:
			to_add[i] = len(layout[i])
		else:
			# Check if layout has clips not found
			if (found[i] < len(layout[i]) - 1):
				to_add[i] = (len(layout[i]) - 1) - found[i]

	pdb(f"ADD: {to_add}\tDEL: {to_delete}")



	# We must also find the maximum numeric ID if we need to add any titles.
	pdb("Finding Max Unused Numeric ID...")
	base_id = -1
	if (to_add != {}):
		ids = ptree.xpath("//property[@name='kdenlive:id']") + ptree.xpath("//property[@name='kdenlive:folderid']")
		for id_prop in ids:
			if int(id_prop.text) > base_id:
				base_id = int(id_prop.text)

	# Now we must adjust our playlists. To do this, we must first find every playlist which
	# has our sequences. Even though kdenlive removes the original playlist names, we can still
	# access them as the entry names are untouched.
	# Therefore, as long as the first item in the title track is a title clip, we can find
	# the correct playlist.
	seq_plays = ptree.xpath("/mlt/playlist[@id!='main_bin']/entry[contains(@producer, 'seq') and contains(@producer, '_clip')]/..")

	# Index of the main sequence in seq_plays. This sequence needs to be processed last.
	main_seq_idx = -1

	# Tracks the length of each sequence, keyed by the UUID of the sequence.
	seq_times = {}

	pdb("Modifying Playlists & Tractors...")
	for i in range(len(seq_plays)):
		pl = seq_plays[i]

		# Check if this is the main sequence title track playlist. If so, save handling it
		# until the other sequences have been processed.
		if (pl[0].get("producer")[:5] == "seq0_"):
			main_seq_idx = i
			continue

		# Get the tractor merging the playlist and the other video track
		merge_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{pl.get("id")}']/..")[0]

		# Get the sequence tractor. This contains the sequence index, so get that too.
		seq_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{merge_trac.get("id")}']/..")[0]
		# NOTE: This method of getting sequence index assumes that the sequence is named
		# "Sequence {IDX}". This won't work if the sequence was renamed! If sequence name
		# changes are implemented later, this will need to change, likely by getting the
		# index in the main playlist.
		seq_idx = int(seq_trac.find("property[@name='kdenlive:clipname']").text[9:])

		# Edit the playlist.
		this_len = modify_playlist(
			pl = pl,
			ptree = ptree,
			projfile = projfile,
			producer_durs = producer_durs,
			seq_layout = layout[seq_idx],
			seq_idx = seq_idx,
			found = found[seq_idx],
			base_id = base_id,
			num_to_add = to_add[seq_idx] if seq_idx in to_add else 0,
			num_to_delete = to_delete[seq_idx] if seq_idx in to_delete else 0
		)

		base_id += to_add[seq_idx] if seq_idx in to_add else 0


		# Modify the tractor containing this playlist.
		merge_trac.set("out", seconds_to_timestamp(this_len - 1 / FRAMERATE))

		# Modify the sequence tractor containing the prior tractor. Set its length to be the
		# length of the longest track.

		# First, find the longest track length.
		longest_len = modify_sequence_tractor(
			seq_trac = seq_trac,
			baseline_len = this_len,
			ptree = ptree,
		)

		# Save the sequence length for later, using the UUID of the sequence for ease of
		# access.
		seq_times[seq_trac.get("id")] = {
			"len": longest_len,
			"before_gap": layout[seq_idx][0]["modifiers"]["before_pause"] if "before_pause" in layout[seq_idx][0]["modifiers"] else SECTION_GAP
		}

		pdb(f"Corresponding Sequence Regenerated.\n")


	# Now it's time to adjust the main sequence.
	# First get the video and audio track playlists. We will need to adjust both.
	pdb(f"Modifying Main Sequence & Playlist...\n")

	mpl_v = seq_plays[main_seq_idx]
	mpl_a = ptree.xpath(f"/mlt/playlist[@id!='main_bin']/entry[contains(@producer, '{list(seq_times.keys())[0]}')]/../property[@name='kdenlive:audio_track']/..")[0]

	# Adjust the intro clips in the video playlist.
	main_len = modify_playlist(
		pl = mpl_v,
		ptree = ptree,
		projfile = projfile,
		producer_durs = producer_durs,
		seq_layout = layout[0],
		seq_idx = 0,
		found = found[0],
		base_id = base_id,
		num_to_add = to_add[0] if 0 in to_add else 0,
		num_to_delete = to_delete[0] if 0 in to_delete else 0
	)

	# Now adjust the rest of each playlist.
	main_len_full = main_len
	for i in range(len(seq_times)):
		seq_uuid = mpl_a[i * 2 + 2].get("producer")

		# Adjust gap before
		b_gap = seq_times[seq_uuid]["before_gap"]
		mpl_v[found[0] * 2 + i * 2 + 1].set("length", seconds_to_timestamp(b_gap))
		main_len_full += b_gap

		if (i == 0):
			b_gap += main_len
		mpl_a[i * 2 + 1].set("length", seconds_to_timestamp(b_gap))

		# Adjust length of sequence itself
		seq_len = seq_times[seq_uuid]["len"]

		mpl_a[i * 2 + 2].set("out", seconds_to_timestamp(seq_len))
		mpl_v[found[0] * 2 + i * 2 + 2].set("out", seconds_to_timestamp(seq_len))
		main_len_full += seq_len

	# With both playlists set, modify BOTH corresponding tractors.
	main_v_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{mpl_v.get("id")}']/..")[0]
	main_v_trac.set("out", seconds_to_timestamp(main_len_full - 1 / FRAMERATE))
	main_a_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{mpl_a.get("id")}']/..")[0]
	main_a_trac.set("out", seconds_to_timestamp(main_len_full - 1 / FRAMERATE))

	# Modify the sequence tractor.
	main_seq_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{main_v_trac.get("id")}']/..")[0]
	main_seq_len = modify_sequence_tractor(
		seq_trac = main_seq_trac,
		baseline_len = main_len_full,
		ptree = ptree
	)

	# Finally, modify the project tractor.
	proj_trac = ptree.xpath(f"/mlt/tractor/track[@producer='{main_seq_trac.get("id")}']/..")[0]
	proj_trac.set("out", seconds_to_timestamp(main_seq_len))
	proj_trac.find("track").set("out", seconds_to_timestamp(main_seq_len))

	pdb(f"Modifications Complete! Saving...\n")

	# Save to file.
	with open(projfile, "w") as projfile_out:
		projfile_out.write(etree.tostring(ptree, pretty_print=True).decode())

	return 0


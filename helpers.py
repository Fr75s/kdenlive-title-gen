import os, math, uuid, hashlib

from constants import *
from templates import *


# Prints a debug message. Will only print if the internal DEBUG variable is true.
def pdb(msg: str):
	if DEBUG:
		print(f"* DEBUG: {msg}")

# Prints a warning message.
def pwrn(msg: str):
	print(f"WARN: {msg}")



# Rounds the given value to 3 decimal places.
def r3(value: float) -> float:
	return round(value * 1000.0) / 1000.0

# Pads an integer with a leading zero if it is less than 10.
def pad2(val: int) -> str:
	if (val < 10):
		return f"0{val}"
	return f"{val}"




# Converts the given amount of seconds to frames based on the current framerate.
# This truncates the exact time to the nearest frame.
def seconds_to_frames(seconds: float) -> int:
	return int(seconds * FRAMERATE)

# Converts a number of frames into a timestamp in the form hh:mm:ss:ff, where ff is
# the frame offset within a second.
def frames_to_timestamp(frames: int) -> str:
	seconds: int = (frames // FRAMERATE) % 60
	minutes: int = (frames // (FRAMERATE * 60)) % 60
	hours: int = (frames // (FRAMERATE * 3600))

	return f"{pad2(hours)}:{pad2(minutes)}:{pad2(seconds)}:{pad2(frames % FRAMERATE)}"

# Converts a number of seconds into a timestamp in the form hh:mm:ss.sss
def seconds_to_timestamp(seconds: float) -> str:
	int_sec: int = int(math.floor(seconds))
	minutes: int = (int_sec // 60) % 60
	hours: int = (int_sec // 3600)

	return f"{pad2(hours)}:{pad2(minutes)}:{pad2(int_sec % 60)}.{str(r3(seconds - int_sec))[2:]}"

# Converts a timestamp to its corresponding amount in seconds
def timestamp_to_seconds(timestamp: str) -> float:
	split_ts: list[str] = timestamp.split(":")

	hours: float = float(split_ts[0]) * 3600
	minutes: float = float(split_ts[1]) * 60
	seconds: float = float(split_ts[2])

	return hours + minutes + seconds


# Converts a layout object (as saved in layout.json) to a list of sequences.
#
# layout: The layout data for a video, acquired by using json.loads on the contents
# of the layout.json file.
# title_last: Whether or not the title sequence should be moved to the end of the sequences list.
def layout_to_sequences(layout: list[dict], title_last: bool = False) -> list[list[dict]]:
	sections = [[]]
	section = 0

	# Iterate through clips
	for clip in layout:
		# Create new section if section clip, otherwise add to existing section
		if clip["ref"][:7] == "section":
			section += 1
			sections.append([clip])
		else:
			sections[section].append(clip)

	if (title_last):
		# Move title section to end
		sections.append(sections[0])
		del sections[0]

	return sections



# Converts a title object which refers to a .kdenlivetitle file to a MLT producer.
#
# title_obj: A dictionary that stores the data for a single title clip. Get these from layout.json.
# projdir: The directory of the project.
# folder_id: The ID of the kdenlive project bin folder this clip will be placed in.
# clip_id: The unique numeric ID given to this clip.
# producer_id: The ID of the clip within the sequence it is in.
# seq_id: The ID of the sequence this clip is in.
#
# Returns the XML for a producer that
def title_to_producer(title_obj: dict, projdir: str, folder_id: int, clip_id: int, producer_id: int, seq_id: int) -> str:
	file_hash = hashlib.md5(open(os.path.join(projdir, "titles", f"{title_obj["ref"]}.kdenlivetitle"), 'rb').read()).hexdigest()

	new_uuid = uuid.uuid4()

	return template_TITLE_PRODUCER(
		seq_id,
		producer_id,
		seconds_to_timestamp(title_obj["duration_time"]),
		title_obj["duration_frames"],
		f"titles/{title_obj["ref"]}.kdenlivetitle",
		seconds_to_timestamp(title_obj["duration_full"]),
		frames_to_timestamp(title_obj["duration_frames"]),
		folder_id,
		clip_id,
		f"{{{new_uuid}}}",
		file_hash
	)



# Returns a new playlist entry definition.
#
# seq_id: The ID of the sequence this clip is in.
# pl_id: The ID of the clip within the sequence it is in.
# unique_id: The unique numeric ID given to this clip.
# duration: The duration (minus one frame) of the clip.
# fade_dur: The duration of the fade in/out of the clip.
#
def playlist_entry(seq_id: int, pl_id: int, unique_id: int, duration: float, fade_dur: float) -> str:
	return template_PLAYLIST_ENTRY (
		seq_idx = seq_id,
		pl_idx = pl_id,
		unique_id = unique_id,
		entry_out = seconds_to_timestamp(duration),
		fadein_out = seconds_to_timestamp(fade_dur),
		fadeout_in = seconds_to_timestamp(duration - fade_dur)
	)

# Returns a new playlist blank space.
# duration: The duration of the blank in seconds.
def playlist_blank(duration: float) -> str:
	return template_PLAYLIST_BLANK (
		duration = seconds_to_timestamp(duration)
	)

# Returns a new entry in main_bin for the given producer
# duration: The duration of the producer in seconds.
def main_bin_entry(seq_id: int, pl_id: int, duration: float) -> str:
	return template_MAIN_BIN_ENTRY (
		producer = f"seq{seq_id}_clip{pl_id}",
		duration = seconds_to_timestamp(duration)
	)

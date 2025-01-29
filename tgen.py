#!/usr/bin/python3
# title generation script for kdenlive
# generates titles for kdenlive from a markdown script

#
# Options
#

# The outputted width and height of each title clip/project file.
RES_WIDTH = 1920
RES_HEIGHT = 1080

# The framerate to process each clip/set as project default to.
FRAMERATE = 60



# speed of each clip in words per second
READ_SPEED = 2.8

# duration_frames of the title clip (the first clip) in seconds
TITLE_DURATION = 6.0

# duration_frames of a section clip in seconds
SECTION_DURATION = 3.0

# gap before and after a section/title clip where no text is shown
SECTION_GAP = 2.5

# gap before content clips where no text is shown
CONTENT_GAP = 1.0

# time to fade titles in/out
TITLE_FADE_DURATION = 1.0

# time to fade content/sections in/out
FADE_DURATION = 0.5



# Name of the font you wish to use.
FONT_NAME = "Inter"

# Size of the font you wish to use, in pixels
FONT_SIZE = 48

# Color components for the font.
# R, G, B, A; 0-255.
# Default: White
FONT_COLOR = (255, 255, 255, 255)

# Outline color for the font.
# Default: Black
FONT_OUTLINE_COLOR = (0, 0, 0, 255)

# Outline thickness in pixels.
FONT_OUTLINE_THICK = 6

# Font weight.
# Regular is 400. Typically a multiple of 100 up to 900.
# Defaults to 600 (Semibold)
FONT_WEIGHT = 600



# Section font size in pixels
SECTION_FONT_SIZE = 96

# Main title font size in pixels
TITLE_FONT_SIZE = 160

# Font weight for title/section clips
TITLE_FONT_WEIGHT = 700

# Subtitle font size in pixels
SUBTITLE_FONT_SIZE = 60

# Subtitle font color tuple
SUBTITLE_FONT_COLOR = (255, 255, 255, 128)

# Supertitle font size in pixels
SUPERTITLE_FONT_SIZE = 36

# Supertitle font color tuple
SUPERTITLE_FONT_COLOR = (109, 130, 186, 192)

# Sub/supertitle font weight
SUBSUPER_FONT_WEIGHT = 500

# Gap between Title/Subtitle and Title/Supertitle, in pixels
TITLE_GAP = 40



# Maximum width content boxes are to be, in pixels
MAX_CONTENT_WIDTH = 1440

# Y position on screen where the text is centered.
Y_CENTER = 860



#
# Internal Vars
#

DEBUG = False

errors = {
	"general": "General Error",
	"dp": "Markdown Parsing Error",
	"cp": "Command Parsing Error",
	"mp": "Modifier Parsing Error",
	"tc": "Title Clip Conversion Error",
	"pf": "Project Creation Error"
}

commands = {
	"pause": [
		["float;0-"]
	],
	"ignore": [
		[]
	]
}

modifiers = {
	"color": [
		["int;0-255","int;0-255","int;0-255"],
		["int;0-255","int;0-255","int;0-255","int;0-255"]
	],
	"font": [
		["string"]
	],
	"font_size": [
		["int;1-2147483647"]
	],
	"outline_color": [
		["int;0-255","int;0-255","int;0-255"],
		["int;0-255","int;0-255","int;0-255","int;0-255"]
	],
	"outline_width": [
		["int;0-2147483647"]
	],
	"y": [
		["int"]
	]
}


#
# IMPORTS
#

from PIL import ImageFont
import os, sys, json, math, time, uuid, hashlib, pathlib, platform

CFG_FILE = ""
CFG_PROJDIR = ""

#
# UTILITY FUNCTIONS
#

# general helpers

# Prints a debug message. Will only print if the internal DEBUG variable is true.
def pdb(msg: str):
	if DEBUG:
		print(f"* DEBUG: {msg}")

# Prints a warning message.
def pwrn(msg: str):
	print(f"WARN: {msg}")

# Prints the given error with the given error key.
def print_error(error_key: str, msg: str):
	print(f"{errors[error_key]}: {msg}")

# Rounds the given value to 3 decimal places.
def r3(value: float) -> float:
	return round(value * 1000.0) / 1000.0

# Pads an integer with a leading zero if it is less than 10.
def pad2(val: int) -> str:
	if (val < 10):
		return f"0{val}"
	return f"{val}"

# titleclips_to_kdenlive Helpers

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

	# NOTES:
	# producer id should be unique
	# in/out in producer is length of clip - 1 frame
	# length is duration_frames in frames (integer)
	# resource is resource reference (e.g. file)
	# kdenlive:duration_frames is duration_frames in hh:mm:ss:ff, where ff is frames
	# id should be unique ??
	# xml was here seems useless??
	# clip_type is always 2 for title clips, 0 for sequence clips
	# file_hash doesn't seem to match up with hash of the file??
	# control_uuid is just a random UUID

	# kdenlive:id (& by extension clip_id) can be seen in tractors (clip_type 0) too.
	# producer_id is only seen in producers (clip_type 2).

	return f"""<producer id="seq{seq_id}_clip{producer_id}" in="00:00:00.000" out="{seconds_to_timestamp(title_obj["duration_time"])}">
	<property name="length">{title_obj["duration_frames"]}</property>
	<property name="eof">pause</property>
	<property name="resource">titles/{title_obj["ref"]}.kdenlivetitle</property>
	<property name="meta.media.progressive">1</property>
	<property name="aspect_ratio">1</property>
	<property name="seekable">1</property>
	<property name="mlt_service">kdenlivetitle</property>
	<property name="kdenlive:duration_frames">{frames_to_timestamp(title_obj["duration_frames"])}</property>
	<property name="xml">was here</property>
	<property name="kdenlive:folderid">{folder_id}</property>
	<property name="kdenlive:id">{clip_id}</property>
	<property name="kdenlive:control_uuid">{{{new_uuid}}}</property>
	<property name="kdenlive:clip_type">2</property>
	<property name="kdenlive:file_hash">{file_hash}</property>
	<property name="force_reload">0</property>
	<property name="meta.media.width">{RES_WIDTH}</property>
	<property name="meta.media.height">{RES_HEIGHT}</property>
	<property name="kdenlive:monitorPosition">0</property>
</producer>\n"""

# Creates the XML for three blank tracks, two audio and one video.
# This creates all necessary producers, playlists, and tractors.
#
# seq_idx: The numeric index of the sequence these blank tracks are for.
# audio_track_count: The number of blank audio tracks to create.
#
# Returns the XML to form three blank tracks.
def prepare_sequence_blanks(seq_idx: int, audio_track_count: int = 2):
	out = ""

	# Add blank video producer
	out += f"""<producer id="seq{seq_idx}_blank" in="00:00:00.000" out="00:05:00.000">
	<property name="length">2147483647</property>
	<property name="eof">continue</property>
	<property name="resource">0</property>
	<property name="aspect_ratio">1</property>
	<property name="mlt_service">color</property>
	<property name="kdenlive:playlistid">black_track</property>
	<property name="mlt_image_format">yuv422</property>
	<property name="set.test_audio">0</property>
</producer>\n"""

	# Add blank audio tracks
	for i in range(audio_track_count):
		out += f"""<playlist id="seq{seq_idx}_a{i}b1">
		<property name="kdenlive:audio_track">1</property>
	</playlist>
	<playlist id="seq{seq_idx}_a{i}b2">
		<property name="kdenlive:audio_track">1</property>
	</playlist>\n"""

		out += f"""<tractor id="seq{seq_idx}_tractor{i}" in="00:00:00.000">
		<property name="kdenlive:audio_track">1</property>
		<property name="kdenlive:trackheight">67</property>
		<property name="kdenlive:timeline_active">1</property>
		<property name="kdenlive:thumbs_format"/>
		<property name="kdenlive:audio_rec"/>

		<track hide="video" producer="seq{seq_idx}_a{i}b1"/>
		<track hide="video" producer="seq{seq_idx}_a{i}b2"/>

		<filter id="seq{seq_idx}_t{i}_f0">
			<property name="window">75</property>
			<property name="max_gain">20dB</property>
			<property name="mlt_service">volume</property>
			<property name="internal_added">237</property>
			<property name="disable">1</property>
		</filter>
		<filter id="seq{seq_idx}_t{i}_f1">
			<property name="channel">-1</property>
			<property name="mlt_service">panner</property>
			<property name="internal_added">237</property>
			<property name="start">0.5</property>
			<property name="disable">1</property>
		</filter>
		<filter id="seq{seq_idx}_t{i}_f2">
			<property name="iec_scale">0</property>
			<property name="mlt_service">audiolevel</property>
			<property name="dbpeak">1</property>
			<property name="disable">0</property>
		</filter>
	</tractor>\n"""

	# Add blank video track
	out += f"""<playlist id="seq{seq_idx}_v1b1"/>
<playlist id="seq{seq_idx}_v1b2"/>
<tractor id="seq{seq_idx}_tractor{audio_track_count}" in="00:00:00.000">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>

	<track hide="audio" producer="seq{seq_idx}_v1b1"/>
	<track hide="audio" producer="seq{seq_idx}_v1b2"/>
</tractor>\n"""

	return out

# Creates the XML for a single sequence from a sequence list.
#
# seq_idx: The index of the sequence
# sequence: A single sequence from the list created by layout_to_sequences
# start_id: The first free unique numeric ID to use for this sequence's producers/tractors.
# folder_obj: A dictionary that stores the ID, Name, and Parent ID of a project bin folder.
# projdir: The directory the outputted kdenlive file will be stored in.
# main_uuid: The UUID of the document.
#
# Returns a tuple with three elements.
# The first is the XML for the given sequence.
# The second is the next free unique numeric ID to use for future sequences.
# The third is a dictionary containing the following keys:
#   "uuid": The UUID of the sequence
#   "id": The numeric ID of the sequence's tractor
#   "seq_dur": The duration of the sequence in seconds.
#   "before_pause": The duration of the gap before the section.
def create_sequence(seq_idx: int, sequence: list[dict], start_id: int, folder_obj: dict, projdir: str, main_uuid: str) -> tuple[str, int, dict]:
	out = ""

	# Add blank video producer
	out += prepare_sequence_blanks(seq_idx)

	# Add all producers from title tracks
	for i in range(len(sequence)):
		out += title_to_producer(title_obj=sequence[i], projdir=projdir, folder_id=folder_obj["id"], clip_id=(start_id + i), producer_id=i, seq_id=seq_idx)

	# Form the playlist
	sequence_len: float = 0.0
	out += f"""<playlist id="seq{seq_idx}_v2b1">"""
	for i in range(len(sequence)):
		# Add entry
		out += f"""	<entry in="00:00:00.000" out="{seconds_to_timestamp(sequence[i]["duration_time"])}" producer="seq{seq_idx}_clip{i}">
		<property name="kdenlive:id">{start_id + i}</property>

		<filter id="seq{seq_idx}_clip{i}_fadein" out="{seconds_to_timestamp(FADE_DURATION)}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_from_black</property>
			<property name="alpha">00:00:00.000=0;{seconds_to_timestamp(FADE_DURATION)}=1</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
		<filter id="seq{seq_idx}_clip{i}_fadeout" in="{seconds_to_timestamp(sequence[i]["duration_time"] - FADE_DURATION)}" out="{seconds_to_timestamp(sequence[i]["duration_time"])}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_to_black</property>
			<property name="alpha">00:00:00.000=1;{seconds_to_timestamp(FADE_DURATION)}=0</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
	</entry>\n"""
		sequence_len += sequence[i]["duration_full"]

		# Add blank
		if (i < len(sequence) - 1):
			if ("before_pause" in sequence[i + 1]["modifiers"]):
				out += f"""<blank length="{seconds_to_timestamp(sequence[i + 1]["modifiers"]["before_pause"])}"/>"""
				sequence_len += sequence[i + 1]["modifiers"]["before_pause"]
			elif (i == 0):
				out += f"""<blank length="{seconds_to_timestamp(SECTION_GAP)}"/>"""
				sequence_len += SECTION_GAP
			else:
				out += f"""<blank length="{seconds_to_timestamp(CONTENT_GAP)}"/>"""
				sequence_len += CONTENT_GAP

	# Add final playlist and track tractor
	out += f"""</playlist>
<playlist id="seq{seq_idx}_v2b2"/>
<tractor id="seq{seq_idx}_tractor3" in="00:00:00.000" out="{seconds_to_timestamp(sequence_len - (1 / FRAMERATE))}">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>

	<track hide="audio" producer="seq{seq_idx}_v2b1"/>
	<track hide="audio" producer="seq{seq_idx}_v2b2"/>
</tractor>\n"""

	# Create Sequence Tractor
	# Get UUID and Hash
	sequence_uuid = uuid.uuid4()
	sequence_hash = hashlib.md5(f"{{{sequence_uuid}}}".encode()).hexdigest()

	# Create
	out += f"""<tractor id="{{{sequence_uuid}}}" in="00:00:00.000" out="{seconds_to_timestamp(sequence_len - (1 / FRAMERATE))}">
	<property name="kdenlive:duration">{seconds_to_timestamp(sequence_len)}</property>
	<property name="kdenlive:maxduration">{seconds_to_frames(sequence_len)}</property>
	<property name="kdenlive:clipname">Sequence {seq_idx}</property>
	<property name="kdenlive:description"/>
	<property name="kdenlive:uuid">{{{sequence_uuid}}}</property>
	<property name="kdenlive:producer_type">17</property>
	<property name="kdenlive:control_uuid">{{{uuid.uuid4()}}}</property>
	<property name="kdenlive:id">{start_id + len(sequence) + 1}</property>
	<property name="kdenlive:clip_type">0</property>
	<property name="kdenlive:file_hash">{sequence_hash}</property>
	<property name="kdenlive:folderid">1</property>
	<property name="kdenlive:sequenceproperties.activeTrack">2</property>
	<property name="kdenlive:sequenceproperties.disablepreview">0</property>
	<property name="kdenlive:sequenceproperties.documentuuid">{{{main_uuid}}}</property>
	<property name="kdenlive:sequenceproperties.hasAudio">1</property>
	<property name="kdenlive:sequenceproperties.hasVideo">1</property>
	<property name="kdenlive:sequenceproperties.position">0</property>
	<property name="kdenlive:sequenceproperties.scrollPos">0</property>
	<property name="kdenlive:sequenceproperties.tracks">4</property>
	<property name="kdenlive:sequenceproperties.tracksCount">4</property>
	<property name="kdenlive:sequenceproperties.verticalzoom">1</property>
	<property name="kdenlive:sequenceproperties.zonein">0</property>
	<property name="kdenlive:sequenceproperties.zoneout">{seconds_to_frames(sequence_len)}</property>
	<property name="kdenlive:sequenceproperties.zoom">8</property>
	<property name="kdenlive:sequenceproperties.groups">[
	]
	</property>
	<property name="kdenlive:sequenceproperties.guides">[
	]
	</property>
	<property name="kdenlive:monitorPosition">0</property>

	<track producer="seq{seq_idx}_blank"/>
	<track producer="seq{seq_idx}_tractor0"/>
	<track producer="seq{seq_idx}_tractor1"/>
	<track producer="seq{seq_idx}_tractor2"/>
	<track producer="seq{seq_idx}_tractor3"/>\n"""

	# Add blank space mixes
	for i in range(4):
		out += f"""	<transition id="transition0">
		<property name="a_track">0</property>
		<property name="b_track">{i + 1}</property>
		<property name="mlt_service">mix</property>
		<property name="kdenlive_id">mix</property>
		<property name="internal_added">237</property>
		<property name="always_active">1</property>
		<property name="accepts_blanks">1</property>
		<property name="sum">1</property>
	</transition>\n"""

	# Add default filters
	out += f"""	<filter id="seq{seq_idx}_filter0">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="seq{seq_idx}_filter1">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
</tractor>\n"""

	# Return Sequence XML
	return (out, start_id + len(sequence) + 2, {
		"uuid": sequence_uuid,
		"id": start_id + len(sequence) + 1,
		"seq_dur": sequence_len,
		"before_pause": sequence[0]["modifiers"]["before_pause"] if "before_pause" in sequence[0]["modifiers"] else SECTION_GAP
	})

# Converts a layout object (as saved in layout.json) to a list of sequences.
#
# layout: The layout data for a video, acquired by using json.loads on the contents
# of the layout.json file.
def layout_to_sequences(layout: list[dict]) -> list[list[dict]]:
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

	# Move title section to end
	sections.append(sections[0])
	del sections[0]

	return sections


# clip_data_to_titleclips Helpers

# Converts a color tuple to a color code, separated by comma.
#
# color_tuple: A tuple of 4 integer values from 0-255, containing the red, green,
# blue, and alpha components of a color respectively.
def color_code(color_tuple: tuple[int, int, int, int]) -> str:
	return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{color_tuple[3]}"

# Converts a variable-width list of RGB components to a color code, separated by comma.
#
# component_list: A list of RGBA components as strings which must be integers from 0-255.
# The list must be 3 or 4 items long. If the list is 3 items long, the A component is set to 255.
def color_code_aopt(component_list: list[str]) -> str:
	if (len(component_list) == 4):
		return color_code((int(component_list[0]), int(component_list[1]), int(component_list[2]), int(component_list[3])))
	elif (len(component_list) == 3):
		return color_code((int(component_list[0]), int(component_list[1]), int(component_list[2]), 255))
	else:
		raise ValueError

# Check if any string in broken_text exceeds max_width given some font data.
# Used as a helper for break_text_by_font_width.
#
# broken_text: A list of strings to perform width checks on.
# max_width: The maximum width that the text can be, in pixels.
# font: A PIL FreeTypeFont object that has font data.
#
# Returns the index of the first line that exceeds max_width, or -1 if no line does so.
def none_exceed_max_width(broken_text: list[str], max_width: int, font) -> int:
	for i in range(len(broken_text)):
		width = font.getlength(broken_text[i])
		if (width > max_width):
			return i
	return -1

# Attempts to get the given font from the system's installed fonts.
#
# font: The name of the font.
#
# Returns the path of the font if it was found, otherwise returns a blank string.
def get_system_font(font: str):
	# Get OS to find directories with installed fonts
	paths = []
	os_name = platform.system()
	if (os_name == "Windows"):
		paths = ["C:\\Windows\\fonts"]
	elif (os_name == "Darwin"):
		HOME = str(pathlib.Path.home())
		paths = ["/Library/Fonts/", "/System/Library/Fonts/", f"{HOME}/Library/Fonts/"]
	else:
		if (os_name != "Linux"):
			pwrn("Unsupported OS, font finder may fail.")
		HOME = str(pathlib.Path.home())
		paths = [f"{HOME}/.local/share/fonts/", "/usr/local/share/fonts", "/usr/share/fonts"]

	# Find font
	font_path = ""
	font_found = False
	pdb(f"Finding Font {font}")
	for font_dir in paths:
		for path, subdirs, filenames in os.walk(font_dir):
			for filename in filenames:
				if (font.lower() in filename.lower()):
					font_path = os.path.join(path, filename)
					font_found = True
					break
			if font_found:
				break
		if font_found:
			break

	pdb(f"Path for font {font}: {font_path}")

	return font_path

# Splits a string of text so that, given a font and size, the text does not
# exceed max_width pixels in width.
#
# text: The text content to split
# font: The name of the font to load. Must be a valid TTF/OTF font in the OS's default font directory.
# font_size: The size of the font in pixels.
# max_width: The maximum width that the text can be, in pixels.
#
# Returns an empty list if an error occurred.
def break_text_by_font_width(text: str, font: str, font_size: int, max_width: int) -> list[str]:
	# Attempt to load font
	font_path = get_system_font(font)
	if (font_path == ""):
		return []

	ifont = None
	try:
		ifont = ImageFont.truetype(font_path, font_size)
	except OSError:
		try:
			ifont = ImageFont.load(font_path, font_size)
		except:
			return []

	broken_text = [text]

	long_idx = none_exceed_max_width(broken_text, max_width, ifont)

	while long_idx >= 0:
		# Binary search the long text until an optimal split point is found
		space_split_line = broken_text[long_idx].split(" ")

		l = 0
		r = len(space_split_line) - 1

		while (l <= r):
			i = (r + l) // 2

			split_width = ifont.getlength(" ".join(space_split_line[:i]))

			if (split_width > max_width):
				r = i - 1
			else:
				l = i + 1

		split_point = l
		if (ifont.getlength(" ".join(space_split_line[:split_point])) > max_width):
			split_point = r

		# Split line at that point
		broken_text.insert(long_idx + 1, " ".join(space_split_line[split_point:]))
		broken_text[long_idx] = " ".join(space_split_line[:split_point])

		# Recheck widths
		long_idx = none_exceed_max_width(broken_text, max_width, ifont)

	return broken_text


# Checks a list of parameters for type validity based on the given keyword and corresponding
# command definition.
#
# keyword: The keyword for a given command.
# params: The list of parameters acquired from the command line, as a list of strings.
# modifier: Whether or not to use the modifiers list. This ensures commands with modifier
# keywords are not checked and vice versa.
#
# Returns whether or not the given parameter list is a valid set for the given command.
def check_paramlist_validity(keyword: str, params: list[str], modifier: bool = False) -> bool:
	cmd_def_list = modifiers[keyword] if modifier else commands[keyword]
	pdb(f"Checking if {params} valid")
	for paramlist in cmd_def_list:
		# Check if lengths are equal
		pdb(f"Checking paramlist {paramlist} for match")
		if (len(params) != len(paramlist)):
			continue

		# Go through each type in param list
		bad_params = False
		for i in range(len(paramlist)):
			combined_type = paramlist[i]
			# Split by restriction
			split_type = combined_type.split(";")

			pdb(f"Param {i} ({params[i]}) should be of type {split_type}")

			# Get restriction on range of values if it exists
			split_range = []
			if (len(split_type) >= 2):
				str_split_range = split_type[1].split("-")
				# Add lower bound
				split_range.append(int(str_split_range[0]))
				# Add upper bound
				if (len(str_split_range) > 0 and str_split_range[1] != ""):
					split_range.append(int(str_split_range[1]))

				pdb(f"type has Range LB/UB {split_range}")

			# Check General Type
			match split_type[0]:
				case "int":
					# Check if correct type
					try:
						int(params[i])
					except ValueError:
						bad_params = True
						break
					# Check if out of bounds
					if (len(split_range) > 0):
						if (int(params[i]) < split_range[0]):
							bad_params = True
							break
						if (len(split_range) > 1):
							if (int(params[i]) > split_range[1]):
								bad_params = True
								break
				case "float":
					# Check if correct type
					try:
						float(params[i])
					except ValueError:
						bad_params = True
						break
					# Check if out of bounds
					if (len(split_range) > 0):
						if (float(params[i]) < split_range[0]):
							bad_params = True
							break
						if (len(split_range) > 1):
							if (float(params[i]) > split_range[1]):
								bad_params = True
								break

		if (bad_params):
			continue

		# Types valid and length valid, param list is therefore valid
		return True

	# No valid form found.
	return False


# Parses a single command line.
#
# line: The entire command line to parse.
#
# Returns a tuple containing two elements. The first is the keyword of the command,
# the second is a list of its parameters as a string.
def parse_command(line: str) -> tuple[str, list[str]]:
	# Check if command
	if (line[0:3] != "-=-"):
		return ("ERROR_NOT_COMMAND", [])

	# Get parameter index
	line = line.replace(" ", "")
	param_i = line.find("(")
	param_end_i = line.find(")")

	# Check if no params
	if (param_i == -1):
		param_i = len(line)
	elif (param_end_i == -1):
		return ("ERROR_UNCLOSED_PARAMS", [])

	# Get command keyword
	keyword = line[3:param_i]

	pdb(f"Parsing Command {keyword}")

	if not(keyword in commands):
		return ("ERROR_INVALID_COMMAND", [])

	# Get command parameters (if present)
	params = []
	if (param_i != -1):
		params = line[param_i + 1:param_end_i].split(";")
		if (len(params) == 1 and len(params[0]) == 0):
			params = []

	# Check validity of params
	params_valid = check_paramlist_validity(keyword, params)
	if not(params_valid):
		return (f"ERROR_PARAMVALID", [])

	return (keyword, params)

# Parses the given block for commands, ensuring only commands are present and that
# all commands are valid.
# Assumes that this block has already been determined to be a command block (i.e. contains
# at least one command line).
#
# lines: The list of lines that form this command block.
# line_num: The number of the first line of the command block in the markdown file.
#
# Returns the list of commands as keyword/parameter list pairs, or an empty list if an
# error occurred while parsing.
def parse_commands(lines: list[str], line_num: int) -> list[tuple[str, list[str]]]:
	cmd_list = []
	for i in range(len(lines)):
		keyerr, paramlist = parse_command(lines[i])
		# Check if error
		if not(keyerr in commands):
			match keyerr:
				case "ERROR_NOT_COMMAND":
					print_error("cp", f"Line in Command Block is Not a Command (Line {i + line_num}).")
				case "ERROR_UNCLOSED_PARAMS":
					print_error("cp", f"Unclosed Parameters (Line {i + line_num})")
				case "ERROR_INVALID_COMMAND":
					print_error("cp", f"Unspecified Command (Line {i + line_num})")
				case "ERROR_PARAMVALID":
					print_error("cp", f"Invalid Parameters (Line {i + line_num})")
			return []

		# Add to list
		cmd_list.append((keyerr, paramlist))

	return cmd_list


# Parses the given block for modifiers, ensuring all modifiers are valid.
# See the documentation for more details regarding modifiers and their syntax.
#
# lines: The list of lines that form this command block.
# line_num: The number of the first line of the command block in the markdown file.
#
# Returns the list of modifiers as a dictionary, with the key being the modifier's keyword
# and the value being the list of parameters the modifier has as an all-string list.
def parse_modifiers(lines: list[str], line_num: int) -> dict[str, list[str]]:
	current_modifiers = {}

	for i in range(len(lines)):
		li = lines[i].replace(" ", "")

		# Check if line specifies a modifier
		if li[0:2] == "{{":
			last_i = li.find("}}")
			if (last_i == -1):
				print_error("mp", f"Unclosed Modifier Keyword (Line {i + line_num})")
				return {"error": True}
			else:
				# Get modifier keyword
				keyword = li[2:last_i]

				pdb(f"Parsing Modifier ({keyword})")

				# Get params
				param_i = li.find("(")
				param_end_i = li.find(")")

				params = []
				if (param_i != -1 and param_end_i != -1):
					params = li[param_i + 1:param_end_i].split(";")
					if (len(params) == 1 and len(params[0]) == 0):
						params = []
				if (param_i != -1 and param_end_i == -1 or param_i == -1 and param_end_i != -1):
					print_error("mp", f"Unclosed Parameter Block (Line {i + line_num})")
					return {"error": True}

				params_valid = check_paramlist_validity(keyword, params, modifier=True)
				if not(params_valid):
					print_error("mp", f"Invalid Parameters (Line {i + line_num})")
					return {"error": True}

				# Create Modifier
				current_modifiers[keyword] = params

	current_modifiers["error"] = False
	return current_modifiers


#
# WORKING FUNCTIONS
#

# Converts a list of title clip objects to a Kdenlive project.
# The clips will be placed in the "V2" timeline and have fade in and out effects applied.
def titleclips_to_kdenlive(projdir):
	# Init file
	# NOTE: Currently this only supports 1080p60.

	main_uuid = uuid.uuid4()
	main_uuid_hash = hashlib.md5(f"{{{main_uuid}}}".encode()).hexdigest()

	base_id = 3

	layout = None

	with open(os.path.join(projdir, "titles", f"layout.json"), "r") as layout_json:
		# Read Layout JSON
		layout = json.loads(layout_json.read())

	# Get all clips and arrange by what sequence they will be put in.
	# The last sequence in this list shall be the main sequence.
	sequences = layout_to_sequences(layout)

	seq_data = []

	# Specify IDs for folders
	folders = [
		{
			"id": 1,
			"name": "Sequences",
			"parent": -1
		},
		{
			"id": 2,
			"name": "Titles",
			"parent": -1
		}
	]

	# Create Header
	output = f"""<?xml version='1.0' encoding='utf-8'?>
<mlt LC_NUMERIC="C" producer="main_bin" root="{os.path.abspath(projdir)}" version="7.28.0">
	<profile colorspace="709" description="HD 1080p 60 fps" display_aspect_den="9" display_aspect_num="16" frame_rate_den="1" frame_rate_num="{FRAMERATE}" height="{RES_HEIGHT}" progressive="1" sample_aspect_den="1" sample_aspect_num="1" width="{RES_WIDTH}"/>\n"""

	# Create subsequences
	for i in range(len(sequences) - 1):
		sequence = sequences[i]

		this_seq_folder = {
			"id": base_id,
			"name": f"Section {i + 1}",
			"parent": 2
		}

		folders.append(this_seq_folder)

		seq_out, new_base_id, seq_entry = create_sequence(seq_idx=(i + 1), sequence=sequence, start_id=(base_id + 1), folder_obj=this_seq_folder, projdir=projdir, main_uuid=main_uuid)
		base_id = new_base_id

		output += seq_out
		seq_data.append(seq_entry)

	# Create main sequence blank tracks
	output += prepare_sequence_blanks(0, audio_track_count=1)

	# Create main sequence outer audio track
	output += f"""<playlist id="seq0_a2b1">
<property name="kdenlive:audio_track">1</property>\n"""

	# Calculate the length of the main sequence before all other sequences are added
	len_sum = 0.0
	for i in range(len(sequences[-1])):
		len_sum += sequences[-1][i]["duration_full"]
		if (i < len(sequences[-1]) - 1):
			if ("before_pause" in sequences[-1][i + 1]["modifiers"]):
				len_sum += sequences[-1][i + 1]["modifiers"]["before_pause"]
			else:
				len_sum += SECTION_GAP if i == 0 else CONTENT_GAP

	# Add all other sequences to playlist, calculating the final length of the main sequence.
	for i in range(len(seq_data)):
		this_gap = seq_data[i]["before_pause"]
		output += f"""	<blank length="{seconds_to_timestamp(len_sum + this_gap) if i == 0 else seconds_to_timestamp(this_gap)}"/>
<entry in="00:00:00.000" out="{seconds_to_timestamp(seq_data[i]["seq_dur"])}" producer="{{{seq_data[i]["uuid"]}}}">
	<property name="kdenlive:maxduration">{seconds_to_frames(seq_data[i]["seq_dur"])}</property>
	<property name="kdenlive:id">{seq_data[i]["id"]}</property>
</entry>\n"""
		len_sum += seq_data[i]["seq_dur"] + this_gap

	output += f"""</playlist>
<playlist id="seq0_a2b2">
	<property name="kdenlive:audio_track">1</property>
</playlist>
<tractor id="seq0_tractor2" in="00:00:00.000" out="{seconds_to_timestamp(len_sum)}">
	<property name="kdenlive:audio_track">1</property>
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:collapsed">0</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	<track hide="video" producer="seq0_a2b1"/>
	<track hide="video" producer="seq0_a2b2"/>
	<filter id="seq0_a2_f0">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="seq0_a2_f1">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
	<filter id="seq0_a2_f2">
		<property name="iec_scale">0</property>
		<property name="mlt_service">audiolevel</property>
		<property name="dbpeak">1</property>
		<property name="disable">0</property>
	</filter>
</tractor>\n"""

	# Create main sequence outer video track

	# Create producers
	for i in range(len(sequences[-1])):
		output += title_to_producer(title_obj=sequences[-1][i], projdir=projdir, folder_id=2, clip_id=(base_id + i), producer_id=i, seq_id=0)

	# Create playlist entries for non-sequences
	output += f"""<playlist id="seq0_v2b1">"""
	for i in range(len(sequences[-1])):
		fade_dur = FADE_DURATION if i > 0 else TITLE_FADE_DURATION
		# Add entry
		output += f"""	<entry in="00:00:00.000" out="{seconds_to_timestamp(sequences[-1][i]["duration_time"])}" producer="seq0_clip{i}">
		<property name="kdenlive:id">{base_id + i}</property>

		<filter id="seq0_clip{i}_fadein" out="{seconds_to_timestamp(fade_dur)}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_from_black</property>
			<property name="alpha">00:00:00.000=0;{seconds_to_timestamp(fade_dur)}=1</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
		<filter id="seq0_clip{i}_fadeout" in="{seconds_to_timestamp(sequences[-1][i]["duration_time"] - fade_dur)}" out="{seconds_to_timestamp(sequences[-1][i]["duration_time"])}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_to_black</property>
			<property name="alpha">00:00:00.000=1;{seconds_to_timestamp(fade_dur)}=0</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
	</entry>\n"""

		# Add blank
		if (i < len(sequences[-1]) - 1):
			if ("before_pause" in sequences[-1][i + 1]["modifiers"]):
				output += f"""<blank length="{seconds_to_timestamp(sequences[-1][i + 1]["modifiers"]["before_pause"])}"/>"""
			elif (i == 0):
				output += f"""<blank length="{seconds_to_timestamp(SECTION_GAP)}"/>\n"""
			else:
				output += f"""<blank length="{seconds_to_timestamp(CONTENT_GAP)}"/>\n"""

	base_id += len(sequences[-1])

	# Create playlist entries for sequences
	for i in range(len(seq_data)):
		output += f"""	<blank length="{seconds_to_timestamp(seq_data[i]["before_pause"])}"/>
	<entry in="00:00:00.000" out="{seconds_to_timestamp(seq_data[i]["seq_dur"])}" producer="{{{seq_data[i]["uuid"]}}}">
		<property name="kdenlive:id">{seq_data[i]["id"]}</property>
	</entry>\n"""

	output += f"""</playlist>
<playlist id="seq0_v2b2"/>
<tractor id="seq0_tractor3" in="00:00:00.000" out="{seconds_to_timestamp(len_sum)}">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:collapsed">0</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	<track hide="audio" producer="seq0_v2b1"/>
	<track hide="audio" producer="seq0_v2b2"/>
</tractor>\n"""

	# Define Main Sequence
	output += f"""<tractor id="{{{main_uuid}}}" in="00:00:00.000" out="{seconds_to_timestamp(len_sum)}">
	<property name="kdenlive:duration">{seconds_to_timestamp(len_sum)}</property>
	<property name="kdenlive:maxduration">{seconds_to_frames(len_sum)}</property>
	<property name="kdenlive:clipname">Main Sequence</property>
	<property name="kdenlive:description"/>
	<property name="kdenlive:uuid">{{{main_uuid}}}</property>
	<property name="kdenlive:producer_type">17</property>
	<property name="kdenlive:control_uuid">{{{main_uuid}}}</property>
	<property name="kdenlive:id">{base_id}</property>
	<property name="kdenlive:clip_type">0</property>
	<property name="kdenlive:file_hash">{main_uuid_hash}</property>
	<property name="kdenlive:folderid">1</property>
	<property name="kdenlive:sequenceproperties.activeTrack">3</property>
	<property name="kdenlive:sequenceproperties.audioTarget">1</property>
	<property name="kdenlive:sequenceproperties.disablepreview">0</property>
	<property name="kdenlive:sequenceproperties.documentuuid">{{{main_uuid}}}</property>
	<property name="kdenlive:sequenceproperties.hasAudio">1</property>
	<property name="kdenlive:sequenceproperties.hasVideo">1</property>
	<property name="kdenlive:sequenceproperties.position">0</property>
	<property name="kdenlive:sequenceproperties.scrollPos">0</property>
	<property name="kdenlive:sequenceproperties.tracks">4</property>
	<property name="kdenlive:sequenceproperties.tracksCount">4</property>
	<property name="kdenlive:sequenceproperties.verticalzoom">1</property>
	<property name="kdenlive:sequenceproperties.zonein">0</property>
	<property name="kdenlive:sequenceproperties.zoneout">{seconds_to_frames(len_sum)}</property>
	<property name="kdenlive:sequenceproperties.zoom">8</property>
	<property name="kdenlive:sequenceproperties.groups">[
	]
	</property>
	<property name="kdenlive:sequenceproperties.guides">[
	]
	</property>
	<property name="kdenlive:monitorPosition">0</property>

	<track producer="seq0_blank"/>
	<track producer="seq0_tractor0"/>
	<track producer="seq0_tractor2"/>
	<track producer="seq0_tractor1"/>
	<track producer="seq0_tractor3"/>\n"""

	# Add blank space mixes
	for i in range(4):
		output += f"""	<transition id="transition0">
		<property name="a_track">0</property>
		<property name="b_track">{i + 1}</property>
		<property name="mlt_service">mix</property>
		<property name="kdenlive_id">mix</property>
		<property name="internal_added">237</property>
		<property name="always_active">1</property>
		<property name="accepts_blanks">1</property>
		<property name="sum">1</property>
	</transition>\n"""

	# Add default filters
	output += f"""	<filter id="seq0_filter0">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="seq0_filter1">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
</tractor>\n"""

	# Add main_bin
	all_seq_uuids = ""
	for entry in seq_data:
		all_seq_uuids += f'{{{entry["uuid"]}}}' + ";"
	all_seq_uuids = all_seq_uuids[:-1]

	output += f"""<playlist id="main_bin">\n"""

	for entry in folders:
		output += f"""	<property name="kdenlive:folder.{entry["parent"]}.{entry["id"]}">{entry["name"]}</property>"""

	output += f"""
	<property name="kdenlive:sequenceFolder">1</property>
	<property name="kdenlive:docproperties.activetimeline">{{{main_uuid}}}</property>
	<property name="kdenlive:docproperties.audioChannels">2</property>
	<property name="kdenlive:docproperties.binsort">100</property>
	<property name="kdenlive:docproperties.browserurl">./</property>
	<property name="kdenlive:docproperties.documentid">{round(time.time())}</property>
	<property name="kdenlive:docproperties.enableTimelineZone">0</property>
	<property name="kdenlive:docproperties.enableexternalproxy">0</property>
	<property name="kdenlive:docproperties.enableproxy">0</property>
	<property name="kdenlive:docproperties.externalproxyparams">./;;.LRV;./;;.MP4</property>
	<property name="kdenlive:docproperties.generateimageproxy">0</property>
	<property name="kdenlive:docproperties.generateproxy">0</property>
	<property name="kdenlive:docproperties.guidesCategories">[
		{{
			"color": "#9b59b6",
			"comment": "Category 1",
			"index": 0
		}},
		{{
			"color": "#3daee9",
			"comment": "Category 2",
			"index": 1
		}},
		{{
			"color": "#1abc9c",
			"comment": "Category 3",
			"index": 2
		}},
		{{
			"color": "#1cdc9a",
			"comment": "Category 4",
			"index": 3
		}},
		{{
			"color": "#c9ce3b",
			"comment": "Category 5",
			"index": 4
		}},
		{{
			"color": "#fdbc4b",
			"comment": "Category 6",
			"index": 5
		}},
		{{
			"color": "#f39c1f",
			"comment": "Category 7",
			"index": 6
		}},
		{{
			"color": "#f47750",
			"comment": "Category 8",
			"index": 7
		}},
		{{
			"color": "#da4453",
			"comment": "Category 9",
			"index": 8
		}}
	]
	</property>
	<property name="kdenlive:docproperties.kdenliveversion">24.12.0</property>
	<property name="kdenlive:docproperties.opensequences">{all_seq_uuids}</property>
	<property name="kdenlive:docproperties.previewextension"/>
	<property name="kdenlive:docproperties.previewparameters"/>
	<property name="kdenlive:docproperties.profile">atsc_1080p_60</property>
	<property name="kdenlive:docproperties.proxyextension"/>
	<property name="kdenlive:docproperties.proxyimageminsize">2000</property>
	<property name="kdenlive:docproperties.proxyimagesize">800</property>
	<property name="kdenlive:docproperties.proxyminsize">1000</property>
	<property name="kdenlive:docproperties.proxyparams"/>
	<property name="kdenlive:docproperties.proxyresize">640</property>
	<property name="kdenlive:docproperties.seekOffset">30000</property>
	<property name="kdenlive:docproperties.sessionid">{{{uuid.uuid4()}}}</property>
	<property name="kdenlive:docproperties.uuid">{{{main_uuid}}}</property>
	<property name="kdenlive:docproperties.version">1.1</property>
	<property name="kdenlive:expandedFolders">1;2</property>
	<property name="kdenlive:binZoom">4</property>
	<property name="kdenlive:extraBins">project_bin:-1:0</property>
	<property name="kdenlive:documentnotes"/>
	<property name="kdenlive:documentnotesversion">2</property>
	<property name="xml_retain">1</property>\n"""

	pdb(sequences)

	# Add entries for all clips
	for i in range(len(sequences)):
		for j in range(len(sequences[i])):
			output += f"""	<entry in="00:00:00.000" out="{seconds_to_timestamp(sequences[i][j]["duration_time"])}" producer="seq{(i + 1) % len(sequences)}_clip{j}"/>\n"""

	# Add entries for all sequences
	for i in range(len(seq_data)):
		output += f"""	<entry in="00:00:00.000" out="{seconds_to_timestamp(seq_data[i]["seq_dur"])}" producer="{{{seq_data[i]["uuid"]}}}"/>"""

	# Add main sequence entry
	output += f"""<entry in="00:00:00.000" out="00:01:06.800" producer="{{{main_uuid}}}"/>\n"""

	output += f"""</playlist>
<tractor id="main_tractor" in="00:00:00.000" out="{seconds_to_timestamp(len_sum)}">
	<property name="kdenlive:projectTractor">1</property>
	<track in="00:00:00.000" out="{seconds_to_timestamp(len_sum)}" producer="{{{main_uuid}}}"/>
</tractor></mlt>"""

	with open(os.path.join(projdir, "project.kdenlive"), "w") as project_file:
		project_file.write(output)



# Converts clip data into title clip objects, which feature the clip's XML definition
# and the timestamp where the clip is to be placed.
def clip_data_to_titleclips(cd, projdir):
	tc_data = []

	section_idx = 0
	content_idx = 0

	if not(os.path.exists(os.path.join(projdir, "titles"))):
		os.mkdir(os.path.join(projdir, "titles"))

	# Go through each clip in the clip data
	for i in range(len(cd)):
		clip = cd[i]
		tc_entry = {}

		# Set durations
		tc_entry["duration_frames"] = round(clip["duration"] * FRAMERATE)
		tc_entry["duration_full"] = r3(clip["duration"])
		tc_entry["duration_time"] = r3(clip["duration"] - (1.0 / FRAMERATE))

		data = f"""<kdenlivetitle LC_NUMERIC="C" duration_frames="{tc_entry["duration_frames"]}" height="{RES_HEIGHT}" out="{tc_entry["duration_frames"]}" width="{RES_WIDTH}">\n"""

		# Pass modifiers to title clip processor in case they are needed (e.g. before_pause)
		tc_entry["modifiers"] = clip["modifiers"]

		# Set default formatting
		y_pos = 0
		clip_content = clip["content"]

		# Get modifiers/default values
		clip_color = color_code_aopt(clip["modifiers"]["color"]) if "color" in clip["modifiers"] else color_code(FONT_COLOR)
		clip_outline_color = color_code_aopt(clip["modifiers"]["outline_color"]) if "outline_color" in clip["modifiers"] else color_code(FONT_OUTLINE_COLOR)

		clip_font = FONT_NAME
		if ("font" in clip["modifiers"]):
			sf = get_system_font(clip["modifiers"]["font"][0])
			if (sf != ""):
				clip_font = clip["modifiers"]["font"][0]
			else:
				pwrn(f"Font modifier for block {i} ({clip_content}) could not be applied due to invalid font.")

		# Apply remaining modifiers
		clip_font_size = 0
		if ("font_size" in clip["modifiers"]):
			clip_font_size = int(clip["modifiers"]["font_size"][0])

		clip_outline_width = int(clip["modifiers"]["outline_width"][0]) if "outline_width" in clip["modifiers"] else FONT_OUTLINE_THICK

		match clip["type"]:
			case "title":
				# Set Values
				tc_entry["ref"] = "title"
				if (clip_font_size) == 0:
					clip_font_size = TITLE_FONT_SIZE

				# get y positions
				y_pos = RES_HEIGHT // 2
				if ("y" in clip["modifiers"]):
					y_pos = int(clip["modifiers"]["y"][0])
				y_pos -= clip_font_size // 2
				subtitle_y_pos = y_pos + clip_font_size + TITLE_GAP
				supertitle_y_pos = y_pos - TITLE_GAP - SUPERTITLE_FONT_SIZE

				# Add optional subtitle
				if ("subtitle" in clip):
					data += f""" <item type="QGraphicsTextItem" z-index="2">
  <position x="0" y="{subtitle_y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(SUBTITLE_FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{SUBTITLE_FONT_SIZE}" font-underline="0" font-weight="{SUBSUPER_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="1;#80000000;4;0;4" tab-width="80" typewriter="0;2;1;0;0">{clip["subtitle"]}</content>
 </item>\n"""

				# Add optional supertitle
				if ("supertitle" in clip):
					data += f""" <item type="QGraphicsTextItem" z-index="1">
  <position x="0" y="{supertitle_y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(SUPERTITLE_FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{SUPERTITLE_FONT_SIZE}" font-underline="0" font-weight="{SUBSUPER_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="1;#80000000;4;0;4" tab-width="80" typewriter="0;2;1;0;0">{clip["supertitle"]}</content>
 </item>\n"""
			case "section":
				# Set Values
				section_idx += 1
				content_idx = 0

				tc_entry["ref"] = f"section_{section_idx}"
				if (clip_font_size) == 0:
					clip_font_size = SECTION_FONT_SIZE

				# create section clip
				y_pos = RES_HEIGHT // 2
				if ("y" in clip["modifiers"]):
					y_pos = int(clip["modifiers"]["y"][0])
				y_pos -= clip_font_size // 2
			case "content":
				# Set Values
				content_idx += 1
				tc_entry["ref"] = f"content_s{section_idx}_c{content_idx}"
				if (clip_font_size) == 0:
					clip_font_size = FONT_SIZE

				# split this content so that it fits on screen width-wise.
				lines = break_text_by_font_width(clip["content"], clip_font, clip_font_size, MAX_CONTENT_WIDTH)
				if (len(lines) == 0):
					print_error("tc", f"Font for clip ({clip_font}) could not be found.")
					sys.exit()

				clip_content = "\n".join(lines)

				# Get Y from Y_CENTER
				y_pos = Y_CENTER
				if ("y" in clip["modifiers"]):
					y_pos = int(clip["modifiers"]["y"][0])
				y_pos -= round((len(lines) / 2.0) * clip_font_size)

		# Add main title
		data += f""" <item type="QGraphicsTextItem" z-index="0">
  <position x="{(RES_WIDTH - MAX_CONTENT_WIDTH) // 2}" y="{y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{MAX_CONTENT_WIDTH}" font="{clip_font}" font-color="{clip_color}" font-italic="0" font-outline="{clip_outline_width}" font-outline-color="{clip_outline_color}" font-pixel-size="{clip_font_size}" font-underline="0" font-weight="{FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="1;#80000000;4;0;4" tab-width="80" typewriter="0;2;1;0;0">{clip_content}</content>
 </item>
 <startviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <endviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <background color="0,0,0,0"/>
</kdenlivetitle>"""

		# Write kdenlivetitle XML to file
		with open(os.path.join(projdir, "titles", f"{tc_entry["ref"]}.kdenlivetitle"), "w") as klt:
			if (data != ""):
				klt.write(data)

		tc_data.append(tc_entry)

	# Write title clip data to layout.json within the titles folder in the project directory.
	with open(os.path.join(projdir, "titles", f"layout.json"), "w") as jsc:
		jsc.write(json.dumps(tc_data))


# Parses a markdown script file for text content.
# Currently, the markdown file must have the following properties:
# - frontmatter with at least a title field at the very start of the file
#   - subtitle, supertitle, and other fields are optional, with subtitle and supertitle being read
# - one empty line after frontmatter
# - at least one line of content
#   - lines are "section titles" if they start with ##
#   - all other lines are treated as normal text
#   - all content lines must have an empty line in between.
def parse_file(f):
	# Initialize title clip
	clip_data = [
		{
			"type": "title",
			"duration": TITLE_DURATION + TITLE_FADE_DURATION
		}
	]

	# Read script
	with open(f) as inp:
		# Frontmatter check 1
		line = inp.readline()
		if (line != "---\n"):
			print_error("dp", "Markdown does not start with frontmatter")
			return []

		# Parse frontmatter
		line = inp.readline()
		title_lines = [line[:-1]]
		line_no = 1
		while (line != "---\n" and line != ""):
			lt = line[:-1]
			# Get title field
			if ("title:" in lt[0:6]):
				clip_data[0]["content"] = lt[7:]

			# Get subtitle field
			if ("subtitle:" in lt[0:9]):
				clip_data[0]["subtitle"] = lt[10:]

			# Get supertitle field
			if ("supertitle:" in lt[0:11]):
				clip_data[0]["supertitle"] = lt[12:]

			line = inp.readline()
			title_lines.append(line[:-1])
			line_no += 1

		clip_data[0]["modifiers"] = parse_modifiers(title_lines, 1)

		# Frontmatter check 2
		if (line != "---\n" or not "content" in clip_data[0]):
			if (line != "---\n"):
				print_error("dp", "Frontmatter incomplete.")
			else:
				print_error("dp", "No 'title' field in frontmatter.")
			return []

		# Content check
		line = inp.readline()
		line = inp.readline()
		line_no += 2
		if (line == ""):
			print_error("dp", "At least one line of text/section header/command must be present in the document.")
			return []

		# Command flags, used for next block
		cmd_flags = {
			"pause": -1,
			"ignore": False
		}

		# Parse content
		while (line != ""):
			# Get lines in block
			lines = []

			while (line != "\n" and line != ""):
				# Eliminate Comments
				if (line[:3] != "/=/"):
					lines.append(line[:-1])
				line = inp.readline()
				line_no += 1

			pdb(f"Block Read: {lines} (now @{line_no})")

			if (len(lines) == 0):
				line = inp.readline()
				line_no += 1
				continue

			# Check if this is a command block
			command_block = False
			for line in lines:
				if (line[0:3] == "-=-"):
					# Command block
					command_block = True
					command_list = parse_commands(lines, line_no - len(lines) + 1)

					if (command_list == []):
						print_error("dp", "An error occurred while parsing a command block.")
						return []
					else:
						# Process Commands
						for command_pair in command_list:
							match command_pair[0]:
								case "pause":
									cmd_flags["pause"] = command_pair[1][0]
								case "ignore":
									cmd_flags["ignore"] = True
			if (command_block):
				line = inp.readline()
				line_no += 1
				continue

			# Not a command block.

			# Check if ignore
			if (cmd_flags["ignore"]):
				cmd_flags["ignore"] = False
				line = inp.readline()
				line_no += 1
				continue

			this_clip = {}

			# Coalesce lines into content
			block_text = ""
			modifiers_present = False
			for line in lines:
				if (line[0:2] != "{{"):
					# Add to block, stripping unnecessary whitespace
					block_text += line.strip() + " "
				else:
					modifiers_present = True
			block_text = block_text[:-1]
			pdb(f"CONTENT: [{block_text}]")

			# Check if contentless block has modifiers
			if (modifiers_present and block_text == ""):
				print_error("dp", "Modifier present with No Content.")
				return []

			# Parse for modifiers
			this_clip["modifiers"] = parse_modifiers(lines, line_no - len(lines) + 1)
			if (this_clip["modifiers"]["error"]):
				return []

			if (block_text[0:2] == "##"):
				# section clip
				this_clip["type"] = "section"
				this_clip["duration"] = SECTION_DURATION + FADE_DURATION * 2

				this_clip["content"] = block_text[3:]
			else:
				# content clip
				this_clip["type"] = "content"

				wc = len(block_text.split(" "))

				# Get duration_frames as a function of reading speed relative to # words
				# multiplied by a factor which shortens the clip length as longer
				# texts are entered
				this_clip["duration"] = r3((wc / READ_SPEED) * (2 ** (-0.01 * wc)))
				# Add fade time
				this_clip["duration"] += FADE_DURATION * 2

				this_clip["content"] = block_text

			# Pause command
			if (cmd_flags["pause"] != -1):
				this_clip["modifiers"]["before_pause"] = float(cmd_flags["pause"])
				cmd_flags["pause"] = -1

			clip_data.append(this_clip)

			line = inp.readline()
			line_no += 1

	pdb(f"CLIPS: {clip_data}")

	return clip_data


# Gets the index of the given flag in sys.argv if it exists.
# If it does not exist, returns -1.
#
# shorthand: The flag's shorthand (e.g. h)
# longhand: The flag's full name (e.g. help)
def get_flag_idx(shorthand: str, longhand: str) -> int:
	try:
		return sys.argv.index(f"-{shorthand}")
	except:
		try:
			return sys.argv.index(f"--{longhand}")
		except:
			return -1

# Gets the argument for the given flag.
# Note: This does not work for longhand arguments adjacent to the flag, e.g. --opt=2
#
# shorthand: The flag's shorthand (e.g. h)
# longhand: The flag's full name (e.g. help)
#
# Returns the argument for this flag, as a string.
def get_flag_arg(shorthand: str, longhand: str) -> str:
	idx = get_flag_idx(shorthand, longhand)

	# Index Check
	if (idx == -1 or idx == len(sys.argv) - 1):
		return ""

	# Get argument
	return sys.argv[idx + 1]


def parse_flags():
	if (get_flag_idx("h", "help") >= 0):
		print("kdenlive title generator")
		print()
		print("Usage: python3 tgen.py [options] -f [file] -d [directory]")
		print("Required Flags:")
		print("  -f\t")
		print("  --file\tSpecify a markdown script to convert.")
		print("  -d\t")
		print("  --directory\tSpecify a directory to save all title clips.")
		print("Options:")
		print("  -n\t")
		print("  --no-proj\tDo not create a project file in this run. Only title clips will be")
		print("              \tcreated or modified.")
		sys.exit()


def main():
	# Get script as second CLI argument.
	parse_flags()
	CFG_FILE = get_flag_arg("f", "file")
	CFG_PROJDIR = get_flag_arg("d", "directory")

	NO_PROJECT = get_flag_idx("n", "no-proj") != -1

	if not os.path.isfile(CFG_FILE) or not os.path.isdir(CFG_PROJDIR):
		if os.path.isfile(CFG_FILE):
			print("Making project directory...")
			os.mkdir(CFG_PROJDIR)
		else:
			print("Invalid file or directory. Both are required.")
			sys.exit()

	# Parse script
	print("Parsing Script...")
	cdata = parse_file(CFG_FILE)
	if (cdata == []):
		print("Invalid Markdown Script!")
		sys.exit()

	print("Creating Title Clips...")
	clip_data_to_titleclips(cdata, CFG_PROJDIR)

	if (not NO_PROJECT):
		print("Creating Project...")
		titleclips_to_kdenlive(CFG_PROJDIR)

main()

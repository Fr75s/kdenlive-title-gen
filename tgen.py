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

# duration of the title clip (the first clip) in seconds
TITLE_DURATION = 6.0

# duration of a section clip in seconds
SECTION_DURATION = 3.0

# gap before and after a section/title clip where no text is shown
SECTION_GAP = 1.5

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
# IMPORTS
#

from PIL import ImageFont
import os, sys, json, math, uuid, hashlib

CFG_FILE = ""
CFG_PROJDIR = ""

#
# UTILITY FUNCTIONS
#

# Rounds the given value to 3 decimal places.
def r3(value: float) -> float:
	return round(value * 1000.0) / 1000.0

# titleclips_to_kdenlive Helpers

# Pads an integer with a leading zero if it is less than 10.
def pad2(val: int) -> str:
	if (val < 10):
		return f"0{val}"
	return f"{val}"

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

	print(int_sec)

	return f"{pad2(hours)}:{pad2(minutes)}:{pad2(int_sec % 60)}.{str(r3(seconds - int_sec))[2:]}"

# Converts a title object which refers to a .kdenlivetitle file to a MLT producer.
def title_to_producer(title_obj: dict, projdir: str, folder_id: int, clip_id: int, producer_id: int) -> str:
	file_hash = hashlib.md5(open(os.path.join(projdir, "titles", f"{title_obj["ref"]}.kdenlivetitle"), 'rb').read()).hexdigest()

	new_uuid = uuid.uuid4()

	# NOTES:
	# producer id should be unique
	# in/out in producer is length of clip - 1 frame
	# length is duration in frames (integer)
	# resource is resource reference (e.g. file)
	# kdenlive:duration is duration in hh:mm:ss:ff, where ff is frames
	# id should be unique ??
	# xml was here seems useless??
	# clip_type is always 2 for title clips, 0 for sequence clips
	# file_hash doesn't seem to match up with hash of the file??
	# control_uuid is just a random UUID

	# kdenlive:id (& by extension clip_id) can be seen in tractors (clip_type 0) too.
	# producer_id is only seen in producers (clip_type 2).

	return f""" <producer id="producer{producer_id}" in="00:00:00.000" out="{seconds_to_timestamp(title_obj["abs_out"])}">
  <property name="length">{title_obj["duration"]}</property>
  <property name="eof">pause</property>
  <property name="resource">titles/{title_obj["ref"]}.kdenlivetitle</property>
  <property name="meta.media.progressive">1</property>
  <property name="aspect_ratio">1</property>
  <property name="seekable">1</property>
  <property name="mlt_service">kdenlivetitle</property>
  <property name="kdenlive:duration">{frames_to_timestamp(title_obj["duration"])}</property>
  <property name="xml">was here</property>
  <property name="kdenlive:folderid">{folder_id}</property>
  <property name="kdenlive:id">{clip_id}</property>
  <property name="kdenlive:control_uuid">{{{new_uuid}}}</property> ***
  <property name="kdenlive:clip_type">2</property>
  <property name="kdenlive:file_hash">{file_hash}</property> ***
  <property name="force_reload">0</property>
  <property name="meta.media.width">{RES_WIDTH}</property>
  <property name="meta.media.height">{RES_HEIGHT}</property>
  <property name="kdenlive:monitorPosition">0</property>
 </producer>"""


# clip_data_to_titleclips Helpers

# Converts a color tuple to a color code, separated by comma.
def color_code(color_tuple: tuple[int, int, int, int]) -> str:
	return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{color_tuple[3]}"

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
	ifont = None
	try:
		ifont = ImageFont.truetype(font + ".ttf", font_size)
	except OSError:
		try:
			ifont = ImageFont.truetype(font + ".otf", font_size)
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


#
# WORKING FUNCTIONS
#

# Converts a list of title clip objects to a Kdenlive project.
# The clips will be placed in the "V2" timeline and have fade in and out effects applied.
def titleclips_to_kdenlive(projdir):
	# Init file
	# NOTE: Currently this only supports 1080p60.
	doc = f"""<?xml version='1.0' encoding='utf-8'?>
<mlt LC_NUMERIC="C" producer="main_bin" root="{projdir}" version="7.28.0">
	<profile colorspace="709" description="HD 1080p 60 fps" display_aspect_den="9" display_aspect_num="16" frame_rate_den="1" frame_rate_num="60" height="1080" progressive="1" sample_aspect_den="1" sample_aspect_num="1" width="1920"/>

	<producer id="producer0" in="00:00:00.000" out="00:05:00.000">
		<property name="length">2147483647</property>
		<property name="eof">continue</property>
		<property name="resource">black</property>
		<property name="aspect_ratio">1</property>
		<property name="mlt_service">color</property>
		<property name="kdenlive:playlistid">black_track</property>
		<property name="mlt_image_format">rgba</property>
		<property name="set.test_audio">0</property>
	</producer>
		<producer id="producer1" in="00:00:00.000" out="00:05:00.000">
		<property name="length">2147483647</property>
		<property name="eof">continue</property>
		<property name="resource">0</property>
		<property name="aspect_ratio">1</property>
		<property name="mlt_service">color</property>
		<property name="kdenlive:playlistid">black_track</property>
		<property name="mlt_image_format">yuv422</property>
		<property name="set.test_audio">0</property>
	</producer>"""

	with open(os.path.join(projdir, "titles", f"layout.json"), "r") as layout_json:
		layout = json.loads(layout_json.read())

		# Prepare IDs
		producer_id = 2
		folder_id = 3 # Folder 2 used for Sequences
		clip_id = 4 # ID 3 used for main_bin

		current_sequence = 0

		# Start going through each set of clips
		for clip in layout[1:]:
			print(title_to_producer(clip, projdir, folder_id, clip_id, producer_id))

		# Add title clip and rearrange


# Converts clip data into title clip objects, which feature the clip's XML definition
# and the timestamp where the clip is to be placed.
def clip_data_to_titleclips(cd, projdir):
	tc_data = []
	current_time = 0.0

	section_idx = 0
	content_idx = 0

	if not(os.path.exists(os.path.join(projdir, "titles"))):
		os.mkdir(os.path.join(projdir, "titles"))

	for i in range(len(cd)):
		clip = cd[i]
		tc_entry = {}

		data = ""

		match clip["type"]:
			case "title":
				# get duration
				duration = round(clip["duration"] * FRAMERATE)

				# get y positions
				title_y_pos = RES_HEIGHT // 2 - TITLE_FONT_SIZE // 2
				subtitle_y_pos = title_y_pos + TITLE_FONT_SIZE + TITLE_GAP
				supertitle_y_pos = title_y_pos - TITLE_GAP - SUPERTITLE_FONT_SIZE

				data = f"""<kdenlivetitle LC_NUMERIC="C" duration="{duration}" height="{RES_HEIGHT}" out="{duration}" width="{RES_WIDTH}">
 <item type="QGraphicsTextItem" z-index="2">
  <position x="0" y="{subtitle_y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(SUBTITLE_FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{SUBTITLE_FONT_SIZE}" font-underline="0" font-weight="{SUBSUPER_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="0;#64000000;3;3;3" tab-width="80" typewriter="0;2;1;0;0">{clip["subtitle"]}</content>
 </item>
 <item type="QGraphicsTextItem" z-index="1">
  <position x="0" y="{supertitle_y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(SUPERTITLE_FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{SUPERTITLE_FONT_SIZE}" font-underline="0" font-weight="{SUBSUPER_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="0;#64000000;3;3;3" tab-width="80" typewriter="0;2;1;0;0">{clip["supertitle"]}</content>
 </item>
 <item type="QGraphicsTextItem" z-index="0">
  <position x="0" y="{title_y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{TITLE_FONT_SIZE}" font-underline="0" font-weight="{TITLE_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="0;#64000000;3;3;3" tab-width="80" typewriter="0;2;1;0;0">{clip["title"]}</content>
 </item>
 <startviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <endviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <background color="0,0,0,0"/>
</kdenlivetitle>"""

				# Set Values
				tc_entry["start"] = r3(current_time)
				tc_entry["out"] = r3(current_time + TITLE_DURATION - (1.0 / FRAMERATE))
				tc_entry["ref"] = "title"
				tc_entry["duration"] = duration
				tc_entry["abs_out"] = r3(TITLE_DURATION - (1.0 / FRAMERATE))

				# adjust time
				current_time += TITLE_DURATION + SECTION_GAP
			case "section":
				# adjust if previous clip was content
				if (cd[i - 1]["type"] == "content"):
					current_time += SECTION_GAP - CONTENT_GAP
				# create section clip

				# get duration
				duration = round(clip["duration"] * FRAMERATE)

				y_pos = RES_HEIGHT // 2 - SECTION_FONT_SIZE // 2

				data = f"""<kdenlivetitle LC_NUMERIC="C" duration="{duration}" height="{RES_HEIGHT}" out="{duration}" width="{RES_WIDTH}">
 <item type="QGraphicsTextItem" z-index="0">
  <position x="0" y="{y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{RES_WIDTH}" font="{FONT_NAME}" font-color="{color_code(FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{SECTION_FONT_SIZE}" font-underline="0" font-weight="{TITLE_FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="0;#ff000000;8;0;0" tab-width="80" typewriter="0;2;1;0;0">{clip["content"]}</content>
 </item>
 <startviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <endviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <background color="0,0,0,0"/>
</kdenlivetitle>"""

				# Set Values
				section_idx += 1
				content_idx = 0

				tc_entry["start"] = r3(current_time)
				tc_entry["out"] = r3(current_time + clip["duration"] - (1.0 / FRAMERATE))
				tc_entry["ref"] = f"section_{section_idx}"
				tc_entry["duration"] = duration
				tc_entry["abs_out"] = r3(clip["duration"] - (1.0 / FRAMERATE))

				# adjust time
				current_time += clip["duration"] + SECTION_GAP
			case "content":
				# create content clip

				# get duration
				duration = round(clip["duration"] * FRAMERATE)
				# split this content so that it fits on screen width-wise.
				lines = break_text_by_font_width(clip["content"], FONT_NAME, FONT_SIZE, MAX_CONTENT_WIDTH)

				# Get Y from Y_CENTER
				y_pos = Y_CENTER - round((len(lines) / 2.0) * FONT_SIZE)

				# Form XML data
				data = f"""<kdenlivetitle LC_NUMERIC="C" duration="{duration}" height="{RES_HEIGHT}" out="{duration}" width="{RES_WIDTH}">
 <item type="QGraphicsTextItem" z-index="0">
  <position x="{(RES_WIDTH - MAX_CONTENT_WIDTH) // 2}" y="{y_pos}">
   <transform>1,0,0,0,1,0,0,0,1</transform>
  </position>
  <content alignment="4" box-height="{RES_HEIGHT}" box-width="{MAX_CONTENT_WIDTH}" font="{FONT_NAME}" font-color="{color_code(FONT_COLOR)}" font-italic="0" font-outline="{FONT_OUTLINE_THICK}" font-outline-color="{color_code(FONT_OUTLINE_COLOR)}" font-pixel-size="{FONT_SIZE}" font-underline="0" font-weight="{FONT_WEIGHT}" letter-spacing="0" line-spacing="0" shadow="0;#ff000000;8;0;0" tab-width="80" typewriter="0;2;1;0;0">{"\n".join(lines)}</content>
 </item>
 <startviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <endviewport rect="0,0,{RES_WIDTH},{RES_HEIGHT}"/>
 <background color="0,0,0,0"/>
</kdenlivetitle>"""

				# Set Values
				content_idx += 1

				tc_entry["start"] = r3(current_time)
				tc_entry["out"] = r3(current_time + clip["duration"] - (1.0 / FRAMERATE))
				tc_entry["ref"] = f"content_s{section_idx}_c{content_idx}"
				tc_entry["duration"] = duration
				tc_entry["abs_out"] = r3(clip["duration"] - (1.0 / FRAMERATE))

				# adjust time
				current_time += clip["duration"] + CONTENT_GAP

		with open(os.path.join(projdir, "titles", f"{tc_entry["ref"]}.kdenlivetitle"), "w") as klt:
			if (data != ""):
				klt.write(data)

		tc_data.append(tc_entry)

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
			return []

		# Parse frontmatter
		line = inp.readline()
		while (line != "---\n" and line != ""):
			lt = line[:-1]
			# Get title field
			if ("title:" in lt[0:6]):
				clip_data[0]["title"] = lt[7:]

			# Get subtitle field
			if ("subtitle:" in lt[0:9]):
				clip_data[0]["subtitle"] = lt[10:]

			# Get supertitle field
			if ("supertitle:" in lt[0:11]):
				clip_data[0]["supertitle"] = lt[12:]

			line = inp.readline()

		# Frontmatter check 2
		if (line != "---\n" or not "title" in clip_data[0]):
			return []

		# Content check
		line = inp.readline()
		line = inp.readline()
		if (line == ""):
			return []

		# Parse content
		while (line != ""):
			lt = line[:-1]

			this_clip = {}

			if (lt[0:2] == "##"):
				# section clip
				this_clip["type"] = "section"
				this_clip["duration"] = SECTION_DURATION + FADE_DURATION * 2

				this_clip["content"] = lt[3:]
			else:
				# content clip
				this_clip["type"] = "content"

				wc = len(lt.split(" "))

				# Get duration as a function of reading speed relative to # words
				# multiplied by a factor which shortens the clip length as longer
				# texts are entered
				this_clip["duration"] = r3((wc / READ_SPEED) * (2 ** (-0.01 * wc)))
				# Add fade time
				this_clip["duration"] += FADE_DURATION * 2

				this_clip["content"] = lt

			clip_data.append(this_clip)

			line = inp.readline()
			line = inp.readline()

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
		print("Options:")
		print("  -f\t")
		print("  --file\tSpecify a markdown script to convert.")
		print("  -d\t")
		print("  --directory\tSpecify a directory to save all title clips.")
		print("  -n\t")
		print("  --nosave\tDo not save title clips as separate files. This will bundle all")
		print("\t\tClips in the project itself. Not recommended unless the script is small.")
		sys.exit()


def main():
	# Get script as second CLI argument.
	parse_flags()
	CFG_FILE = get_flag_arg("f", "file")
	CFG_PROJDIR = get_flag_arg("d", "directory")

	if not os.path.isfile(CFG_FILE) or not os.path.isdir(CFG_PROJDIR):
		print("Invalid file or directory. Both are required.")
		sys.exit()

	# Parse script
	cdata = parse_file(CFG_FILE)
	if (cdata == []):
		print("Invalid Markdown Script!")
		sys.exit()

	clip_data_to_titleclips(cdata, CFG_PROJDIR)

	titleclips_to_kdenlive(CFG_PROJDIR)

main()

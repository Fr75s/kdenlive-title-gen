from constants import *

#
# A series of template Macros for various XML data.
#

# Title Clip Producer
def template_TITLE_PRODUCER(seq_id: int, clip_id: int, out: str, length: str, titlepath: str, duration: str, duration_frames: str, folder_id: int, unique_id: int, uuid: str, file_hash: str) -> str:
	return f"""<producer id="seq{seq_id}_clip{clip_id}" in="00:00:00.000" out="{out}">
	<property name="length">{length}</property>
	<property name="eof">pause</property>
	<property name="resource">{titlepath}</property>
	<property name="meta.media.progressive">1</property>
	<property name="aspect_ratio">1</property>
	<property name="seekable">1</property>
	<property name="mlt_service">kdenlivetitle</property>
	<property name="kdenlive:duration">{duration}</property>
	<property name="kdenlive:duration_frames">{duration_frames}</property>
	<property name="xml">was here</property>
	<property name="kdenlive:folderid">{folder_id}</property>
	<property name="kdenlive:id">{unique_id}</property>
	<property name="kdenlive:control_uuid">{uuid}</property>
	<property name="kdenlive:clip_type">2</property>
	<property name="kdenlive:file_hash">{file_hash}</property>
	<property name="force_reload">0</property>
	<property name="meta.media.width">{RES_WIDTH}</property>
	<property name="meta.media.height">{RES_HEIGHT}</property>
	<property name="kdenlive:monitorPosition">0</property>
</producer>\n"""



# Playlist Clip Entry
def template_PLAYLIST_ENTRY(seq_idx: int, pl_idx: int, unique_id: int, entry_out: str, fadein_out: str, fadeout_in: str) -> str:
	return f"""	<entry in="00:00:00.000" out="{entry_out}" producer="seq{seq_idx}_clip{pl_idx}">
		<property name="kdenlive:id">{unique_id}</property>
		<filter id="seq{seq_idx}_clip{pl_idx}_fadein" out="{fadein_out}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_from_black</property>
			<property name="alpha">00:00:00.000=0;{fadein_out}=1</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
		<filter id="seq{seq_idx}_clip{pl_idx}_fadeout" in="{fadeout_in}" out="{entry_out}">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_to_black</property>
			<property name="alpha">00:00:00.000=1;{fadein_out}=0</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
	</entry>\n"""



# Playlist Blank
def template_PLAYLIST_BLANK(duration: str):
	return f"""<blank length="{duration}"/>\n"""



# main_bin entry
def template_MAIN_BIN_ENTRY(duration: str, producer: str):
	return f"""<entry in="00:00:00.000" out="{duration}" producer="{producer}"/>\n"""

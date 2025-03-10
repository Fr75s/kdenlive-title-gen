# sample.kdenlive readthrough

This document walks through the .kdenlive file generated from sample.md, documenting how a .kdenlive file is formed and how video sequences are defined.

```xml
<?xml version='1.0' encoding='utf-8'?>
```

Standard XML Versioning. This is present in pretty much all XML documents.

```xml
<mlt LC_NUMERIC="C" producer="main_bin" root="{{1}}" version="7.28.0">
```

Outermost tag of the document, specifying the beginning of the actual content.

- LC_NUMERIC: unknown.
- main_bin: referred to later, used to specify the main video.
- root: The root path of all items used in the video. {{1}} is this directory. For this script, it will be the directory passed into the script (under the titles/ subdirectory).
- version: MLT version (presumably).

```xml
<profile colorspace="709" description="HD 1080p 60 fps" display_aspect_den="9" display_aspect_num="16" frame_rate_den="1" frame_rate_num="60" height="1080" progressive="1" sample_aspect_den="1" sample_aspect_num="1" width="1920"/>
```

Profile definition. Contains some important information that determines properties of the video.

- Resolution is controlled by `height` and `width`.
- `display_aspect_den` & `display_aspect_num` seem to be aspect ratio height/width.
- `frame_rate_num` controls frame rate. No clue on `frame_rate_den`.
- `sample_aspect_*` is unknown.
- `description` is the name of the current profile.

```xml
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
</producer>
```

Default Blank Video/Audio producers. Used when no other source is available. You don't need to consider these much, but do note that the first one will be used for the main video, while the second one is only used for Sequence 1.

```xml
<playlist id="playlist1"/>
<playlist id="playlist2"/>
```

Blank playlists, used in the following blank tractor.

```xml
<tractor id="tractor0" in="00:00:00.000">
	<property name="kdenlive:audio_track">1</property>
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	
	<track hide="video" producer="playlist1"/>
	<track hide="video" producer="playlist2"/>
	
	<filter id="filter0">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="filter1">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
	<filter id="filter2">
		<property name="iec_scale">0</property>
		<property name="mlt_service">audiolevel</property>
		<property name="dbpeak">1</property>
		<property name="disable">0</property>
	</filter>
</tractor>
```

A blank tractor, used to specify a blank audio track (NOTE the hide="video" on each track and the filters being for audio effects).

```xml
<playlist id="playlist3"/>
<playlist id="playlist4"/>

<tractor id="tractor1" in="00:00:00.000">
	...
</tractor>
```

Another blank playlist/tractor set for another blank audio track.

```xml
<playlist id="playlist5"/>
<playlist id="playlist6"/>
<tractor id="tractor2" in="00:00:00.000">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	
	<track hide="audio" producer="playlist5"/>
	<track hide="audio" producer="playlist6"/>
</tractor>
```

Another blank playlist/tractor set, but this time for a blank video track.

```xml
<producer id="producer2" in="00:00:00.000" out="00:00:03.983">
	<property name="length">240</property>
	<property name="eof">pause</property>
	<property name="resource">sample_proj/titles/section_1.kdenlivetitle</property>
	<property name="meta.media.progressive">1</property>
	<property name="aspect_ratio">1</property>
	<property name="seekable">1</property>
	<property name="mlt_service">kdenlivetitle</property>
	<property name="kdenlive:duration">00:00:04:00</property>
	<property name="xml">was here</property>
	<property name="kdenlive:folderid">17</property>
	<property name="kdenlive:id">11</property>
	<property name="kdenlive:control_uuid">{a8eea7c5-d87f-485f-812a-2985fa451ff5}</property>
	<property name="kdenlive:clip_type">2</property>
	<property name="kdenlive:file_hash">f483d0886f73aa005dea148779ffefe1</property>
	<property name="force_reload">0</property>
	<property name="meta.media.width">1920</property>
	<property name="meta.media.height">1080</property>
	<property name="kdenlive:monitorPosition">0</property>
</producer>
```

Finally, we get to an actual title producer. This defines a reference to a single title clip in Kdenlive. As for each of its properties...

- id: A unique ID for this producer.
- in: Always 00:00:00.000.
- out: The duration of the clip, minus one frame in seconds.

- length: The duration of the clip in frames.
- eof: Behavior on end of clip (??)
- resource: The location of the file this producer gets its media from, relative to the `<mlt>` tag's root parameter.
- meta.media.progressive: ???
- aspect_ratio: Here it's always 1. Doesn't seem to matter.
- seekable: Always 1, probably should stay that way.
- mlt_service: Likely a way for MLT to differentiate between types of clips. Since all of our real clips generated are `.kdenlivetitle`s, this will just be `kdenlivetitle`.
- kdenlive:duration: The duration of the clip in frames, but formatted in hh:mm:ss:ff, where ff is the total number of frames mod framerate.
- xml: Always `was here` (???)
- kdenlive:folderid: The ID of the project bin folder that contains this clip. This property will be seen later when we specify the `main_bin` producer.
- kdenlive:id: A unique ID for this producer. Used as an extra reference for each playlist, and is also present in `<tractor>`s. Likely used to differentiate between clips in Kdenlive itself.
- kdenlive:control_uuid: A UUID for this producer. Not used anywhere else.
- kdenlive:clip_type: Specifies the type of clip within kdenlive. Known types are as follows:
	- 0: Video Data (INCLUDING Sequences AND Chains)
	- 1: Audio Data
	- 2: Still Image Data (INCLUDING Titles, as seen here)
- kdenlive:file_hash: Seemingly an MD5 Hash for the clip (according to the source code) except generating an MD5 hash here for the file doesn't yield the same result... (more info [here](https://github.com/KDE/kdenlive/blob/db87eb236b3a995f6a8f3b081ad18cd9aeebac49/src/bin/playlistclip.cpp#L237))
- force_reload: ???
- meta.media.width: Width of the clip itself
- meta.media.height: Height of the clip itself
- kdenlive:monitorPosition: ???

That was a lot of properties. Thankfully, since all of our title clips are quite similar, there's no need to go over all of them again.

```xml
<producer id="producer3" in="00:00:00.000" out="00:00:05.233">
	...
</producer>
<producer id="producer4" in="00:00:00.000" out="00:00:04.000">
	...
</producer>
<producer id="producer5" in="00:00:00.000" out="00:00:10.133">
	...
</producer>
```

More producers for the remaining title clips in this Sequence. Understanding the differences in the properties for each is left as an exercise to the reader.

```xml
<playlist id="playlist7">
	<entry in="00:00:00.000" out="00:00:03.983" producer="producer2">
		<property name="kdenlive:id">11</property>
		<property name="kdenlive:activeeffect">0</property>
		
		<filter id="filter6" out="00:00:00.500">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_from_black</property>
			<property name="alpha">00:00:00.000=0;00:00:00.500=1</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
		<filter id="filter7" in="00:00:03.483" out="00:00:03.983">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_to_black</property>
			<property name="alpha">00:00:00.000=1;00:00:00.500=0</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
	</entry>
	<blank length="00:00:01.500"/>
	...
```

Now we've reached the playlist that actually contains the corresponding data for the track itself. The playlist itself has its own unique ID (past all of those belonging to the blank tracks before it). There is also one entry for each title clip producer from before, in sequential order, with properties as follows:

- in, out: Same as the corresponding title clip producer's in/out.
- producer: The `id` of the corresponding title clip producer.
- kdenlive:id: The `kdenlive:id` property of the corresponding producer.
- kdenlive:activeeffect: ???

Additionally, each entry has two filters. These filters define the fade in/out effect for each title clip. The properties of the filters are as follows:

- id: A unique ID for the filter. Each entry's filter is only used once even if two or more do the same thing.
- in: Point where the filter's effects start. In this case, the fade out filter starts 0.5 seconds before the end of the clip.
- out: Point where the filter's effects end. For the fade in filter, this is 0.5 seconds into the clip. For the fade out filter, this is the end of the clip.
- start: Always 1. (???)
- level: Always 1. (???)
- mlt_service: Tells MLT this is a filter, specifically for "brightness." (likely fade in/out is done at a lower level by modifying brightness in MLT).
- kdenlive_id: The ID of the effect in kdenlive itself.
- alpha: Defines a set of points in time corresponding to alpha levels. Easing is likely done this way, but since easing for each title clip's fade in/out is linear, this will always be 00:00:00.000=0;00:00:00.000=1 for fade in and 00:00:00.000=1;00:00:00.000=0 for fade out.
- kdenlive:collapsed: Presumably whether or not the effect is collapsed within Kdenlive's GUI itself.

Finally, after the clip there is a `<blank>`, which specifies blank space between each title clip. It's easy to see that its only property, `length`, just specifies the duration of the blank space, aka the spacing between the previous and next entry.

```xml
	<entry ...>
		...
	</entry>
	<blank length="00:00:01.000"/>
	<entry ...>
		...
	</entry>
	<blank length="00:00:01.000"/>
	<entry ...>
		...
	</entry>
</playlist>
```

The next few entries are added much like the first, and finally the video playlist for this track is over.

```xml
<playlist id="playlist8"/>

<tractor id="tractor3" in="00:00:00.000" out="00:00:26.983">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	<track hide="audio" producer="playlist7"/>
	<track hide="audio" producer="playlist8"/>
</tractor>
```

Finally, to round of the sequence we get another blank playlist and the tractor for the track that actually contains our title clips. I'm not sure what the other playlist was for, but I presume it's for *something*.

The `out` property of this tractor is just the length of the sequence, i.e. the sum of the length of all `<entry>` and `<blank>` tags. Additionally, I didn't explain this before, but the `kdenlive:trackheight` property is the visual height in pixels of the track within Kdenlive's GUI.

Prepare yourself for the next one, because it's pretty big.

```xml
<tractor id="{39d357f0-ac39-4c22-a816-375e07f021bc}" in="00:00:00.000" out="00:00:26.983">
	<property name="kdenlive:duration">00:00:27.000</property>
	<property name="kdenlive:maxduration">1620</property>
	<property name="kdenlive:clipname">Sequence 1</property>
	<property name="kdenlive:description"/>
	<property name="kdenlive:uuid">{39d357f0-ac39-4c22-a816-375e07f021bc}</property>
	<property name="kdenlive:producer_type">17</property>
	<property name="kdenlive:control_uuid">{851fdb2e-84a7-47cc-82ee-09eb5b7aaf0d}</property>
	<property name="kdenlive:id">15</property>
	<property name="kdenlive:clip_type">0</property>
	<property name="kdenlive:file_hash">966041317ba33b4140cb34a16ac08e8f</property>
	<property name="kdenlive:folderid">2</property>
	<property name="kdenlive:sequenceproperties.activeTrack">2</property>
	<property name="kdenlive:sequenceproperties.disablepreview">0</property>
	<property name="kdenlive:sequenceproperties.documentuuid">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:sequenceproperties.hasAudio">1</property>
	<property name="kdenlive:sequenceproperties.hasVideo">1</property>
	<property name="kdenlive:sequenceproperties.position">102</property>
	<property name="kdenlive:sequenceproperties.scrollPos">0</property>
	<property name="kdenlive:sequenceproperties.tracks">4</property>
	<property name="kdenlive:sequenceproperties.tracksCount">4</property>
	<property name="kdenlive:sequenceproperties.verticalzoom">1</property>
	<property name="kdenlive:sequenceproperties.zonein">0</property>
	<property name="kdenlive:sequenceproperties.zoneout">1620</property>
	<property name="kdenlive:sequenceproperties.zoom">8</property>
	<property name="kdenlive:sequenceproperties.groups">[
	]
	</property>
	<property name="kdenlive:sequenceproperties.guides">[
	]
	</property>
	<property name="kdenlive:monitorPosition">1166</property>
```

This next tractor is for the full Sequence itself. Its job is to combine all 4 of the previous tractors to create a sequence. For this, we have a whole bunch of properties:

- id: The ID of this tractor. Uniquely, it is a UUID. This UUID is shared with its `kdenlive:uuid` property. Oddly enough, within the [official documentation](https://github.com/KDE/kdenlive/blob/master/dev-docs/fileformat.md#project-xml-structure), this tractor has an ordinary tractor ID, but I guess that changed in a more recent Kdenlive version.
- in: Always 00:00:00.000
- out: The duration of the longest track. Since our sequence only has one track that isn't blank, `out` here is the same as `out` in that track's `<tractor>`.

- kdenlive:duration: The duration of the Sequence as a timestamp. This doesn't exclude the final frame, unlike all previous items we've seen before.
- kdenlive:maxduration: The duration of the Sequence as a number of frames. Notice that maxduration/framerate = duration.
- kdenlive:clipname: The name of the Sequence.
- kdenlive:description: A description field for the sequence. Left blank, at least here.
- kdenlive:producer_type: Specifies a "producer type". Seemingly always 17 for Sequences.
- kdenlive:control_uuid: A different unique UUID for this tractor. Unused elsewhere.
- kdenlive:id: A unique numerical ID for this tractor, much like those for our `<producer>`s.
- kdenlive:clip_type: The same clip_type property as in our `<producer>`s, except 0 because it is a Video Source.
- kdenlive:file_hash: The MD5 hash of the sequence's UUID, **including the curly brackets**.
- kdenlive:folderid: Same as a `<producer>`.

Then we get a *whole bunch* of `kdenlive.sequenceproperties` properties. I'll remove the prefix to make defining each of these easier.

- activeTrack: The index of the currently active track.
- disablepreview: Whether or not the preview is disabled (??)
- documentuuid: The UUID of the Main Sequence.
- hasAudio: Whether or not audio is enabled in the sequence (?)
- hasVideo: Whether or not video is enabled in the sequence (?)
- position: The current position of the cursor within the sequence.
- scrollPos: Likely the vertical scroll within the sequence.
- tracks, tracksCount: Two fields for the same value, the number of tracks within this sequence.
- verticalZoom: Likely how zoomed in the sequence is vertically (greater = less tracks visible?)
- zonein: Start frame of the sequence
- zoneout: End frame of the sequence
- zoom: How zoomed in the sequence is time-wise (greater = Less frames visible in timeline)

- groups, guides: Blank on here and the next content sequence, but not on the main sequence. More will be covered in that part.

And with that, all of the properties for a sequence tractor are done. Now we can move on to its actual definition.

```xml
	<track producer="producer1"/>
	<track producer="tractor0"/>
	<track producer="tractor1"/>
	<track producer="tractor2"/>
	<track producer="tractor3"/>
	
	<transition id="transition0">
		<property name="a_track">0</property>
		<property name="b_track">1</property>
		<property name="mlt_service">mix</property>
		<property name="kdenlive_id">mix</property>
		<property name="internal_added">237</property>
		<property name="always_active">1</property>
		<property name="accepts_blanks">1</property>
		<property name="sum">1</property>
	</transition>
	<transition id="transition1">
		...
	</transition>
	<transition id="transition2">
		...
	</transition>
	<transition id="transition3">
		...
	</transition>
```

This part of the tractor specifies each track within the sequence. Near the top you can see one `<track>` for each tractor we made previously. There is also an additional track for `producer1`, our blank producer, which, when combined with the transitions below, mixes in the blank feed into our tracks. These are internally added by Kdenlive, and each transition only differs by its `b_track` property, which is from 1-4. It's not necessary to really know whats going on with each transition.

```xml
	<filter id="filter14">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="filter15">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
</tractor>
```

Finally, we specify some filters specific to this tractor. These are also internally added. I'm unsure what they do. This finishes off the sequence tractor. Wow! What a journey.

After this, sample.kdenlive generates another Sequence. This one is defined nearly identically to the first, except it uses other title clips. So now we know the full definition of a sequence, which goes from a `<producer>` specifying blank video to a Sequence `<tractor>`.

Let's skip forward until we reach the end of the second Sequence's tractor.

```xml
<playlist id="playlist0">
	<property name="kdenlive:audio_track">1</property>
	<blank length="00:00:08.500"/>
	<entry in="00:00:00.000" out="00:00:26.983" producer="{39d357f0-ac39-4c22-a816-375e07f021bc}">
		<property name="kdenlive:maxduration">1620</property>
		<property name="kdenlive:id">15</property>
	</entry>
	<blank length="00:00:01.500"/>
	<entry in="00:00:00.000" out="00:00:29.800" producer="{3304572b-8242-458e-8538-0f9f4e02fff9}">
		<property name="kdenlive:maxduration">1789</property>
		<property name="kdenlive:id">16</property>
	</entry>
</playlist>
<playlist id="playlist17">
	<property name="kdenlive:audio_track">1</property>
</playlist>
```

The next two playlists specify the feed for one of the audio tracks of the main sequence. Even though the audio of our Sequences are null, they still create an audio track so we must deal with them. The first playlist looks a lot like the title clip track playlists for each of our sequences, but with a few key differences.

First, the first item is a blank. This happens to be the duration of our title clip + 1.5 seconds, the empty space between sections.

Next, each entry is produced from the Sequence tractor, as seen by the producer field being the Sequence tractor's UUID. It also specifies the same `kdenlive:maxduration`, `kdenlive:id`, and `out` fields.

Finally, we specify this is an audio track with `kdenlive:audio_track`.

With our actual playlist and blank playlist done, we can create our track.

```xml
<tractor id="tractor8" in="00:00:00.000" out="00:01:06.800">
	<property name="kdenlive:audio_track">1</property>
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:collapsed">0</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	
	<track hide="video" producer="playlist0"/>
	<track hide="video" producer="playlist17"/>
	
	<filter id="filter34">
		<property name="window">75</property>
		<property name="max_gain">20dB</property>
		<property name="mlt_service">volume</property>
		<property name="internal_added">237</property>
		<property name="disable">1</property>
	</filter>
	<filter id="filter35">
		<property name="channel">-1</property>
		<property name="mlt_service">panner</property>
		<property name="internal_added">237</property>
		<property name="start">0.5</property>
		<property name="disable">1</property>
	</filter>
	<filter id="filter36">
		<property name="iec_scale">0</property>
		<property name="mlt_service">audiolevel</property>
		<property name="dbpeak">1</property>
		<property name="disable">1</property>
	</filter>
</tractor>
```

This tractor creates our track. Since our video ends with a sequence, its `out` field is the length of the entire video. There are a few builtin filters added to this tractor, but other than that it is pretty standard.

```xml
<playlist id="playlist18">
	<property name="kdenlive:audio_track">1</property>
</playlist>
<playlist id="playlist19">
	<property name="kdenlive:audio_track">1</property>
</playlist>
<tractor id="tractor9" in="00:00:00.000">
	...
</tractor>
<playlist id="playlist20"/>
<playlist id="playlist21"/>
<tractor id="tractor10" in="00:00:00.000">
	...
</tractor>
```

The next few `<playlist>`s and `<tractor>`s define the other blank tracks within the video. Not much to say here.

```xml
<producer id="producer12" in="00:00:00.000" out="00:00:06.983">
	<property name="length">420</property>
	<property name="eof">pause</property>
	<property name="resource">sample_proj/titles/title.kdenlivetitle</property>
	...
</producer>
```

The next producer defines the title clip for the entire video, formed by the frontmatter of our original script. This has the same properties as our other title clips.

```xml
<playlist id="playlist22">
	<entry in="00:00:00.000" out="00:00:06.983" producer="producer12">
		<property name="kdenlive:id">13</property>
		<property name="kdenlive:activeeffect">0</property>
		
		<filter id="filter40" out="00:00:01.000">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_from_black</property>
			<property name="alpha">00:00:00.000=0;00:00:01.000=1</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
		<filter id="filter41" in="00:00:05.983" out="00:00:06.983">
			<property name="start">1</property>
			<property name="level">1</property>
			<property name="mlt_service">brightness</property>
			<property name="kdenlive_id">fade_to_black</property>
			<property name="alpha">00:00:00.000=1;00:00:01.000=0</property>
			<property name="kdenlive:collapsed">0</property>
		</filter>
	</entry>
	<blank length="00:00:01.500"/>
	<entry in="00:00:00.000" out="00:00:26.983" producer="{39d357f0-ac39-4c22-a816-375e07f021bc}">
		<property name="kdenlive:id">15</property>
	</entry>
	<blank length="00:00:01.500"/>
	<entry in="00:00:00.000" out="00:00:29.800" producer="{3304572b-8242-458e-8538-0f9f4e02fff9}">
		<property name="kdenlive:id">16</property>
	</entry>
</playlist>
<playlist id="playlist23"/>
```

The next playlist defines our main video track. Here, you can see our title clip, as well as the video feed of our Sequences, be placed onto one playlist. Each blank in the playlist is the blank time between sequences, and each `<entry>` has its corresponding unique numeric id in its `kdenlive:id` property.

Note that the main title clip also has 1 second fade in/out filters, which work near identically to those seen in our previous title clips.

```xml
<tractor id="tractor11" in="00:00:00.000" out="00:01:06.800">
	<property name="kdenlive:trackheight">67</property>
	<property name="kdenlive:timeline_active">1</property>
	<property name="kdenlive:collapsed">0</property>
	<property name="kdenlive:thumbs_format"/>
	<property name="kdenlive:audio_rec"/>
	<track hide="audio" producer="playlist22"/>
	<track hide="audio" producer="playlist23"/>
</tractor>
```

Next we get the tractor for our main video. It's already defined in the playlist, so there's not much to do here.

```xml
<tractor id="{3ff62b61-665f-46dd-b3bd-d1349831c00d}" in="00:00:00.000" out="00:01:06.800">
	<property name="kdenlive:uuid">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:clipname">Main Sequence</property>
	<property name="kdenlive:sequenceproperties.hasAudio">1</property>
	<property name="kdenlive:sequenceproperties.hasVideo">1</property>
	<property name="kdenlive:sequenceproperties.activeTrack">3</property>
	<property name="kdenlive:sequenceproperties.tracksCount">4</property>
	<property name="kdenlive:sequenceproperties.documentuuid">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:control_uuid">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:duration">00:01:06.817</property>
	<property name="kdenlive:maxduration">4009</property>
	<property name="kdenlive:producer_type">17</property>
	<property name="kdenlive:id">3</property>
	<property name="kdenlive:clip_type">0</property>
	<property name="kdenlive:file_size">0</property>
	<property name="kdenlive:folderid">2</property>
	...
	<property name="kdenlive:sequenceproperties.zoom">10</property>
```

Finally, its time for the tractor for our Main Sequence. You can tell it's the main sequence because its `kdenlive:sequenceproperties.document_uuid` property is identical to its `id` (as well as its control_uuid). Aside from this, most of its properties are similarly defined to the other sequences.

```xml
	<property name="kdenlive:sequenceproperties.groups">[
		{
			"children": [
				{
					"data": "3:510:-1",
					"leaf": "clip",
					"type": "Leaf"
				},
				{
					"data": "0:510:-1",
					"leaf": "clip",
					"type": "Leaf"
				}
			],
			"type": "AVSplit"
		},
		{
			"children": [
				{
					"data": "3:2220:-1",
					"leaf": "clip",
					"type": "Leaf"
				},
				{
					"data": "0:2220:-1",
					"leaf": "clip",
					"type": "Leaf"
				}
			],
			"type": "AVSplit"
		}
	]
	</property>
	<property name="kdenlive:sequenceproperties.guides">[
	]
	</property>
	<property name="kdenlive:monitorPosition">0</property>
```

Now we move on to the `kdenlive:sequenceproperties.groups` field, which isn't blank here. This field specified grouped clips within the Sequence. As you can see, this sequence has two groups, which, as shown by their type, are Links to corresponding Audio/Video data.

Each group has a list of children. These are clips specified by 3 values: data, which is further split as `track index:start frame:???`, leaf, which is just "clip", and type, which like the outer group just specifies the type of item this element in the group is.

There is also a `kdenlive:sequenceproperties.guides` property, which I don't know the specifics of, and monitorPosition, which I also don't know the specifics of.

```xml
	<track producer="producer0"/>
	<track producer="tractor8"/>
	<track producer="tractor9"/>
	<track producer="tractor10"/>
	<track producer="tractor11"/>

	<transition id="transition8">
		...
	</transition>
		...
	</transition>
	<transition id="transition10">
		...
	</transition>
	<transition id="transition11">
		...
	</transition>

	<filter id="filter42">
		...
	</filter>
	<filter id="filter43">
		...
	</filter>
</tractor>
```

Next we add our tracks and add our standard set of filters/transitions to add default effects to the tractor. With this, we have defined our Main Sequence.

Now it's time to move on to the main_bin playlist, which basically contains everything else related to the project.

```xml
<playlist id="main_bin">
	<property name="kdenlive:folder.-1.2">Sequences</property>
	<property name="kdenlive:sequenceFolder">2</property>
	<property name="kdenlive:docproperties.audioChannels">2</property>
	<property name="kdenlive:docproperties.binsort">100</property>
	<property name="kdenlive:docproperties.browserurl">sample_proj/</property>
	<property name="kdenlive:docproperties.documentid">1736004640027</property>
	<property name="kdenlive:docproperties.enableTimelineZone">0</property>
	<property name="kdenlive:docproperties.enableexternalproxy">0</property>
	<property name="kdenlive:docproperties.enableproxy">0</property>
	<property name="kdenlive:docproperties.externalproxyparams">./;;.LRV;./;;.MP4</property>
	<property name="kdenlive:docproperties.generateimageproxy">0</property>
	<property name="kdenlive:docproperties.generateproxy">0</property>
```

The main_bin playlist starts with a bunch of properties. As they go:

- `kdenlive:folder.-1.2` defines a folder in the Project Bin. This particular property field defines the default "Sequences" folder always present in a new project. The -1 indicates this is a root-level folder (i.e. its parent is the Project Bin root), and the 2 is the unique ID of this folder (which is different from all other `kdenlive:id`s).
- `kdenlive:sequenceFolder` specifies the folder to put all of our sequences in. Since we just defined it, we use folder 2.

Until we reach the end of the `docproperties` fields, I will not add the `kdenlive:docproperties` prefix. Continuing on...

- audioChannels: The number of Audio Channels in the Audio Mixer.
- binsort: Likely specifies how the project bin is sorted.
- browserurl: Path open in the Media Browser (View » Media Browser)
- documentid: The document ID, which is just set to the number of milliseconds since the Unix Epoch.
- enableTimelineZone: Whether or not the Timeline Zone (blue bar above the timeline) is enabled for inserting clips. See [this page](https://userbase.kde.org/Kdenlive/Manual/Timeline/Editing) or [this page](https://kdenlive.org/project/insert-overwrite-advanced-timeline-editing/) for more info.
- enableexternalproxy: Whether or not External Proxy Clips are enabled in the project settings (0=no, 1=yes; if 1, enableproxy should be 1)
- enableproxy: Whether or not Proxy Clips are enabled in the project settings. Proxied clips are smaller resized copies of clips.
- externalproxyparams: String formatted version of the currently selected option under "External proxy clips"
- generateimageproxy: Whether or not proxies are generated for large enough images
- generateproxy: Whether or not proxies are generated for large enough videos

```xml
	<property name="kdenlive:docproperties.guidesCategories">[
		{
			"color": "#9b59b6",
			"comment": "Category 1",
			"index": 0
		},
		{
			"color": "#3daee9",
			"comment": "Category 2",
			"index": 1
		},
		{
			"color": "#1abc9c",
			"comment": "Category 3",
			"index": 2
		},
		{
			"color": "#1cdc9a",
			"comment": "Category 4",
			"index": 3
		},
		{
			"color": "#c9ce3b",
			"comment": "Category 5",
			"index": 4
		},
		{
			"color": "#fdbc4b",
			"comment": "Category 6",
			"index": 5
		},
		{
			"color": "#f39c1f",
			"comment": "Category 7",
			"index": 6
		},
		{
			"color": "#f47750",
			"comment": "Category 8",
			"index": 7
		},
		{
			"color": "#da4453",
			"comment": "Category 9",
			"index": 8
		}
	]
	</property>
```

- guidesCategories: Specifies several colors and titles for Guides. Since our project uses no guides, this remains unused. These can be seen in the project settings under the Guides Tab.

```xml
	<property name="kdenlive:docproperties.kdenliveversion">24.12.0</property>
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
	<property name="kdenlive:docproperties.sessionid">{4e2506dd-d82d-475a-a657-2ebb486209e1}</property>
	<property name="kdenlive:docproperties.uuid">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:docproperties.version">1.1</property>
```

- kdenliveversion: The version of Kdenlive this project was made on.
- previewextension: Selected Encoding profile for Timeline Preview (bottom of Project Settings » Settings)
- previewparameters: Parameters for the Timeline Preview. Used in addition to encoding profile, and can be seen in Kdenlive by opening the settings gear next to the currently selected Timeline Preview.
- profile: Identifier for the project's current profile. If it's a custom profile, it instead is a path to the custom profile.
- proxyextension: Selected Encoding profile for Proxy Clips
- proxyimageminsize: Width threshold to determine whether or not to proxy an image. If an image is wider than this amount (in pixels), it will be proxied.
- proxyimagesize: Width (in pixels) to resize proxied images
- proxyminsize: Width threshold to determine whether or not to proxy a video. If a video is wider than this amount (in pixels), it will be proxied.
- proxyparams: Parameters for Proxy Clips. Used in addition to encoding profile, and can be seen in Kdenlive by opening the settings gear next to the currently selected Encoding Profile.
- proxyresize: Width (in pixels) to resize proxied videos.
- seekOffset: Duration after the end point of a Sequence which can still be seeked to (in frames)
- sessionid: UUID generated upon opening Kdenlive (?)
- uuid: The UUID of the document (??), identical to the UUID of our Main Sequence.
- version: The Kdenlive document version. Currently 1.1, corresponding to "Generation 5" of the Kdenlive document format.

```xml
	<property name="kdenlive:expandedFolders">14;2</property>
	<property name="kdenlive:binZoom">4</property>
	<property name="kdenlive:extraBins">project_bin:-1:0</property>
	<property name="kdenlive:documentnotes"/>
	<property name="kdenlive:documentnotesversion">2</property>
	<property name="kdenlive:docproperties.opensequences">{3ff62b61-665f-46dd-b3bd-d1349831c00d};{39d357f0-ac39-4c22-a816-375e07f021bc};{3304572b-8242-458e-8538-0f9f4e02fff9}</property>
	<property name="kdenlive:docproperties.activetimeline">{3ff62b61-665f-46dd-b3bd-d1349831c00d}</property>
	<property name="kdenlive:folder.-1.14">titles</property>
	<property name="kdenlive:folder.14.17">Section 1</property>
	<property name="kdenlive:folder.14.18">Section 2</property>
	<property name="xml_retain">1</property>
```

- kdenlive:expandedFolders: The numeric IDs of each folder currently opened in the project bin, separated by `;`
- kdenlive:binZoom: Zoom level in the project bin.
- kdenlive:extraBins: A list of all project bins. They are in the form [project_bin_id];[folder];[???], where project_bin_id is a unique string identifier for the bin, folder is the numeric folder ID of the currently open bin (with -1 being the root folder), and ??? being unknown.
- kdenlive:documentnotes: HTML formatted notes for the project. See [this page](https://docs.kdenlive.org/en/project_and_asset_management/project_notes.html) for more info.
- kdenlive:documentnotesversion: Version number for document notes. Currently 2.
- kdenlive:docproperties.opensequences: The UUIDs of each sequence currently open in Kdenlive, separated by `;`
- kdenlive:docproperties.activetimeline: The UUID of the active sequence.
- kdenlive:folder.-1.14: Custom folder to organize our titles.
- kdenlive:folder.14.17: Custom folder, within the titles folder, to organize our Section 1 titles.
- kdenlive:folder.14.18: Custom folder, within the titles folder, to organize our Section 2 titles.
- xml_retain: ??? (always 1??)

With that, all of the properties of main_bin have been covered.

```xml
	<entry in="00:00:00.000" out="00:00:00.000" producer="{3ff62b61-665f-46dd-b3bd-d1349831c00d}"/>
	<entry in="00:00:00.000" out="00:00:00.000" producer="{39d357f0-ac39-4c22-a816-375e07f021bc}"/>
	<entry in="00:00:00.000" out="00:00:00.000" producer="{3304572b-8242-458e-8538-0f9f4e02fff9}"/>
	<entry in="00:00:00.000" out="00:00:03.983" producer="producer2"/>
	<entry in="00:00:00.000" out="00:00:05.233" producer="producer3"/>
	<entry in="00:00:00.000" out="00:00:04.000" producer="producer4"/>
	<entry in="00:00:00.000" out="00:00:10.133" producer="producer5"/>
	<entry in="00:00:00.000" out="00:00:06.933" producer="producer11"/>
	<entry in="00:00:00.000" out="00:00:03.983" producer="producer7"/>
	<entry in="00:00:00.000" out="00:00:02.717" producer="producer8"/>
	<entry in="00:00:00.000" out="00:00:05.817" producer="producer9"/>
	<entry in="00:00:00.000" out="00:00:06.100" producer="producer10"/>
	<entry in="00:00:00.000" out="00:00:06.983" producer="producer12"/>
</playlist>
```

The final part of main_bin is to have one entry for each clip we use. Sequences are first (with the main sequence being the very first item), followed by all title clips. The `out` field of each sequence is 00:00:00.000, while the `out` field of each clip is the same as when we defined them.

```xml
<tractor id="tractor12" in="00:00:00.000" out="00:01:06.800">
	<property name="kdenlive:projectTractor">1</property>
	<track in="00:00:00.000" out="00:01:06.800" producer="{3ff62b61-665f-46dd-b3bd-d1349831c00d}"/>
</tractor>
</mlt>
```

Finally, we specify the tractor for main_bin. `out` is the duration of our video. `kdenlive:projectTractor` specifies this is the tractor for the entire project, and the producer of the one track for this tractor is the Main Sequence's UUID.

With that, we have formed our video, and can close the MLT tag to form our document.



# kdenlivetitle walkthrough

A .kdenlive title is much shorter than a full project document. The XML for a .kdenlivetitle may be saved elsewhere or may be bundled within the .kdenlive project file itself.

```xml
<kdenlivetitle LC_NUMERIC="C" duration_frames="315" height="1080" out="315" width="1920">
	<item type="QGraphicsTextItem" z-index="0">
		<position x="240" y="836">
			<transform>1,0,0,0,1,0,0,0,1</transform>
		</position>
		<content alignment="4" box-height="1080" box-width="1440" font="Inter" font-color="255,255,255,255" font-italic="0" font-outline="6" font-outline-color="0,0,0,255" font-pixel-size="48" font-underline="0" font-weight="600" letter-spacing="0" line-spacing="0" shadow="0;#ff000000;8;0;0" tab-width="80" typewriter="0;2;1;0;0">This is the first section of the video, not much to see here.</content>
	</item>
	<startviewport rect="0,0,1920,1080"/>
	<endviewport rect="0,0,1920,1080"/>
	<background color="0,0,0,0"/>
</kdenlivetitle>
```

This is the content of one .kdenlivetitle file. As you can see, its outermost tag has a few properties:

- LC_NUMERIC: unknown, but identical to the respective property in a .kdenlive project's `<mlt>`.
- duration_frames: The duration of the clip in frames.
- height: The height of the clip.
- width: The width of the clip.
- out: Cutoff point for the clip in frames, generally identical to duration_frames.

The main content of the file is located within one of several `<item>` tags. These define the text that appears.

The `<item>` tag itself has a few properties:

- type: The Qt type of the item. QGraphicsTextItem for text, QGraphicsEllipseItem for ellipses, and so on.
- z-index: The index of the z-order of the item. A greater z-index means the item will be placed in front of all items with smaller z-indices.

Additionally, the `<item>` tag has `<position>` and `<content>` tags within.

The `<position>` tag has two properties: `x` and `y`. These are the X and Y positions of the top-left corner of the item respectively. Additionally, it has a `<transform>` tag, which can hold the following properties:

- rotation: The X, Y, and Z rotation respectively of the item in degrees, separated by comma.
- zoom: The zoom on the item as a percentage. A value of 100 indicates the item is at its normal size.

The content of the `<transform>` tag is the values of the 3x3 transformation matrix that performs all of the transformations specified in its properties.

The `<content>` tag has much more properties, depending on the type of the item. For QGraphicsTextItem:

- alignment: The horizontal text alignment of a text block. 1: Left, 4: Center, 2: Right, 3: Also left (but unused)
- box-width, box-height: The width and height of the box text is placed in respectively.
- color: The RGBA components of the text's color, from 0-255.
- font: The name of the font used for text in this item.
- font-pixel-size: The size in pixels of the text.
- font-italic: Whether or not the text is italicized (0: No, 1: Yes)
- font-underline: Whether or not the text is underlined (0: No, 1: Yes)
- font-weight: The weight of the font in font weight units. Generally a multiple of 100 from 100-900, where 400 is Regular and 700 is Bold.
- font-outline: The thickness in pixels of the outline present on each letter.
- font-outline-color: The RGBA components of the font outline's color, from 0-255.
- letter-spacing: Added spacing between letters, in pixels. Can be negative.
- line-spacing: Added spacing between lines of text, in pixels. Can be negative.
- tab-width: The width of tab characters, in pixels.
- shadow: Components that define the text's shadow, separated by semicolon. In order...
	- Whether or not the shadow is enabled. (0: No, 1: Yes)
	- The color of the shadow as an RGBA hex code (#AARRGGBB)
	- The blur amount in pixels of the shadow.
	- The X offset of the shadow.
	- The Y offset of the shadow.
- typewriter: Defines an optional typewriter effect for this text. Each component is separated by semicolon. In order...
	- Whether or not the effect is enabled. (0: No, 1: Yes)
	- The "Frame Step" of the effect.
	- The Expansion Mode of the effect (1: By character, 2: By word, 3: By line)
	- The Variation of the effect.
	- The Seed of the effect, used for variation.

The content of the `<content>` tag is merely the text itself. Newlines are included as a part of this content as themselves.

Finally, we get to the remaining tags within the `<kdenlivetitle>`. These are the `<startviewport>`, `<endviewport>`, and `<background>` tags.

The `<startviewport>` and `<endviewport>` tags define the start and end viewports respectively. These indicate where on screen the contents of the title should display. They both have one property, `rect`, which defines a rectangle for the viewport. In order, its 4 components are the X position of the top-left corner, the Y position of the top-left corner, the width, and the height. Each component is separated by comma.

Finally, the `<background>` tag defines the background color. The background is defined for the part of the clip that appears on screen. It has one property, `color`, which is defined by the RGBA components of the background's color from 0-255, divided by comma.

With that, every property of the .kdenlivetitle has been covered.



# the general process

This is how the script works in general. It is also how a .kdenlive file can be manually made.

Per Sequence:

- Create 3 blank tracks (2 audio, 1 video) via 6 playlists and 3 tractors
- Create producers for all title clips
- Create playlist for title clips + extra blank playlist
- Create tractor for actual playlist
- Create sequence tractor

Per File:

- Init profile/first producer
- Create Sequences
- Create Audio tractor of Main Sequence
- Create title clip producer
- Create playlist for video track
- Create corresponding tractor
- Define Main Sequence
- Define main_bin

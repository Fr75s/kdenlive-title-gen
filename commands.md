# syntax & command compendium

This documents list special syntax needed to take full advantage of this script. This document also lists all commands and modifiers supported by this script, as well as explains how to use them.

## general syntax

Take the following basic document as an example of a well-formed document.

```
---
title: My Title
subtitle: My Subtitle
---

This is my first line.

/=/ This is a comment.

## This is a section header.

This is my second line.
This is the second part of my second line.
```

### required fields

The following features are required for a document:

- A frontmatter section at the top of the document (denoted by the two `---` lines) with a `title` field
- At least one line of real content below the title. This can be anything.

### forming content

Blocks of text separated by at least one blank line will be separated into different title clips. By writing multiple blocks of text, multiple clips can be made. It is recommended to split text often to not create excessively long clips.

### sections

Sections headers are denoted by `##` at the start of their line. These display differently than normal text clips and denote where the script will split a video into Sequences.

### comments

Comments are made by having a `/=/` at the beginning of a line. In doing so, all text until the next line will be ignored. There are currently no inline comments.



## commands

Commands are standalone instructions that are read by the document parser. These are in their own blocks of text; placing a command alongside text or a modifier in a block will result in an error. Commands are specified with a `-=-` at the beginning of their line.

Correct Usage:

```
...

This is my line of text.

-=- pause (0.5)
-=- ignore

This line will be ignored.

...
```

Incorrect Usage:

```
...

This is my line of text.
-=- pause (0.5)
{{color}}(128;128;128;255)

The parser will error before it reaches this line.

...
```

Commands may also take parameters, as seen in the above example. Parameters for a command are supplied by putting them in a single parentheses (`()`). Multiple parameters are separated by semicolon (`;`). If a command takes no parameters, then the parentheses are optional.

It is recommended to separate the command name, `-=-`, and parameters with one space.

You can also specify more than one command in one block. Additionally, you can specify commands in consecutive blocks; all commands will be treated as one block and affect the next clip.

The following is a list of all commands currently available:

### pause

- `pause (TIME: float)`

Sets the duration in between two content clips where no text is shown to TIME seconds.

### ignore

- `ignore ()`

Ignores the next content block, if it exists. This will make it not appear in the video, and a `.kdenlivetitle` will not be created for this block.

Ignoring a section header will bypass the header and will not create a new Sequence.

Any other commands next to an `ignore` will act upon the next non-ignored block.



## modifiers

Modifiers are instructions that are appended to content blocks or section headers. They can be placed anywhere within a content block, as long as they are within their own line. Placing more than one modifier in a line will ignore all but the first modifier. 

Modifiers must be added to blocks which already contain content; standalone modifiers (or modifiers attached to commands) will result in an error. More than one modifier can be placed in a single block. If multiple of the same modifier are placed in the block, only the last one sequentially will take effect.

Additionally, modifiers can be placed within the frontmatter; this will apply the modifier to the title clip. Only some modifiers work for the title clip; these modifiers will be marked by "(TITLE)" in the documentation. It is best to modify the configuration values of the script for different titles.

Modifiers are specified with their keyword in double curly brackets (`{{}}`). Parameters for modifiers are passed in a single parentheses (`()`) after the curly brackets.

Correct Usage:

```
...

This is my line of text.
{{color}}(128;128;128;255)
{{font}}(Arial)

/=/ The above is a modifier.

...
```

Incorrect Usage:

```
...

This is my line of text.

{{color}} (128;128;128;255)

/=/ Below also doesn't work.

-=- ignore ()
{{font}}(Arial)

...
```

It is recommended to place all modifiers after the last line of content in a block, and to either have no space between the curly brackets and parameters or to evenly space all parameters so that they are aligned horizontally.

The following is a list of all modifiers currently available:

### color

- `color (RED: int;GREEN: int;BLUE: int)`
- `color (RED: int;GREEN: int;BLUE: int;ALPHA: int)`

Sets the color of the text in the text block to the given color (in RGB components from 0-255). If no `A` parameter is specified, the text will be fully opaque.

### font

- `font (NAME: string)`

Sets the font of the text in the text block to NAME. This will result in an error if NAME.ttf or NAME.otf does not exist in one of your font installation locations.

### font_size

- `font_size (VALUE: int)`

Sets the size of the text in the text block to VALUE. VALUE will be the height of a line of text in pixels. If value is less than 1, this will result in an error.

### outline_color

- `outline_color (RED: int;GREEN: int;BLUE: int)`
- `outline_color (RED: int;GREEN: int;BLUE: int;ALPHA: int)`

Sets the color of the outline of the text in the text block to the given color (in RGB components from 0-255). If no `A` parameter is specified, the text will be fully opaque.

### y

**(TITLE)**

- `y (VALUE: int)`

Sets the vertical position of the center of the text block in the video to VALUE.

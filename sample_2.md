---
title: Command Showcase
subtitle: All Commands and Modifiers.
supertitle: Part of ktg
---

This is a standard text segment. Before the next segment, the pause command will run.

-=- pause (0.5)

The pause command sets the gap between text clips to be different than the default.
It takes one parameter, which specifies the length of the pause in seconds.

The next command is called ignore, and will ignore the next text paragraph.

-=- ignore ()

This text will not display in the video.

/=/ Note that you can also make text not display by adding `/=/` before it.
/=/
/=/ This can also be used to space text in a block.

The previous text segment did not display. This is intended.

## Modifier Showcase

This text has multiple modifiers on it. Check them out on the file this script was generated from.
{{color}}(80;255;128;255)
{{outline_color}}(255;255;255;255)
{{font}}(Impact)
{{font_size}}(36)
{{y}}(220)

Note that default values can be read by the script itself. It is a bad practice to use modifiers
if it appears all of your clips use them.

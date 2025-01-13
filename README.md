# kdenlive title generator

Generates a kdenlive project with title clips from one markdown file.

## Prerequisites

- python 3.12 or above
- [pillow](https://pypi.org/project/pillow/) (`pip install pillow`)

## Usage

Check out [this document (commands.md)](commands.md) for information on how to format a Markdown document for use with this script.

To use this script, clone this repo and run the following command in a command line:

```
python3 tgen.py -f [YOUR FILE] -d [FOLDER TO PUT PROJECT FILE IN]
```

## Additional Information

In order to create this script, I needed to document how Kdenlive's project file format works. [I have compiled my findings in this file](format.md), which walks through a Kdenlive video project file made to look like this script's output when given the file `sample.md`. While this does not cover all details, it is more thorough than the official documentation (as of writing).

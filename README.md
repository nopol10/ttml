# ttml

This is a fork of on-three's NHK ttml to SRT/ASS converter with some fixes.

Note: ASS output does not work correctly! **_Use SRT only!_**

---

## Usage

1. Install Python 3 if you do not already have it

1. Download the convert.py python file

1. Run `python convert.py filename.ttml` in command prompt / terminal

---

## Arguments

```
python convert.py [-h] [-o OUTFILE] [-f] [-e EXTENSION] infile
```

Mandatory argument:

- infile: The name of the input NHK .ttml file. If --folder is specified, this must be the path to the folder. Omit any trailing slashes

Optional arguments:

- --outfile: The name of the output file. If omitted, the output file will be named inputfile.[extension]. When using file mode, include the desired extension as part of the name (e.g. mysubtitle.srt if you want an SRT output).

- --folder: Specify this flag to treat infile as a folder. All files within the folder will be converted to the given format specified in extension.

- --extension: The extension of the output file. Only works when the folder flag is specified. Can be srt or ass. Defaults to srt.

# music-generator

## Requirements

* midi2audio (https://github.com/bzamecnik/midi2audio)
* python-midi (https://github.com/vishnubob/python-midi)
* pandas

## Usage

```
$ python comp_to_music.py <comp.json> [--seed] [--bpm] [--root]
```

* bpm: tempo. Default: 120.
* root: key of generated music. Default: None. Use int range [33, ..., 47].
* seed: for reproducibility. Default: None
* .json files need to be in 'comps' folder.
* .mp3 files are created in 'audio_files' folder.



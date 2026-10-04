# Attribution and dependencies

## FreeMote

Author: Ulysses (UlyssesWu / wdwxy12345).
Source: https://github.com/UlyssesWu/FreeMote
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.
The upstream license notice is included in `licenses/FreeMote.LICENSE.txt`.

`game_reader.py` is a new Python adaptation of the PSB v3 reading logic studied in FreeMote's `FreeMote.Psb/Psb.cs` and `PsbValues.cs`, including array encoding, name tries and value type decoding. It omits writing, rendering and resource decoding and adds limits and game-specific dialogue handling. This project is distributed under CC BY-NC-SA 4.0; non-commercial use only. No FreeMote binaries are bundled.

## SGRE Mod Manager

Author/uploader: sora9187 / asdadslab.
Source: https://gitlab.com/asdadslab/sgre-mod-manager

Its documented string-table anchor, resource wrapper description and patch target structure informed compatibility research. No manager source files or binaries are included. The manager must be obtained and installed separately under its own terms. This project is not endorsed by its author.

## Python dependencies

NumPy: https://numpy.org/ — BSD-3-Clause.
python-zstandard: https://github.com/indygreg/python-zstandard — BSD license.
Dependencies are installed separately via pip; their binaries are not included in this package. See each distribution's license notices.

## Development

Prepared for Yuxin Zhang with OpenAI Codex assistance. Game files supplied for validation remain outside the public package. Neither game assets nor the extracted resource key are included. STEINS;GATE and game assets belong to their respective rights holders. This is an unofficial fan project.

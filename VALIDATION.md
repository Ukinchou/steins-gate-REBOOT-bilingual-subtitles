# Validation

Validated on 2026-10-04 with the user-supplied STEINS;GATE RE:BOOT executable, scenario index and scenario body. These inputs and generated game-text ZIPs are not part of this repository.

## End-to-end generation

- Executable read as bytes; never executed.
- Resource key read locally and validated against the MZS scenario index.
- 187 index members, including 182 `*.ks` scenario scripts.
- 175 archive entries with 24,514 bilingual replacements.
- Replacement maps `(entry, JSON pointer) -> text` compared with the original complete mod: exact equality, no missing, added or changed dialogue replacements.
- The `config/language.psb.m` patch also matches the original exactly.
- ZIP metadata (version, description, notes, formatting) differs; ZIP bytes are not expected to match.

Both explicit input-file arguments and automatic discovery via `--game-dir` were exercised. Directory discovery used a local fixture linking the supplied input files under canonical game names, rather than a running Steam installation.

## Automated checks

All 11 unit tests pass. They cover language order, dialogue pointers, inline markup, untranslated scripts, equivalent markers, missing languages, invalid MZS headers, truncated PSB data, duplicate paths and generator output. All four executable Python modules compile successfully.

## Not validated

- Windows batch launchers and graphical folder picker on Windows.
- Applying the newly generated ZIP with a Mod Manager.
- In-game rendering, all story routes, font coverage and text overflow.
- Other game builds, other games or conflicts with configuration mods.

This validates extraction, alignment and generated patch data. It does not establish in-game compatibility or legal permission to modify a game.

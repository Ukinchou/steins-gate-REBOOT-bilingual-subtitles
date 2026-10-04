# STEINS;GATE RE:BOOT Bilingual Subtitle Toolkit

Generate Japanese–Simplified Chinese bilingual subtitle patches **locally from your own Steam game files**. The toolkit reads the scenario archive, pairs the game's built-in languages by dialogue slot, and writes a ZIP for a compatible `psb_patch` mod manager.

The public repository contains code, documentation and original demo sentences only. It contains no official dialogue, game executable, resource archive or game key.

## Windows: select your game folder

1. Install **Python 3.10 or later** with the Windows Python launcher and Tcl/Tk support (available in the standard Python installer).
2. Download this repository with **Code → Download ZIP**, then extract it.
3. Double-click `install_dependencies.bat` once. This creates a local virtual environment and installs NumPy and python-zstandard; internet access is needed for this step.
4. Double-click `start_windows.bat`.
5. Select the **SGRE install folder containing `sgre_steam.exe`**, then click **生成双语字幕 Mod** and choose where to save the output ZIP.
6. Install a compatible [SGRE Mod Manager](https://gitlab.com/asdadslab/sgre-mod-manager) separately. Place the generated ZIP in its `mods` folder and use the manager to enable/rebuild the mod as described by its author. Keep the game language set to **Japanese**.

The generator only reads game files. It does not modify the original executable or archives, install the loader, or invoke the manager. Chinese rendering uses the `textsc` configuration patch observed in the supplied working mod; layout and loader behavior still need in-game verification.

## Command line

From the extracted project directory:

```sh
python -m pip install -r requirements.txt
python build_from_game.py --game-dir "C:\Program Files (x86)\Steam\steamapps\common\SGRE"
```

Output defaults to `dist/bilingual_subtitles.zip`. For separately copied files or filenames changed during upload:

```sh
python build_from_game.py --exe "path/to/sgre_steam.exe" --info "path/to/scenario_info.psb.m" --body "path/to/scenario_body.bin" --output dist/bilingual_subtitles.zip
```

Internal resource names are canonical game names; uploaded filenames do not affect resource decoding. Use matching executable and scenario archive files from the same supported game build.

## How it works

- Validates a resource-key candidate read from the user's local executable against the scenario index. No key is hardcoded, printed or saved.
- Reads MZS-wrapped scenario members and plain PSB v3 data.
- Finds Simplified Chinese via the scenario's `languages` list (`sc`). Japanese occupies the base slot; translations occupy the following slots.
- Matches languages within each existing dialogue record, avoiding fuzzy matching and machine translation.
- Joins Japanese and Chinese with an actual newline while retaining inline markup and literal escape sequences.
- Leaves untranslated/empty pairs and identical text (ignoring trailing Japanese full stops) unchanged. This avoids duplicate forum markers and equivalent names.
- Generates scenario replacements and the optional language configuration used by the supplied original mod.

## Validation and limitations

The generation pipeline was run against the user-supplied executable and archives:

- 182 scenario scripts inspected.
- 175 scenario entries patched.
- 24,514 bilingual dialogue replacements.
- Scenario replacement paths and values compared against the existing complete mod.

See `VALIDATION.md` for the exact comparison and test results. This is a newly written implementation, not recovered source code of the original generator. It was developed with OpenAI Codex assistance.

**Not verified in-game:** text overflow, ruby/inline tag behavior, all scenes, and the loader/config patch on other versions. The Windows GUI and batch launchers have not been exercised on a Windows machine. Game updates can change the executable anchor, resource format or language layout; unsupported layouts produce errors. Other games are not supported merely because they contain two languages.

The font patch replaces the whole `/0` language configuration value with the configuration from the original supplied mod. Compatibility with other mods or changed game configurations is not guaranteed.

## Existing aligned JSON / private mod

The original lightweight generator remains available:

```sh
python generate_mod.py --input examples/sample.json --output dist/demo.zip
python generate_mod.py --input private/dialogue.json --font-patch
python generate_mod.py --from-mod private/original.zip
```

The original demo sentences are not game content; `demo.zip` is a format demonstration, not a playable full-game patch. Aligned input records use `entry`, `path`, `ja` and `zh`; see `examples/sample.json`.

## Tests

```sh
python -m unittest discover -s tests -v
```

## Publishing and license

Upload the source files and documentation. **Do not upload original game files, `private/`, `dist/` or generated Mod ZIPs**, which contain game dialogue. GitHub browser uploads do not obey `.gitignore` automatically.

CC BY-NC-SA 4.0, non-commercial use only. See `LICENSE` and `THIRD_PARTY_NOTICES.md`. The PSB reader is adapted with reference to FreeMote; attribution and its license notice are included. This project provides no assurance that a game's license authorizes extraction or modification. It does not bypass ownership checks or launch the game.

## 中文说明

这是《STEINS;GATE RE:BOOT》Steam 版专用的本地双语字幕生成器。

安装 Python → 运行 `install_dependencies.bat` → 运行 `start_windows.bat` → 选择游戏目录 → 保存字幕 ZIP。然后通过另外安装的兼容 Mod Manager 加载，并把游戏语言设为日语。

它从你自己的游戏中读取官方日文和简体中文，不需要自己整理 24,514 条台词。公开仓库不包含游戏台词、程序、资源或密钥；生成的完整字幕 ZIP 留在本地。已验证提取与生成数据，但尚未在游戏中验证新版显示效果。Windows 图形窗口与批处理也尚未在 Windows 实机测试。

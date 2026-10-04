"""Generate an SGRE bilingual ZIP from the user's local game files."""
import argparse
import json
from pathlib import Path
import zipfile

from game_reader import read_game
from generate_mod import generate, validate_mod


def build(exe, info, body, output, progress=print):
    rows = read_game(exe, info, body, progress)
    mod = generate(rows, font_patch=True)
    mod['Version'] = '2.0.0'
    validate_mod(mod)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('mod.json', json.dumps(mod, ensure_ascii=False, indent=2))
        archive.writestr('README.txt', 'Generated from your local game files.\nInstall a compatible SGRE psb_patch mod manager separately.\nPlace this ZIP in its mods folder, enable it, and rebuild via that manager.\nKeep the game language set to Japanese.\nThis generated ZIP contains game dialogue; do not publish it.\n')
    progress(f'Created {output} with {len(rows)} bilingual dialogue replacements.')
    return len(rows)


def locate(root):
    root = Path(root)
    exe = root / 'sgre_steam.exe'
    candidates = list(root.rglob('scenario_info.psb.m'))
    if not exe.is_file() or len(candidates) != 1:
        raise ValueError('Select the SGRE folder containing sgre_steam.exe and exactly one scenario archive')
    info = candidates[0]
    body = info.with_name('scenario_body.bin')
    if not body.is_file():
        raise ValueError('scenario_body.bin is missing beside scenario_info.psb.m')
    return exe, info, body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path)
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--info', type=Path)
    parser.add_argument('--body', type=Path)
    parser.add_argument('--output', type=Path, default=Path('dist/bilingual_subtitles.zip'))
    args = parser.parse_args()
    try:
        if args.game_dir:
            if any((args.exe, args.info, args.body)):
                raise ValueError('Use --game-dir or the three explicit file paths, not both')
            paths = locate(args.game_dir)
        elif all((args.exe, args.info, args.body)):
            paths = (args.exe, args.info, args.body)
        else:
            raise ValueError('Provide --game-dir or --exe, --info and --body')
        build(*paths, args.output)
    except (ValueError, OSError, KeyError, IndexError, UnicodeError) as error:
        parser.error(str(error))

if __name__ == '__main__':
    main()

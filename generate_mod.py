"""Generate a loader-compatible bilingual patch without distributing game text."""
import argparse
import json
from pathlib import Path
import re
import zipfile


def generate(rows, font_patch=False):
    entries = {}
    seen = set()
    if not isinstance(rows, list) or not rows:
        raise ValueError('Input must be a non-empty list of aligned dialogue records.')
    for row in rows:
        entry, path, jp, zh = (row[k] for k in ('entry', 'path', 'ja', 'zh'))
        if not all(isinstance(v, str) and v for v in (entry, path, jp, zh)):
            raise ValueError('entry, path, ja and zh must be non-empty strings.')
        if not re.fullmatch(r'/scenes/\d+/texts/\d+/1/0/1', path):
            raise ValueError(f'Unsupported Japanese dialogue pointer: {path}')
        if (entry, path) in seen:
            raise ValueError(f'Duplicate dialogue pointer: {entry} {path}')
        seen.add((entry, path))
        entries.setdefault(entry, []).append({'op': 'replace', 'path': path, 'value': jp + '\n' + zh})
    targets = [{'Archive': 'scenario', 'Entries': entries}]
    if font_patch:
        targets.append({'Archive': 'config', 'Entries': {'language.psb.m': [{
            'op': 'replace', 'path': '/0', 'value': {
                'facemap': {'text': 'textsc'},
                'option': {'width_time_scale': False, 'word_break': False},
                'prefix': 'jp', 'subfontscale': 0.6000000000000001}}]}})
    return {'Name': 'JP + Simplified Chinese Bilingual Subtitles',
            'Description': 'Combines locally supplied Japanese and Simplified Chinese dialogue.',
            'Version': '1.0.0', 'Type': 'psb_patch', 'Priority': 100, 'Targets': targets}


def validate_mod(mod):
    if not isinstance(mod, dict) or mod.get('Type') != 'psb_patch' or not isinstance(mod.get('Targets'), list) or not mod['Targets']:
        raise ValueError('Expected a psb_patch mod with non-empty Targets.')
    count = 0
    for target in mod['Targets']:
        if not isinstance(target.get('Archive'), str) or not isinstance(target.get('Entries'), dict):
            raise ValueError('Invalid archive target.')
        for patches in target['Entries'].values():
            if not isinstance(patches, list):
                raise ValueError('Expected patch arrays.')
            for patch in patches:
                if patch.get('op') != 'replace' or not isinstance(patch.get('path'), str) or not patch['path'].startswith('/') or 'value' not in patch:
                    raise ValueError('Expected replace operations with JSON pointers and values.')
                count += 1
    return count


def load_existing(path):
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as archive:
            return json.loads(archive.read('mod.json'))
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path, help='Locally prepared aligned dialogue JSON')
    source.add_argument('--from-mod', type=Path, help='Existing private mod.json or ZIP to repackage')
    parser.add_argument('--font-patch', action='store_true', help='Include the config patch observed in the supplied mod')
    parser.add_argument('--output', type=Path, default=Path('dist/bilingual_subtitles.zip'))
    args = parser.parse_args()
    try:
        if args.from_mod and args.font_patch:
            raise ValueError('--font-patch is only available with --input; repackaging preserves existing configuration.')
        mod = load_existing(args.from_mod) if args.from_mod else generate(json.loads(args.input.read_text(encoding='utf-8-sig')), args.font_patch)
        count = validate_mod(mod)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('mod.json', json.dumps(mod, ensure_ascii=False, indent=2))
            archive.writestr('README.txt', 'Generated locally. Keep the game language set to Japanese.\nUse the compatible mod loader and installation folder from your existing setup.\nGame text in this generated archive is for local use; do not commit it.\n')
        print(f'Wrote {args.output} ({count} replacement operations)')
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()

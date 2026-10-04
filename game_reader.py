"""Read locally owned SGRE assets. No game data or keys are embedded.

PSB decoding adapted with reference to FreeMote (UlyssesWu), CC BY-NC-SA 4.0.
See THIRD_PARTY_NOTICES.md and licenses/FreeMote.LICENSE.txt.
"""
import hashlib
from pathlib import Path
import struct

import numpy as np
import zstandard as zstd

MAX_PLAIN = 128 * 1024 * 1024


def unwrap(data, base_key, filename):
    if data[:4] != b'mzs\0' or len(data) < 12:
        raise ValueError(f'{filename}: expected an MZS resource')
    expected = struct.unpack_from('<I', data, 4)[0]
    if not 0 < expected <= MAX_PLAIN:
        raise ValueError(f'{filename}: invalid decompressed size')
    seed = np.frombuffer(hashlib.md5((base_key + filename).encode()).digest(), dtype='<u4')
    rng = np.random.RandomState(seed)
    stream = rng.randint(0, 2**32, size=33, dtype=np.uint32).astype('<u4').tobytes()[:131]
    # The title repeats a 131-byte XOR stream over each independently wrapped entry.
    encrypted = np.frombuffer(data, dtype=np.uint8, offset=8)
    mask = np.resize(np.frombuffer(stream, dtype=np.uint8), len(encrypted))
    compressed = np.bitwise_xor(encrypted, mask).tobytes()
    if compressed[:4] != b'\x28\xb5\x2f\xfd':
        raise ValueError(f'{filename}: resource key or filename does not match')
    plain = zstd.ZstdDecompressor().decompress(compressed, max_output_size=MAX_PLAIN)
    if len(plain) != expected:
        raise ValueError(f'{filename}: decompressed size mismatch')
    return plain


class PSB:
    """Subset reader for plain PSB v3 as observed in the supplied scenario archive."""
    def __init__(self, data):
        self.data = data
        if len(data) < 44 or data[:4] != b'PSB\0' or struct.unpack_from('<HH', data, 4) != (3, 0):
            raise ValueError('Expected an unencrypted PSB v3 payload')
        header = struct.unpack_from('<8I', data, 8)
        names_offset, strings_offset, self.strings_data, self.root = header[1], header[2], header[3], header[7]
        charset, pos = self.array(names_offset)
        parents, pos = self.array(pos)
        terminals, pos = self.array(pos)
        self.names = []
        for terminal in terminals:
            node = parents[terminal]
            chars = []
            visited = set()
            while node:
                if node in visited:
                    raise ValueError('Cyclic PSB name trie')
                visited.add(node)
                parent = parents[node]
                chars.append(node - charset[parent])
                node = parent
            self.names.append(bytes(reversed(chars)).decode('utf-8'))
        self.strings, _ = self.array(strings_offset)

    def read(self, pos, size):
        if pos < 0 or size < 0 or pos + size > len(self.data):
            raise ValueError('PSB read outside payload')
        return self.data[pos:pos + size]

    def uint(self, pos, size):
        return int.from_bytes(self.read(pos, size), 'little')

    def array(self, pos):
        count_width = self.uint(pos, 1) - 12
        if not 1 <= count_width <= 8:
            raise ValueError('Invalid PSB array tag')
        pos += 1
        count = self.uint(pos, count_width)
        pos += count_width
        item_width = self.uint(pos, 1) - 12
        pos += 1
        if not 1 <= item_width <= 8 or count > 1_000_000:
            raise ValueError('Invalid PSB array width or count')
        raw = self.read(pos, count * item_width)
        return [int.from_bytes(raw[i:i + item_width], 'little') for i in range(0, len(raw), item_width)], pos + len(raw)

    def string(self, index):
        pos = self.strings_data + self.strings[index]
        self.read(pos, 1)
        end = self.data.find(b'\0', pos)
        if end < 0:
            raise ValueError('Unterminated PSB string')
        return self.data[pos:end].decode('utf-8')

    def value(self, pos, depth=0):
        if depth > 100:
            raise ValueError('PSB nesting limit exceeded')
        tag = self.uint(pos, 1)
        pos += 1
        if tag in (0, 1):
            return None
        if tag in (2, 3):
            return tag == 3
        if tag == 4:
            return 0
        if 5 <= tag <= 12:
            return int.from_bytes(self.read(pos, tag - 4), 'little', signed=True)
        if 13 <= tag <= 20:
            return self.array(pos - 1)[0]
        if 21 <= tag <= 24:
            return self.string(self.uint(pos, tag - 20))
        if 25 <= tag <= 28:
            return {'resource_index': self.uint(pos, tag - 24)}
        if tag == 29:
            return 0.0
        if tag in (30, 31):
            return struct.unpack('<f' if tag == 30 else '<d', self.read(pos, 4 if tag == 30 else 8))[0]
        if tag == 32:
            offsets, base = self.array(pos)
            return [self.value(base + offset, depth + 1) for offset in offsets]
        if tag == 33:
            names, pos = self.array(pos)
            offsets, base = self.array(pos)
            if len(names) != len(offsets) or len(set(names)) != len(names):
                raise ValueError('Invalid PSB dictionary')
            return {self.names[name]: self.value(base + offset, depth + 1) for name, offset in zip(names, offsets)}
        raise ValueError(f'Unsupported PSB tag: {tag}')

    def load(self):
        return self.value(self.root)


def extract_key(exe_path, info_bytes):
    """Find a nearby key candidate and validate it against the user's archive.

    The public mod manager documents the script_info.psb.m string-table anchor.
    This reader scans a small surrounding region rather than storing a game key.
    """
    data = Path(exe_path).read_bytes()
    if data[:2] != b'MZ':
        raise ValueError('Expected the local Windows game executable')
    anchor = b'script_info.psb.m'
    offset = 0
    while True:
        offset = data.find(anchor, offset)
        if offset < 0:
            break
        for start in range(max(1, offset - 80), offset):
            end = start + 13
            candidate = data[start:end]
            if data[start - 1] != 0 or data[end:end + 1] != b'\0' or len(candidate) != 13 or not all(32 <= b <= 126 for b in candidate):
                continue
            key = candidate.decode('ascii')
            try:
                plain = unwrap(info_bytes, key, 'scenario_info.psb.m')
                if plain[:4] == b'PSB\0':
                    return key
            except (ValueError, zstd.ZstdError):
                pass
        offset += len(anchor)
    raise ValueError('Game build not supported: could not validate its resource key')


def align_dialogue(document, entry):
    """Use per-dialogue language slots, never fuzzy matching or machine translation."""
    if not isinstance(document, dict) or 'scenes' not in document:
        return []
    languages = document.get('languages')
    if not isinstance(languages, list) or 'sc' not in languages:
        raise ValueError(f'{entry}: missing Simplified Chinese language identifier')
    chinese_slot = languages.index('sc') + 1  # slot zero is the base Japanese text
    rows = []
    for scene_index, scene in enumerate(document['scenes']):
        for text_index, text in enumerate(scene.get('texts', [])):
            if not isinstance(text, list) or len(text) < 2 or not isinstance(text[1], list):
                raise ValueError(f'{entry}: unexpected dialogue structure')
            slots = text[1]
            if len(slots) <= chinese_slot:
                continue  # Some bundled test scripts contain Japanese only.
            if not isinstance(slots[0], list) or not isinstance(slots[chinese_slot], list) or len(slots[0]) < 2 or len(slots[chinese_slot]) < 2:
                raise ValueError(f'{entry}: incomplete language slots')
            japanese, chinese = slots[0][1], slots[chinese_slot][1]
            if japanese is None or chinese is None or japanese == '' or chinese == '':
                continue
            if not isinstance(japanese, str) or not isinstance(chinese, str):
                raise ValueError(f'{entry}: unexpected dialogue value')
            if japanese.rstrip('。') == chinese.rstrip('。'):
                continue  # Equivalent markers/names; tolerate a trailing full stop.
            rows.append({'entry': entry, 'path': f'/scenes/{scene_index}/texts/{text_index}/1/0/1', 'ja': japanese, 'zh': chinese})
    return rows


def read_game(exe, info, body_path, progress=print):
    info_bytes = Path(info).read_bytes()
    key = extract_key(exe, info_bytes)
    index = PSB(unwrap(info_bytes, key, 'scenario_info.psb.m')).load()
    files = index.get('file_info')
    suffixes = index.get('expire_suffix_list')
    if not isinstance(files, dict) or suffixes != ['.scn.m']:
        raise ValueError('Unsupported scenario index layout')
    rows = []
    inspected = 0
    with Path(body_path).open('rb') as body:
        size = Path(body_path).stat().st_size
        for name, span in files.items():
            if not isinstance(span, list) or len(span) != 2 or not all(isinstance(v, int) and v >= 0 for v in span):
                raise ValueError('Invalid scenario entry span')
            offset, length = span
            if offset + length > size:
                raise ValueError('Scenario span exceeds body size')
            # Scenario scripts are the *.ks members. Registry/sample entries are
            # inspected too; they produce no rows if they have no dialogue.
            if not name.endswith('.ks'):
                continue
            filename = name + '.scn.m'
            body.seek(offset)
            plain = unwrap(body.read(length), key, filename)
            document = PSB(plain).load()
            rows.extend(align_dialogue(document, filename))
            inspected += 1
            if inspected % 20 == 0:
                progress(f'Inspected {inspected} scenario scripts...')
    if not rows:
        raise ValueError('No bilingual dialogue found')
    progress(f'Aligned {len(rows)} dialogue pairs from {inspected} scripts.')
    return rows

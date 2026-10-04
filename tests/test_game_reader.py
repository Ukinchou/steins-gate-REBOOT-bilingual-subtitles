import struct
import unittest
from game_reader import PSB, align_dialogue, unwrap

class ReaderTests(unittest.TestCase):
    def document(self, languages=None):
        return {'languages': languages or ['en', 'tc', 'sc'], 'scenes': [{'texts': [['speaker', [[None, '日本語', 1], [None, 'English', 1], [None, '繁體', 1], [None, '简体', 1]]]]}]}

    def test_language_order_is_not_hardcoded(self):
        d = self.document(['sc', 'en', 'tc'])
        d['scenes'][0]['texts'][0][1][1][1] = '中文'
        self.assertEqual(align_dialogue(d, 'example')[0]['zh'], '中文')

    def test_pointer_and_markup_preserved(self):
        d = self.document()
        d['scenes'][0]['texts'][0][1][0][1] = '[語]日本語\\n次'
        row = align_dialogue(d, 'example')[0]
        self.assertEqual(row['path'], '/scenes/0/texts/0/1/0/1')
        self.assertEqual(row['ja'], '[語]日本語\\n次')

    def test_untranslated_test_lines_unchanged(self):
        d = self.document()
        d['scenes'][0]['texts'][0][1] = [[None, 'テスト', 1]]
        self.assertEqual(align_dialogue(d, 'example'), [])

    def test_equivalent_markers_unchanged(self):
        d = self.document()
        d['scenes'][0]['texts'][0][1][0][1] = '>>123'
        d['scenes'][0]['texts'][0][1][3][1] = '>>123'
        self.assertEqual(align_dialogue(d, 'example'), [])

    def test_missing_language_rejected(self):
        with self.assertRaises(ValueError):
            align_dialogue(self.document(['en']), 'example')

    def test_bad_mzs_and_oversized_header_rejected(self):
        with self.assertRaises(ValueError):
            unwrap(b'not-mzs-data', 'fake', 'example')
        with self.assertRaises(ValueError):
            unwrap(b'mzs\0' + struct.pack('<I', 2**31) + b'xxxx', 'fake', 'example')

    def test_truncated_psb_rejected(self):
        with self.assertRaises(ValueError):
            PSB(b'PSB\0')

if __name__ == '__main__':
    unittest.main()

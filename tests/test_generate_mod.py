import unittest
from generate_mod import generate, validate_mod

class GeneratorTests(unittest.TestCase):
    def row(self):
        return {'entry': 'demo.ks.scn.m', 'path': '/scenes/1/texts/0/1/0/1', 'ja': '例\\n[語]ことば', 'zh': '示例'}

    def test_preserves_markup_and_literal_escapes(self):
        mod = generate([self.row()], True)
        self.assertEqual(mod['Targets'][0]['Entries']['demo.ks.scn.m'][0]['value'], '例\\n[語]ことば\n示例')
        self.assertEqual(validate_mod(mod), 2)
        self.assertEqual(mod['Targets'][1]['Entries']['language.psb.m'][0]['value']['facemap'], {'text': 'textsc'})

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            generate([self.row(), self.row()])

    def test_invalid_pointer_rejected(self):
        row = self.row()
        row['path'] = '/unrelated'
        with self.assertRaises(ValueError):
            generate([row])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            generate([])

if __name__ == '__main__':
    unittest.main()

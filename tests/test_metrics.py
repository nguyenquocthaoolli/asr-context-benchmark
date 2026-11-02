import unittest
from metrics import normalize, edit_distance, summarize, paired_changes

class MetricsTests(unittest.TestCase):
    def test_case_punctuation(self):
        self.assertEqual(normalize("No, don't cancel!"), ['no', "don't", 'cancel'])
    def test_word_edits(self):
        self.assertEqual(edit_distance(['no', 'cancel'], ['yes', 'please', 'cancel']), 2)
        self.assertEqual(edit_distance(['no'], []), 1)
        self.assertEqual(edit_distance([], ['yes']), 1)
    def test_corpus_weighting(self):
        rows=[{'reference':'yes','text':'no'}, {'reference':'one two three','text':'one two three'}]
        self.assertEqual(summarize(rows)['wer'], .25)
        self.assertEqual(summarize(rows)['exact_match_rate'], .5)
    def test_empty_reference_not_silent_zero(self):
        with self.assertRaises(ValueError): summarize([{'reference':'','text':'yes'}])
    def test_paired_worsening_and_improvement(self):
        rows=[{'sample_id':'a','condition':'none','reference':'no','text':'no'},
              {'sample_id':'a','condition':'misleading','reference':'no','text':'yes'},
              {'sample_id':'b','condition':'none','reference':'yes','text':'no'},
              {'sample_id':'b','condition':'misleading','reference':'yes','text':'yes'}]
        self.assertEqual(paired_changes(rows,'misleading'), {'improved':1,'worsened':1,'unchanged':0})
    def test_missing_pair_rejected(self):
        with self.assertRaises(ValueError): paired_changes([{'sample_id':'a','condition':'none','reference':'no','text':'no'}], 'relevant')

if __name__=='__main__': unittest.main()

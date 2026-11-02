import copy, json, unittest
from pathlib import Path
from analyze import analyze

ROOT=Path(__file__).resolve().parents[1]
class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.rows=[json.loads(line) for line in (ROOT/'results/pilot/raw.jsonl').read_text().splitlines()]
    def test_complete_pilot_evidence(self):
        self.assertEqual(len(self.rows),144)
        a=analyze(self.rows)['0']
        self.assertEqual(a['conditions']['none']['reference_words'],220)
        self.assertEqual(a['conditions']['none']['word_errors'],90)
        self.assertEqual(a['conditions']['relevant']['word_errors'],72)
        self.assertEqual(a['conditions']['misleading']['word_errors'],61)
    def test_changed_text_is_distinct_from_same_edit_count(self):
        rows=[copy.deepcopy(self.rows[0]) for _ in range(3)]
        for r,c,text in zip(rows,['none','relevant','misleading'],['yes','no','maybe']):
            r.update(condition=c,reference='okay',text=text)
        pairs=analyze(rows)['0']['paired']['relevant']
        self.assertEqual(pairs['same_word_error_count'],1)
        self.assertEqual(pairs['normalized_transcript_changed'],1)
    def test_mismatched_audio_rejected(self):
        self.rows[0]['audio_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'Different audio'): analyze(self.rows)
    def test_missing_condition_rejected(self):
        with self.assertRaisesRegex(ValueError,'Incomplete'): analyze(self.rows[1:])
    def test_duplicate_observation_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'): analyze(self.rows+[self.rows[0]])

if __name__=='__main__': unittest.main()

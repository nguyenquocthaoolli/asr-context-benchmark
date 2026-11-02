import hashlib, json, unittest, wave
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class IntegrityTests(unittest.TestCase):
    def test_manifest_is_complete_factorial_and_audio_unchanged(self):
        rows=json.loads((ROOT/'manifest.json').read_text())
        self.assertEqual(len(rows),48)
        self.assertEqual(len({r['sample_id'] for r in rows}),48)
        cases=json.loads((ROOT/'cases.json').read_text())
        self.assertEqual({(r['id'],r['voice'],r['variant']) for r in rows},
                         {(c['id'],v,n) for c in cases for v in ['en-us','en-gb'] for n in ['clean','noise12db']})
        for r in rows:
            path=ROOT/r['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),r['sha256'])
            self.assertEqual(r['clipped_samples'],0)
            with wave.open(str(path),'rb') as f:
                self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(1,2,16000))
                self.assertAlmostEqual(f.getnframes()/16000,r['duration_s'])
    def test_prompts_do_not_copy_entire_reference(self):
        for c in json.loads((ROOT/'cases.json').read_text()):
            for cond in ['relevant','misleading']:
                self.assertNotIn(c['reference'].lower().strip('.'),c[cond].lower())

if __name__=='__main__': unittest.main()

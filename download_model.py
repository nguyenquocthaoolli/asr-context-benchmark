"""Download pinned model files without requiring a Hugging Face account."""
import argparse, hashlib, json, urllib.request
from pathlib import Path

REPO='Systran/faster-whisper-tiny.en'
REVISION='0d3d19a32d3338f10357c0889762bd8d64bbdeba'
FILES=['config.json','model.bin','tokenizer.json','vocabulary.txt']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination',type=Path,default=Path('models/tiny.en'))
    args=p.parse_args(); args.destination.mkdir(parents=True,exist_ok=True)
    expected=json.loads((Path(__file__).parent/'model_provenance.json').read_text())
    hashes={}
    for name in FILES:
        target=args.destination/name
        with urllib.request.urlopen(f'https://huggingface.co/{REPO}/resolve/{REVISION}/{name}',timeout=120) as r:
            data=r.read()
        digest=hashlib.sha256(data).hexdigest()
        if digest!=expected['sha256'][name]: raise ValueError(f'Model checksum mismatch: {name}')
        target.write_bytes(data); hashes[name]=digest
        print(name, len(data))
    (args.destination/'provenance.json').write_text(json.dumps({'repository':REPO,'revision':REVISION,'sha256':hashes},indent=2)+'\n')

if __name__=='__main__': main()

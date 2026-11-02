"""Run offline Whisper context comparisons; no API credentials required."""
import argparse, hashlib, importlib.metadata, json, os, platform, random, time, wave
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from faster_whisper import WhisperModel
from metrics import summarize, paired_changes

ROOT=Path(__file__).resolve().parent
CONDITIONS=('none','relevant','misleading')
SETTINGS=dict(language='en',beam_size=5,temperature=0.0,condition_on_previous_text=False,
              vad_filter=False,word_timestamps=False)

def load_audio(path):
    with wave.open(str(path), "rb") as wav:
        return np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float32)/32768.0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'results'/'pilot')
    parser.add_argument('--sample',action='append',help='Restrict to exact manifest sample ID; repeatable')
    parser.add_argument('--repetitions',type=int,default=1)
    args=parser.parse_args()
    if args.repetitions<1: parser.error('--repetitions must be positive')
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'manifest.json').read_text())
    if args.sample:
        unknown=set(args.sample)-{r['sample_id'] for r in manifest}
        if unknown: parser.error(f'Unknown sample IDs: {sorted(unknown)}')
        manifest=[r for r in manifest if r['sample_id'] in args.sample]
    for item in manifest:
        path=ROOT/item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError(f'Audio hash mismatch: {path}')
        with wave.open(str(path),'rb') as wav:
            if (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())!=(1,2,16000):
                raise ValueError(f'Expected mono 16-bit 16 kHz WAV: {path}')
    model_dir=args.model_dir.resolve()
    provenance=json.loads((model_dir/'provenance.json').read_text())
    for name,expected in provenance['sha256'].items():
        if hashlib.sha256((model_dir/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Model hash mismatch: {name}')
    metadata={'started_utc':datetime.now(timezone.utc).isoformat(),'model':provenance,
              'python':platform.python_version(),'platform':platform.platform(),'cpu_count':os.cpu_count(),
              'packages':{name:importlib.metadata.version(name) for name in ['faster-whisper','ctranslate2','numpy','av','tokenizers']},
              'device':'cpu','compute_type':'int8','cpu_threads':4,'settings':SETTINGS,
              'condition_order_seed':42,'repetitions':args.repetitions,
              'manifest_sha256':hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest(),
              'timing':'Wall-clock complete offline transcription incl audio decode and generator iteration, after one warmup; not streaming or end-to-end voice latency'}
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    model=WhisperModel(str(model_dir),device='cpu',compute_type='int8',cpu_threads=4,num_workers=1,local_files_only=True)
    segments,_=model.transcribe(load_audio(ROOT/manifest[0]['path']),**SETTINGS)
    list(segments)
    jobs=[(rep,item,condition) for rep in range(args.repetitions) for item in manifest for condition in CONDITIONS]
    random.Random(42).shuffle(jobs)
    results=[]
    with (out/'raw.jsonl').open('w') as f:
        for index,(rep,item,condition) in enumerate(jobs):
            prompt=None if condition=='none' else item[condition]
            start=time.perf_counter()
            segments,info=model.transcribe(load_audio(ROOT/item['path']),initial_prompt=prompt,**SETTINGS)
            segments=list(segments)
            elapsed=time.perf_counter()-start
            row={'sample_id':item['sample_id'],'case_id':item['id'],'category':item['category'],
                 'voice':item['voice'],'variant':item['variant'],'reference':item['reference'],
                 'audio_path':item['path'],'audio_sha256':item['sha256'],'duration_s':item['duration_s'],
                 'condition':condition,'prompt':prompt,'repetition':rep,'text':''.join(s.text for s in segments).strip(),
                 'offline_compute_s':elapsed,'segments':[{'start':s.start,'end':s.end,'text':s.text} for s in segments]}
            results.append(row); f.write(json.dumps(row)+'\n'); f.flush()
            print(f"{index+1}/{len(jobs)} {item['sample_id']} {condition}: {row['text']}",flush=True)
    summaries={}
    for rep in range(args.repetitions):
        subset=[r for r in results if r['repetition']==rep]
        summaries[str(rep)]={c:summarize([r for r in subset if r['condition']==c]) for c in CONDITIONS}
        summaries[str(rep)]['paired']={c:paired_changes(subset,c) for c in CONDITIONS if c!='none'}
    (out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')

if __name__=='__main__': main()

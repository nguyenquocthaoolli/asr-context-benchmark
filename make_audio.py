"""Generate controlled synthetic fixtures; included WAVs are canonical."""
import hashlib, json, subprocess, tempfile, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def main():
    cases=json.loads((ROOT/'cases.json').read_text())
    dest=ROOT/'audio'; dest.mkdir(exist_ok=True)
    rows=[]
    for i,case in enumerate(cases):
        for voice in ['en-us','en-gb']:
            with tempfile.TemporaryDirectory() as temp:
                src=Path(temp)/'tts.wav'; converted=Path(temp)/'pcm.wav'
                subprocess.run(['espeak-ng','-v',voice,'-s','155','-w',str(src),case['reference']],check=True)
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(converted)],check=True)
                with wave.open(str(converted),'rb') as f:
                    signal=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32768
            # Silence padding is identical in every condition.
            padded=np.pad(signal,(3200,4800))
            for variant in ['clean','noise12db']:
                seed=20261102+i*10+(voice=='en-gb')
                audio=padded.copy()
                if variant=='noise12db':
                    noise=np.random.default_rng(seed).normal(size=len(audio))
                    # SNR relative to RMS of complete unpadded TTS output, including its pauses.
                    noise*=np.sqrt(np.mean(signal**2))/(10**(12/20)*np.sqrt(np.mean(noise**2)))
                    audio+=noise
                clipped=int(np.count_nonzero(np.abs(audio)>1))
                pcm=(np.clip(audio,-1,1)*32767).astype('<i2')
                sample=f"{case['id']}_{voice}_{variant}"; path=dest/f'{sample}.wav'
                with wave.open(str(path),'wb') as f:
                    f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000); f.writeframes(pcm.tobytes())
                rows.append({**case,'sample_id':sample,'voice':voice,'variant':variant,
                             'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                             'duration_s':len(pcm)/16000,'noise_seed':seed if variant!='clean' else None,'clipped_samples':clipped})
    (ROOT/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    tools={name:subprocess.check_output(command,text=True).splitlines()[0] for name,command in
           [('espeak-ng',['espeak-ng','--version']),('ffmpeg',['ffmpeg','-version'])]}
    (ROOT/'audio_provenance.json').write_text(json.dumps({'tools':tools,'synthetic':True,'human_audio':False,'sample_rate':16000,'speed_wpm':155,'noise':'Gaussian white noise, nominal 12 dB; RMS uses complete unpadded TTS waveform','cases_sha256':hashlib.sha256((ROOT/'cases.json').read_bytes()).hexdigest()},indent=2)+'\n')
    print(f'Generated {len(rows)} WAV files')

if __name__=='__main__': main()

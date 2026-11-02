# ASR context-sensitivity pilot

A small, reproducible experiment on whether textual context helps or distorts speech recognition. This package contains the audio, prompts, raw outputs, scoring code, model checksums, and a draft failure report.

**Scope:** offline Whisper tiny.en, through faster-whisper with CPU int8 inference. It does not benchmark Flux, AssemblyAI, Soniox, X2Streaming-ASR, streaming turn detection, or speech-to-speech response latency. Those systems motivated the question but were not available in this environment.

## Results

Read [REPORT.md](REPORT.md) for the full findings and [FAILURE_REPORT.md](FAILURE_REPORT.md) for the standalone behavior report. The pilot contains 144 transcriptions plus 18 repeat observations.

## Reproduce

Tested on Linux, Python 3.13. The model download is about 75 MB plus tokenizer/configuration files; no API key is needed. Install dependencies in an isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python download_model.py --destination models/tiny.en
.venv/bin/python run_benchmark.py --model-dir models/tiny.en --output results/my-run
```

Output directories must be new, to prevent overwriting evidence. Audio and model checksums are verified before inference. Included results can be analyzed without downloading a model.

```bash
.venv/bin/python analyze.py --input results/pilot/raw.jsonl --output results/pilot/analysis.json
```

To repeat only one fixture:

```bash
.venv/bin/python run_benchmark.py --model-dir models/tiny.en \
  --sample name_en-gb_clean --repetitions 3 --output results/my-name-repro
```

## Protocol

- Twelve utterances authored before inference: negation, short answers, names, location, technical vocabulary, self-corrections, identifier, address, and refund intent.
- Two eSpeak NG voices (`en-us`, `en-gb`), each at 155 words/minute; these are synthetic voices, not independent human speakers or representative accents.
- Clean and nominal 12 dB Gaussian noise versions: 48 WAV files, mono PCM16, 16 kHz. All WAVs are included and are the canonical reproduction inputs.
- Each identical waveform is tested with no initial prompt, relevant context, and deliberately misleading/conflicting context: 144 transcriptions.
- Relevant prompts may contain candidate vocabulary (including the correct entity), which is intentional vocabulary biasing, not independent discovery of an unknown name. Conflicting prompts may contain alternative names or false assumptions. This pilot does not isolate dialogue memory from vocabulary effects.
- Prompts do not contain the full reference transcript. No prompt or audio was selected or revised based on pilot outcomes. The highlighted failure is selected after evaluation and is therefore exploratory.
- Fixed model revision and model-file SHA-256 checksums; beam size 5; temperature 0; language English; VAD disabled; previous-text conditioning disabled. Each call supplies only that condition's initial prompt.
- All jobs shuffled with seed 42; one unscored warmup. Raw outputs retain execution order, context, repetition, audio hash, and timings.

## Metrics and interpretation

Word error rate (WER) is the sum of token edit distances divided by total reference words, not the average of sentence WERs. Normalization lowercases ASCII words, strips punctuation, and retains internal apostrophes. **Numeral rendering and contractions are not normalized**: `749` versus `seven four nine`, or `it's` versus `it is`, can incur errors without changing meaning. WER is not semantic intent accuracy.

Paired counts classify each audio fixture as improved/worsened/unchanged versus no context by lexical edit distance. Exact match is normalized lexical equality. The four variants of each utterance are correlated; 48 fixtures are not 48 independent speakers or conversations. No significance or generalization claim is made.

`offline_compute_s` measures the complete local transcription call, including PCM reading and generator iteration, after model loading/warmup. It is neither word emission latency nor turn-end latency. Timing depends on hardware and other processes.

References are the text submitted to TTS. The project owner listened to `name_en-gb_clean.wav` and confirmed hearing “Mira Patel” on 2026-11-02. Other fixtures have not been independently human-transcribed; pronunciation ambiguities can affect apparent recognition errors. There are no recorded people, customer data, or external speech datasets in this pilot.

## Regenerate audio (optional)

Requires `espeak-ng` and `ffmpeg` system executables, in addition to NumPy. Exact tool versions are recorded in `audio_provenance.json`.

```bash
.venv/bin/python make_audio.py
```

This overwrites WAVs and their manifest. Tool/version changes can produce different audio: use the bundled WAVs to reproduce the published observations. Noise is scaled using RMS over the entire unpadded TTS waveform (including pauses), not an active-speech SNR measurement.

## Contribution and publication status

Published repository: [nguyenquocthaoolli/asr-context-benchmark](https://github.com/nguyenquocthaoolli/asr-context-benchmark). Maintainer question: [faster-whisper discussion #1687](https://github.com/SYSTRAN/faster-whisper/discussions/1687).

This repository contains the complete pilot and a reproducible behavior report in `FAILURE_REPORT.md`, not a claim of a new implementation defect. The highlighted name clip has been checked by the project owner; the remaining fixtures still need human validation. Keep model weights and virtual environments out of Git; their download instructions and hashes are included instead.

Useful follow-ups are human-validated audio; more speakers and languages; balanced unrelated/stale contexts; multiple prompt wordings; a larger Whisper model; and adapters to contextual streaming APIs. Test each provider's native context interface separately.

## Sources

- [Whisper model card](https://huggingface.co/openai/whisper-tiny.en)
- [Converted model](https://huggingface.co/Systran/faster-whisper-tiny.en)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Pipecat STT benchmark](https://github.com/pipecat-ai/stt-benchmark)

## License

Original benchmark code is offered under the MIT license in `LICENSE`. Original case text, prompts, and generated audio fixtures are offered under CC0-1.0 (see `DATA_LICENSE.md`). Third-party models, runtimes and synthesis tools retain their own licenses and are not included. Model outputs are included as evaluation evidence, without a claim of exclusive ownership.

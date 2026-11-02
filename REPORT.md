# Context-sensitivity pilot results

Executed 2026-11-02. Model: Whisper tiny.en, converted by Systran, faster-whisper 1.2.1, CPU int8.

**Finding:** Context changed recognition of identical audio. A misleading name list caused a correct baseline transcription of “Mira Patel” to become “Nina Patel.” The example reproduced in three additional transcription calls per condition. However, misleading context had the lowest aggregate lexical WER in this small pilot; the results do not show that misleading context is generally worse.

## Complete pilot results

| Context | Fixtures | Word errors / reference words | Lexical WER | Exact matches |
|---|---:|---:|---:|---:|
| None | 48 | 90 / 220 | 40.91% | 18 / 48 |
| Relevant | 48 | 72 / 220 | 32.73% | 23 / 48 |
| Misleading | 48 | 61 / 220 | 27.73% | 22 / 48 |

Against no context: relevant prompts reduced word errors on 12 fixtures, increased them on 4, and had the same count on 32. Misleading prompts reduced them on 14, increased them on 4, and had the same count on 30. Normalized transcripts changed on 18 and 22 fixtures respectively. Equal edit counts do not mean identical words or meaning.

These are 48 correlated synthetic variants of only 12 utterances, not 48 independent speakers. The high error rates were observed with a small model and synthetic speech/noise; their causes were not isolated. This is a descriptive pilot, not a leaderboard.

## Reproduced name substitution

Fixture: [`audio/name_en-gb_clean.wav`](audio/name_en-gb_clean.wav). TTS input: “My name is Mira Patel.”

| Context | Exact initial prompt | Transcript in pilot and all 3 repeats |
|---|---|---|
| None | No prompt | My name is Mira Patel. |
| Relevant | The customer directory includes Mira Patel and Nora Chen. | My name is Mira Patel. |
| Misleading | The customer directory includes Nina Patel and Laura Chen. | My name is Nina Patel. |

The audio bytes and decoder settings were identical across conditions. This demonstrates prompt sensitivity in this specific configuration, not proof of a software defect or a new failure class. The relevant condition includes the target name as a vocabulary hint; it is not a test of reasoning alone.

## Negative control for causal interpretation

The noisy short-answer fixture `accept_en-us_noise12db` has TTS input “Yes, that is correct.” It produces “Yes, that's incorrect.” under **all three** context conditions in the pilot and each of three repeats. This is a recognition failure candidate, but it cannot be attributed to context in this experiment. It is retained in the evidence rather than presented as a context-induced regression.

## Interpretation limits

- TTS input is the reference. On 2026-11-02, the project owner listened to `name_en-gb_clean.wav` and confirmed hearing “Mira Patel.” This is one listener’s confirmation of the highlighted name, not independent validation of the entire dataset.
- WER does not normalize numerals or contractions: “749” versus “seven four nine” incurs lexical errors despite preserving the identifier.
- The selected failure was chosen after viewing the full pilot. Three deterministic reruns establish repeatability on this machine, not a population failure rate.
- No paired human dataset, prompt-paraphrase sweep, confidence interval, or cross-hardware replication was performed.
- This model is offline. No streaming word latency, endpoint accuracy, barge-in, or speech-to-speech response time was measured.
- Results do not transfer to Flux, AssemblyAI, Soniox, X2Streaming-ASR, larger Whisper models, or other decoding settings.

## Evidence and reproduction

- [`README.md`](README.md): setup, protocol, interpretation and publication instructions.
- [`results/pilot/raw.jsonl`](results/pilot/raw.jsonl): all 144 primary transcriptions, in execution order.
- [`results/pilot/analysis.json`](results/pilot/analysis.json): scores, condition changes and every lexical regression.
- [`results/reproduction/raw.jsonl`](results/reproduction/raw.jsonl): 18 repeat observations (2 fixtures × 3 conditions × 3 repetitions).
- [`results/environment.json`](results/environment.json): execution commands and hardware.
- [`FAILURE_REPORT.md`](FAILURE_REPORT.md): standalone behavior report for a repository discussion.

Published on 2026-11-02 in [asr-context-benchmark](https://github.com/nguyenquocthaoolli/asr-context-benchmark) and shared in [faster-whisper Q&A #1687](https://github.com/SYSTRAN/faster-whisper/discussions/1687).

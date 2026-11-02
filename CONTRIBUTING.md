# Contributing

Start with a reproducible example or a proposed experimental change. Do not change the original pilot cases or stored outputs to improve reported scores. Add a versioned dataset/run instead.

Useful contributions:
- Human-validated speech with documented consent and redistribution rights.
- Balanced correct, unrelated, stale, and conflicting context conditions.
- Provider adapters recording native API settings, model version/date, exact prompt, waveform hash, and all outputs.
- Semantic annotation for negation, entities, corrections, and identifiers, separate from lexical WER.
- Streaming measurements with explicit boundaries: word emission, transcript finalization, turn-end detection, and first audible response.

Run `python -m unittest discover -s tests -v` before proposing a change. Include every evaluated case, software/hardware metadata, and failures. Do not include API keys or private customer recordings.

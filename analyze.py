"""Recompute descriptive results from raw benchmark evidence."""
import argparse, json, statistics
from pathlib import Path
from metrics import summarize, paired_changes, normalize, errors

def analyze(rows):
    result={}
    for rep in sorted({r['repetition'] for r in rows}):
        subset=[r for r in rows if r['repetition']==rep]
        by_sample={}
        for r in subset:
            pair=by_sample.setdefault(r['sample_id'],{})
            if r['condition'] in pair: raise ValueError('Duplicate sample-condition pair')
            pair[r['condition']]=r
        for pair in by_sample.values():
            if set(pair)!={'none','relevant','misleading'}: raise ValueError('Incomplete context comparison')
            if len({r['audio_sha256'] for r in pair.values()})!=1: raise ValueError('Different audio in paired comparison')
            if len({r['reference'] for r in pair.values()})!=1: raise ValueError('Different references in paired comparison')
        condition_summary={}
        for cond in ['none','relevant','misleading']:
            selected=[r for r in subset if r['condition']==cond]
            times=sorted(r['offline_compute_s'] for r in selected)
            condition_summary[cond]={**summarize(selected),
                'median_offline_compute_s':statistics.median(times),
                'by_audio_variant':{variant:summarize([r for r in selected if r['variant']==variant]) for variant in sorted({r['variant'] for r in selected})}}
        pairs={}
        for cond in ['relevant','misleading']:
            change=paired_changes(subset,cond)
            pairs[cond]={'fewer_word_errors':change['improved'],'more_word_errors':change['worsened'],
                         'same_word_error_count':change['unchanged'],
                         'normalized_transcript_changed':sum(normalize(p[cond]['text'])!=normalize(p['none']['text']) for p in by_sample.values())}
        regressions=[{'sample_id':sid,'condition':cond,'reference':pair[cond]['reference'],
                      'none':pair['none']['text'],'context_output':pair[cond]['text'],
                      'prompt':pair[cond]['prompt'],'extra_word_errors':errors(pair[cond])-errors(pair['none'])}
                     for sid,pair in sorted(by_sample.items()) for cond in ['relevant','misleading']
                     if errors(pair[cond])>errors(pair['none'])]
        result[str(rep)]={'conditions':condition_summary,'paired':pairs,'lexical_regressions':regressions}
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    rows=[json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    if not rows: p.error('Input contains no observations')
    args.output.write_text(json.dumps(analyze(rows),indent=2)+'\n')
    print(f'Analyzed {len(rows)} observations -> {args.output}')

if __name__=='__main__': main()

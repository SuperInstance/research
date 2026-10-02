"""Round 22: JEV evaluates the discovery summary itself."""
import sys, json
sys.path.insert(0, '/workspace/research')
from jev_client import ask, noul, score, choice

text = open('/workspace/research/SEPT24_DISCOVERY_SUMMARY.md').read()
print(f'Text length: {len(text)}')

r = ask(text[:4000], {
    'is_useful': noul('Is this a useful discovery summary?'),
    'novelty': score('Rate novelty', ['common', 'uncommon', 'novel', 'frontier']),
    'depth': score('Rate technical depth', ['shallow', 'moderate', 'deep', 'frontier']),
    'is_publishable': noul('Is this publishable as a research artifact?'),
    'domain': choice('Which domain?',
                      {"ai_infra": "AI infrastructure",
                       "ai_research": "AI research",
                       "doctrine": "doctrinal / philosophy",
                       "engineering": "engineering"}),
    'people_who_care': choice('Who cares about this most?',
                                {"engineers": "software engineers",
                                 "ai_researchers": "AI researchers",
                                 "founders": "founders / VCs",
                                 "doctrine_seekers": "doctrine-seekers"}),
})
print(json.dumps(r, indent=2))

"""Round 27: JEV self-evaluation."""
import sys, json
sys.path.insert(0, '/workspace/research')
from jev_client import ask, noul, score, choice

text = open('/workspace/research/JEV_DISCOVERY_LOG.md').read()
print(f'Length: {len(text)} chars')

r = ask(text[:4000], {
    'meta_useful': noul('Is this discovery log useful as a record?'),
    'methodology': score('Rate the methodology', ['ad-hoc', 'systematic', 'rigorous', 'frontier']),
    'reproducibility': noul('Could another agent reproduce these findings?'),
    'gate_useful': noul('Is the fleet canon gate useful operationally?'),
    'integration_value': choice('How should this integrate with the existing fleet?',
                                 {"canonical": "as canon doctrine",
                                  "tool": "as a tool",
                                  "experimental": "as experimental"}),
})
print(json.dumps(r, indent=2))

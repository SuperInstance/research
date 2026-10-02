import sys, json
sys.path.insert(0, '/workspace/research')
from jev_client import ask, noul, score, choice

print('=== Round 20: JEV evaluates quantumaudio outputs ===\n')

qpam_text = '''QPAM (Quantum Probability Amplitude Modulation) is the most
compact quantumaudio scheme. For 10ms audio: 9 qubits, depth-2 circuit.
Round-trip with 20000 shots: Pearson correlation 0.99, MSE 0.01.

It encodes each audio sample's value as a quantum probability amplitude
over time bins. The circuit is depth-2 because each sample maps to a
single rotation.'''

r = ask(qpam_text, {
    'is_doctrine': noul('Is this a Quilt doctrine?'),
    'novelty': score('Rate novelty', ['common', 'uncommon', 'novel', 'frontier']),
    'practical': noul('Is this practical / buildable today?'),
    'audience': choice('Who would care?',
                        {"physicists": "physicists",
                         "ai_researchers": "AI researchers",
                         "musicians": "musicians",
                         "everyone": "everyone who works with audio"}),
})
print(json.dumps(r['answers'], indent=2))

qult_text = open('/workspace/repos/quilt-cell-harness/QULT.md').read()
r = ask(qult_text[:4000], {
    'is_quilt_canon': noul('Is this canon-worthy?'),
    'domain': choice('What domain?',
                      {"biology": "biological",
                       "cs": "computer science",
                       "philosophy": "philosophy",
                       "engineering": "engineering practice"}),
    'fractal_signal': noul('Does this describe a fractal architecture?'),
    'novel_idea': noul('Is this novel / not in standard CS textbooks?'),
})
print('\n=== QULT.md ===')
print(json.dumps(r['answers'], indent=2))

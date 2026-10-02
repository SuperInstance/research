#!/usr/bin/env python3
"""Fleet Canary Audit — verify fnv1a-64("café Δ 日本語") == 0x024a555471370b18d across all ships."""
import os
import re
import json
import sys

CANARY = 'café Δ 日本語'
EXPECTED = 0x024a555471370b18d

def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

# Compute
actual = fnv1a_64(CANARY)
print(f'FNV-1a 64-bit hash of "{CANARY}":')
print(f'  Expected: 0x{EXPECTED:016x}')
print(f'  Actual:   0x{actual:016x}')
print(f'  Match:    {actual == EXPECTED}')
print()

# Audit ships
# Auto-discover all substrate-* packages + canonical ships
import glob
ships = []
for pkg_path in sorted(glob.glob('/workspace/repos/substrate-*')):
    name = os.path.basename(pkg_path)
    if 'substrate-llm-client' in name:
        ships.append((f'TS: {name}', pkg_path))
    elif 'substrate-rng' in name or 'substrate-vectors' in name or 'substrate-embedding' in name:
        ships.append((f'TS: {name}', pkg_path))
    elif 'tests' in name:
        continue
    else:
        ships.append((f'TS: {name}', pkg_path))
ships.append(('TS: jev-receipts', '/workspace/repos/jev-receipts'))
ships.append(('Python: jev-quilt', '/workspace/repos/jev-quilt'))
ships.append(('Rust: jev-quilt (ports/rust)', '/workspace/repos/jev-quilt/ports/rust'))

results = []
for name, path in ships:
    found = False
    pinned_value = None
    if os.path.exists(path):
        # Grep all source files for the canary value
        for root, dirs, files in os.walk(path):
            if 'node_modules' in root or '.git' in root or 'target' in root or '__pycache__' in root:
                continue
            for f in files:
                if not f.endswith(('.ts', '.js', '.py', '.rs', '.json', '.md', '.toml')):
                    continue
                fp = os.path.join(root, f)
                try:
                    content = open(fp).read()
                    # Look for 0x024a555471370b18d pattern
                    m = re.search(r'0x024a555471370b18[dD]', content)
                    if m:
                        found = True
                        # Try to extract surrounding context
                        ctx = content[max(0, m.start()-50):min(len(content), m.end()+50)]
                        pinned_value = ctx[:120]
                        break
                except:
                    continue
            if found:
                break
    results.append({'ship': name, 'path': path, 'canary_pinned': found, 'context': pinned_value})
    
print('=== Fleet Canary Audit ===\n')
ok = sum(1 for r in results if r['canary_pinned'])
print(f'Pinned: {ok}/{len(results)}\n')
for r in results:
    marker = '✓' if r['canary_pinned'] else '✗'
    print(f'  {marker} {r["ship"]}')
    if r['context']:
        ctx = r['context'].replace('\n', ' ').strip()
        print(f'      ...{ctx[:100]}...')

# Save report
out = {
    'audit': 'fleet_canary',
    'iso': os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip(),
    'canary_string': CANARY,
    'expected': f'0x{EXPECTED:016x}',
    'actual': f'0x{actual:016x}',
    'verified': actual == EXPECTED,
    'ships': results,
    'pinned_count': ok,
    'total_ships': len(results),
}
with open('/workspace/research/fleet_canary_audit.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/research/fleet_canary_audit.json')

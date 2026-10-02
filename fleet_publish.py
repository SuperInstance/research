#!/usr/bin/env python3
"""Fleet Publish Pipeline - drain the queue per issue #16.

Steps:
1. DISCOVER: find publish-ready packages
2. PIN FLEET CANARY: 0x024a555471370b18d (fnv1a-64 "café Δ 日本語")
3. VERIFY: run each package's tests
4. PUBLISH: version-claim, dry-run, real publish
5. REPORT: package@version, registry URL, test counts, refused

Credentials from env (no echo): CRATES_TOKEN, NPMJS_TOKEN, PYPI_TOKEN
"""
import os, sys, json, time, subprocess, hashlib, glob

CANARY_INPUT = "café Δ 日本語"
EXPECTED_CANARY = 0x024a555471370b18d

def fnv1a_64(s):
    h = 0xcbf29ce484222325
    for c in s.encode('utf-8'):
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

def verify_canary():
    """Verify the fleet crack-detector canary. Returns (passed, got)."""
    got = fnv1a_64(CANARY_INPUT)
    return got == EXPECTED_CANARY, got

def find_packages():
    """Find publish-ready packages in /workspace/repos/."""
    pkgs = {'npm': [], 'pypi': [], 'cargo': []}

    # Special-case: jev-quilt/ports/rust (cargo on main branch)
    jevq_main_cargo = '/workspace/repos/jev-quilt/ports/rust/Cargo.toml'
    if os.path.exists(jevq_main_cargo):
        with open(jevq_main_cargo) as f:
            content = f.read()
        if 'name = "jev-quilt"' in content and 'license' in content.lower():
            pkgs['cargo'].append({
                'name': 'jev-quilt',
                'path': '/workspace/repos/jev-quilt/ports/rust',
                'note': 'ports/rust from main branch',
                'test_cmd': 'cargo test',
            })

    for repo in glob.glob('/workspace/repos/*/'):
        # npm
        pkg_json = os.path.join(repo, 'package.json')
        if os.path.exists(pkg_json):
            with open(pkg_json) as f:
                try:
                    data = json.load(f)
                except:
                    continue
            name = data.get('name', '')
            version = data.get('version', '')
            private = data.get('private', False)
            license = data.get('license', '')
            has_test = 'test' in data.get('scripts', {})
            if name and version and not private and license:
                pkgs['npm'].append({
                    'name': name,
                    'version': version,
                    'path': repo,
                    'license': license,
                    'has_test': has_test,
                    'test_cmd': data.get('scripts', {}).get('test', 'echo no-test'),
                })

        # pypi
        pyproject = os.path.join(repo, 'pyproject.toml')
        if os.path.exists(pyproject):
            with open(pyproject) as f:
                content = f.read()
            import re
            name_m = re.search(r'^name\s*=\s*["\']([^"\']+)', content, re.M)
            ver_m = re.search(r'^version\s*=\s*["\']([^"\']+)', content, re.M)
            lic_m = re.search(r'license\s*=\s*[{"]\s*text["]?\s*:\s*["]([^"]+)', content) or \
                    re.search(r'^license\s*=\s*["\']([^"\']+)', content, re.M)
            if name_m and ver_m:
                pkgs['pypi'].append({
                    'name': name_m.group(1),
                    'version': ver_m.group(1),
                    'path': repo,
                    'license': lic_m.group(1) if lic_m else '',
                    'test_cmd': f'cd {repo} && python3 -m pytest tests/ -x 2>&1 | tail -3',
                })

        # cargo (already handled jev-quilt above)
        cargo = os.path.join(repo, 'Cargo.toml')
        if os.path.exists(cargo) and repo != '/workspace/repos/jev-quilt/':  # skip jev-quilt (handled separately)
            with open(cargo) as f:
                content = f.read()
            import re
            name_m = re.search(r'^name\s*=\s*["\']([^"\']+)', content, re.M)
            ver_m = re.search(r'^version\s*=\s*["\']([^"\']+)', content, re.M)
            desc_m = re.search(r'^description\s*=\s*["\']([^"\']+)', content, re.M)
            lic_m = re.search(r'^license\s*=\s*["\']([^"\']+)', content, re.M)
            if name_m and ver_m:
                pkgs['cargo'].append({
                    'name': name_m.group(1),
                    'version': ver_m.group(1),
                    'path': repo,
                    'description': desc_m.group(1) if desc_m else '',
                    'license': lic_m.group(1) if lic_m else '',
                    'test_cmd': f'cd {repo} && cargo test',
                })

    return pkgs

def main():
    print('=== FLEET PUBLISH PIPELINE (Issue #16) ===\n')

    # Step 0: Verify canary
    print('--- Step 0: Verify FLEET CANARY ---')
    ok, got = verify_canary()
    print(f'  FNV-1a-64({CANARY_INPUT!r}) = 0x{got:016x}')
    print(f'  Expected:                   0x{EXPECTED_CANARY:016x}')
    print(f'  CANARY: {"VERIFIED ✓" if ok else "FAILED ✗"}')
    if not ok:
        print('\nCANARY FAILED - ABORTING. The fleet crack-detector is broken.')
        sys.exit(1)
    print()

    # Step 1: Discover
    print('--- Step 1: DISCOVER packages ---')
    pkgs = find_packages()
    for kind, items in pkgs.items():
        print(f'\n{kind.upper()}: {len(items)} packages')
        for p in items:
            extra = ''
            if kind == 'npm':
                extra = f'  has_test={p["has_test"]}'
            elif kind == 'cargo':
                extra = f'  desc={p.get("description", "")[:50]}'
            print(f'  {p["name"]} @ {p["version"]}  ({p["license"]}){extra}')

    # Save discovery for next steps
    with open('/workspace/research/fleet_publish_discovery.json', 'w') as f:
        json.dump({
            'canary_verified': ok,
            'canary_input': CANARY_INPUT,
            'canary_hash': f'0x{got:016x}',
            'packages': pkgs,
            'timestamp': time.time(),
            'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }, f, indent=2)
    print(f'\nSaved discovery: /workspace/research/fleet_publish_discovery.json')

if __name__ == '__main__':
    main()

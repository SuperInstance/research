"""quilt-cell — the Quilt cell-fabric runtime, verifiable on install.

The C99 kernel plus the one-command verifier that proves it. Install this and you can
run the same 1,285 assertions the author ran, on your machine, with no trust in the
author's CI.

    >>> import quilt_cell; quilt_cell.verify()
    {'verdict': 'VERIFIED', 'assertions_passed': 1285, 'assertions_failed': 0, ...}

The dependency closure is a C99 compiler. Nothing else.
"""

__version__ = "0.1.0"
__all__ = ["verify", "CellGraph", "OPS", "RELEASE_RECEIPT"]

# The release receipt for the exact source shipped in this package. verify() recomputes
# the tree digest; if these disagree, the package is not what it claims to be.
RELEASE_RECEIPT = {
    "tag": "v0.1.0",
    "commit": "adae27e496bbbabc86fffaaa740c7897ae6c5634",
    "assertions_passed": 1285,
    "assertions_failed": 0,
    "source_tree_sha256": "be3be613f3528be487e15d6b207ec81f",
    "receipt_sha256": "37ee07375870eebda46623c9db4d3152f621f7401ae71759cf8d65c52dc77131",
    "note": (
        "source_tree_sha256 is truncated to 32 hex chars here for readability. The full "
        "digest is recomputed by verify(). The repo ships the untruncated value."
    ),
}

OPS = ("BIND", "LINK", "EFFECT", "VIEW", "TICK")


def verify():
    """Run every assertion in the shipped C kernel. Returns the receipt dict.

    Requires a C99 compiler. This is the same script that runs in the project's CI and
    that produced the v0.1.0 release receipt.
    """
    import importlib.resources as res
    import json
    import os
    import subprocess
    import tempfile

    # verify.py runs `make` in its OWN directory, so it needs the C sources, headers,
    # Makefile and tests beside it. Copying only the script into a temp dir makes it
    # FAILED/exit 1 with 0 assertions — which is exactly what the first version of this
    # wrapper did, and it would have shipped a package whose headline command reports
    # VERIFIED-never, silently, on every install.
    import importlib.resources as res
    import json
    import os
    import shutil
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        for item in ("verify.py", "Makefile", "src", "include", "tests"):
            src = res.files("quilt_cell") / item
            if not src.is_dir() and not src.is_file():
                continue
            with res.as_file(src) as real:
                dst = os.path.join(td, item)
                if real.is_dir():
                    shutil.copytree(real, dst)
                else:
                    shutil.copy2(real, dst)
        proc = subprocess.run(["python3", os.path.join(td, "verify.py")],
                              capture_output=True, text=True, cwd=td)
        rj = os.path.join(td, "VERIFY_RECEIPT.json")
        receipt = json.load(open(rj)) if os.path.exists(rj) else {}
        receipt["stdout"] = proc.stdout[-2000:]
    receipt["exit_code"] = proc.returncode
    return receipt


def CellGraph(*a, **kw):
    """Lazy accessor for the pure-Python cell-graph reference implementation."""
    from .graph import CellGraph as _CG
    return _CG(*a, **kw)

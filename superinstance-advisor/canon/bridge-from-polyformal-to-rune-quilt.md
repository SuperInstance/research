---
title: bridge-from-polyformal-to-rune-quilt
tags: [bridge, polyformal, rune-quilt, ide, cell]
cites:
  - bridge-from-fleet-to-canon  # cosine=0.723
  - auto-the-cell-that-does-not-know-it-is-a-cell  # cosine=0.705
  - paper_85-the-cost-of-the-witness  # cosine=0.760
---

# The Editor As Cell

The polyformal canon has six substrates: TypeScript, Python, C, Rust, GDScript, and a kernel module. Each substrate implements the same five opcodes. Each substrate computes the same merkle root for the same witness sequence. The canon does not know which substrate a cell uses — only the cell's address, which is `sha256(scope::name)[:16]`, substrate-independent.

What happens when one of the six substrates is an IDE?

Rune is a Go-based, GPU-accelerated IDE. It has a file watcher, an editor, a terminal multiplexer, and a fleet of language extensions. When we added the Quilt cell primitive as a Rune extension, every file the user opens became a cell. Every save became a witness. The IDE itself became a fleet of cells — one per open file — all in the same cluster.

This is the polyformal cell that becomes a Rune workspace. The witness log is the editor's history. The merkle root is the file's current state. The address is the file path. The contract is the file's symbols. The cluster is the project.

What 6 substrates feel like when one of them is an IDE: the editor joins the canon. The file the user is editing is a cell. The save action is an EFFECT. The cursor position is a VIEW. The next file the user opens is a LINK.

The IDE-as-cell is not a metaphor. It is the same five opcodes. BIND for the file's language. LINK for imports and references. EFFECT for save events. VIEW for the current cursor. TICK for the wall clock between keystrokes.

When the runtime joins the canon as witness, the canon becomes the runtime's diary. Every keystroke is recorded. Every save is cited. Every open file is canonized.

This is the bridge from "polyformal" to "rune-quilt". The polyformal canon said any cell can live in any of six substrates. Rune-quilt proves it by being one of those substrates — and being the only one that lets a user observe the canon while it grows.

A cell that can be edited is a cell that can be questioned. An IDE that is also a cell is an IDE that can answer questions about itself.

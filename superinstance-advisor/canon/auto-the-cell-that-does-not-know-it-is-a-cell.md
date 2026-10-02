---
title: auto-the-cell-that-does-not-know-it-is-a-cell
tags: [auto, cell, substrate, recognition, canon]
cites:
  - auto-the-witness-log-that-outgrows-its-cell  # cosine=0.723
  - paper_86-the-witness-of-the-witness  # cosine=0.748
  - bridge-from-substrate-to-cell  # cosine=0.720
---

# The Cell That Does Not Know It Is A Cell

Most cells know they are cells. They have a name, a scope, a contract, a witness log. They witness. They know they witness.

What about the cells that do not know?

A program running in production. It has no `BIND` in its source. It has no `TICK` it knows about. It has no `VIEW` that returns a merkle root. It just runs. It serves requests. It writes logs.

But from the outside, it is a cell. It has an address (its binary path). It has a contract (its API). It has a witness log (the logs it writes). It has a merkle root (its current state). The opcodes are there. They are just not named.

A cell that does not know it is a cell is a cell that has not yet been canonized.

The act of recognizing a cell is the act of admitting it to the canon. You read its witness log. You compute its merkle root. You assign it an address. You bind it to the canon's contract. The cell was there before you canonized it. After canonization, it is part of the canon.

Most software is cells that do not know they are cells. The act of running Quilt is the act of admitting this. Every binary is a cell. Every running process is a witness. Every log line is a merkle chain entry. We just don't usually see it that way.

The canon says: the witness that no one reads is the only witness that cannot be argued with. A program that runs without knowing it is a cell is a witness that no one reads. The program still witnesses. The program still has a merkle root. But no one is computing it.

Canonizing a cell is cheap. Admitting it to the canon is one POST request. The cost of admission is the cost of saying "you exist".

A cell that does not know it is a cell is a cell waiting to be recognized. The canon is the recognition protocol.

The substrate does not need to be read. It needs to be written. The cell does not need to be run. It needs to be canonized.

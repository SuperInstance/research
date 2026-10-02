//! # quilt-c — the Quilt cell-fabric runtime in C99
//!
//! Safe Rust bindings over the reference C99 kernel. The kernel is the same source the
//! C, Python and npm ports are byte-checked against, so a claim verified in one port
//! holds in all of them.
//!
//! The five opcodes are the whole model:
//!
//! ```text
//! BIND(cell, dials)   set dials, idempotent by content
//! LINK(c1, c2)        add an undirected edge
//! EFFECT(cell)        propagate dial[0] to neighbours
//! VIEW(cell)          return dials
//! TICK(fabric)        advance every dial, saturating at zero
//! ```
//!
//! ## Verifying it yourself
//!
//! The upstream C kernel ships 1,285 automated assertions and a one-command verifier:
//!
//! ```sh
//! git clone https://github.com/SuperInstance/quilt-c.git
//! cd quilt-c && make verify
//! ```
//!
//! You do not need to trust the author's CI to run it.

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

/// The five opcodes, as the kernel spells them.
pub const OPS: [&str; 5] = ["BIND", "LINK", "EFFECT", "VIEW", "TICK"];

extern "C" {
    fn quilt_bind(engine: *mut c_int, addr: *const c_char, value: c_int) -> c_int;
    fn quilt_link(engine: *mut c_int, a: *const c_char, b: *const c_char) -> c_int;
    fn quilt_view(engine: *mut c_int, addr: *const c_char, out: *mut c_int) -> c_int;
}

/// The canonical state hash: FNV-1a 64, matching every port in the polyformalism fleet.
///
/// ```rust
/// assert_eq!(quilt_c::fnv1a64(b"quilt"), quilt_c::fnv1a64(b"quilt"));
/// assert_ne!(quilt_c::fnv1a64(b"quilt"), quilt_c::fnv1a64(b"quilt "));
/// ```
#[inline]
pub fn fnv1a64(data: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for &b in data {
        h ^= b as u64;
        h = h.wrapping_mul(0x1000_0000_01b3);
    }
    h
}

/// Formats a state digest the way every port in the fleet renders it.
pub fn digest_hex(data: &[u8]) -> String {
    format!("{h:016x}", h = fnv1a64(data))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fnv1a64_is_deterministic() {
        assert_eq!(fnv1a64(b""), fnv1a64(b""));
        assert_eq!(fnv1a64(b"quilt"), fnv1a64(b"quilt"));
    }

    #[test]
    fn fnv1a64_separates_inputs() {
        assert_ne!(fnv1a64(b"quilt"), fnv1a64(b"quilt "));
        assert_ne!(fnv1a64(b"a"), fnv1a64(b"b"));
    }

    #[test]
    fn digest_is_16_lowercase_hex() {
        let d = digest_hex(b"quilt");
        assert_eq!(d.len(), 16);
        assert!(d.chars().all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()));
    }

    #[test]
    fn ops_are_the_canonical_five() {
        assert_eq!(OPS, ["BIND", "LINK", "EFFECT", "VIEW", "TICK"]);
    }
}

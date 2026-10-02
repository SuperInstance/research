//! substrate-delegate: DELEGATE opcode
//! Grants a capability to another node. Capabilities are attenuatable
//! (sub-capabilities can be derived) and revocable.

use observation_primitive::fnv1a64_hex;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DelegationReceipt {
    #[serde(rename = "type")]
    pub kind: String,
    pub id: String,
    pub from: String,
    pub to: String,
    pub capabilities: Vec<String>,
    pub time: u64,
    #[serde(rename = "is_revocable")]
    pub is_revocable: bool,
    #[serde(rename = "is_attenuatable")]
    pub is_attenuatable: bool,
}

pub fn delegate(delegator: &str, target: &str, capabilities: Vec<String>) -> DelegationReceipt {
    assert!(!capabilities.is_empty(), "delegate requires non-empty capabilities");
    let time = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let mut sorted_caps = capabilities.clone();
    sorted_caps.sort();
    let payload = serde_json::json!({
        "from": delegator,
        "to": target,
        "caps": sorted_caps,
        "t": time,
    });
    DelegationReceipt {
        kind: "delegation".into(),
        id: fnv1a64_hex(&payload.to_string()),
        from: delegator.into(),
        to: target.into(),
        capabilities,
        time,
        is_revocable: true,
        is_attenuatable: true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn delegate_basic() {
        let r = delegate("alice", "bob", vec!["read".into(), "write".into()]);
        assert_eq!(r.from, "alice");
        assert!(r.is_attenuatable);
    }
}

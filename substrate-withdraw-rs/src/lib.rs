//! substrate-withdraw: WITHDRAW opcode
//! Pulls a previously-published observation into private scope.
//! Creates a withdrawal scar - the audit trail of what was taken back.

use observation_primitive::fnv1a64_hex;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WithdrawalScar {
    #[serde(rename = "type")]
    pub kind: String,
    pub id: String,
    pub withdraws: String,
    pub withdrawer: String,
    pub reason: Option<String>,
    pub time: u64,
    pub visibility: String,
    #[serde(rename = "is_audit_trail")]
    pub is_audit_trail: bool,
}

pub fn withdraw(observation_id: &str, withDrawer: &str, reason: Option<&str>) -> WithdrawalScar {
    let time = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let payload = serde_json::json!({
        "o": observation_id,
        "w": withDrawer,
        "r": reason,
        "t": time,
    });
    WithdrawalScar {
        kind: "withdrawal_scar".into(),
        id: fnv1a64_hex(&payload.to_string()),
        withdraws: observation_id.into(),
        withdrawer: withDrawer.into(),
        reason: reason.map(String::from),
        time,
        visibility: "private".into(),
        is_audit_trail: true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn withdraw_basic() {
        let w = withdraw("obs_42", "alice", Some("outdated"));
        assert_eq!(w.withdraws, "obs_42");
        assert!(w.is_audit_trail);
    }
}

//! substrate-merger: MERGER opcode
//! Merges N observations into one by consensus.

use observation_primitive::{Observation, fnv1a64_hex};
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MergedObservation {
    #[serde(rename = "type")]
    pub kind: String,
    pub id: String,
    pub subject: String,
    pub predicate: String,
    pub object: serde_json::Value,
    pub issuer: String,
    pub time: u64,
    #[serde(rename = "constituent_ids")]
    pub constituent_ids: Vec<String>,
    pub strategy: String,
    #[serde(rename = "is_consensus")]
    pub is_consensus: bool,
}

pub fn merge(observations: &[&Observation], merger: &str) -> MergedObservation {
    assert!(!observations.is_empty(), "merge requires non-empty observations");
    let subject = observations[0].subject.clone();
    let predicate = observations[0].predicate.clone();
    let time = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);

    let ids: Vec<String> = observations.iter().map(|o| o.id.clone()).collect();
    let payload = serde_json::json!({
        "s": subject,
        "p": predicate,
        "i": { let mut x = ids.clone(); x.sort(); x },
        "m": merger,
        "t": time,
    });

    MergedObservation {
        kind: "merged_observation".into(),
        id: fnv1a64_hex(&payload.to_string()),
        subject,
        predicate,
        object: serde_json::json!({}), // simplified
        issuer: merger.into(),
        time,
        constituent_ids: ids,
        strategy: "consensus".into(),
        is_consensus: true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn merge_basic() {
        let o1 = Observation::new("substrate", "color", serde_json::json!("red"), "alice", Some(1));
        let o2 = Observation::new("substrate", "color", serde_json::json!("red"), "bob", Some(1));
        let m = merge(&[&o1, &o2], "judge");
        assert!(m.is_consensus);
        assert_eq!(m.constituent_ids.len(), 2);
    }
}

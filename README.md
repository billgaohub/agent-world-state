# agent-world-state

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-EXPERIMENTAL-orange.svg)](SPECIFICATION.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> `agent-world-state` is an empirically derived specification for representing evidence-grounded observations, claims, temporal context, verification, and revision in changing external environments. It does not own upstream facts.

---

## 1. Overview

Autonomous agents operating in complex environments require an objective, auditable representation of external world state. In practice, agent auditing frequently suffers from:
- **Conflated Trust**: Mixing source authority, observer verification depth, and propositional claim validity into scalar "confidence scores".
- **Temporal Confusion**: Blurring external event timestamps, UI dashboard clocks, and local agent execution times.
- **Metadata Promotion**: Mistaking verified API/video metadata (e.g. duration, status code) for physical content inspection.
- **Uncontrolled Drift**: Rewriting historical logs when upstream data changes rather than appending structured revisions.

`agent-world-state` provides a lightweight, fail-closed specification and reference validator derived from empirical multi-agent field studies (GrokBot multimodal livestream demos and Xiaomi MiMo-V2.6 distributed reinforcement learning infrastructure).

---

## 2. Core Epistemic Foundations

### The Three Orthogonal Axes

Rather than reducing truth to a single score, observations are classified across three independent dimensions:

1. **Source Authority**: The epistemic standing of the data provider (`PRIMARY`, `MIRROR`, `SECONDARY`, `LOCAL_BASELINE`).
2. **Review Depth**: The physical rigor executed by the observer (`identity_pinned`, `metadata_verified`, `content_reviewed`, composable `evidence_modalities`).
3. **Temporal Integrity**: Decoupling `absolute_event_time`, `relative_source_offset`, `collector_time`, and `published_or_observed_clock`, with explicit clock skew calibration.

```
       Source Authority (Origin Standing)
             ▲
             │
             │   ▲ Review Depth (Observer Rigor)
             │  /
             │ /
             └──────────────► Temporal Integrity (Decoupled Timeline)
```

### Raw Evidence Immutability vs. Epistemic Decay

`agent-world-state` enforces a strict distinction between immutable historical records and dynamic propositional claims:

```text
Raw evidence record
= immutable / historically fixed

Claim validity / freshness / context / coverage
= may decay or become stale

Source revision
→ STALE_SOURCE_DRIFT
→ re-verification
→ Correction
```

- **Raw Evidence Records**: Grounded observations (`Observation`) committed with cryptographic locators are historically fixed. Historical events do not change retroactively.
- **Propositional Claims & Freshness**: Propositions (`Claim`) are subject to fact decay, context drift, coverage expiration, and consensus shifts.
- **Source Drift & Correction**: When upstream realities change, downstream observers detect `STALE_SOURCE_DRIFT`, re-evaluate affected claims, and append an immutable `Correction` record.

### Single Source of Truth (SSOT) Contract

> **`agent-world-state never owns field-study facts.`**

Upstream field studies, repositories, and sensory pipelines retain primary factual authority. `agent-world-state` acts as a derived model authority for representation, validation, and audit.

---

## 3. Repository Structure

```text
agent-world-state/
├── README.md                 # Project overview and core axioms
├── SPECIFICATION.md          # Full normative specification
├── LICENSE                   # MIT License
├── CHANGELOG.md              # Version history
├── evidence-map.md           # SSOT boundary and evidence locator mapping
├── schemas/                  # JSON Schemas (Draft 2020-12)
│   ├── source.schema.json
│   ├── observation.schema.json
│   ├── claim.schema.json
│   ├── temporal-context.schema.json
│   └── correction.schema.json
├── validator/                # Reference Python validator
│   └── validator.py
├── fixtures/                 # Desensitized valid and invalid test fixtures
│   ├── valid_grokbot_obs.yaml
│   ├── valid_mimo_obs.yaml
│   ├── invalid_scalar_tier_conflation.yaml
│   ├── invalid_uncalibrated_clock_skew.yaml
│   ├── invalid_metadata_promoted.yaml
│   └── invalid_unpinned_secondary_promoted.yaml
├── tests/                    # Deterministic exit-code test suite
│   └── test_validator.py
└── models/                   # Architecture and relational models
    └── README.md
```

---

## 4. Quick Start & Validation

### Requirements
- Python 3.9+
- `pyyaml`

```bash
pip install pyyaml
```

### Running the Reference Validator

Validate a single observation fixture:
```bash
python3 validator/validator.py fixtures/valid_grokbot_obs.yaml
```

Validate all fixtures in batch:
```bash
python3 validator/validator.py fixtures/*.yaml
```

### Running the Test Suite

The test suite runs individual subprocess checks against each fixture and verifies authentic exit codes (exit 0 for valid fixtures, exit 1 for fail-closed invalid fixtures):

```bash
python3 tests/test_validator.py
```

Expected output:
```text
test_batch_execution_all_valid (__main__.TestValidator) ... ok
test_batch_execution_mixed (__main__.TestValidator) ... ok
test_invalid_metadata_promoted (__main__.TestValidator) ... ok
test_invalid_scalar_tier_conflation (__main__.TestValidator) ... ok
test_invalid_uncalibrated_clock_skew (__main__.TestValidator) ... ok
test_invalid_unpinned_secondary_promoted (__main__.TestValidator) ... ok
test_valid_grokbot_fixture (__main__.TestValidator) ... ok
test_valid_mimo_fixture (__main__.TestValidator) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.37s

OK
```

---

## 5. Specification Lineage & Status

- **Current Version**: `0.1.0`
- **Status**: `EXPERIMENTAL / EMPIRICALLY_DERIVED`
- **Lineage**: Derived from 2 heterogeneous field studies; not asserted as a universal standard.

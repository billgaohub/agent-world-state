# Changelog

All notable changes to `agent-world-state` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-20

### Added
- **Initial Experimental Specification**: Formal specification for agent world-state telemetry, observation lifecycles, and epistemic evidence models.
- **Three Orthogonal Axes**: Decoupled `Source Authority`, `Review Depth`, and `Temporal Integrity` into independent verification dimensions.
- **Deconstructed Observation & Claim Models**:
  - `observation_kind` (7 event types) separated from `claim_status` (4 proposition states) and `support_level` (4 evidence grades).
  - Replaced scalar enums with composable `evidence_modalities`.
- **Temporal Context Decoupling**: Decoupled `absolute_event_time`, `relative_source_offset`, `collector_time`, and `published_or_observed_clock`, with explicit clock skew calibration checks.
- **Epistemic Decay vs. Evidence Immutability**: Explicitly defined that raw historical evidence is immutable, while claims, contextual scope, and ranking decay over time.
- **Executable Validator (`validator/validator.py`)**: Standalone CLI and programmatic validator enforcing fail-closed checks against historical audit pitfalls.
- **Test Suite (`tests/test_validator.py`)**: Subprocess unit tests verifying authentic exit codes for 2 valid and 4 invalid test fixtures.
- **JSON Schemas (`schemas/`)**: Draft 2020-12 schemas for `source`, `observation`, `claim`, `temporal-context`, and `correction`.
- **SSOT Contract & Evidence Map (`evidence-map.md`)**: Demarcated boundary establishing that `agent-world-state never owns field-study facts`.

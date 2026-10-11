# Changelog

All notable changes to `agent-world-state` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-10-11

### Added
- **Optional Writer Identity & Signature** (`writer_id`, `signature` on Observation): closes the
  round-1 dogfood gap — observations previously had no writer/signer identity field, which is
  the core of Agent OS Rev A three-way arbitration (authorized writer + valid predecessor +
  valid signature). Both fields optional; `signature` requires `writer_id` (`dependentRequired`
  in JSON schema + validator rule 7, fail-closed).
- **Ed25519 Signature Scheme**: canonical serialization = observation minus `signature`,
  sorted-keys compact JSON, UTF-8. Documented in SPECIFICATION.md §3.4.
- **Optional Signature Verification**: `validator.py --verify-sig <PUBKEY_HEX>` verifies present
  signatures, fail-closed on mismatch (`ERR_SIGNATURE_INVALID`). Soft dependency on `pynacl`;
  core fail-closed rules unchanged and require nothing new.
- **Round-2 Dogfood Fixture** (`fixtures/valid_signed_obs.yaml`): real transition —
  aiobn-site PR #73 merged 2026-10-11T04:34:29Z (verified via `gh pr view`), signed with an
  explicitly-labeled PILOT experimental key (private key never committed).
- **Negative Fixtures**: `invalid_sig_tampered.yaml` (flipped hex digit → `ERR_SIGNATURE_INVALID`),
  `invalid_sig_no_writer.yaml` (signature without writer → `ERR_SIGNATURE_WITHOUT_WRITER`).

### Backward Compatibility
- v0.1.0 observations (without `writer_id`/`signature`) still PASS, with and without `--verify-sig`.
- No existing validator rule was modified; rules 7–8 are purely additive and fail-closed.

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

#!/usr/bin/env python3
"""
Unit tests for agent-world-state Schema Validator (v0.1.0).
Directly tests each fixture individually and captures authentic process exit codes.
"""

import sys
import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PY = REPO_ROOT / "validator" / "validator.py"
FIXTURES_DIR = REPO_ROOT / "fixtures"

# PILOT experimental ed25519 public key (test-only, 2026-10-11 dogfood round 2).
# The private key was generated ephemerally, labeled PILOT-EXPERIMENTAL-ONLY,
# kept in /tmp, and never committed to the repo. This public key is not a secret.
PILOT_PUBKEY_HEX = "134fd3d3f5d8e349cfc0cc2524011b05b9d23d51c37af07ca25ec25b7e93e53e"

class TestValidator(unittest.TestCase):

    def run_validator(self, *fixture_names) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(VALIDATOR_PY)]
        for name in fixture_names:
            cmd.append(str(FIXTURES_DIR / name))
        return subprocess.run(cmd, capture_output=True, text=True)

    def run_validator_with_sig(self, pubkey_hex, *fixture_names) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(VALIDATOR_PY), "--verify-sig", pubkey_hex]
        for name in fixture_names:
            cmd.append(str(FIXTURES_DIR / name))
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_valid_grokbot_fixture(self):
        """Test valid GrokBot observation fixture passes with exit code 0."""
        res = self.run_validator("valid_grokbot_obs.yaml")
        self.assertEqual(res.returncode, 0, f"Expected returncode 0, got {res.returncode}. Output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("PASS", res.stdout)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

    def test_valid_mimo_fixture(self):
        """Test valid MiMo observation fixture passes with exit code 0."""
        res = self.run_validator("valid_mimo_obs.yaml")
        self.assertEqual(res.returncode, 0, f"Expected returncode 0, got {res.returncode}. Output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("PASS", res.stdout)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

    def test_invalid_scalar_tier_conflation(self):
        """Test legacy conflated keys trigger fail-closed with exit code 1."""
        res = self.run_validator("invalid_scalar_tier_conflation.yaml")
        self.assertEqual(res.returncode, 1, f"Expected returncode 1, got {res.returncode}. Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_CONFLATED_LEGACY_KEYS", res.stdout)

    def test_invalid_uncalibrated_clock_skew(self):
        """Test large uncalibrated clock skew (>60s) triggers fail-closed with exit code 1."""
        res = self.run_validator("invalid_uncalibrated_clock_skew.yaml")
        self.assertEqual(res.returncode, 1, f"Expected returncode 1, got {res.returncode}. Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_UNCALIBRATED_CLOCK_SKEW", res.stdout)

    def test_invalid_metadata_promoted(self):
        """Test content_reviewed=false claiming physical inspection triggers fail-closed with exit code 1."""
        res = self.run_validator("invalid_metadata_promoted.yaml")
        self.assertEqual(res.returncode, 1, f"Expected returncode 1, got {res.returncode}. Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_METADATA_PROMOTED_TO_CONTENT", res.stdout)
        self.assertIn("ERR_CONTENT_UNREVIEWED_PHYSICAL_CLAIM", res.stdout)

    def test_invalid_unpinned_secondary_promoted(self):
        """Test unpinned secondary source claiming physical verification triggers fail-closed with exit code 1."""
        res = self.run_validator("invalid_unpinned_secondary_promoted.yaml")
        self.assertEqual(res.returncode, 1, f"Expected returncode 1, got {res.returncode}. Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_UNPINNED_SECONDARY_PHYSICAL_CLAIM", res.stdout)

    def test_batch_execution_mixed(self):
        """Test batch run containing any invalid fixture exits with code 1."""
        res = self.run_validator("valid_grokbot_obs.yaml", "invalid_scalar_tier_conflation.yaml")
        self.assertEqual(res.returncode, 1)
        self.assertIn("PASS", res.stdout)
        self.assertIn("FAIL-CLOSED", res.stdout)

    def test_batch_execution_all_valid(self):
        """Test batch run with only valid fixtures exits with code 0."""
        res = self.run_validator("valid_grokbot_obs.yaml", "valid_mimo_obs.yaml")
        self.assertEqual(res.returncode, 0)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

    # ---- v0.2: writer_id + signature ----

    def test_signed_fixture_passes_without_flag(self):
        """Backward compat: signed fixture passes without --verify-sig (signature ignored)."""
        res = self.run_validator("valid_signed_obs.yaml")
        self.assertEqual(res.returncode, 0, f"Output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("PASS", res.stdout)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

    def test_signed_fixture_signature_verifies(self):
        """Round-2 dogfood: real PR #73 observation verifies against pilot pubkey."""
        res = self.run_validator_with_sig(PILOT_PUBKEY_HEX, "valid_signed_obs.yaml")
        self.assertEqual(res.returncode, 0, f"Output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("signature OK", res.stdout)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

    def test_tampered_signature_fail_closed(self):
        """Flipped hex digit must fail closed with ERR_SIGNATURE_INVALID."""
        res = self.run_validator_with_sig(PILOT_PUBKEY_HEX, "invalid_sig_tampered.yaml")
        self.assertEqual(res.returncode, 1, f"Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_SIGNATURE_INVALID", res.stdout)

    def test_signature_without_writer_fail_closed(self):
        """Signature without writer_id must fail closed (unattributable signature)."""
        res = self.run_validator("invalid_sig_no_writer.yaml")
        self.assertEqual(res.returncode, 1, f"Output:\n{res.stdout}")
        self.assertIn("FAIL-CLOSED", res.stdout)
        self.assertIn("ERR_SIGNATURE_WITHOUT_WRITER", res.stdout)

    def test_unsigned_fixture_ignores_verify_flag(self):
        """Legacy fixture with --verify-sig still passes (no signature = no check)."""
        res = self.run_validator_with_sig(PILOT_PUBKEY_HEX, "valid_grokbot_obs.yaml")
        self.assertEqual(res.returncode, 0, f"Output:\n{res.stdout}\n{res.stderr}")
        self.assertIn("PASS", res.stdout)
        self.assertNotIn("FAIL-CLOSED", res.stdout)

if __name__ == "__main__":
    unittest.main(verbosity=2)

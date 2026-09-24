"""Tests for GitHub Actions Google Flow runner entrypoint."""

import base64
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from mini_run_pipeline.flow_gha_runner import (
    DEFAULT_TRANSCRIPT,
    hydrate_browser_profile,
    resolve_auth_strategy,
    run_hostile_critique,
)


class TestFlowGhaRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_gha_runner_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hydrate_browser_profile_roundtrip(self):
        """Verifies that hydrate_browser_profile decrypts AES-GCM bundle and sets DPAPI key."""
        tmp_path = Path(self.test_dir)
        profile_src = tmp_path / "mock_profile"
        profile_src.mkdir()

        raw_key = os.urandom(32)
        (profile_src / "raw_master_key.bin").write_bytes(raw_key)

        initial_ls = {
            "os_crypt": {
                "encrypted_key": base64.b64encode(b"dummy_encrypted").decode("utf-8")
            }
        }
        (profile_src / "Local State").write_text(json.dumps(initial_ls), encoding="utf-8")
        (profile_src / "some_data.txt").write_text("flow session data", encoding="utf-8")

        # Tar it
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            for r, _, fs in os.walk(profile_src):
                for f in fs:
                    fp = os.path.join(r, f)
                    rel = os.path.relpath(fp, profile_src)
                    tar.add(fp, arcname=rel)
        tar_bytes = buf.getvalue()

        # Encrypt with AESGCM
        key_bytes = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key_bytes)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, tar_bytes, None)
        enc_path = tmp_path / "test_bundle.enc"
        enc_path.write_bytes(nonce + ciphertext)

        # Hydrate into target dir
        target_dir = tmp_path / "hydrated_profile"
        hydrate_browser_profile(enc_path, target_dir, key_bytes.hex())

        # Assert extraction and DPAPI processing
        self.assertTrue((target_dir / "some_data.txt").exists())
        self.assertEqual(
            (target_dir / "some_data.txt").read_text(encoding="utf-8"),
            "flow session data",
        )
        self.assertTrue((target_dir / "Local State").exists())

        with open(target_dir / "Local State", "r", encoding="utf-8") as f:
            ls_after = json.load(f)

        if sys.platform == "win32":
            import win32crypt
            enc_b64 = ls_after["os_crypt"]["encrypted_key"]
            enc_bytes = base64.b64decode(enc_b64)
            self.assertTrue(enc_bytes.startswith(b"DPAPI"))
            decrypted = win32crypt.CryptUnprotectData(enc_bytes[5:], None, None, None, 0)[1]
            self.assertEqual(decrypted, raw_key)

    def test_default_transcript_structure(self):
        """Ensures default transcript adheres to schema expectations."""
        self.assertGreaterEqual(len(DEFAULT_TRANSCRIPT), 2)
        for chunk in DEFAULT_TRANSCRIPT:
            self.assertIn("chunkIndex", chunk)
            self.assertIn("startMs", chunk)
            self.assertIn("endMs", chunk)
            self.assertIn("text", chunk)
            self.assertGreater(len(chunk["text"]), 0)

    def test_run_hostile_critique_missing_file(self):
        """Ensures hostile critique gracefully flags missing files without crashing."""
        tmp_path = Path(self.test_dir)
        res = run_hostile_critique(tmp_path / "non_existent.mp4")
        self.assertIn(res["status"], ("PASS", "FLAGGED", "SKIPPED"))

    def test_resolve_auth_strategy_prefers_cdp_live(self):
        """Ensures active CDP session is prioritized over all file-based auth."""
        from unittest.mock import patch
        tmp_path = Path(self.test_dir)
        repo_cookies = tmp_path / "flow_cookies.json"
        repo_cookies.write_text("[]", encoding="utf-8")
        enc_bundle = tmp_path / "flow_auth_bundle.enc"
        enc_bundle.write_bytes(b"mock_encrypted_data")

        with patch("mini_run_pipeline.google_flow_service.is_cdp_endpoint_alive", return_value=True):
            res = resolve_auth_strategy(
                repo_cookies=repo_cookies,
                enc_path=enc_bundle,
                auth_key="abcdef123456",
                cdp_url="http://127.0.0.1:9222",
            )
            self.assertEqual(res, "cdp_live")

    def test_resolve_auth_strategy_prefers_repo_cookies(self):
        """Ensures repo cookies are strictly prioritized over encrypted bundle when CDP is absent."""
        tmp_path = Path(self.test_dir)
        repo_cookies = tmp_path / "flow_cookies.json"
        repo_cookies.write_text("[]", encoding="utf-8")
        enc_bundle = tmp_path / "flow_auth_bundle.enc"
        enc_bundle.write_bytes(b"mock_encrypted_data")

        res = resolve_auth_strategy(
            repo_cookies=repo_cookies,
            enc_path=enc_bundle,
            auth_key="abcdef123456",
            cdp_url="http://127.0.0.1:65534",
        )
        self.assertEqual(res, "repo_cookies")

    def test_resolve_auth_strategy_falls_back_to_bundle(self):
        """Ensures fallback to encrypted bundle when repo cookies and CDP are absent."""
        tmp_path = Path(self.test_dir)
        repo_cookies = tmp_path / "absent_cookies.json"
        enc_bundle = tmp_path / "flow_auth_bundle.enc"
        enc_bundle.write_bytes(b"mock_encrypted_data")

        res = resolve_auth_strategy(
            repo_cookies=repo_cookies,
            enc_path=enc_bundle,
            auth_key="abcdef123456",
            cdp_url="http://127.0.0.1:65534",
        )
        self.assertEqual(res, "enc_bundle")

    def test_resolve_auth_strategy_raises_when_neither(self):
        """Ensures failure fast when neither auth mechanism is available."""
        tmp_path = Path(self.test_dir)
        repo_cookies = tmp_path / "absent_cookies.json"
        enc_bundle = tmp_path / "absent_bundle.enc"

        with self.assertRaises(RuntimeError):
            resolve_auth_strategy(
                repo_cookies=repo_cookies,
                enc_path=enc_bundle,
                auth_key=None,
                cdp_url="http://127.0.0.1:65534",
            )


if __name__ == "__main__":
    unittest.main()

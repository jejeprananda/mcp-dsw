from pathlib import Path
from unittest.mock import patch

from utils.ssl import _BUNDLE_PATH, _SECTIGO_CA, apply_ssl_verify, get_ssl_verify


class TestGetSslVerify:
    def test_returns_false_when_ssl_verify_disabled(self):
        with patch("utils.ssl.SSL_VERIFY", False):
            assert get_ssl_verify() is False

    def test_returns_override_path_when_ssl_ca_bundle_set(self, tmp_path):
        custom_bundle = tmp_path / "custom.pem"
        custom_bundle.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----\n"
        )

        with (
            patch("utils.ssl.SSL_VERIFY", True),
            patch("utils.ssl.SSL_CA_BUNDLE", str(custom_bundle)),
        ):
            assert get_ssl_verify() == str(custom_bundle.resolve())

    def test_builds_default_bundle_when_not_disabled(self):
        with (
            patch("utils.ssl.SSL_VERIFY", True),
            patch("utils.ssl.SSL_CA_BUNDLE", None),
        ):
            if _BUNDLE_PATH.exists():
                _BUNDLE_PATH.unlink()

            result = get_ssl_verify()

        assert isinstance(result, str)
        bundle = Path(result)
        assert bundle.exists()
        content = bundle.read_bytes()
        assert _SECTIGO_CA.read_bytes().strip() in content
        assert content.startswith(b"-----BEGIN CERTIFICATE-----")

    def test_session_verify_is_set(self):
        import importlib

        import client.session as session_module

        importlib.reload(session_module)

        verify = session_module.session.verify
        assert verify is not False
        assert Path(verify).exists()
        assert session_module.session.trust_env is False

    def test_apply_ssl_verify_disables_trust_env(self):
        import requests

        session = requests.Session()
        apply_ssl_verify(session)

        assert session.trust_env is False
        assert Path(session.verify).exists()

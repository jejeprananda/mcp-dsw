from unittest.mock import MagicMock, patch

import requests

from client.auth import login
from tools.login import login_dsw


class TestAuthLogin:
    def test_login_success_when_ci_session_present(self):
        mock_cookies = MagicMock()
        mock_cookies.get.return_value = "abc123"

        with patch("client.auth.session.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            with patch("client.auth.session.cookies", mock_cookies):
                result = login("user", "pass", "2026")

        assert result == {"success": True, "message": "Login berhasil"}
        mock_post.assert_called_once()

    def test_login_failure_when_ci_session_absent(self):
        mock_cookies = MagicMock()
        mock_cookies.get.return_value = None

        with patch("client.auth.session.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            with patch("client.auth.session.cookies", mock_cookies):
                result = login("user", "pass", "2026")

        assert result == {
            "success": False,
            "message": "Login gagal — ci_session tidak ditemukan",
        }

    def test_login_failure_on_request_error(self):
        with patch("client.auth.session.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("network down")
            result = login("user", "pass", "2026")

        assert result["success"] is False
        assert "Request gagal" in result["message"]


class TestLoginDswTool:
    def test_missing_credentials(self):
        with patch("tools.login.DSW_USER", None), patch("tools.login.DSW_PASSWORD", None):
            result = login_dsw()

        assert result == {
            "success": False,
            "message": "Kredensial belum dikonfigurasi di .env",
        }

    def test_delegates_to_auth_login(self):
        with (
            patch("tools.login.DSW_USER", "user"),
            patch("tools.login.DSW_PASSWORD", "pass"),
            patch("tools.login.THANG", "2026"),
            patch("tools.login.login") as mock_login,
        ):
            mock_login.return_value = {"success": True, "message": "Login berhasil"}
            result = login_dsw()

        mock_login.assert_called_once_with("user", "pass", "2026")
        assert result == {"success": True, "message": "Login berhasil"}

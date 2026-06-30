from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from client.puslay import check_user
from tools.checkuser import check_user_dsw
from utils.puslay_parser import parse_check_user_html

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseCheckUserHtml:
    def test_parses_sample_html(self):
        html = (FIXTURES / "checkuser_sample.html").read_text()
        result = parse_check_user_html(html, userid="527010")

        assert result["success"] is True
        assert result["found"] is True
        assert result["userid"] == "527010"
        assert result["nama"] == "DENI HARYONO"
        assert result["nip"] == "197812142000121001"
        assert result["no_hp"] == "081352237779"
        assert result["email"] == "dipa_djpb@kemenkeu.go.id"
        assert "KANTOR PUSAT" in result["unit"]
        assert result["password_asli"] == "204b22"
        assert "Berikut Kami Sampaikan" in result["sugesti"]

    def test_user_not_found(self):
        html = (FIXTURES / "checkuser_not_found.html").read_text()
        result = parse_check_user_html(html, userid="999999")

        assert result["success"] is True
        assert result["found"] is False
        assert result["userid"] == "999999"
        assert result["password_asli"] == ""
        assert result["sugesti"] == ""

    def test_missing_textareas(self):
        result = parse_check_user_html("<html><body></body></html>")

        assert result == {
            "success": False,
            "message": "Gagal parse response HTML",
        }


class TestCheckUserClient:
    def test_request_failure(self):
        with patch("client.puslay.session.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("network down")
            result = check_user("527010")

        assert result["success"] is False
        assert "Request gagal" in result["message"]

    def test_delegates_to_parser(self):
        html = (FIXTURES / "checkuser_sample.html").read_text()
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("client.puslay.session.get", return_value=mock_response):
            result = check_user("527010")

        assert result["found"] is True
        assert result["nama"] == "DENI HARYONO"


class TestCheckUserDswTool:
    def test_empty_userid(self):
        result = check_user_dsw("  ")
        assert result == {"success": False, "message": "userid wajib diisi"}

    def test_auto_login_when_not_logged_in(self):
        with (
            patch("tools.checkuser.is_logged_in", return_value=False),
            patch("tools.checkuser.login") as mock_login,
            patch("tools.checkuser.check_user") as mock_check_user,
        ):
            mock_login.return_value = {"success": True, "message": "Login berhasil"}
            mock_check_user.return_value = {"success": True, "found": True, "userid": "527010"}

            result = check_user_dsw("527010")

        mock_login.assert_called_once()
        mock_check_user.assert_called_once_with("527010")
        assert result["found"] is True

    def test_skips_login_when_already_logged_in(self):
        with (
            patch("tools.checkuser.is_logged_in", return_value=True),
            patch("tools.checkuser.login") as mock_login,
            patch("tools.checkuser.check_user") as mock_check_user,
        ):
            mock_check_user.return_value = {"success": True, "found": True}
            check_user_dsw("527010")

        mock_login.assert_not_called()

    def test_login_failure(self):
        with (
            patch("tools.checkuser.is_logged_in", return_value=False),
            patch("tools.checkuser.login") as mock_login,
        ):
            mock_login.return_value = {"success": False, "message": "ci_session tidak ditemukan"}
            result = check_user_dsw("527010")

        assert result["success"] is False
        assert "Login gagal" in result["message"]

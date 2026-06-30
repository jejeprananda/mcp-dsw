from client.auth import login
from client.puslay import check_user
from config import DSW_PASSWORD, DSW_USER, THANG
from mcp_app import mcp
from utils.helper import is_logged_in


@mcp.tool
def check_user_dsw(userid: str) -> dict:
    """Cek data user SatuDJA di DSW berdasarkan User ID."""
    userid = userid.strip()
    if not userid:
        return {"success": False, "message": "userid wajib diisi"}

    if not is_logged_in():
        login_result = login(DSW_USER, DSW_PASSWORD, THANG)
        if not login_result.get("success"):
            message = login_result.get("message", "Login gagal")
            return {"success": False, "message": f"Login gagal: {message}"}

    return check_user(userid)

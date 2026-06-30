from client.auth import login
from config import DSW_PASSWORD, DSW_USER, THANG
from mcp_app import mcp


@mcp.tool
def login_dsw() -> dict:
    """Login ke DSW menggunakan kredensial dari .env."""
    if not DSW_USER or not DSW_PASSWORD:
        return {
            "success": False,
            "message": "Kredensial belum dikonfigurasi di .env",
        }

    return login(DSW_USER, DSW_PASSWORD, THANG)

import requests

from client.session import session
from config import BASE_URL
from utils.ssl import apply_ssl_verify


def login(iduser: str, password: str, thang: str) -> dict:
    verify = apply_ssl_verify(session)

    try:
        session.post(
            f"{BASE_URL}/login/login_user",
            data={
                "iduser": iduser,
                "password": password,
                "thang": thang,
            },
            verify=verify,
        )
    except requests.RequestException as exc:
        return {"success": False, "message": f"Request gagal: {exc}"}

    ci_session = session.cookies.get("ci_session")
    if ci_session:
        return {"success": True, "message": "Login berhasil"}

    return {"success": False, "message": "Login gagal — ci_session tidak ditemukan"}

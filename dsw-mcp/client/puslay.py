import requests

from client.session import session
from config import BASE_URL
from utils.puslay_parser import parse_check_user_html
from utils.ssl import apply_ssl_verify


def check_user(userid: str) -> dict:
    verify = apply_ssl_verify(session)
    referer = f"{BASE_URL}/puslay?q=p4sly&userid={userid}&typ=chekuser"

    try:
        response = session.get(
            f"{BASE_URL}/puslay",
            params={"q": "p4sly", "userid": userid, "typ": "chekuser"},
            headers={
                "Referer": referer,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            verify=verify,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"success": False, "message": f"Request gagal: {exc}"}

    return parse_check_user_html(response.text, userid=userid)

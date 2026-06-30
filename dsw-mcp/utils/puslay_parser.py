import re

from bs4 import BeautifulSoup

_TXT1_FIELD_MAP = {
    "nama": "nama",
    "nip": "nip",
    "no hp": "no_hp",
    "email": "email",
    "login": "login",
}


def _parse_txt1(text: str) -> dict:
    fields: dict[str, str] = {
        "unit": "",
        "nama": "",
        "nip": "",
        "no_hp": "",
        "email": "",
        "login": "",
    }

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.lower().startswith("user :"):
            fields["unit"] = stripped.split(":", 1)[1].strip()
            continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        mapped = _TXT1_FIELD_MAP.get(key.strip().lower())
        if mapped:
            fields[mapped] = value.strip()

    return fields


def _parse_txt2(text: str) -> dict:
    password_match = re.search(
        r"Password\s+Asli\s*:\s*(\S+)",
        text,
        re.IGNORECASE,
    )
    return {
        "sugesti": text.strip(),
        "password_asli": password_match.group(1) if password_match else "",
    }


def _is_user_found(txt1_fields: dict) -> bool:
    return any(
        txt1_fields.get(field)
        for field in ("unit", "nama", "nip", "no_hp", "email", "login")
    )


def parse_check_user_html(html: str, userid: str = "") -> dict:
    soup = BeautifulSoup(html, "html.parser")
    txt1_el = soup.find("textarea", id="txt1")
    txt2_el = soup.find("textarea", id="txt2")

    if txt1_el is None and txt2_el is None:
        return {
            "success": False,
            "message": "Gagal parse response HTML",
        }

    txt1_text = txt1_el.get_text() if txt1_el else ""
    txt2_text = txt2_el.get_text() if txt2_el else ""

    txt1_fields = _parse_txt1(txt1_text)
    txt2_fields = _parse_txt2(txt2_text)
    found = _is_user_found(txt1_fields)

    result = {
        "success": True,
        "found": found,
        "userid": userid,
        **txt1_fields,
        **txt2_fields,
    }

    if not found:
        result["sugesti"] = ""
        result["password_asli"] = ""

    return result

from pathlib import Path

import certifi

from config import SSL_CA_BUNDLE, SSL_VERIFY

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SECTIGO_CA = _PROJECT_ROOT / "certs" / "sectigo-ov-r36.pem"
_BUNDLE_PATH = _PROJECT_ROOT / "certs" / "dsw-ca-bundle.pem"
_VERSION_FILE = _PROJECT_ROOT / "certs" / ".bundle-version"
_BUNDLE_VERSION = 2


def _normalize_pem(data: bytes) -> bytes:
    if not data.endswith(b"\n"):
        data += b"\n"
    return data


def _build_ca_bundle() -> Path:
    _BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    sectigo_ca = _normalize_pem(_SECTIGO_CA.read_bytes())
    certifi_bundle = _normalize_pem(Path(certifi.where()).read_bytes())

    # Intermediate first so chain building finds Sectigo R36 before roots.
    _BUNDLE_PATH.write_bytes(sectigo_ca + certifi_bundle)
    _VERSION_FILE.write_text(str(_BUNDLE_VERSION))
    return _BUNDLE_PATH


def _bundle_is_stale() -> bool:
    if not _BUNDLE_PATH.exists():
        return True

    if not _VERSION_FILE.exists():
        return True

    if _VERSION_FILE.read_text().strip() != str(_BUNDLE_VERSION):
        return True

    bundle_mtime = _BUNDLE_PATH.stat().st_mtime
    certifi_mtime = Path(certifi.where()).stat().st_mtime
    sectigo_mtime = _SECTIGO_CA.stat().st_mtime
    return bundle_mtime < certifi_mtime or bundle_mtime < sectigo_mtime


def get_ssl_verify() -> str | bool:
    if not SSL_VERIFY:
        return False

    if SSL_CA_BUNDLE:
        return str(Path(SSL_CA_BUNDLE).expanduser().resolve())

    if not _SECTIGO_CA.exists():
        raise FileNotFoundError(
            f"Sectigo intermediate CA not found: {_SECTIGO_CA}"
        )

    if _bundle_is_stale():
        return str(_build_ca_bundle().resolve())

    return str(_BUNDLE_PATH.resolve())


def apply_ssl_verify(session) -> str | bool:
    verify = get_ssl_verify()
    session.verify = verify
    session.trust_env = False
    return verify

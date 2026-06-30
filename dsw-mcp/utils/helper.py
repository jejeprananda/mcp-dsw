from client.session import session


def get_session_cookie() -> str | None:
    return session.cookies.get("ci_session")


def is_logged_in() -> bool:
    return get_session_cookie() is not None

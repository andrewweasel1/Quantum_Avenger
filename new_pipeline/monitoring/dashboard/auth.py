"""Dashboard auth gate (restored from the legacy dashboard).

Credentials come from env vars (``DASHBOARD_USER`` / ``DASHBOARD_PASS``) — never
stored in config or code. ``verify_credentials`` is a pure, constant-time check
so it is testable without Streamlit; ``require_login`` wires it into the app.
"""

import hmac
import os


def verify_credentials(
    username, password, expected_user=None, expected_password=None
) -> bool:
    expected_user = (
        expected_user if expected_user is not None else os.environ.get("DASHBOARD_USER", "")
    )
    expected_password = (
        expected_password
        if expected_password is not None
        else os.environ.get("DASHBOARD_PASS", "")
    )
    if not expected_user or not expected_password:
        return False  # fail closed when no credentials are configured
    return hmac.compare_digest(str(username), expected_user) and hmac.compare_digest(
        str(password), expected_password
    )


def require_login(st) -> bool:  # pragma: no cover - exercised via the Streamlit app
    """Render a login gate; return True once authenticated."""
    if st.session_state.get("authenticated"):
        return True
    st.title("🛡️ Quantum Avenger — Sign in")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign in"):
        if verify_credentials(username, password):
            st.session_state["authenticated"] = True
            return True
        st.error("Invalid credentials.")
    return False

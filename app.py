import os
import requests
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="E-commerce KG Chat UI", page_icon="🕸️", layout="wide")
st.title("E-commerce Knowledge Graph — Chat UI")
st.caption("Streamlit on Cloud Run")

# ---------- Settings ----------
DEFAULT_BACKEND = os.getenv("BACKEND_URL", "").strip()
DEFAULT_PATH = os.getenv("BACKEND_PATH", "/").strip() or "/"

with st.sidebar:
    st.header("Settings")
    backend_url = st.text_input(
        "Backend base URL",
        value=DEFAULT_BACKEND,
        placeholder="https://ecom-kg-chat-backend-XXXX-asia-south1.run.app",
        help="Your Cloud Run backend URL",
    )
    backend_path = st.text_input(
        "Endpoint path",
        value=DEFAULT_PATH,
        help="Keep as '/' unless your backend uses something else",
    )

st.divider()

# ---------- Health / connectivity ----------
@st.cache_data(ttl=30)
def check_backend(url: str, path: str) -> tuple[bool, str]:
    if not url:
        return False, "No backend URL set."
    try:
        u = url.rstrip("/") + path
        r = requests.get(u, timeout=5)
        if r.ok:
            return True, f"GET {u} → {r.status_code}"
        return False, f"GET {u} → {r.status_code}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

col1, col2 = st.columns(2)
with col1:
    st.subheader("App Status")
    st.success("Streamlit is running ✅")

with col2:
    st.subheader("Backend Status")
    ok, msg = check_backend(backend_url, backend_path) if backend_url else (False, "Backend not configured.")
    (st.success if ok else st.info)(msg)

# ---------- Simple UI ----------
st.subheader("Ask the backend")
user_q = st.text_input("Your question:", placeholder="e.g., Top products by revenue last month")
go = st.button("Submit")

if go:
    if not backend_url:
        st.warning("Set the backend URL in the sidebar first.")
    elif not user_q.strip():
        st.warning("Type a question.")
    else:
        u = backend_url.rstrip("/") + backend_path
        with st.spinner("Calling backend..."):
            try:
                # Contract: POST / with {"text": "..."}
                resp = requests.post(u, json={"text": user_q}, timeout=60)
                if resp.ok:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw_text": resp.text}
                    # Try common keys, but also show full payload
                    preferred = None
                    for k in ["answer", "output", "response", "message", "text", "result"]:
                        if isinstance(data, dict) and k in data:
                            preferred = data[k]
                            break
                    if preferred:
                        st.markdown("**Response:**")
                        st.write(preferred)
                        st.expander("Full payload").write(data)
                    else:
                        st.markdown("**Response (raw payload):**")
                        st.write(data)
                else:
                    st.error(f"Backend HTTP {resp.status_code}")
                    st.code(resp.text[:2000])
            except Exception as e:
                st.error(f"Request failed: {e}")

st.divider()
st.caption("Configured to POST '/' with JSON {'text': '...'} per your backend’s requirement.")

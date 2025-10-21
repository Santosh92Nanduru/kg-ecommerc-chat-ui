import os, json, time, requests, pandas as pd, streamlit as st

SERVICE_URL = os.getenv("SERVICE_URL", "https://ecom-kg-chat-860672618801.asia-south1.run.app/")
TIMEOUT_SEC = 90

st.set_page_config(page_title="E-com KG Chat", page_icon="🛒", layout="wide")

@st.cache_data(ttl=60)
def health():
    try:
        r = requests.get(SERVICE_URL, params={"health":"1"}, timeout=10)
        r.raise_for_status()
        return True, r.json()
    except Exception as e:
        return False, {"error": str(e)}

def call_backend(q: str) -> dict:
    t0 = time.time()
    r = requests.post(SERVICE_URL,
                      headers={"Content-Type":"application/json"},
                      data=json.dumps({"text": q}),
                      timeout=TIMEOUT_SEC)
    out = r.json()
    out.setdefault("meta", {})["took_ms"] = int((time.time()-t0)*1000)
    return out

st.title("🛒 E-commerce KG Chat (POC)")
ok, h = health()
st.caption(f"Backend: {'Healthy' if ok else 'Down'}  •  rev {h.get('version','?') if ok else ''}")

with st.expander("Examples", expanded=False):
    c1, c2, c3 = st.columns(3)
    if c1.button("Monthly revenue trend for 2025"):
        st.session_state["q"] = "Monthly revenue trend for 2025"
    if c2.button("Top 10 products by revenue in 2025"):
        st.session_state["q"] = "Top 10 products by revenue in 2025"
    if c3.button("Revenue by country for 2025 (desc)"):
        st.session_state["q"] = "Revenue by country for 2025, sort by revenue desc"

q = st.text_input("Your question", key="q", placeholder="e.g., Top 10 products by revenue")

if st.button("Send") and q.strip():
    with st.spinner("Thinking…"):
        try:
            resp = call_backend(q.strip())
        except Exception as e:
            st.error(f"Request failed: {e}")
        else:
            if "error" in resp:
                st.error(resp["error"])
            else:
                st.subheader("Generated Cypher")
                st.code(resp.get("cypher",""), language="cypher")
                rows = (resp.get("answer") or {}).get("rows", [])
                if rows:
                    df = pd.DataFrame(rows)
                    st.subheader("Results")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No rows returned. Try a different time window (your data seems to be in 2025).")

from __future__ import annotations
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_backend_url() -> str:
    """Resolve backend url from Streamlit secrets or environment."""
    secrets_url = st.secrets.get("BACKEND_URL", "").strip() if st.secrets else ""
    env_url = os.getenv("BACKEND_URL", "").strip()
    fallback_url = "http://127.0.0.1:8000"
    return secrets_url or env_url or fallback_url


BACKEND_URL = get_backend_url().rstrip("/")

st.set_page_config(page_title="StockFlow Demo", page_icon="📦", layout="centered")
st.title("📦 StockFlow")
st.caption("Minimal stock management demo with FastAPI + Streamlit")

st.info(f"Using backend API: `{BACKEND_URL}`")
if "127.0.0.1" in BACKEND_URL or "localhost" in BACKEND_URL:
    st.warning(
        "If you deploy on Streamlit Community Cloud, localhost points to the Streamlit "
        "container itself. Configure BACKEND_URL in Streamlit Secrets or environment "
        "variables to your deployed FastAPI URL."
    )

st.subheader("Register movement")
with st.form("movement_form"):
    movement_product_id = st.text_input("Product ID", placeholder="ABC123")
    movement_quantity = st.number_input("Quantity", min_value=0, step=1, value=0)
    movement_type = st.selectbox("Type", options=["in", "out"])
    submit_movement = st.form_submit_button("Submit movement")

if submit_movement:
    payload = {
        "product_id": movement_product_id,
        "quantity": int(movement_quantity),
        "type": movement_type,
    }
    try:
        response = requests.post(f"{BACKEND_URL}/movements", json=payload, timeout=10)
        data = response.json()
        if response.ok:
            st.success(
                f"Movement saved for {data['product_id']}. Current stock: {data['current_stock']}"
            )
        else:
            st.error(data.get("detail", "Failed to register movement"))
    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")

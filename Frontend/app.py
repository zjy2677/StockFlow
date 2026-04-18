from __future__ import annotations

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_backend_url() -> str:
    """Resolve backend URL from Streamlit secrets or environment."""
    secrets_url = st.secrets.get("BACKEND_URL", "").strip() if st.secrets else ""
    env_url = os.getenv("BACKEND_URL", "").strip()
    fallback_url = "http://127.0.0.1:8000"
    return secrets_url or env_url or fallback_url


def extract_error_message(response: requests.Response, fallback: str) -> str:
    """Get a user-friendly API error message."""
    try:
        data: dict[str, Any] = response.json()
        detail = data.get("detail", fallback)
        if isinstance(detail, list):
            return "; ".join(str(item) for item in detail)
        return str(detail)
    except ValueError:
        return fallback


def init_local_inventory() -> None:
    """Initialize local in-memory inventory for frontend-only mode."""
    if "local_inventory" not in st.session_state:
        st.session_state.local_inventory = {}


def register_local_movement(product_id: str, quantity: int, movement_type: str) -> tuple[bool, str]:
    """Register stock movement in local session state."""
    clean_id = product_id.strip()
    if not clean_id:
        return False, "Product ID must not be empty."

    inventory = st.session_state.local_inventory
    current_stock = int(inventory.get(clean_id, 0))

    if movement_type == "in":
        current_stock += quantity
    else:
        if clean_id not in inventory:
            return False, "Product does not exist in local inventory."
        current_stock -= quantity
        if current_stock < 0:
            return False, "Insufficient stock for this movement."

    inventory[clean_id] = current_stock
    return True, f"Movement saved for {clean_id}. Current stock: {current_stock}"


def get_local_stock(product_id: str) -> tuple[bool, str]:
    """Get stock from local session state inventory."""
    clean_id = product_id.strip()
    if not clean_id:
        return False, "Product ID must not be empty."

    inventory = st.session_state.local_inventory
    if clean_id not in inventory:
        return False, "Product does not exist in local inventory."

    return True, f"Current stock for {clean_id}: {inventory[clean_id]}"


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

left_col, right_col = st.columns(2)

with left_col:
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

with right_col:
    st.subheader("Check inventory")
    with st.form("inventory_form"):
        stock_product_id = st.text_input("Product ID to check", placeholder="ABC123")
        check_inventory = st.form_submit_button("Check stock")

    if check_inventory:
        try:
            response = requests.get(
                f"{BACKEND_URL}/products/{stock_product_id}/stock",
                timeout=10,
            )
            data = response.json()
            if response.ok:
                st.success(
                    f"Current stock for {data['product_id']}: {data['current_stock']}"
                )
            else:
                st.error(data.get("detail", "Failed to retrieve stock"))
        except requests.RequestException as exc:
            st.error(f"Could not connect to backend: {exc}")

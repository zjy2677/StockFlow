from __future__ import annotations
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="StockFlow Demo", page_icon="📦", layout="centered")
st.title("📦 StockFlow")
st.caption("Minimal stock management demo with FastAPI + Streamlit")

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

st.divider()
st.subheader("Check current stock")
with st.form("stock_form"):
    stock_product_id = st.text_input("Product ID to query", placeholder="ABC123")
    submit_stock = st.form_submit_button("Get stock")

if submit_stock:
    try:
        response = requests.get(f"{BACKEND_URL}/products/{stock_product_id}/stock", timeout=10)
        data = response.json()
        if response.ok:
            st.success(f"Product {data['product_id']} current stock: {data['current_stock']}")
        else:
            st.error(data.get("detail", "Failed to fetch stock"))
    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")

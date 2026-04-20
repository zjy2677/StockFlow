from __future__ import annotations
import os
from pathlib import Path

import requests
import streamlit as st

from utilities import extract_error_message, set_bg


ROOT_DIR = Path(__file__).resolve().parents[1]
API_BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
IMG_PATH = ROOT_DIR / "Frontend" / "photo" / "background_img.png"

st.set_page_config(page_title="StockFlow Demo", layout="centered")
set_bg(IMG_PATH)

defaults = {
    "movement_product_id": "",
    "movement_quantity": 1,
    "movement_type": "in",
    "movement_message": None,
    "movement_message_type": None,
    "stock_product_id": "",
    "stock_message": None,
    "stock_message_type": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_movement_form():
    st.session_state["movement_product_id"] = ""
    st.session_state["movement_quantity"] = 1
    st.session_state["movement_type"] = "in"
    st.session_state["movement_message"] = None
    st.session_state["movement_message_type"] = None


def reset_inventory_form():
    st.session_state["stock_product_id"] = ""
    st.session_state["stock_message"] = None
    st.session_state["stock_message_type"] = None


with st.sidebar:
    st.header("User's Guide")

    st.markdown("""
### Register Stock
- Enter a valid **Product ID**
- Specify **Quantity**
- Choose movement type: **in** (add) or **out** (remove)
- Click **Submit movement**

### Check Inventory
- Enter an existing **Product ID**
- Click **Check stock**

---

### Input Rules
- **Product ID**
  - Only lowercase letters (`a–z`) and numbers (`0–9`)
  - Length: 1–30 characters
- **Quantity**
  - Integer only
  - Range: 1 to 1,000,000
- **Type**
  - Must be `"in"` or `"out"`
- Products must be **registered before checking inventory**

---

### Validation Coverage
This app includes structured validation logic to handle:
- Invalid characters
- Whitespace-only inputs
- Mixed invalid formats (characters + spaces)

Errors are handled gracefully with user-friendly feedback.
""")

st.title("StockFlow")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Stock Register")

    with st.form("movement_form"):
        movement_product_id = st.text_input(
            "Product ID",
            placeholder="ABC123",
            key="movement_product_id",
        )
        movement_quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1,
            key="movement_quantity",
        )
        movement_type = st.selectbox(
            "Type",
            options=["in", "out"],
            key="movement_type",
        )

        btn_col1, spacer, btn_col2 = st.columns([1, 1.3, 1])
        with btn_col1:
            submit_movement = st.form_submit_button("register")
        with btn_col2:
            reset_movement = st.form_submit_button(
                "reset",
                on_click=reset_movement_form,
            )

    if submit_movement:
        try:
            response = requests.post(
                f"{API_BACKEND_URL}/movements",
                json={
                    "product_id": movement_product_id,
                    "quantity": int(movement_quantity),
                    "type": movement_type,
                },
                timeout=10,
            )

            if response.status_code == 201:
                result = response.json()
                st.session_state["movement_message"] = (
                    f"{result['message']}. Current stock of {result['product_id']} "
                    f"has been updated to {result['current_stock']}."
                )
                st.session_state["movement_message_type"] = "success"
            else:
                st.session_state["movement_message"] = extract_error_message(response)
                st.session_state["movement_message_type"] = "error"

        except requests.exceptions.ConnectionError:
            st.session_state["movement_message"] = (
                "Cannot connect to backend API. Make sure FastAPI is running."
            )
            st.session_state["movement_message_type"] = "error"
        except requests.exceptions.Timeout:
            st.session_state["movement_message"] = "Backend API request timed out."
            st.session_state["movement_message_type"] = "error"
        except Exception as exc:
            st.session_state["movement_message"] = f"Unexpected error: {exc}"
            st.session_state["movement_message_type"] = "error"

    if st.session_state["movement_message"]:
        if st.session_state["movement_message_type"] == "success":
            st.success(st.session_state["movement_message"])
        else:
            st.error(st.session_state["movement_message"])


with right_col:
    st.subheader("Inventory Checker")

    with st.form("inventory_form"):
        stock_product_id = st.text_input(
            "Product ID to check",
            placeholder="ABC123",
            key="stock_product_id",
        )

        btn_col1, spacer, btn_col2 = st.columns([1, 1.8, 1])
        with btn_col1:
            check_inventory = st.form_submit_button("check")
        with btn_col2:
            reset_inventory = st.form_submit_button(
                "reset",
                on_click=reset_inventory_form,
            )

    if check_inventory:
        try:
            response = requests.get(
                f"{API_BACKEND_URL}/products/{stock_product_id}/stock",
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                st.session_state["stock_message"] = (
                    f"Current stock for {result['product_id']}: {result['current_stock']}"
                )
                st.session_state["stock_message_type"] = "success"
            else:
                st.session_state["stock_message"] = extract_error_message(response)
                st.session_state["stock_message_type"] = "error"

        except requests.exceptions.ConnectionError:
            st.session_state["stock_message"] = (
                "Cannot connect to backend API. Make sure FastAPI is running."
            )
            st.session_state["stock_message_type"] = "error"
        except requests.exceptions.Timeout:
            st.session_state["stock_message"] = "Backend API request timed out."
            st.session_state["stock_message_type"] = "error"
        except Exception as exc:
            st.session_state["stock_message"] = f"Unexpected error: {exc}"
            st.session_state["stock_message_type"] = "error"

    if st.session_state["stock_message"]:
        if st.session_state["stock_message_type"] == "success":
            st.success(st.session_state["stock_message"])
        else:
            st.error(st.session_state["stock_message"])

from __future__ import annotations
import os
from pathlib import Path
import streamlit as st
import requests
import base64


ROOT_DIR = Path(__file__).resolve().parents[1]
API_BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")from __future__ import annotations
IMG_PATH = ROOT_DIR / "Frontend" / "photo" / "background_img.png"


def set_bg(img_path):
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(
                    rgba(255, 255, 255, 0.28),
                    rgba(255, 255, 255, 0.32)
                ),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .main .block-container {{
            background: rgba(255, 255, 255, 1);
            padding: 2rem 2.5rem;
            border-radius: 18px;
        }}

        html, body, [class*="css"] {{
            font-size: 18px;
        }}

        h1 {{
            font-size: 42px !important;
            font-weight: 700;
        }}

        h2, h3 {{
            font-size: 24px !important;
            font-weight: 600;
        }}

        label {{
            font-size: 16px !important;
            font-weight: 600;
        }}

        input, textarea {{
            font-size: 18px !important;
        }}

        button {{
            font-size: 14px !important;
            padding: 0.5rem 1rem;
        }}

        div[data-testid="stForm"] {{
            background: rgba(255, 255, 255, 0.99);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.12);
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
        }}

        div[data-testid="stForm"] .stTextInput,
        div[data-testid="stForm"] .stNumberInput,
        div[data-testid="stForm"] .stSelectbox {{
            margin-bottom: 0.8rem;
        }}

        div[data-testid="stAlert"],
        div[data-testid="stAlert"] > div {{
            border-radius: 12px !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
            background-image: none !important;
            opacity: 1 !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }}

        div[data-testid="stAlert"][kind="success"],
        div[data-testid="stAlert"][kind="success"] > div {{
            background: #d4edda !important;
            color: #155724 !important;
        }}

        div[data-testid="stAlert"][kind="error"],
        div[data-testid="stAlert"][kind="error"] > div {{
            background: #f8d7da !important;
            color: #721c24 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

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
IMG_PATH = ROOT_DIR / "Frontend" / "photo" / "background_img.png"


def set_bg(img_path):
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(
                    rgba(255, 255, 255, 0.28),
                    rgba(255, 255, 255, 0.32)
                ),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .main .block-container {{
            background: rgba(255, 255, 255, 1);
            padding: 2rem 2.5rem;
            border-radius: 18px;
        }}

        html, body, [class*="css"] {{
            font-size: 18px;
        }}

        h1 {{
            font-size: 42px !important;
            font-weight: 700;
        }}

        h2, h3 {{
            font-size: 24px !important;
            font-weight: 600;
        }}

        label {{
            font-size: 16px !important;
            font-weight: 600;
        }}

        input, textarea {{
            font-size: 18px !important;
        }}

        button {{
            font-size: 14px !important;
            padding: 0.5rem 1rem;
        }}

        div[data-testid="stForm"] {{
            background: rgba(255, 255, 255, 0.99);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.12);
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
        }}

        div[data-testid="stForm"] .stTextInput,
        div[data-testid="stForm"] .stNumberInput,
        div[data-testid="stForm"] .stSelectbox {{
            margin-bottom: 0.8rem;
        }}

        /* Shared alert styling */
        div[data-testid="stAlert"],
        div[data-testid="stAlert"] > div {{
            border-radius: 12px !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
            background-image: none !important;
            opacity: 1 !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }}

        /* SUCCESS */
        div[data-testid="stAlert"][kind="success"],
        div[data-testid="stAlert"][kind="success"] > div {{
            background: #d4edda !important;
            color: #155724 !important;
        }}

        /* ERROR */
        div[data-testid="stAlert"][kind="error"],
        div[data-testid="stAlert"][kind="error"] > div {{
            background: #f8d7da !important;
            color: #721c24 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="StockFlow Demo", layout="centered")
set_bg(IMG_PATH)

# ---- Session state init ----
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


# Sidebar
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

# LEFT: Register
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
            movement = MovementRequest(
                product_id=movement_product_id,
                quantity=int(movement_quantity),
                type=movement_type,
            )
            result = stock_service.register_movement(movement)
            st.session_state["movement_message"] = (
                f"{result.message}. Current stock of {result.product_id} "
                f"has been updated to {result.current_stock}."
            )
            st.session_state["movement_message_type"] = "success"
        except HTTPException as exc:
            st.session_state["movement_message"] = exc.detail
            st.session_state["movement_message_type"] = "error"
        except ValidationError as exc:
            err = exc.errors()[0]["msg"].replace("Value error,", "").strip()
            st.session_state["movement_message"] = err
            st.session_state["movement_message_type"] = "error"
        except Exception as exc:
            st.session_state["movement_message"] = f"Unexpected error: {exc}"
            st.session_state["movement_message_type"] = "error"

    if st.session_state["movement_message"]:
        if st.session_state["movement_message_type"] == "success":
            st.success(st.session_state["movement_message"])
        else:
            st.error(st.session_state["movement_message"])

# RIGHT: Check
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
            result = stock_service.get_stock(stock_product_id)
            st.session_state["stock_message"] = (
                f"Current stock for {result.product_id}: {result.current_stock}"
            )
            st.session_state["stock_message_type"] = "success"
        except HTTPException as exc:
            st.session_state["stock_message"] = exc.detail
            st.session_state["stock_message_type"] = "error"
        except ValueError as exc:
            st.session_state["stock_message"] = str(exc)
            st.session_state["stock_message_type"] = "error"
        except Exception as exc:
            st.session_state["stock_message"] = f"Unexpected error: {exc}"
            st.session_state["stock_message_type"] = "error"

    if st.session_state["stock_message"]:
        if st.session_state["stock_message_type"] == "success":
            st.success(st.session_state["stock_message"])
        else:
            st.error(st.session_state["stock_message"])

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
from fastapi import HTTPException
import base64

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from Backend.service import MovementRequest, stock_service

IMG_PATH = ROOT_DIR / "Frontend" / "photo" / "background_img.png"

def set_bg(img_path):
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(
                    rgba(255, 255, 255, 0.36),
                    rgba(255, 255, 255, 0.36)
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
        </style>
        """,
        unsafe_allow_html=True)


st.set_page_config(page_title="StockFlow Demo", layout="centered")
set_bg(IMG_PATH)

st.title("StockFlow")
st.caption("Tiny stock management demo")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Register movement")

    with st.form("movement_form"):
        movement_product_id = st.text_input("Product ID", placeholder="ABC123")
        movement_quantity = st.number_input("Quantity", min_value=0, step=1, value=0)
        movement_type = st.selectbox("Type", options=["in", "out"])
        submit_movement = st.form_submit_button("Submit movement")

    if submit_movement:
        try:
            movement = MovementRequest(
                product_id=movement_product_id,
                quantity=int(movement_quantity),
                type=movement_type,
            )
            result = stock_service.register_movement(movement)
            st.success(
                f"Movement saved for {result.product_id}. Current stock: {result.current_stock}"
            )
        except HTTPException as exc:
            st.error(exc.detail)
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

with right_col:
    st.subheader("Check inventory")

    with st.form("inventory_form"):
        stock_product_id = st.text_input("Product ID to check", placeholder="ABC123")
        check_inventory = st.form_submit_button("Check stock")

    if check_inventory:
        try:
            result = stock_service.get_stock(stock_product_id)
            st.success(
                f"Current stock for {result.product_id}: {result.current_stock}"
            )
        except HTTPException as exc:
            st.error(exc.detail)
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

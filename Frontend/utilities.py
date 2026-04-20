from __future__ import annotations
import requests
import base64

def extract_error_message(response: requests.Response) -> str:
    try:
        data = response.json()
        detail = data.get("detail", "Unknown error")

        if isinstance(detail, list) and len(detail) > 0:
            first_error = detail[0]
            if isinstance(first_error, dict):
                return str(first_error.get("msg", "Validation error"))

        return str(detail)
    except Exception:
        return f"Request failed with status code {response.status_code}"

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

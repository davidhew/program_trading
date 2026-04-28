import streamlit as st

st.html("""
    <style>
        /* Change the background color of the main app area */
        .stApp {
            background-color: #f0f2f6;
        }
        /* Style all buttons */
        .stButton>button {
            color: white;
            background-color: #ff4b4b;
            border-radius: 20px;
        }
    </style>
""")

st.button("Styled Button")
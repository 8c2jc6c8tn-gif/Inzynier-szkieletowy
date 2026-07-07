import streamlit as st

st.title("Test działania")
st.write("Jeśli to widzisz, aplikacja działa!")

menu = st.sidebar.radio("Wybór", ["Start", "Opcja 1"])
if menu == "Start":
    st.write("Witaj w aplikacji.")

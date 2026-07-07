import streamlit as st

st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja stanu ---
if 'geo' not in st.session_state:
    st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}

# --- Zakładki ---
# Zastosowanie 'key' w tabs pozwala na stabilniejszą pracę
tabs = st.tabs([
    "1. Geometria", 
    "2. Konstr. Dachu", 
    "3. Wykończenie Dachu", 
    "4. Konstr. Ścian", 
    "5. Wykończenie Ścian", 
    "6. Akcesoria", 
    "7. Kosztorys"
])

# 1. Geometria
with tabs[0]:
    st.header("1. Geometria Budynku")
    st.session_state.geo['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'], key="i_wys")
    st.session_state.geo['szer'] = st.number_input("Wysokość (cm)", 200, 1000, st.session_state.geo['szer'], key="i_szer")
    st.session_state.geo['dlug'] = st.number_input("Wysokość (cm)", 200, 1500, st.session_state.geo['dlug'], key="i_dlug")

# 4. Konstrukcja Ścian (Tu wybierasz słupki)
with tabs[3]:
    st.header("4. Konstrukcja Ścian")
    # Dodanie klucza 'key' zapobiega resetowaniu strony
    przekroj = st.selectbox(
        "Przekrój słupków", 
        ["95x45", "145x45", "195x45"], 
        key="wybor_slupkow"
    )
    st.write(f"Wybrano przekrój: {przekroj}")

# --- Reszta zakładek ---
with tabs[1]: st.header("2. Konstrukcja Dachu")
with tabs[2]: st.header("3. Wykończenie Dachu")
with tabs[4]: st.header("5. Wykończenie Ścian")
with tabs[5]: st.header("6. Akcesoria")
with tabs[6]: st.header("7. Kosztorys")

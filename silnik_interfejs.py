import streamlit as st
import math

# Konfiguracja
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja ---
if 'geo' not in st.session_state: 
    st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}

# --- Zakładki (zamiast przycisków - to jest bardziej stabilne) ---
tab_names = ["Geometria", "Konstr. Dachu", "Wykończenie Dachu", "Konstr. Ścian", "Wykończenie Ścian", "Akcesoria", "Kosztorys"]
tabs = st.tabs(tab_names)

# --- LOGIKA MODUŁÓW ---

with tabs[0]: # Geometria
    st.header("1. Geometria Budynku")
    st.session_state.geo['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'])
    st.session_state.geo['szer'] = st.number_input("Szerokość (cm)", 200, 1000, st.session_state.geo['szer'])
    st.session_state.geo['dlug'] = st.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'])

with tabs[1]: # Konstr. Dachu
    st.header("2. Konstrukcja Dachu")
    rozstaw = st.selectbox("Rozstaw belek (cm)", [30, 40, 60])
    kat = st.slider("Kąt nachylenia (°)", 0, 45, 20)
    st.write("Tu dodamy parametry okapów.")

with tabs[2]: # Wykończenie Dachu
    st.header("3. Wykończenie Dachu")
    pokrycie = st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"])

with tabs[3]: # Konstr. Ścian
    st.header("4. Konstrukcja Ścian")
    przekroj = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])

with tabs[4]: # Wykończenie Ścian
    st.header("5. Wykończenie Ścian")
    st.write("Płyty OSB, izolacje.")

with tabs[5]: # Akcesoria
    st.header("6. Akcesoria")

with tabs[6]: # Kosztorys
    st.header("7. Kosztorys")

# --- Podsumowanie ---
with st.sidebar:
    st.header("Szybki podgląd")
    pow_pod = (st.session_state.geo['szer'] * st.session_state.geo['dlug']) / 10000
    st.metric("Pow. podłogi", f"{pow_pod:.2f} m²")

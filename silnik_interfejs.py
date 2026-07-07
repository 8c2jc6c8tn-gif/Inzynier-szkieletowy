import streamlit as st
import math

# Konfiguracja
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja sesji ---
if 'geo' not in st.session_state: 
    st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}
if 'tab' not in st.session_state: 
    st.session_state.tab = "Geometria"

# --- Nawigacja ---
menu = ["Geometria", "Konstr. Dachu", "Wykończenie Dachu", "Konstr. Ścian", "Wykończenie Ścian", "Akcesoria", "Kosztorys"]
cols = st.columns(len(menu))

for i, name in enumerate(menu):
    if cols[i].button(name, use_container_width=True):
        st.session_state.tab = name

st.divider()

# --- LOGIKA MODUŁÓW ---
if st.session_state.tab == "Geometria":
    st.header("1. Geometria Budynku")
    st.session_state.geo['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'])
    st.session_state.geo['szer'] = st.number_input("Szerokość (cm)", 200, 1000, st.session_state.geo['szer'])
    st.session_state.geo['dlug'] = st.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'])

elif st.session_state.tab == "Konstr. Dachu":
    st.header("2. Konstrukcja Dachu")
    rozstaw = st.selectbox("Rozstaw belek (cm)", [30, 40, 60])
    kat = st.slider("Kąt nachylenia (°)", 0, 45, 20)
    st.write("Sekcja parametrów okapów w budowie...")

elif st.session_state.tab == "Wykończenie Dachu":
    st.header("3. Wykończenie Dachu")
    pokrycie = st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"])

elif st.session_state.tab == "Konstr. Ścian":
    st.header("4. Konstrukcja Ścian")
    przekroj = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])

elif st.session_state.tab == "Wykończenie Ścian":
    st.header("5. Wykończenie Ścian")
    st.write("Ustawienia płyt OSB i folii.")

elif st.session_state.tab == "Akcesoria":
    st.header("6. Akcesoria i Łączniki")

elif st.session_state.tab == "Kosztorys":
    st.header("7. Analiza Kosztów")

# --- Podsumowanie w bocznym pasku ---
with st.sidebar:
    st.header("Szybki podgląd")
    pow_pod = (st.session_state.geo['szer'] * st.session_state.geo['dlug']) / 10000
    st.metric("Pow. podłogi", f"{pow_pod:.2f} m²")

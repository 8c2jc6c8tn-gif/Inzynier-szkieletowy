import streamlit as st
import math

# Konfiguracja
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja ---
if 'okna' not in st.session_state: st.session_state.okna = []
if 'geo' not in st.session_state: st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}
if 'tab' not in st.session_state: st.session_state.tab = "Geometria"

# --- Nawigacja (Kafelki) ---
menu = ["Geometria", "Konstr. Dachu", "Wykończenie Dachu", "Konstr. Ścian", "Wykończenie Ścian", "Akcesoria", "Kosztorys"]
cols = st.columns(len(menu))
for i, name in enumerate(menu):
    if cols[i].button(name, use_container_width=True): st.session_state.tab = name

st.divider()

# --- LOGIKA MODUŁÓW ---

if st.session_state.tab == "Geometria":
    st.header("1. Geometria Budynku")
    col1, col2 = st.columns(2)
    st.session_state.geo['wys'] = col1.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'])
    st.session_state.geo['szer'] = col1.number_input("Szerokość (cm)", 200, 1000, st.session_state.geo['szer'])
    st.session_state.geo['dlug'] = col1.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'])

elif st.session_state.tab == "Konstr. Dachu":
    st.header("2. Konstrukcja Dachu")
    rozstaw = st.selectbox("Rozstaw belek (cm)", [30, 40, 60])
    kat = st.slider("Kąt nachylenia (°)", 0, 45, 20)
    c1, c2 = st.columns(2)
    o_przod = c1.slider("Okap przód (cm)", 0, 100, 20)
    o_tyl = c1.slider("Okap tył (cm)", 0, 100, 20)
    o_lewo = c2.slider("Okap lewo (cm)", 0, 100, 20)
    o_prawo = c2.slider("Okap prawo (cm)", 0, 100, 20)
    st.info("Obliczenia powierzchni dachu w toku...")

elif st.session_state.tab == "Wykończenie Dachu":
    st.header("3. Wykończenie Dachu")
    pokrycie = st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"])
    st.write(f"Konfiguracja dla: {pokrycie}")

elif st.session_state.tab == "Konstr. Ścian":
    st.header("4. Konstrukcja Ścian")
    przekroj = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])
    st.write("Tu dodamy logikę słupków i podwalin.")

elif st.session_state.tab == "Wykończenie Ścian":
    st.header("5. Wykończenie Ścian")
    st.write("Wybór OSB, wiatroizolacji, fasady wewnętrznej/zewnętrznej.")

elif st.session_state.tab == "Akcesoria":
    st.header("6. Akcesoria i Łączniki")
    st.write("Wkręty, taśmy, kątowniki.")

elif st.session_state.tab == "Kosztorys":
    st.header("7. Analiza Kosztów")
    st.write("Tabela zbiorcza wszystkich modułów.")

# --- Podsumowanie w bocznym pasku ---
with st.sidebar:
    st.header("Szybki podgląd")
    pow_pod = (st.session_state.geo['szer'] * st.session_state.geo['dlug']) / 10000
    st.metric("Pow. podłogi", f"{pow_pod:.2f} m²")
    st.write("Nawiguj między zakładkami, aby uzupełnić dane.")

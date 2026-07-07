import streamlit as st

st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych dynamicznych ---
if 'okna' not in st.session_state:
    st.session_state.okna = []

import streamlit as st
import math

st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Moduł Geometrii")

# --- MODUŁ 1: GEOMETRIA ---
with st.sidebar:
    st.header("1. Parametry Budynku")
    wys = st.slider("Wysokość (cm)", 200, 500, 250)
    szer = st.slider("Szerokość (cm)", 200, 1000, 600)
    dlug = st.slider("Długość (cm)", 200, 1500, 800)
    
    st.header("Dach")
    kat_stopnie = st.slider("Kąt nachylenia (°):", 0, 45, 20)
    
    # Przelicznik
    kat_rad = math.radians(kat_stopnie)
    kat_procent = math.tan(kat_rad) * 100
    
    # Wyświetlanie wyników
    col1, col2 = st.columns(2)
    col1.metric("Kąt", f"{kat_stopnie}°")
    col2.metric("Pochylenie", f"{kat_procent:.1f}%")
    
    st.info(f"Spadek: {math.tan(kat_rad):.2f} m na 1 m.")

# --- Główna część aplikacji ---
st.write("Witaj w inżynierskim kalkulatorze. Jeśli widzisz ten tekst, to znaczy, że moduł geometrii działa poprawnie.")

# Tu będziemy dodawać kolejne moduły (Materiały, Akcesoria itd.)


# --- 2. Zakładki ---
tab1, tab2, tab3, tab4 = st.tabs(["Konstrukcja", "Poszycia", "Akcesoria", "Kosztorys"])

with tab1:
    st.header("Konstrukcja")
    rodzaj_drewna = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])
    dlugosc_desek = st.number_input("Dostępne długości desek (m)", value=5.0)
    procent_odpadu = st.slider("Procent resztek/odpadu (%)", 0, 30, 15)

with tab2:
    st.header("Poszycie i Izolacja")
    st.checkbox("Poszycie wewnętrzne")
    # Tu później dodamy logikę wyboru z listy produktów

with tab3:
    st.header("Akcesoria i Łączniki")
    st.write("Wkręty Klimas, taśmy, kątowniki...")

with tab4:
    st.header("Analiza Kosztów")
    st.write("Tabela zbiorcza...")

# --- Logika obliczeniowa ---
# Tutaj będziemy "mielić" dane ze wszystkich zakładek
obw_scian = (szer + dlug) * 2
pow_scian = (obw_scian * wys) / 10000 
st.sidebar.write(f"Powierzchnia ścian: {pow_scian:.2f} m2")

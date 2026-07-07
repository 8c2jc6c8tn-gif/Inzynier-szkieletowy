import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych dynamicznych ---
if 'okna' not in st.session_state:
    st.session_state.okna = []

# --- Zakładki główne ---
tab_geo, tab_konstr, tab_posz, tab_akc, tab_koszt = st.tabs([
    "Geometria", "Konstrukcja", "Poszycia", "Akcesoria", "Kosztorys"
])

# --- 1. Zakładka: Geometria ---
with tab_geo:
    st.header("1. Parametry Geometrii")
    wys = st.slider("Wysokość (cm)", 200, 500, 250)
    szer = st.slider("Szerokość (cm)", 200, 1000, 600)
    dlug = st.slider("Długość (cm)", 200, 1500, 800)
    
    st.subheader("Dach")
    kat_stopnie = st.slider("Kąt nachylenia (°):", 0, 45, 20)
    
    # Przelicznik kątów
    kat_rad = math.radians(kat_stopnie)
    kat_procent = math.tan(kat_rad) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Kąt", f"{kat_stopnie}°")
    col2.metric("Pochylenie", f"{kat_procent:.1f}%")

# --- 2. Zakładka: Konstrukcja ---
with tab_konstr:
    st.header("Konstrukcja")
    rodzaj_drewna = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])
    dlugosc_desek = st.number_input("Dostępne długości desek (m)", value=5.0)
    procent_odpadu = st.slider("Procent resztek/odpadu (%)", 0, 30, 15)

# --- 3. Zakładka: Poszycia ---
with tab_posz:
    st.header("Poszycie i Izolacja")
    st.checkbox("Poszycie wewnętrzne")

# --- 4. Zakładka: Akcesoria ---
with tab_akc:
    st.header("Akcesoria i Łączniki")
    st.write("Wkręty Klimas, taśmy, kątowniki...")

# --- 5. Zakładka: Kosztorys ---
with tab_koszt:
    st.header("Analiza Kosztów")
    st.write("Tabela zbiorcza...")

# --- Pasek boczny (dane wyliczone) ---
with st.sidebar:
    st.header("Podsumowanie obliczeń")
    obw_scian = (szer + dlug) * 2
    pow_scian = (obw_scian * wys) / 10000 
    st.metric("Powierzchnia ścian", f"{pow_scian:.2f} m²")

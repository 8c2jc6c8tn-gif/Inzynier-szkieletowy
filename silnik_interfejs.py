import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych dynamicznych ---
if 'okna' not in st.session_state:
    st.session_state.okna = []

# --- Zakładki ---
tab_geo, tab_konstr, tab_posz, tab_akc, tab_koszt = st.tabs([
    "1. Geometria", "2. Konstrukcja", "3. Poszycia", "4. Akcesoria", "5. Kosztorys"
])

# --- MODUŁ 1: GEOMETRIA ---
with tab_geo:
    st.header("1. Parametry Geometrii")
    
    col_a, col_b = st.columns(2)
    with col_a:
        wys = st.number_input("Wysokość budynku (cm)", 200, 500, 250)
        szer = st.number_input("Szerokość budynku (cm)", 200, 1000, 600)
        dlug = st.number_input("Długość budynku (cm)", 200, 1500, 800)
    
    with col_b:
        st.subheader("Dach i okapy")
        kat_stopnie = st.slider("Kąt nachylenia (°):", 0, 45, 20)
        kat_rad = math.radians(kat_stopnie)
        kat_procent = math.tan(kat_rad) * 100
        
        c1, c2 = st.columns(2)
        c1.metric("Kąt", f"{kat_stopnie}°")
        c2.metric("Pochylenie", f"{kat_procent:.1f}%")
        
        okap_a = st.slider("Okap A (przód) [cm]", 0, 100, 20)
        okap_b = st.slider("Okap B (tył) [cm]", 0, 100, 20)
        okap_c = st.slider("Okap C (lewo) [cm]", 0, 100, 20)
        okap_d = st.slider("Okap D (prawo) [cm]", 0, 100, 20)

    st.subheader("Otwory (Okna i Drzwi)")
    if st.button("Dodaj nowy otwór"):
        st.session_state.okna.append({'szer': 90, 'wys': 120})
    
    suma_otworow = 0
    for i, okno in enumerate(st.session_state.okna):
        c1, c2, c3 = st.columns([2, 2, 1])
        okno['szer'] = c1.number_input(f"Szer. otworu {i+1} (cm)", value=okno['szer'], key=f"s_{i}")
        okno['wys'] = c2.number_input(f"Wys. otworu {i+1} (cm)", value=okno['wys'], key=f"w_{i}")
        suma_otworow += (okno['szer'] * okno['wys']) / 10000 
        if c3.button("Usuń", key=f"del_{i}"):
            st.session_state.okna.pop(i)
            st.rerun()

    obwod = (szer + dlug) * 2 / 100
    pow_scian_brutto = obwod * (wys / 100)
    pow_scian_netto = pow_scian_brutto - suma_otworow
    
    st.divider()
    st.metric("Powierzchnia ścian netto", f"{pow_scian_netto:.2f} m²")

# --- MODUŁ 2: KONSTRUKCJA ---
with tab_konstr:
    st.header("2. Konstrukcja")
    rodzaj_drewna = st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"], key="konstr_drewno")
    dlugosc_desek = st.number_input("Długość desek (m)", value=5.0, key="konstr_dlugosc")
    procent_odpadu = st.slider("Procent resztek/odpadu (%)", 0, 30, 15, key="konstr_odpad")

# --- MODUŁ 3: POSZYCIA ---
with tab_posz:
    st.header("3. Poszycie i Izolacja")
    st.checkbox("Poszycie wewnętrzne", key="posz_wew")

# --- MODUŁ 4: AKCESORIA ---
with tab_akc:
    st.header("4. Akcesoria i Łączniki")
    st.write("Wkręty Klimas, taśmy, kątowniki...")

# --- MODUŁ 5: KOSZTORYS ---
with tab_koszt:
    st.header("5. Analiza Kosztów")
    st.write("Tabela zbiorcza...")

# --- Pasek boczny ---
with st.sidebar:
    st.header("Podsumowanie")
    st.metric("Powierzchnia ścian", f"{pow_scian_netto:.2f} m²")

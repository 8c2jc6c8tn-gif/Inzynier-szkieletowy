import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych globalnych ---
if 'okna' not in st.session_state:
    st.session_state.okna = []
if 'geo' not in st.session_state:
    st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}

# --- Zakładki ---
tab_geo, tab_dach_konstr, tab_dach_wyk, tab_konstr_scian, tab_posz, tab_akc, tab_koszt = st.tabs([
    "1. Geometria", "2. Konstr. Dachu", "3. Wykończenie Dachu", "4. Konstr. Ścian", "5. Poszycia", "6. Akcesoria", "7. Kosztorys"
])

# --- MODUŁ 1: GEOMETRIA ---
with tab_geo:
    st.header("1. Wymiary Budynku")
    col1, col2 = st.columns(2)
    st.session_state.geo['wys'] = col1.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'])
    st.session_state.geo['szer'] = col1.number_input("Szerokość (cm)", 200, 1000, st.session_state.geo['szer'])
    st.session_state.geo['dlug'] = col1.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'])
    
    st.subheader("Otwory (Okna i Drzwi)")
    if st.button("Dodaj otwór", key="add_win"):
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

    pow_podlogi = (st.session_state.geo['szer'] * st.session_state.geo['dlug']) / 10000
    pow_scian_netto = (((st.session_state.geo['szer'] + st.session_state.geo['dlug']) * 2) * (st.session_state.geo['wys'] / 100)) - suma_otworow
    
    st.divider()
    st.metric("Powierzchnia podłogi", f"{pow_podlogi:.2f} m²")
    st.metric("Powierzchnia ścian netto", f"{pow_scian_netto:.2f} m²")

# --- MODUŁ 2: KONSTRUKCJA DACHU ---
with tab_dach_konstr:
    st.header("2. Konstrukcja Dachu")
    rozstaw = st.selectbox("Rozstaw belek (cm)", [30, 40, 60], key="d_rozstaw")
    kat = st.slider("Kąt nachylenia (°)", 0, 45, 20, key="d_kat")
    okap_a = st.slider("Okap przód/tył (cm)", 0, 100, 20, key="d_okap_a")
    okap_c = st.slider("Okap lewo/prawo (cm)", 0, 100, 20, key="d_okap_c")
    
    pow_dachu = (((st.session_state.geo['szer'] + 2*okap_c) * (st.session_state.geo['dlug'] + 2*okap_a)) / 10000) / math.cos(math.radians(kat))
    st.metric("Powierzchnia dachu", f"{pow_dachu:.2f} m²")

# --- MODUŁ 3: WYKOŃCZENIE DACHU ---
with tab_dach_wyk:
    st.header("3. Wykończenie Dachu")
    pokrycie = st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"], key="d_pokrycie")
    st.info(f"Wybrano: {pokrycie}. Logika materiałowa w budowie.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("Podsumowanie")
    st.metric("Ściany netto", f"{pow_scian_netto:.2f} m²")
    st.metric("Dach", f"{pow_dachu:.2f} m²")

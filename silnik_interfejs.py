import streamlit as st
import math

st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja ---
if 'okna' not in st.session_state:
    st.session_state.okna = []

# --- Zakładki ---
tab_geo, tab_dach_konstr, tab_dach_wyk, tab_konstr_scian, tab_posz, tab_akc, tab_koszt = st.tabs([
    "1. Geometria", "2. Konstr. Dachu", "3. Wykończenie Dachu", "4. Konstr. Ścian", "5. Poszycia", "6. Akcesoria", "7. Kosztorys"
])

# --- MODUŁ 1: GEOMETRIA ---
with tab_geo:
    st.header("1. Wymiary Budynku")
    col1, col2 = st.columns(2)
    wys = col1.number_input("Wysokość (cm)", 200, 500, 250, key="g_wys")
    szer = col1.number_input("Szerokość (cm)", 200, 1000, 600, key="g_szer")
    dlug = col1.number_input("Długość (cm)", 200, 1500, 800, key="g_dlug")
    
    # Obliczenia
    pow_podlogi = (szer * dlug) / 10000
    kubatura = pow_podlogi * (wys / 100)
    
    st.divider()
    st.metric("Powierzchnia podłogi", f"{pow_podlogi:.2f} m²")
    st.metric("Kubatura", f"{kubatura:.2f} m³")

# --- MODUŁ 2: KONSTRUKCJA DACHU ---
with tab_dach_konstr:
    st.header("2. Konstrukcja Dachu")
    rozstaw = st.selectbox("Rozstaw belek (cm)", [30, 40, 60], key="d_rozstaw")
    kat = st.slider("Kąt nachylenia (°)", 0, 45, 20, key="d_kat")
    okap_a = st.slider("Okap przód/tył (cm)", 0, 100, 20, key="d_okap_a")
    okap_c = st.slider("Okap lewo/prawo (cm)", 0, 100, 20, key="d_okap_c")
    
    # Powierzchnia dachu
    pow_dachu = ((szer + 2*okap_c) * (dlug + 2*okap_a) / 10000) / math.cos(math.radians(kat))
    st.metric("Powierzchnia dachu", f"{pow_dachu:.2f} m²")

# --- MODUŁ 3: WYKOŃCZENIE DACHU ---
with tab_dach_wyk:
    st.header("3. Wykończenie Dachu")
    pokrycie = st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"], key="d_pokrycie")
    st.info(f"Wybrano: {pokrycie}. Logika materiałowa w budowie.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("Podsumowanie ogólne")
    st.write("Wymiary budynku i dachu pobierane z zakładek.")
    # Usunąłem tutaj odwołanie do zmiennych lokalnych, które powodowały błąd NameError

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

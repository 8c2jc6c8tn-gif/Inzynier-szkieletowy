import streamlit as st

# Konfiguracja strony
st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych (Session State) ---
# Używamy jednego słownika 'data' dla wszystkich wartości, co jest najbezpieczniejszą formą
if 'data' not in st.session_state:
    st.session_state.data = {
        'geo': {'wys': 250, 'szer': 600, 'dlug': 800},
        'konstrukcja': {'slupki': "95x45", 'rozstaw': 60},
        'dach': {'kat': 20, 'pokrycie': "Papa"}
    }

# --- Definicja zakładek ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Geometria", 
    "2. Konstr. Dachu", 
    "3. Wykończenie Dachu", 
    "4. Konstr. Ścian", 
    "5. Wykończenie Ścian", 
    "6. Akcesoria", 
    "7. Kosztorys"
])

# --- MODUŁ 1: GEOMETRIA ---
with tab1:
    st.header("1. Geometria Budynku")
    st.session_state.data['geo']['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.data['geo']['wys'], key="geo_wys")
    st.session_state.geo['szer'] = st.number_input("Szerokość (cm)", 200, 1000, st.session_state.data['geo']['szer'], key="geo_szer")
    st.session_state.geo['dlug'] = st.number_input("Długość (cm)", 200, 1500, st.session_state.data['geo']['dlug'], key="geo_dlug")

# --- MODUŁ 4: KONSTRUKCJA ŚCIAN ---
with tab4:
    st.header("4. Konstrukcja Ścian")
    # Teraz ten Selectbox ma swój unikalny klucz i nie przeładuje całej strony
    st.session_state.data['konstrukcja']['slupki'] = st.selectbox(
        "Przekrój słupków", 
        ["95x45", "145x45", "195x45"], 
        key="slupki_select"
    )
    st.write(f"Wybrany przekrój: {st.session_state.data['konstrukcja']['slupki']}")

# --- Reszta zakładek (puste kontenery dla stabilności) ---
with tab2: st.header("2. Konstrukcja Dachu")
with tab3: st.header("3. Wykończenie Dachu")
with tab5: st.header("5. Wykończenie Ścian")
with tab6: st.header("6. Akcesoria")
with tab7: st.header("7. Kosztorys")

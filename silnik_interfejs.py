import streamlit as st

st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja danych dynamicznych ---
if 'okna' not in st.session_state:
    st.session_state.okna = []

# --- 1. Moduł: Geometria ---
with st.sidebar:
    st.header("1. Geometria")
    wys = st.slider("Wysokość (cm)", 200, 500, 250)
    szer = st.slider("Szerokość (cm)", 200, 1000, 600)
    dlug = st.slider("Długość (cm)", 200, 1500, 800)
    
    st.subheader("Otwory")
    if st.button("Dodaj okno"):
        st.session_state.okna.append({'szer': 100, 'wys': 100})
    
    for i, okno in enumerate(st.session_state.okna):
        col1, col2 = st.columns(2)
        okno['szer'] = col1.number_input(f"Szer. okna {i+1}", value=okno['szer'])
        okno['wys'] = col2.number_input(f"Wys. okna {i+1}", value=okno['wys'])

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

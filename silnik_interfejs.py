import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# 1. Inicjalizacja danych - zawsze na początku
if 'geo' not in st.session_state:
    st.session_state.geo = {'wys': 250, 'szer': 600, 'dlug': 800}

# 2. Definicja zakładek - to jest "pancerna" struktura Streamlit
tabs = st.tabs([
    "1. Geometria", 
    "2. Konstr. Dachu", 
    "3. Wykończenie Dachu", 
    "4. Konstr. Ścian", 
    "5. Wykończenie Ścian", 
    "6. Akcesoria", 
    "7. Kosztorys"
])

# 3. Treść poszczególnych zakładek
with tabs[0]:
    st.header("1. Geometria Budynku")
    st.session_state.geo['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.geo['wys'])
    st.session_state.geo['szer'] = st.number_input("Szerokość (cm)", 200, 1000, st.session_state.geo['szer'])
    st.session_state.geo['dlug'] = st.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'])

with tabs[1]:
    st.header("2. Konstrukcja Dachu")
    st.selectbox("Rozstaw belek (cm)", [30, 40, 60])
    st.slider("Kąt nachylenia (°)", 0, 45, 20)

with tabs[2]:
    st.header("3. Wykończenie Dachu")
    st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"])

with tabs[3]:
    st.header("4. Konstrukcja Ścian")
    st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])

with tabs[4]:
    st.header("5. Wykończenie Ścian")
    st.write("Ustawienia płyt OSB i folii.")

with tabs[5]:
    st.header("6. Akcesoria")
    st.write("Wkręty, taśmy, łączniki.")

with tabs[6]:
    st.header("7. Analiza Kosztów")
    st.write("Tabela zbiorcza.")

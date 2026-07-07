import streamlit as st
import math

# --- Konfiguracja strony ---
st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- 1. INICJALIZACJA DANYCH (To chroni przed resetowaniem i błędami) ---
if 'wys' not in st.session_state: st.session_state.wys = 250
if 'szer' not in st.session_state: st.session_state.szer = 600
if 'dlug' not in st.session_state: st.session_state.dlug = 800

if 'rozstaw' not in st.session_state: st.session_state.rozstaw = 60
if 'kat' not in st.session_state: st.session_state.kat = 20
if 'okap_przod' not in st.session_state: st.session_state.okap_przod = 20
if 'okap_tyl' not in st.session_state: st.session_state.okap_tyl = 20
if 'okap_lewo' not in st.session_state: st.session_state.okap_lewo = 20
if 'okap_prawo' not in st.session_state: st.session_state.okap_prawo = 20

if 'slupki' not in st.session_state: st.session_state.slupki = "145x45"
if 'pokrycie' not in st.session_state: st.session_state.pokrycie = "Papa"

# --- 2. NAWIGACJA (Pionowe menu, które nigdy nie wyjdzie poza ekran) ---
menu = [
    "1. Geometria budynku",
    "2. Konstrukcja dachu",
    "3. Wykończenie dachu",
    "4. Konstrukcja ścian",
    "5. Wykończenie ścian",
    "6. Akcesoria",
    "7. Kosztorys"
]
wybor = st.sidebar.radio("Menu projektu:", menu)
st.divider()

# --- 3. GLOBALNE OBLICZENIA (Przeliczane na bieżąco dla każdej zakładki) ---
pow_podlogi = (st.session_state.szer * st.session_state.dlug) / 10000
kubatura = pow_podlogi * (st.session_state.wys / 100)

# Obliczenie powierzchni dachu z uwzględnieniem 4 okapów i kąta nachylenia
szer_z_okapami = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
dlug_z_okapami = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
pow_rzutu_dachu = (szer_z_okapami * dlug_z_okapami) / 10000
pow_dachu = pow_rzutu_dachu / math.cos(math.radians(st.session_state.kat))

# --- 4. LOGIKA POSZCZEGÓLNYCH ROZDZIAŁÓW ---

# --- ROZDZIAŁ 1: GEOMETRIA ---
if wybor == "1. Geometria budynku":
    st.header("🏠 1. Geometria budynku")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Wysokość budynku (cm)", 200, 500, key="wys")
        st.number_input("Szerokość budynku (cm)", 200, 1000, key="szer")
        st.number_input("Długość budynku (cm)", 200, 1500, key="dlug")
    with col2:
        st.subheader("Wyniki obliczeń")
        st.metric("Powierzchnia po podłodze", f"{pow_podlogi:.2f} m²")
        st.metric("Kubatura przestrzeni", f"{kubatura:.2f} m³")

# --- ROZDZIAŁ 2: KONSTRUKCJA DACHU ---
elif wybor == "2. Konstrukcja dachu":
    st.header("📐 2. Konstrukcja dachu")
    
    st.subheader("Rozstaw belek")
    st.selectbox("Wybierz rozstaw (cm)", [30, 40, 60], key="rozstaw")
    
    st.subheader("Pochylenie i okapy")
    st.slider("Kąt nachylenia dachu (°)", 0, 45, key="kat")
    
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Okap przód (cm)", 0, 100, key="okap_przod")
        st.slider("Okap tył (cm)", 0, 100, key="okap_tyl")
    with c2:
        st.slider("Okap lewo (cm)", 0, 100, key="okap_lewo")
        st.slider("Okap prawo (cm)", 0, 100, key="okap_prawo")
        
    st.divider()
    st.subheader("Podsumowanie dachu")
    st.metric("Ogólna powierzchnia dachu", f"{pow_dachu:.2f} m²")

# --- ROZDZIAŁ 3: WYKOŃCZENIE DACHU ---
elif wybor == "3. Wykończenie dachu":
    st.header("🎨 3. Wykończenie dachu")
    st.selectbox("Wybierz rozwiązanie", ["Papa", "Blachodachówka", "EPDM"], key="pokrycie")
    st.write(f"Wybrane wykończenie: **{st.session_state.pokrycie}**")
    st.metric("Wymagana powierzchnia materiału", f"{pow_dachu:.2f} m²")

# --- ROZDZIAŁ 4: KONSTRUKCJA ŚCIAN ---
elif wybor == "4. Konstrukcja ścian":
    st.header("🏗️ 4. Konstrukcja ścian")
    st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"], key="slupki")
    st.write(f"Aktualny przekrój konstrukcyjny: **{st.session_state.slupki}**")

# --- ROZDZIAŁ 5: WYKOŃCZENIE ŚCIAN ---
elif wybor == "5. Wykończenie ścian":
    st.header("🧱 5. Wykończenie ścian")
    st.write("Tu wdrożymy poszycia zewnętrzne i wewnętrzne (OSB, GK, izolacje).")

# --- ROZDZIAŁ 6: AKCESORIA ---
elif wybor == "6. Akcesoria":
    st.header("🔩 6. Akcesoria i Łączniki")
    st.write("Miejsce na wkręty, taśmy i łączniki ciesielskie.")

# --- ROZDZIAŁ 7: KOSZTORYS ---
elif wybor == "7. Kosztorys":
    st.header("📊 7. Analiza Kosztów")
    st.write("Tabela zbiorcza spajająca wydatki ze wszystkich modułów.")

# --- BOCZNY PANEL (Szybki podgląd pod menu) ---
st.sidebar.markdown("---")
st.sidebar.subheader("Szybki podgląd")
st.sidebar.metric("Podłoga", f"{pow_podlogi:.2f} m²")
st.sidebar.metric("Dach całkowity", f"{pow_dachu:.2f} m²")

import streamlit as st

st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- Inicjalizacja stanu ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'geo': {'wys': 250, 'szer': 600, 'dlug': 800},
        'konstrukcja': {'slupki': "95x45"},
        'dach': {'kat': 20}
    }

# --- Pasek boczny jako Menu (Nigdy nie wyjdzie poza ekran) ---
with st.sidebar:
    st.header("Nawigacja")
    menu_wybor = st.radio(
        "Wybierz moduł:",
        ["Geometria", "Konstr. Dachu", "Wykończenie Dachu", "Konstr. Ścian", "Wykończenie Ścian", "Akcesoria", "Kosztorys"]
    )

# --- LOGIKA MODUŁÓW (Wszystko w głównym oknie) ---
if menu_wybor == "Geometria":
    st.header("1. Geometria Budynku")
    st.session_state.data['geo']['wys'] = st.number_input("Wysokość (cm)", 200, 500, st.session_state.data['geo']['wys'], key="g_wys")
    st.session_state.data['geo']['szer'] = st.number_input("Szerokość (cm)", 200, 1000, st.session_state.data['geo']['szer'], key="g_szer")
    st.session_state.data['geo']['dlug'] = st.number_input("Długość (cm)", 200, 1500, st.session_state.geo['dlug'], key="g_dlug")

elif menu_wybor == "Konstr. Dachu":
    st.header("2. Konstrukcja Dachu")
    st.slider("Kąt nachylenia (°)", 0, 45, 20, key="d_kat")

elif menu_wybor == "Wykończenie Dachu":
    st.header("3. Wykończenie Dachu")
    st.selectbox("Wybierz pokrycie", ["Papa", "Blachodachówka", "EPDM"], key="d_pokrycie")

elif menu_wybor == "Konstr. Ścian":
    st.header("4. Konstrukcja Ścian")
    st.session_state.data['konstrukcja']['slupki'] = st.selectbox(
        "Przekrój słupków", ["95x45", "145x45", "195x45"], key="s_slupki"
    )

elif menu_wybor == "Wykończenie Ścian":
    st.header("5. Wykończenie Ścian")
    st.write("Ustawienia płyt OSB i fasady.")

elif menu_wybor == "Akcesoria":
    st.header("6. Akcesoria i Łączniki")

elif menu_wybor == "Kosztorys":
    st.header("7. Analiza Kosztów")
    st.write("Tabela zbiorcza.")

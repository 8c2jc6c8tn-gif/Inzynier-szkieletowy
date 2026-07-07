import streamlit as st

# Podstawowa konfiguracja
st.set_page_config(layout="wide")
st.title("Inżynier Szkieletowy - Modułowy Pro")

# --- NAWIGACJA (Sidebar) ---
st.sidebar.header("Nawigacja")
menu = st.sidebar.radio(
    "Wybierz sekcję:",
    ["Geometria", "Konstr. Dachu", "Wykończenie Dachu", "Konstr. Ścian", "Wykończenie Ścian", "Akcesoria", "Kosztorys"]
)

# --- LOGIKA MODUŁÓW ---
if menu == "Geometria":
    st.header("1. Geometria")
    st.number_input("Wysokość (cm)", 200, 500, 250)
    st.number_input("Szerokość (cm)", 200, 1000, 600)
    st.number_input("Długość (cm)", 200, 1500, 800)

elif menu == "Konstr. Dachu":
    st.header("2. Konstrukcja Dachu")
    st.write("W trakcie prac...")

elif menu == "Wykończenie Dachu":
    st.header("3. Wykończenie Dachu")
    st.write("W trakcie prac...")

elif menu == "Konstr. Ścian":
    st.header("4. Konstrukcja Ścian")
    st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"])

elif menu == "Wykończenie Ścian":
    st.header("5. Wykończenie Ścian")
    st.write("W trakcie prac...")

elif menu == "Akcesoria":
    st.header("6. Akcesoria")
    st.write("W trakcie prac...")

elif menu == "Kosztorys":
    st.header("7. Kosztorys")
    st.write("W trakcie prac...")

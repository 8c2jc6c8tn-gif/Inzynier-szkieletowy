import streamlit as st

st.title("Inżynier Szkieletowy - Prototyp v1.0")

# 1. Zakładki dla rozdziałów
tab_projekt, tab_sciany, tab_podloga, tab_dach = st.tabs(["Projekt", "Ściany", "Podłoga", "Dach"])

# Inicjalizacja słownika wyników
if 'koszty' not in st.session_state:
    st.session_state.koszty = {"Ściany": 0.0, "Podłoga": 0.0, "Dach": 0.0}

with tab_projekt:
    st.header("Parametry ogólne budynku")
    szerokosc = st.number_input("Szerokość (m)", value=6.0)
    dlugosc = st.number_input("Długość (m)", value=8.0)

with tab_sciany:
    st.header("Moduł: Ściany")
    sciana_A = st.number_input("Powierzchnia Ściany A (m2)", value=15.0)
    sciana_B = st.number_input("Powierzchnia Ściany B (m2)", value=15.0)
    # Symulacja obliczeń
    st.session_state.koszty["Ściany"] = (sciana_A + sciana_B) * 50  # Przykładowy przelicznik

with tab_podloga:
    st.header("Moduł: Podłoga")
    pow_p = st.number_input("Powierzchnia podłogi (m2)", value=szerokosc * dlugosc)
    st.session_state.koszty["Podłoga"] = pow_p * 40

with tab_dach:
    st.header("Moduł: Dach")
    st.write("Logika dachu w trakcie implementacji...")
    st.session_state.koszty["Dach"] = 2000.0

# 3. Podsumowanie (zawsze widoczne)
st.divider()
st.subheader("Podsumowanie projektu")
suma = sum(st.session_state.koszty.values())
st.metric("Łączny szacunkowy koszt", f"{suma:,.2f} PLN")
st.write("Rozbicie kosztów:", st.session_state.koszty)


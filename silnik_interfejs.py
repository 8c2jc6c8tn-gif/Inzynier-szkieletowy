import streamlit as st
import json

# 1. Wczytanie stałych (Standardy)
# W rzeczywistym środowisku upewnij się, że plik stale.json jest w tym samym folderze
try:
    with open('stale.json', 'r') as f:
        stale = json.load(f)
except:
    # Wartości domyślne na wypadek braku pliku
    stale = {"standardy": {"rozstaw_belek": 0.6}, "ceny": {"drewno_mb": 5.5}}

st.title("🏗️ Inżynier Szkieletowy v1.0")

# 2. Interfejs użytkownika (Wprowadzanie zmiennych)
st.sidebar.header("Parametry projektu")
dlugosc = st.sidebar.number_input("Długość ściany (m)", 1.0, 20.0, 5.0)
wysokosc = st.sidebar.number_input("Wysokość ściany (m)", 2.0, 5.0, 2.7)
liczba_drzwi = st.sidebar.number_input("Liczba otworów drzwiowych", 0, 5, 0)

# 3. Silnik obliczeniowy
if st.button("Oblicz materiał"):
    rozstaw = stale['standardy']['rozstaw_belek']
    slupki = int(dlugosc / rozstaw) + 1 - liczba_drzwi # proste odejmowanie za otwory
    
    st.success(f"Wynik dla ściany {dlugosc}m x {wysokosc}m:")
    
    # Prezentacja danych
    st.write(f"### Potrzebna ilość słupków: {slupki} szt.")
    st.write(f"### Łącznie drewna (mb): {round(slupki * wysokosc, 2)} mb")
    
    # Możliwość podejrzenia używanych stałych
    with st.expander("Zobacz użyte standardy"):
        st.json(stale)

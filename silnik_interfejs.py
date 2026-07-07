import streamlit as st
import math

st.title("Kalkulator Dachu Jednospadowego")

# Dane wejściowe
szerokosc = st.number_input("Szerokość budynku (m):", min_value=1.0, value=6.0)
kat = st.slider("Kąt nachylenia dachu (°):", min_value=5, max_value=45, value=20)
okap = st.number_input("Wysięg okapu (m):", min_value=0.0, value=0.5)

# Konwersja kąta na radiany
kat_rad = math.radians(kat)

# Obliczenia
dlugosc_krokwi = szerokosc / math.cos(kat_rad)
dlugosc_okapu = okap / math.cos(kat_rad)
calkowita_dlugosc = dlugosc_krokwi + dlugosc_okapu
wysokosc_roznica = szerokosc * math.tan(kat_rad)

# Wyniki
st.subheader("Wyniki obliczeń:")
st.write(f"Długość samej krokwi: {dlugosc_krokwi:.2f} m")
st.write(f"Długość okapu: {dlugosc_okapu:.2f} m")
st.write(f"**Całkowita długość krokwi: {calkowita_dlugosc:.2f} m**")
st.write(f"Różnica wysokości (spadek): {wysokosc_roznica:.2f} m")

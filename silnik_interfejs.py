import streamlit as st
import math

st.title("Inżynier Szkieletowy - Kalkulator")

# --- 1-4. Parametry geometryczne ---
st.header("1. Wymiary budynku i dachu")
szerokosc = st.number_input("Szerokość budynku (m):", value=6.0)
dlugosc = st.number_input("Długość budynku (m):", value=8.0)
wysokosc = st.number_input("Wysokość ściany (m):", value=2.5)
kat = st.slider("Kąt nachylenia dachu (°):", 0, 45, 20)

st.subheader("Okapy (m)")
col1, col2 = st.columns(2)
okap_A = col1.number_input("Okap A (przód)", value=0.5)
okap_B = col2.number_input("Okap B (tył)", value=0.5)
okap_C = col1.number_input("Okap C (lewo)", value=0.3)
okap_D = col2.number_input("Okap D (prawo)", value=0.3)

# --- 6. Drzwi ---
st.header("2. Otwory")
drzwi_wys = st.number_input("Wysokość drzwi (m):", value=2.0)
drzwi_szer = st.number_input("Szerokość drzwi (m):", value=0.9)

# --- 7-9. Materiały ---
st.header("3. Materiały i podłoga")
grubosc_osb = st.selectbox("Grubość OSB-3 (mm):", [12, 15, 18, 22])
ocieplenie_gr = st.number_input("Grubość ocieplenia (cm):", value=15.0)
podloga_podwojna = st.checkbox("Podwójna podłoga")

# --- Ceny ---
st.header("4. Ceny jednostkowe")
cena_osb = st.number_input("Cena OSB za m2:", value=30.0)
cena_ocieplenia = st.number_input("Cena ocieplenia za m2:", value=20.0)
cena_drewna = st.number_input("Cena drewna za m3:", value=1200.0)

# --- OBLICZENIA ---
pow_scian = (2 * (szerokosc + dlugosc) * wysokosc) - (drzwi_wys * drzwi_szer)
pow_podlogi = szerokosc * dlugosc * (2 if podloga_podwojna else 1)
pow_dachu = (szerokosc + okap_C + okap_D) * (dlugosc + okap_A + okap_B) / math.cos(math.radians(kat))

koszt_osb = pow_scian * cena_osb
koszt_ocieplenia = pow_scian * cena_ocieplenia
# Uproszczone założenie dla drewna (kubatura konstrukcji)
kubatura_drewna = (pow_scian * 0.05) + (pow_dachu * 0.1) 
koszt_drewna = kubatura_drewna * cena_drewna

# --- WYNIKI ---
st.divider()
st.subheader("Podsumowanie kosztów:")
st.write(f"Koszt OSB: {koszt_osb:.2f} PLN")
st.write(f"Koszt ocieplenia: {koszt_ocieplenia:.2f} PLN")
st.write(f"Koszt drewna: {koszt_drewna:.2f} PLN")
st.success(f"**Łącznie szacunkowo: {koszt_osb + koszt_ocieplenia + koszt_drewna:.2f} PLN**")

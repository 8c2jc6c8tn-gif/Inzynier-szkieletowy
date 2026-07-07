import streamlit as st
import math

st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy Pro")

# ---------- INICJALIZACJA STANU ----------
def init_state():
    defaults = {
        'wys': 250, 'szer': 600, 'dlug': 800,
        'rozstaw': 60, 'kat': 20,
        'okap_przod': 20, 'okap_tyl': 20, 'okap_lewo': 20, 'okap_prawo': 20,
        'slupki': "145x45", 'pokrycie': "Papa",
        'otwory': [], 'dlugosc_desek': 600,  # cm
        'osb_zew': 12, 'osb_wew': 0, 'gk_wew': 12.5,
        'ocieplenie_dach': 15, 'podloga_podwojna': False,
        'ceny_uzytkownika': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ---------- FUNKCJE OBLICZENIOWE ----------
def pow_scian_brutto():
    return 2 * (st.session_state.szer + st.session_state.dlug) * st.session_state.wys / 1e6

def pow_otworow():
    return sum(o['szer'] * o['wys'] for o in st.session_state.otwory) / 1e6

def pow_scian_netto():
    return max(0, pow_scian_brutto() - pow_otworow())

def obwod_scian():
    return 2 * (st.session_state.szer + st.session_state.dlug) / 100

def liczba_slupkow():
    obwod = obwod_scian()
    rozstaw = st.session_state.rozstaw / 100
    # Podstawowa ilość słupków w rastrze + narożniki + otwory
    n = math.ceil(obwod / rozstaw) + 4  # +4 na narożniki
    for o in st.session_state.otwory:
        n += 2  # słupki przy otworach
    return n

def dlugosc_listwy():
    # Całkowita długość słupków (każdy na wysokość ściany)
    return liczba_slupkow() * st.session_state.wys / 100

def ile_desek(dlugosc_calkowita, dlugosc_handlowa):
    return math.ceil(dlugosc_calkowita / (dlugosc_handlowa / 100))

def pow_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    rzut = (szer * dlug) / 1e4
    return rzut / math.cos(math.radians(st.session_state.kat))

# ---------- INTERFEJS ----------
st.title("🏗️ Inżynier Szkieletowy - Modułowy Pro")
menu = ["1. Geometria", "2. Konstrukcja ścian", "3. Poszycia i izolacje", "4. Dach", "5. Akcesoria", "6. Kosztorys"]
wybor = st.sidebar.radio("Menu", menu)
st.divider()

# ==================== 1. GEOMETRIA ====================
if wybor == "1. Geometria":
    st.header("📐 Geometria budynku i otwory")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Wysokość (cm)", 200, 600, key='wys')
        st.number_input("Szerokość (cm)", 200, 1500, key='szer')
        st.number_input("Długość (cm)", 200, 2000, key='dlug')
        st.number_input("Długość handlowa desek (cm)", 200, 1200, key='dlugosc_desek')
    with c2:
        st.subheader("Wyniki")
        st.metric("Pow. podłogi", f"{st.session_state.szer * st.session_state.dlug / 1e4:.2f} m²")
        st.metric("Pow. ścian brutto", f"{pow_scian_brutto():.2f} m²")
        st.metric("Pow. otworów", f"{pow_otworow():.2f} m²")
        st.metric("Pow. ścian netto", f"{pow_scian_netto():.2f} m²")

    st.divider()
    st.subheader("🚪 Otwory (drzwi i okna)")
    for i, o in enumerate(st.session_state.otwory):
        cols = st.columns([2,2,2,1])
        cols[0].text_input("Nazwa", o.get('nazwa',''), key=f"nazwa_{i}")
        cols[1].number_input("Szer (cm)", 30, 500, o['szer'], key=f"szer_{i}")
        cols[2].number_input("Wys (cm)", 30, 500, o['wys'], key=f"wys_{i}")
        if cols[3].button("❌", key=f"del_{i}"):
            st.session_state.otwory.pop(i)
            st.rerun()

    if st.button("➕ Dodaj otwór"):
        st.session_state.otwory.append({'nazwa': 'Okno', 'szer': 100, 'wys': 120})
        st.rerun()

# ==================== 2. KONSTRUKCJA ŚCIAN ====================
elif wybor == "2. Konstrukcja ścian":
    st.header("🪵 Konstrukcja ścian")
    st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"], key='slupki')
    st.selectbox("Rozstaw słupków (cm)", [30, 40, 60], key='rozstaw')

    obwod = obwod_scian()
    n = liczba_slupkow()
    dl_calk = dlugosc_listwy()
    dl_handl = st.session_state.dlugosc_desek / 100
    sztuk = ile_desek(dl_calk, st.session_state.dlugosc_desek)
    resztki = (sztuk * dl_handl - dl_calk) / (sztuk * dl_handl) * 100 if sztuk > 0 else 0

    st.divider()
    st.subheader("Zapotrzebowanie na drewno")
    c1, c2, c3 = st.columns(3)
    c1.metric("Liczba słupków", n)
    c2.metric("Całkowita długość", f"{dl_calk:.2f} m")
    c3.metric(f"Desek {st.session_state.dlugosc_desek} cm", sztuk)
    st.metric("Procent resztek", f"{resztki:.1f} %")

# ==================== 3. POSZYCIA I IZOLACJE ====================
elif wybor == "3. Poszycia i izolacje":
    st.header("🧱 Poszycia i izolacje")
    st.subheader("Poszycie zewnętrzne")
    st.number_input("Grubość OSB-3 zewn. (mm)", 8, 25, key='osb_zew')
    # Wiatroizolacja
    wiatro_opcje = {"Membrana Standard 120g": 120, "Membrana Premium 160g": 160, "Folia wiatrochronna 100g": 100}
    wybor_wiatro = st.selectbox("Wiatroizolacja", list(wiatro_opcje.keys()), key='wiatro')
    pow_zapas = pow_scian_netto() * 1.1  # 10% zapasu
    st.write(f"Potrzebna powierzchnia: {pow_zapas:.2f} m² (z zapasem 10%)")

    st.subheader("Poszycie wewnętrzne (opcjonalne)")
    if st.checkbox("Dodaj poszycie wewnętrzne", key='posz_wew'):
        st.number_input("Płyta GK (mm)", 6, 25, key='gk_wew')
        st.number_input("OSB-3 wewn. (mm, 0=pomiń)", 0, 25, key='osb_wew')
        st.checkbox("Paroizolacja", True, key='paro')
    st.subheader("Izolacja termiczna")
    st.number_input("Grubość ocieplenia dachu (cm)", 5, 30, key='ocieplenie_dach')
    st.checkbox("Podwójna podłoga (całoroczna)", key='podloga_podwojna')

# ==================== 4. DACH ====================
elif wybor == "4. Dach":
    st.header("📐 Dach")
    st.slider("Kąt nachylenia (°)", 0, 45, key='kat')
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Okap przód (cm)", 0, 100, key='okap_przod')
        st.slider("Okap lewo (cm)", 0, 100, key='okap_lewo')
    with c2:
        st.slider("Okap tył (cm)", 0, 100, key='okap_tyl')
        st.slider("Okap prawo (cm)", 0, 100, key='okap_prawo')
    st.selectbox("Pokrycie", ["Papa", "Blachodachówka", "EPDM"], key='pokrycie')
    st.metric("Powierzchnia dachu", f"{pow_dachu():.2f} m²")

# ==================== 5. AKCESORIA ====================
elif wybor == "5. Akcesoria":
    st.header("🔩 Akcesoria")
    st.subheader("Wkręty")
    # Założenie: wkręty co 15 cm na obwodzie płyty + co 30 cm w środku
    pow_osb = pow_scian_netto()  # uproszczenie
    wkrety_na_m2 = 25  # szt./m²
    wkrety = math.ceil(pow_osb * wkrety_na_m2 * 1.15)
    opakowania = math.ceil(wkrety / 200)  # 200 szt. w opakowaniu
    st.write(f"**Wkręty do OSB (Klimas)**: {wkrety} szt. (z zapasem 15%) → **{opakowania}** opakowań")

    st.subheader("Taśmy")
    # Do wiatroizolacji i paroizolacji
    mb_tasm = obwod_scian() * 2  # okna, drzwi, łączenia - uproszczenie
    st.metric("Taśma do folii (mb)", f"{mb_tasm:.1f} m")

    st.subheader("Łączniki ciesielskie")
    katowniki = liczba_slupkow() * 2  # góra i dół
    st.metric("Kątowniki (szt.)", katowniki)

# ==================== 6. KOSZTORYS ====================
elif wybor == "6. Kosztorys":
    st.header("📊 Kosztorys")
    # Ceny domyślne (możesz je zmienić)
    CENY = {
        'Drewno 95x45': 12.0, 'Drewno 145x45': 18.0, 'Drewno 195x45': 24.0,  # zł/mb
        'OSB-3': 18.0, 'GK': 15.0,  # zł/m²
        'Wiatroizolacja': 8.0, 'Paroizolacja': 5.0,  # zł/m²
        'Ocieplenie dach': 40.0,  # zł/m²
        'Wkręty opak.': 35.0, 'Taśma rolka': 25.0, 'Kątownik': 3.5,
        'Pokrycie Papa': 25.0, 'Pokrycie Blacha': 45.0, 'Pokrycie EPDM': 70.0
    }

    # Obliczenia ilości
    dlugosc_mb = dlugosc_listwy()
    deski = ile_desek(dlugosc_mb, st.session_state.dlugosc_desek)
    pow_netto = pow_scian_netto()
    opak_wkrety = math.ceil(pow_netto * 25 * 1.15 / 200)

    kosztorys = [
        ("Drewno konstrukcyjne", f"{deski} szt. (mb: {dlugosc_mb:.1f})", dlugosc_mb * CENY[f"Drewno {st.session_state.slupki}"]),
        ("OSB-3 zewnętrzne", f"{pow_netto:.1f} m²", pow_netto * CENY['OSB-3']),
        ("Wiatroizolacja", f"{pow_netto*1.1:.1f} m²", pow_netto*1.1 * CENY['Wiatroizolacja']),
        ("Wkręty (opakowania)", f"{opak_wkrety} op.", opak_wkrety * CENY['Wkręty opak.']),
        ("Pokrycie dachowe", f"{pow_dachu():.1f} m²", pow_dachu() * CENY[f"Pokrycie {st.session_state.pokrycie}"]),
    ]

    suma = 0
    for nazwa, ilosc, koszt in kosztorys:
        c1, c2, c3 = st.columns([3,2,1])
        c1.write(nazwa)
        c2.write(ilosc)
        c3.write(f"{koszt:.2f} zł")
        suma += koszt
    st.divider()
    st.subheader(f"Suma całkowita: **{suma:.2f} zł**")
    st.caption("Dodaj własne ceny w sekcji '6. Kosztorys' w kodzie (słownik CENY).")
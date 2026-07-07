import streamlit as st
import math
import uuid

st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy Pro")

# ---------- INICJALIZACJA STANU ----------
def init_state():
    defaults = {
        'wys': 250, 'szer': 600, 'dlug': 800,
        'rozstaw': 60, 'kat': 20,
        'okap_przod': 20, 'okap_tyl': 20, 'okap_lewo': 20, 'okap_prawo': 20,
        'slupki': "145x45", 'pokrycie': "Papa",
        'otwory': [], 'dlugosc_desek': 600,
        'osb_zew': 12, 'osb_wew': 0, 'gk_wew': 12.5,
        'ocieplenie_dach': 15, 'podloga_podwojna': False,
        'active_tab': 'Geometria'  # domyślnie wybrana zakładka
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # uzupełnij identyfikatory w otworach
    for o in st.session_state.otwory:
        if 'id' not in o:
            o['id'] = str(uuid.uuid4())

init_state()

# ---------- POPRAWIONE FUNKCJE OBLICZENIOWE ----------
def pow_podlogi():
    return st.session_state.szer * st.session_state.dlug / 10_000

def kubatura():
    return pow_podlogi() * st.session_state.wys / 100

def pow_scian_brutto():
    obwod = 2 * (st.session_state.szer + st.session_state.dlug)
    pole_cm2 = obwod * st.session_state.wys
    return pole_cm2 / 10_000

def pow_otworow():
    suma_cm2 = sum(o.get('szer', 0) * o.get('wys', 0) for o in st.session_state.otwory)
    return suma_cm2 / 10_000

def pow_scian_netto():
    return max(0.0, pow_scian_brutto() - pow_otworow())

def obwod_scian():
    return 2 * (st.session_state.szer + st.session_state.dlug) / 100

def liczba_slupkow():
    obwod = obwod_scian()
    rozstaw_m = st.session_state.rozstaw / 100
    n = math.ceil(obwod / rozstaw_m) + 4
    for _ in st.session_state.otwory:
        n += 2
    return max(n, 4)

def dlugosc_listwy():
    return liczba_slupkow() * st.session_state.wys / 100

def ile_desek(dlugosc_calkowita_m, dlugosc_handlowa_cm):
    dl_handl_m = dlugosc_handlowa_cm / 100
    return math.ceil(dlugosc_calkowita_m / dl_handl_m)

def pow_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    rzut_m2 = (szer * dlug) / 10_000
    return rzut_m2 / math.cos(math.radians(st.session_state.kat))

# ---------- MENU JAKO POZIOMY RADIO ----------
st.title("🏗️ Inżynier Szkieletowy Pro")
st.caption("Wszystkie dane są współdzielone. Wybierz moduł poniżej.")

zakladki = ["Geometria", "Konstrukcja ścian", "Poszycia i izolacje", "Dach", "Podłoga", "Akcesoria", "Kosztorys"]
wybor = st.radio("", zakladki, key='active_tab', horizontal=True)

# ---------- ZAWARTOŚĆ MODUŁÓW ----------
if wybor == "Geometria":
    st.header("📐 Geometria budynku – wymiary główne")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Wysokość (cm)", 200, 600, key='wys')
        st.number_input("Szerokość (cm)", 200, 1500, key='szer')
        st.number_input("Długość (cm)", 200, 2000, key='dlug')
    with c2:
        st.subheader("Podstawowe parametry")
        st.metric("Powierzchnia podłogi", f"{pow_podlogi():.2f} m²")
        st.metric("Kubatura", f"{kubatura():.2f} m³")
        st.metric("Powierzchnia ścian (brutto)", f"{pow_scian_brutto():.2f} m²")
    st.info("Otwory okienne i drzwiowe definiuje się w module **Konstrukcja ścian**.")

elif wybor == "Konstrukcja ścian":
    st.header("🏗️ Konstrukcja ścian")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"], key='slupki')
        st.selectbox("Rozstaw słupków (cm)", [30, 40, 60], key='rozstaw')
    with col2:
        st.number_input("Długość handlowa desek (cm)", 200, 1200, key='dlugosc_desek')

    st.divider()
    st.subheader("🚪 Otwory (drzwi i okna)")
    for o in st.session_state.otwory:
        oid = o['id']
        cols = st.columns([2,2,2,1])
        cols[0].text_input("Nazwa", o.get('nazwa',''), key=f"nazwa_{oid}")
        cols[1].number_input("Szer (cm)", 30, 500, o.get('szer',100), key=f"szer_{oid}")
        cols[2].number_input("Wys (cm)", 30, 500, o.get('wys',120), key=f"wys_{oid}")
        if cols[3].button("❌", key=f"del_{oid}"):
            st.session_state.otwory = [x for x in st.session_state.otwory if x['id'] != oid]
            st.rerun()
    if st.button("➕ Dodaj otwór"):
        new_id = str(uuid.uuid4())
        st.session_state.otwory.append({
            'id': new_id,
            'nazwa': 'Okno',
            'szer': 100,
            'wys': 120
        })
        st.rerun()

    st.divider()
    st.subheader("Zapotrzebowanie na drewno")
    n = liczba_slupkow()
    dl_calk = dlugosc_listwy()
    sztuk = ile_desek(dl_calk, st.session_state.dlugosc_desek)
    dl_handl_m = st.session_state.dlugosc_desek / 100
    resztki = (sztuk * dl_handl_m - dl_calk) / (sztuk * dl_handl_m) * 100 if sztuk > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Liczba słupków", n)
    c2.metric("Całkowita długość", f"{dl_calk:.2f} m")
    c3.metric(f"Desek {st.session_state.dlugosc_desek} cm", sztuk)
    st.metric("Procent resztek", f"{resztki:.1f} %")

elif wybor == "Poszycia i izolacje":
    st.header("🧱 Poszycia i izolacje")
    st.subheader("Poszycie zewnętrzne")
    st.number_input("Grubość OSB-3 zewn. (mm)", 8, 25, key='osb_zew')
    wiatro_opcje = {"Membrana Standard 120g": 120, "Membrana Premium 160g": 160, "Folia wiatrochronna 100g": 100}
    wybor_wiatro = st.selectbox("Wiatroizolacja", list(wiatro_opcje.keys()), key='wiatro')
    pow_netto = pow_scian_netto()
    pow_zapas = pow_netto * 1.1
    st.write(f"Powierzchnia ścian netto: {pow_netto:.2f} m²")
    st.write(f"Potrzebna wiatroizolacja (z 10% zapasem): {pow_zapas:.2f} m²")

    st.subheader("Poszycie wewnętrzne (opcjonalne)")
    if st.checkbox("Dodaj poszycie wewnętrzne", key='posz_wew'):
        st.number_input("Płyta GK (mm)", 6, 25, key='gk_wew')
        st.number_input("OSB-3 wewn. (mm, 0=pomiń)", 0, 25, key='osb_wew')
        st.checkbox("Paroizolacja", True, key='paro')

    st.subheader("Izolacja termiczna")
    st.number_input("Grubość ocieplenia dachu (cm)", 5, 30, key='ocieplenie_dach')

elif wybor == "Dach":
    st.header("🔺 Dach")
    # Użyjemy dwóch podstron na stałe, ale bez zagnieżdżonych tabs (mogą resetować) – proste podradio
    dach_opcje = st.radio("Wybierz", ["Konstrukcja", "Wykończenie"], key='dach_podstrona', horizontal=True)
    if dach_opcje == "Konstrukcja":
        st.subheader("Parametry konstrukcji")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Rozstaw belek (cm)", [30, 40, 60], key='rozstaw_dach')
            st.slider("Kąt nachylenia (°)", 0, 45, key='kat')
        with col2:
            st.markdown("**Okapy (cm)**")
            st.slider("Przód", 0, 100, key='okap_przod')
            st.slider("Tył", 0, 100, key='okap_tyl')
            st.slider("Lewo", 0, 100, key='okap_lewo')
            st.slider("Prawo", 0, 100, key='okap_prawo')
        st.metric("Całkowita powierzchnia dachu", f"{pow_dachu():.2f} m²")
    else:
        st.subheader("Wykończenie pokrycia dachowego")
        st.selectbox("Rodzaj pokrycia", ["Papa", "Blachodachówka", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")

        if st.session_state.pokrycie == "Papa":
            sztuk = math.ceil(pow_dach / 2)
            st.write("**Materiały:** Papa termozgrzewalna, podkład, gaz...")
            st.write(f"- Papa w rolkach: {sztuk} szt.")
        elif st.session_state.pokrycie == "Blachodachówka":
            sztuk = math.ceil(pow_dach / 0.8)
            st.write("**Materiały:** Blachodachówka, wkręty, gąsiory...")
            st.write(f"- Arkusze: {sztuk} szt.")
        elif st.session_state.pokrycie == "EPDM":
            st.write("**Materiały:** Membrana EPDM, klej, taśmy...")
            st.write(f"- Membrana: {pow_dach:.1f} m²")

        ceny = {"Papa": 25.0, "Blachodachówka": 45.0, "EPDM": 70.0}
        cena_m2 = ceny[st.session_state.pokrycie]
        st.write(f"**Cena za m²:** {cena_m2:.2f} zł")
        st.write(f"**Szacunkowy koszt pokrycia:** {pow_dach * cena_m2:.2f} zł")

elif wybor == "Podłoga":
    st.header("🏠 Podłoga")
    st.checkbox("Podwójna podłoga (całoroczna)", key='podloga_podwojna')
    pow_podl = pow_podlogi()
    st.write(f"Powierzchnia podłogi: {pow_podl:.2f} m²")
    if st.session_state.podloga_podwojna:
        st.write("Dodatkowa warstwa podłogi zostanie uwzględniona w kosztorysie.")

elif wybor == "Akcesoria":
    st.header("🔩 Akcesoria i łączniki")
    pow_osb = pow_scian_netto()
    wkrety = math.ceil(pow_osb * 25 * 1.15)
    opakowania = math.ceil(wkrety / 200)
    st.subheader("Wkręty do OSB (Klimas)")
    st.write(f"- Ilość: {wkrety} szt. (z zapasem 15%)")
    st.write(f"- Opakowania (po 200 szt.): {opakowania}")

    st.subheader("Taśmy")
    mb_tasm = obwod_scian() * 2
    st.write(f"- Taśma do folii: {mb_tasm:.1f} mb")

    st.subheader("Łączniki ciesielskie")
    katowniki = liczba_slupkow() * 2
    st.write(f"- Kątowniki: {katowniki} szt.")

elif wybor == "Kosztorys":
    st.header("📊 Kosztorys zbiorczy")
    CENY = {
        'Drewno 95x45': 12.0, 'Drewno 145x45': 18.0, 'Drewno 195x45': 24.0,
        'OSB-3': 18.0, 'GK': 15.0,
        'Wiatroizolacja': 8.0, 'Paroizolacja': 5.0,
        'Ocieplenie dach': 40.0,
        'Wkręty opak.': 35.0, 'Taśma rolka': 25.0, 'Kątownik': 3.5,
        'Pokrycie Papa': 25.0, 'Pokrycie Blacha': 45.0, 'Pokrycie EPDM': 70.0
    }
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
    st.caption("Ceny można edytować w słowniku CENY w kodzie.")
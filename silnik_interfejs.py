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
        'active_tab': 'Geometria',
        'cena_drewna_m3': 1600.0,
        'use_wlasna_cena': False,
        'dach_podstrona': 'Konstrukcja'
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    for o in st.session_state.otwory:
        if 'id' not in o:
            o['id'] = str(uuid.uuid4())

init_state()

# ---------- FUNKCJE OBLICZENIOWE ----------
def pow_podlogi():
    return st.session_state.szer * st.session_state.dlug / 10_000

def kubatura():
    return pow_podlogi() * st.session_state.wys / 100

def pow_scian_brutto():
    obwod = 2 * (st.session_state.szer + st.session_state.dlug)
    return (obwod * st.session_state.wys) / 10_000

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

def objetosc_drewna():
    przekroje = {
        "95x45": 0.095 * 0.045,
        "145x45": 0.145 * 0.045,
        "195x45": 0.195 * 0.045
    }
    pole_m2 = przekroje[st.session_state.slupki]
    dl_m = dlugosc_listwy()
    return pole_m2 * dl_m

def pow_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    rzut_m2 = (szer * dlug) / 10_000
    return rzut_m2 / math.cos(math.radians(st.session_state.kat))

# ---------- MENU GŁÓWNE ----------
st.title("🏗️ Inżynier Szkieletowy Pro")
st.caption("Wszystkie dane są współdzielone. Wybierz moduł poniżej.")

zakladki = ["Geometria", "Konstrukcja ścian", "Wykończenie ścian", "Dach", "Podłoga", "Akcesoria", "Kosztorys"]
wybor = st.radio("", zakladki, key='active_tab', horizontal=True)

# ==================== MODUŁY ====================

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
        st.selectbox("Rozstaw słupków (cm)", [60, 120], key='rozstaw')
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
    m3 = objetosc_drewna()

    row1_col1, row1_col2 = st.columns(2)
    row1_col1.metric("Liczba słupków", n)
    row1_col2.metric("Całkowita długość", f"{dl_calk:.2f} m")
    row2_col1, row2_col2 = st.columns(2)
    row2_col1.metric(f"Desek {st.session_state.dlugosc_desek} cm", sztuk)
    row2_col2.metric("Procent resztek", f"{resztki:.1f} %")
    st.metric("Objętość drewna", f"{m3:.3f} m³")

    st.divider()
    st.subheader("Koszt drewna konstrukcyjnego")
    use_wlasna = st.checkbox("Użyj własnej ceny za m³", key='use_wlasna_cena')
    if use_wlasna:
        st.number_input("Twoja cena za m³ (zł)", min_value=0.0, value=st.session_state.cena_drewna_m3, step=100.0, key='cena_drewna_m3')
        koszt_drewna = m3 * st.session_state.cena_drewna_m3
    else:
        koszt_drewna = m3 * 1600.0
    st.write(f"Koszt drewna: **{koszt_drewna:.2f} zł** (wg {'Twojej' if use_wlasna else 'domyślnej'} ceny)")

elif wybor == "Wykończenie ścian":
    st.header("🧱 Wykończenie ścian")
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

    st.subheader("Elewacja")
    st.write("(Opcje wykończenia elewacji – deski, tynki itp. można dodać w przyszłości)")

    st.subheader("Izolacja termiczna")
    st.number_input("Grubość ocieplenia dachu (cm)", 5, 30, key='ocieplenie_dach')

elif wybor == "Dach":
    st.header("🔺 Dach")
    dach_opcje = st.radio("Wybierz podstronę", ["Konstrukcja dachu", "Wykończenie dachu"], key='dach_podstrona', horizontal=True)

    if dach_opcje == "Konstrukcja dachu":
        st.markdown("---")
        st.subheader("Rozdział 1: Rozstaw belek")
        st.selectbox("Rozstaw belek (cm)", [30, 40, 60], key='rozstaw_dach')

        st.subheader("Rozdział 2: Pochylenie i okapy")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Kąt nachylenia dachu (°)", 0, 45, key='kat')
        with col2:
            st.markdown("**Okapy (cm)**")
            st.slider("Przód", 0, 100, key='okap_przod')
            st.slider("Tył", 0, 100, key='okap_tyl')
            st.slider("Lewo", 0, 100, key='okap_lewo')
            st.slider("Prawo", 0, 100, key='okap_prawo')

        st.markdown("---")
        st.subheader("Podsumowanie")
        st.metric("Całkowita powierzchnia dachu", f"{pow_dachu():.2f} m²")

    else:
        st.subheader("Wykończenie pokrycia dachowego")
        st.selectbox("Rodzaj pokrycia", ["Papa", "Blachodachówka", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")
        st.markdown("---")
        st.subheader("Lista materiałów")

        if st.session_state.pokrycie == "Papa":
            rolki = math.ceil(pow_dach / 2)
            cena_rolka = 120.0
            st.write(f"- Papa termozgrzewalna: **{rolki} rolek** (2 m²/rolka)")
            st.write(f"  Potrzebna ilość: {rolki * 2:.1f} m²")
            st.write(f"  Cena jednostkowa: {cena_rolka:.2f} zł/rolka")
            st.write(f"  Koszt papy: **{rolki * cena_rolka:.2f} zł**")
            st.write("- Podkład, gaz, akcesoria – doliczane ręcznie.")
        elif st.session_state.pokrycie == "Blachodachówka":
            arkusze = math.ceil(pow_dach / 0.8)
            cena_arkusz = 85.0
            st.write(f"- Blachodachówka: **{arkusze} arkuszy** (0.8 m²/ark.)")
            st.write(f"  Potrzebna ilość: {arkusze * 0.8:.1f} m²")
            st.write(f"  Cena jednostkowa: {cena_arkusz:.2f} zł/arkusz")
            st.write(f"  Koszt blachodachówki: **{arkusze * cena_arkusz:.2f} zł**")
            st.write("- Wkręty, gąsiory, obróbki – doliczane ręcznie.")
        elif st.session_state.pokrycie == "EPDM":
            st.write(f"- Membrana EPDM: **{pow_dach:.1f} m²** (na wymiar)")
            cena_m2_epdm = 90.0
            st.write(f"  Cena jednostkowa: {cena_m2_epdm:.2f} zł/m²")
            st.write(f"  Koszt membrany: **{pow_dach * cena_m2_epdm:.2f} zł**")
            st.write("- Klej, taśmy, akcesoria – doliczane ręcznie.")

elif wybor == "Podłoga":
    st.header("🏠 Podłoga")
    st.checkbox("Podwójna podłoga (całoroczna)", key='podloga_podwojna')
    pow_podl = pow_podlogi()
    st.write(f"Powierzchnia podłogi: {pow_podl:.2f} m²")
    if st.session_state.podloga_podwojna:
        st.write("Dodatkowa warstwa podłogi (np. 95 mm) zostanie uwzględniona w kosztorysie.")

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
    if st.session_state.get('use_wlasna_cena', False):
        cena_drewna = st.session_state.get('cena_drewna_m3', 1600.0)
    else:
        cena_drewna = 1600.0

    CENY = {
        'Drewno m3': cena_drewna,
        'OSB-3': 18.0, 'GK': 15.0,
        'Wiatroizolacja': 8.0, 'Paroizolacja': 5.0,
        'Ocieplenie dach': 40.0,
        'Wkręty opak.': 35.0, 'Taśma rolka': 25.0, 'Kątownik': 3.5,
        'Pokrycie Papa': 25.0, 'Pokrycie Blacha': 45.0, 'Pokrycie EPDM': 70.0
    }

    m3_drewna = objetosc_drewna()
    pow_netto = pow_scian_netto()
    opak_wkrety = math.ceil(pow_netto * 25 * 1.15 / 200)

    kosztorys = [
        (f"Drewno konstrukcyjne ({st.session_state.slupki})",
         f"{m3_drewna:.3f} m³",
         m3_drewna * CENY['Drewno m3']),
        ("OSB-3 zewnętrzne", f"{pow_netto:.1f} m²", pow_netto * CENY['OSB-3']),
        ("Wiatroizolacja", f"{pow_netto*1.1:.1f} m²", pow_netto*1.1 * CENY['Wiatroizolacja']),
        ("Wkręty do OSB", f"{opak_wkrety} op.", opak_wkrety * CENY['Wkręty opak.']),
        (f"Pokrycie dachowe – {st.session_state.pokrycie}",
         f"{pow_dachu():.1f} m²",
         pow_dachu() * CENY[f"Pokrycie {st.session_state.pokrycie}"]),
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
    st.caption("Ceny można edytować w kodzie (słownik CENY) lub za pomocą pól w odpowiednich modułach.")
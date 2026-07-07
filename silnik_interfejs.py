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
        'ocieplenie_dach': 15, 'technika_podlogi': 'Standardowa',
        'active_tab': 'Geometria',
        'cena_drewna_m3': 1600.0,
        'use_wlasna_cena': False,
        'dach_podstrona': 'Konstrukcja dachu',
        'sciany_podstrona': 'Konstrukcja ścian',
        # nowe zmienne
        'wiatro_dach': None,          # wybór wiatroizolacji dachowej
        'izolacja_scian': False,      # checkbox izolacji termicznej ścian
        'grubosc_izolacji_scian': 10, # cm
        'rozstaw_kantowek': 60        # cm
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Uzupełnij id otworów
    for o in st.session_state.otwory:
        if 'id' not in o:
            o['id'] = str(uuid.uuid4())
    # Domyślna wiatroizolacja dachu
    if st.session_state.wiatro_dach is None:
        st.session_state.wiatro_dach = "Membrana Standard 120g"

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

def nachylenie_procent():
    return math.tan(math.radians(st.session_state.kat)) * 100

# Parametry dachu dla obliczeń materiałowych
def dlugosc_polaci():
    """Długość od kalenicy do okapu (w metrach)"""
    polowa_szer = (st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo) / 2 / 100
    return polowa_szer / math.cos(math.radians(st.session_state.kat))

def liczba_krokwi():
    dlugosc_cm = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    rozstaw_cm = st.session_state.get('rozstaw_dach', 60)
    return math.ceil(dlugosc_cm / rozstaw_cm) + 1

# ---------- MENU GŁÓWNE ----------
st.title("🏗️ Inżynier Szkieletowy Pro")
st.caption("Wszystkie dane są współdzielone. Wybierz moduł poniżej.")

zakladki = ["Geometria", "Ściany", "Dach", "Podłoga", "Akcesoria", "Kosztorys"]
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
    st.info("Otwory i konstrukcję ścian definiuje się w module **Ściany**.")

elif wybor == "Ściany":
    st.header("🧱 Ściany")
    sciany_opcje = st.radio("", ["Konstrukcja ścian", "Wykończenie ścian"], key='sciany_podstrona', horizontal=True)

    if sciany_opcje == "Konstrukcja ścian":
        st.subheader("Materiał i rozstaw")
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

        # Układ 2x2 + 1
        r1c1, r1c2 = st.columns(2)
        r1c1.metric("Liczba słupków", n)
        r1c2.metric("Całkowita długość", f"{dl_calk:.2f} m")
        r2c1, r2c2 = st.columns(2)
        r2c1.metric(f"Desek {st.session_state.dlugosc_desek} cm", sztuk)
        r2c2.metric("Procent resztek", f"{resztki:.1f} %")
        st.metric("Objętość drewna", f"{m3:.3f} m³")

        st.divider()
        st.subheader("Koszt drewna konstrukcyjnego")
        use_wlasna = st.checkbox("Użyj własnej ceny za m³", key='use_wlasna_cena')
        if use_wlasna:
            st.number_input("Twoja cena za m³ (zł)", min_value=0.0, value=st.session_state.cena_drewna_m3, step=100.0, key='cena_drewna_m3')
            koszt_drewna = m3 * st.session_state.cena_drewna_m3
            st.write(f"**Koszt drewna (wg Twojej ceny):** {koszt_drewna:.2f} zł")
        else:
            koszt_drewna = m3 * 1600.0
            st.write(f"**Koszt drewna (cena domyślna 1600 zł/m³):** {koszt_drewna:.2f} zł")

    else:  # Wykończenie ścian
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

        st.subheader("Izolacja termiczna ścian (opcjonalnie)")
        if st.checkbox("Dodaj izolację termiczną ścian", key='izolacja_scian'):
            col_iz1, col_iz2 = st.columns(2)
            with col_iz1:
                st.number_input("Grubość wełny (cm)", 5, 20, key='grubosc_izolacji_scian')
            with col_iz2:
                st.number_input("Rozstaw kantówek poziomych (cm)", 30, 80, key='rozstaw_kantowek')
            # Obliczenia
            wys_m = st.session_state.wys / 100
            obwod_m = obwod_scian()
            rozstaw_m = st.session_state.rozstaw_kantowek / 100
            liczba_rzedow = math.ceil(wys_m / rozstaw_m) + 1
            dlugosc_kantowek_m = liczba_rzedow * obwod_m
            st.write(f"**Kantówki poziome (np. 45x45):** {dlugosc_kantowek_m:.1f} mb")
            st.write(f"**Wełna mineralna:** {pow_netto:.1f} m² (gr. {st.session_state.grubosc_izolacji_scian} cm)")

        st.subheader("Elewacja")
        st.write("(Opcje wykończenia elewacji – deski, tynki itp. można dodać w przyszłości)")

        st.subheader("Izolacja termiczna dachu")
        st.number_input("Grubość ocieplenia dachu (cm)", 5, 30, key='ocieplenie_dach')

elif wybor == "Dach":
    st.header("🔺 Dach")
    dach_opcje = st.radio("", ["Konstrukcja dachu", "Wykończenie dachu"], key='dach_podstrona', horizontal=True)

    if dach_opcje == "Konstrukcja dachu":
        st.subheader("Rozstaw belek")
        st.selectbox("Rozstaw belek (cm)", [30, 40, 60], key='rozstaw_dach')

        st.subheader("Pochylenie i okapy")
        col1, col2 = st.columns(2)
        with col1:
            kat = st.slider("Kąt nachylenia dachu (°)", 0, 45, key='kat')
            st.caption(f"Nachylenie: **{nachylenie_procent():.1f}%**")
        with col2:
            st.markdown("**Okapy (cm)**")
            st.slider("Przód", 0, 100, key='okap_przod')
            st.slider("Tył", 0, 100, key='okap_tyl')
            st.slider("Lewo", 0, 100, key='okap_lewo')
            st.slider("Prawo", 0, 100, key='okap_prawo')

        st.divider()
        st.subheader("Podsumowanie")
        st.metric("Całkowita powierzchnia dachu", f"{pow_dachu():.2f} m²")

    else:  # Wykończenie dachu
        st.subheader("Wykończenie pokrycia dachowego")
        st.selectbox("Rodzaj pokrycia", ["Papa", "Blachodachówka", "Gont bitumiczny", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")
        st.markdown("---")

        # ----- PAPA -----
        if st.session_state.pokrycie == "Papa":
            st.subheader("Papa – materiały")
            dl_polaci = dlugosc_polaci()
            szer_polaci = (st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl) / 100
            # Zakładka 10 cm -> efektywna szerokość rolki 0.9 m
            liczba_pasow = math.ceil(dl_polaci / 0.9)
            st.write(f"Długość połaci: **{dl_polaci:.2f} m** → przy zakładzie 10 cm potrzeba **{liczba_pasow} pasów** papy")
            if st.session_state.okap_przod < 20 or st.session_state.okap_tyl < 20:
                st.info("💡 Zmniejszając okapy, można zejść do 3–4 pasów papy, co obniży koszty.")
            # Papa podkładowa i wierzchnia – każda warstwa
            pow_z_zakladem = pow_dach * 1.15  # 15% zapas na zakłady i odpady
            rolki = math.ceil(pow_z_zakladem / 10)  # rolka 10 m²
            st.write(f"**Papa podkładowa:** {rolki} rolek (10 m²/rolka)")
            st.write(f"**Papa wierzchnia:** {rolki} rolek (10 m²/rolka)")
            # Lepik / masa bitumiczna
            masa_kg = pow_dach * 0.5  # szacunkowo 0.5 kg/m²
            st.write(f"**Masa bitumiczna (lepik):** ok. {masa_kg:.1f} kg (np. {math.ceil(masa_kg/5)} wiaderek 5 kg)")

        # ----- BLACHODACHÓWKA -----
        elif st.session_state.pokrycie == "Blachodachówka":
            st.subheader("Blachodachówka – materiały")
            arkusze = math.ceil(pow_dach / 0.8)
            cena_arkusz = 85.0
            st.write(f"- **Arkusze blachodachówki:** {arkusze} szt. (0.8 m²/szt.)")
            st.write(f"  Koszt: {arkusze * cena_arkusz:.2f} zł")
            # Wiatroizolacja
            st.selectbox("Wiatroizolacja dachu", list({"Membrana Standard 120g":120, "Membrana Premium 160g":160}.keys()), key='wiatro_dach')
            rolki_wiatro = math.ceil(pow_dach * 1.1 / 50)  # rolka 50 m²
            st.write(f"- **Wiatroizolacja:** {rolki_wiatro} rolek (50 m²/rolka, z zapasem)")
            # Łaty i kontrłaty
            liczba_kr = liczba_krokwi()
            dl_pol = dlugosc_polaci()
            kontr_laty_mb = liczba_kr * dl_pol * 2  # dwie połacie
            # Łaty poziome co 35 cm
            rozstaw_lat = 0.35
            liczba_lat = math.ceil(dl_pol / rozstaw_lat) + 1
            laty_mb = liczba_lat * szer_polaci * 2
            st.write(f"- **Kontrłaty (np. 25x50):** {kontr_laty_mb:.1f} mb")
            st.write(f"- **Łaty (np. 40x50):** {laty_mb:.1f} mb")
            # Wkręty do blachodachówki
            wkrety_blacha = arkusze * 8  # średnio 8 wkrętów na arkusz
            st.write(f"- **Wkręty farmerskie z uszczelką:** ok. {wkrety_blacha} szt.")

        # ----- GONT BITUMICZNY -----
        elif st.session_state.pokrycie == "Gont bitumiczny":
            st.subheader("Gont bitumiczny – materiały")
            # Podkład (papa podkładowa)
            rolki_podklad = math.ceil(pow_dach * 1.1 / 10)
            st.write(f"- **Papa podkładowa:** {rolki_podklad} rolek (10 m²/rolka, z zapasem)")
            # Gonty
            opakowania_gont = math.ceil(pow_dach / 3)  # 1 op. = 3 m²
            st.write(f"- **Gont bitumiczny:** {opakowania_gont} opakowań (3 m²/op.)")
            # Masa bitumiczna
            tubki = math.ceil(pow_dach / 5)  # 1 tubka na 5 m²
            st.write(f"- **Masa bitumiczna (tubki):** {tubki} szt. (do uszczelnień)")
            # Wiatroizolacja jako opcja
            if st.checkbox("Dodaj wiatroizolację dachową"):
                st.selectbox("Wiatroizolacja", list({"Membrana Standard 120g":120, "Membrana Premium 160g":160}.keys()), key='wiatro_dach_gont')
                rolki_wiatro = math.ceil(pow_dach * 1.1 / 50)
                st.write(f"- **Wiatroizolacja:** {rolki_wiatro} rolek (50 m²/rolka)")

        # ----- EPDM -----
        else:
            st.subheader("EPDM – materiały")
            st.write(f"- **Membrana EPDM:** {pow_dach:.1f} m² (na wymiar)")
            klej_l = pow_dach / 5
            st.write(f"- **Klej kontaktowy:** {math.ceil(klej_l)} litrów (1 l na 5 m²)")
            primer_l = pow_dach * 0.3
            st.write(f"- **Primer:** {primer_l:.1f} l")
            obwod_dachu = 2 * ((st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo)/100 + 
                                (st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl)/100)
            st.write(f"- **Taśma EPDM (do krawędzi):** ok. {math.ceil(obwod_dachu/10)} rolek (10 m/rolka)")
            st.info("💡 Membranę można układać na podkładzie z płyt OSB, betonie lub starym pokryciu.")

elif wybor == "Podłoga":
    st.header("🏠 Podłoga")
    st.radio("Technika budowy podłogi:", ["Standardowa (pojedyncza warstwa OSB)", "Ze stołem roboczym (dodatkowa warstwa OSB)"],
             key='technika_podlogi')
    pow_podl = pow_podlogi()
    st.write(f"Powierzchnia podłogi: **{pow_podl:.2f} m²**")

    if st.session_state.technika_podlogi == "Ze stołem roboczym (dodatkowa warstwa OSB)":
        st.subheader("Materiały na stół roboczy")
        # Płyty OSB 22 mm
        plyty_osb = math.ceil(pow_podl * 1.1 / 3)  # płyta 125x250 = 3.125 m², ale zaokrąglam 3 m²
        st.write(f"- **Płyty OSB-3 (22 mm):** {plyty_osb} szt. (3.1 m²/szt., z 10% zapasem)")
        # Legary (co 60 cm, wzdłuż krótszego boku)
        krotszy = min(st.session_state.szer, st.session_state.dlug)
        dluzszy = max(st.session_state.szer, st.session_state.dlug)
        ile_legarow = math.ceil(dluzszy / 60) + 1
        mb_legarow = ile_legarow * krotszy / 100
        st.write(f"- **Legary (np. 45x145 mm):** {mb_legarow:.1f} mb ({ile_legarow} szt. po {krotszy/100:.2f} m)")
        st.write("- **Wkręty do legarów:** ok. 2 op. (po 200 szt.)")

elif wybor == "Akcesoria":
    st.header("🔩 Akcesoria i łączniki")
    # Wkręty do OSB
    pow_osb = pow_scian_netto()
    wkrety_osb = math.ceil(pow_osb * 25 * 1.15)
    op_osb = math.ceil(wkrety_osb / 200)
    st.write(f"**Wkręty do OSB (Klimas WK 4,5x60):** {wkrety_osb} szt. → {op_osb} op. (200 szt./op.) * ~35 zł/op.")

    # Wkręty do GK (jeśli wybrano płyty GK)
    if st.session_state.get('posz_wew', False) and st.session_state.get('gk_wew', 0) > 0:
        pow_gk = pow_scian_netto()
        wkrety_gk = math.ceil(pow_gk * 20 * 1.15)  # ok. 20 szt/m²
        op_gk = math.ceil(wkrety_gk / 1000)
        st.write(f"**Wkręty do GK (Klimas 3,5x25):** {wkrety_gk} szt. → {op_gk} op. (1000 szt./op.) * ~20 zł/op.")

    # Wkręty ciesielskie (do konstrukcji)
    st.write(f"**Wkręty ciesielskie (Klimas WK 6x80):** ok. {liczbę_slupkow() * 4} szt. (do połączeń słupków) → {math.ceil(liczbę_slupkow() * 4 / 100)} op. (100 szt./op.) * ~45 zł/op.")

    # Taśmy
    mb_tasm = obwod_scian() * 2
    st.write(f"**Taśma butylowa do folii:** {mb_tasm:.1f} mb → {math.ceil(mb_tasm/10)} rolek (10 m/rolka) * ~25 zł/rolka")

    # Kątowniki
    katowniki = liczba_slupkow() * 2
    st.write(f"**Kątowniki montażowe (60x60x40):** {katowniki} szt. * ~3,5 zł/szt.")

    # Dodatkowo akcesoria dachowe – jeśli wybrano blachodachówkę
    if st.session_state.pokrycie == "Blachodachówka":
        st.write(f"**Wkręty farmerskie do blachodachówki:** ok. {math.ceil(pow_dachu() / 0.8) * 8} szt. → {math.ceil(math.ceil(pow_dachu() / 0.8) * 8 / 250)} op. (250 szt./op.) * ~55 zł/op.")

elif wybor == "Kosztorys":
    st.header("📊 Kosztorys zbiorczy")
    if st.session_state.get('use_wlasna_cena', False):
        cena_drewna = st.session_state.get('cena_drewna_m3', 1600.0)
    else:
        cena_drewna = 1600.0

    # Sekcje kosztorysu
    st.subheader("Konstrukcja")
    m3 = objetosc_drewna()
    st.write(f"- Drewno konstrukcyjne: {m3:.3f} m³ × {cena_drewna:.2f} zł/m³ = **{m3 * cena_drewna:.2f} zł**")

    st.subheader("Poszycia")
    pow_netto = pow_scian_netto()
    st.write(f"- OSB-3 zewnętrzne: {pow_netto:.1f} m² × 18 zł/m² = **{pow_netto * 18:.2f} zł**")
    st.write(f"- Wiatroizolacja: {pow_netto*1.1:.1f} m² × 8 zł/m² = **{pow_netto*1.1*8:.2f} zł**")

    st.subheader("Dach")
    pow_dach = pow_dachu()
    st.write(f"- Pokrycie ({st.session_state.pokrycie}): {pow_dach:.1f} m²")
    if st.session_state.pokrycie == "Papa":
        st.write(f"   Papa podkładowa + wierzchnia: {math.ceil(pow_dach*1.15/10)*2} rolek × 120 zł = **{math.ceil(pow_dach*1.15/10)*2*120:.2f} zł**")
        st.write(f"   Masa bitumiczna: ok. {pow_dach*0.5:.1f} kg × 6 zł/kg = **{pow_dach*0.5*6:.2f} zł**")
    elif st.session_state.pokrycie == "Blachodachówka":
        arkusze = math.ceil(pow_dach / 0.8)
        st.write(f"   Blachodachówka: {arkusze} szt. × 85 zł = **{arkusze*85:.2f} zł**")
        st.write(f"   Łaty/kontrłaty: ok. **200.00 zł** (szacunkowo)")
    elif st.session_state.pokrycie == "Gont bitumiczny":
        st.write(f"   Gonty: {math.ceil(pow_dach/3)} op. × 120 zł = **{math.ceil(pow_dach/3)*120:.2f} zł**")
    else:  # EPDM
        st.write(f"   Membrana EPDM + klej: ok. **{pow_dach*90 + pow_dach/5*30:.2f} zł**")

    st.subheader("Podłoga")
    if st.session_state.technika_podlogi == "Ze stołem roboczym (dodatkowa warstwa OSB)":
        st.write(f"- Stół roboczy (OSB + legary): ok. **{pow_podlogi()*50:.2f} zł**")
    else:
        st.write("- Standardowa (wliczona w konstrukcję)")

    st.subheader("Akcesoria")
    st.write("- Wkręty, taśmy, kątowniki: ok. **150.00 zł** (orientacyjnie)")

    st.divider()
    suma_calosc = (m3 * cena_drewna + pow_netto * (18 + 8*1.1) +
                   (math.ceil(pow_dach*1.15/10)*2*120 + pow_dach*0.5*6) +  # Papa
                   (150 + pow_podlogi()*50 if st.session_state.technika_podlogi == "Ze stołem roboczym (dodatkowa warstwa OSB)" else 150))
    st.subheader(f"**Szacunkowa suma całkowita: {suma_calosc:.2f} zł**")
    st.caption("Ceny są orientacyjne – bazują na wprowadzonych danych.")
import streamlit as st
import math
import uuid

st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy Pro")

# ---------- INICJALIZACJA ----------
def init_state():
    defaults = {
        'wys': 250, 'szer': 600, 'dlug': 800,
        'rozstaw': 60, 'kat': 20,
        'okap_przod': 20, 'okap_tyl': 20, 'okap_lewo': 20, 'okap_prawo': 20,
        'slupki': "145x45", 'pokrycie': "Papa",
        'otwory': [], 'dlugosc_desek': 600,
        'osb_zew': 12, 'osb_wew': 12, 'gk_wew': 12.5,
        'technika_podlogi': 'Standardowa',
        'active_tab': 'Geometria',
        'cena_drewna_m3': 1600.0, 'use_wlasna_cena': False,
        'dach_podstrona': 'Konstrukcja dachu',
        'sciany_podstrona': 'Konstrukcja ścian',
        'wiatro_dach': "Membrana Standard 120g",
        'paroizolacja': "Folia PE 0,2mm",
        'posz_wew': False,
        'dlugosc_rolki_papa': 10.0,
        'szerokosc_rolki_papa': 1.0,
        'zaklad_papa': 0.10,
        'dodatkowa_izolacja': False,
        # ceny własne – inicjowane domyślnie
        'cena_osb_wew': 18.0, 'cena_gk': 15.0, 'cena_paro': 3.5,
        'cena_welna_glowna': 35.0, 'cena_welna_dod': 25.0, 'cena_kantowki': 6.0,
        'cena_osb_zew': 18.0, 'cena_wiatro': 8.0,
        'use_wlasna_cena_osb_wew': False, 'use_wlasna_cena_gk': False,
        'use_wlasna_cena_paro': False, 'use_wlasna_cena_welna_glowna': False,
        'use_wlasna_cena_welna_dod': False, 'use_wlasna_cena_kantowki': False,
        'use_wlasna_cena_osb_zew': False, 'use_wlasna_cena_wiatro': False,
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
    n += 2 * len(st.session_state.otwory)
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
    return pole_m2 * dlugosc_listwy()

def pow_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    rzut = (szer * dlug) / 10_000
    return rzut / math.cos(math.radians(st.session_state.kat))

def nachylenie_procent():
    return math.tan(math.radians(st.session_state.kat)) * 100

def dlugosc_polaci():
    polowa = (st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo) / 200
    return polowa / math.cos(math.radians(st.session_state.kat))

def liczba_krokwi():
    dl_cm = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    return math.ceil(dl_cm / st.session_state.get('rozstaw_dach', 60)) + 1

# ---------- MENU ----------
st.title("🏗️ Inżynier Szkieletowy Pro")
zakladki = ["Geometria", "Ściany", "Dach", "Podłoga", "Akcesoria", "Kosztorys"]
wybor = st.radio("", zakladki, key='active_tab', horizontal=True)

# ==================== GEOMETRIA ====================
if wybor == "Geometria":
    st.header("📐 Geometria")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Wysokość (cm)", 200, 600, key='wys')
        st.number_input("Szerokość (cm)", 200, 1500, key='szer')
        st.number_input("Długość (cm)", 200, 2000, key='dlug')
    with c2:
        st.subheader("Parametry")
        st.metric("Powierzchnia podłogi", f"{pow_podlogi():.2f} m²")
        st.metric("Kubatura", f"{kubatura():.2f} m³")
        st.metric("Pow. ścian brutto", f"{pow_scian_brutto():.2f} m²")
    st.info("Otwory i konstrukcję definiujesz w module **Ściany**.")

# ==================== ŚCIANY ====================
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
            st.number_input("Dł. handlowa desek (cm)", 200, 1200, key='dlugosc_desek')

        st.divider()
        st.subheader("🚪 Otwory")
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
            st.session_state.otwory.append({'id': str(uuid.uuid4()), 'nazwa':'Okno', 'szer':100, 'wys':120})
            st.rerun()

        st.divider()
        st.subheader("Zapotrzebowanie na drewno")
        n = liczba_slupkow()
        dl_calk = dlugosc_listwy()
        sztuk = ile_desek(dl_calk, st.session_state.dlugosc_desek)
        dl_handl_m = st.session_state.dlugosc_desek / 100
        resztki = (sztuk * dl_handl_m - dl_calk) / (sztuk * dl_handl_m) * 100 if sztuk > 0 else 0
        m3 = objetosc_drewna()

        # Tabelka markdown
        st.markdown(f"""
        | Parametr | Wartość |
        |----------|---------|
        | Liczba słupków | **{n}** |
        | Całkowita długość listew | **{dl_calk:.2f} m** |
        | Desek {st.session_state.dlugosc_desek} cm | **{sztuk} szt.** |
        | Procent resztek | **{resztki:.1f} %** |
        | Objętość drewna | **{m3:.3f} m³** |
        """)

        st.subheader("Koszt drewna")
        use_wlasna = st.checkbox("Użyj własnej ceny za m³", key='use_wlasna_cena')
        if use_wlasna:
            st.number_input("Twoja cena za m³", value=st.session_state.cena_drewna_m3, step=100.0, key='cena_drewna_m3')
            koszt = m3 * st.session_state.cena_drewna_m3
            st.write(f"Koszt wg Twojej ceny: **{koszt:.2f} zł**")
        else:
            koszt = m3 * 1600.0
            st.write(f"Koszt (cena domyślna 1600 zł/m³): **{koszt:.2f} zł**")

    else:  # Wykończenie ścian
        st.subheader("🧵 Wykończenie ścian")
        st.checkbox("Uwzględnij poszycie wewnętrzne", key='posz_wew')

        if st.session_state.posz_wew:
            st.markdown("## Poszycie wewnętrzne")
            pow_netto = pow_scian_netto()

            # 1. Izolacja główna (między słupkami) – zawsze
            grub_map = {"95x45":100, "145x45":150, "195x45":200}
            gr = grub_map[st.session_state.slupki]
            st.markdown(f"**Wełna Knauf Ecose {gr} mm**")
            pokrycie_map = {100:5.76, 150:4.32, 200:2.88}
            paczki = math.ceil(pow_netto / pokrycie_map[gr])
            cena_dom = 35.0
            col_a, col_b = st.columns([1,2])
            own = col_a.checkbox("Własna cena", key='use_wlasna_cena_welna_glowna')
            if own:
                cena = col_b.number_input("Cena za m²", value=st.session_state.cena_welna_glowna, key='cena_welna_glowna')
            else:
                cena = cena_dom
                col_b.write(f"Cena domyślna: {cena_dom:.2f} zł/m²")
            st.write(f"Powierzchnia: **{pow_netto:.1f} m²** → **{paczki} paczek** (razem {paczki*pokrycie_map[gr]:.1f} m²)")
            st.write(f"Koszt: **{pow_netto * cena:.2f} zł**")

            # 2. Dodatkowa izolacja 5 cm – opcjonalna
            if st.checkbox("Dodatkowa izolacja termiczna 5 cm", key='dodatkowa_izolacja'):
                st.markdown("**Wełna 50 mm**")
                paczki5 = math.ceil(pow_netto / 8.64)
                cena_dom5 = 25.0
                col_a2, col_b2 = st.columns([1,2])
                own5 = col_a2.checkbox("Własna cena", key='use_wlasna_cena_welna_dod')
                if own5:
                    cena5 = col_b2.number_input("Cena za m²", value=st.session_state.cena_welna_dod, key='cena_welna_dod')
                else:
                    cena5 = cena_dom5
                    col_b2.write(f"Cena domyślna: {cena_dom5:.2f} zł/m²")
                st.write(f"Powierzchnia: **{pow_netto:.1f} m²** → **{paczki5} paczek**")
                st.write(f"Koszt: **{pow_netto * cena5:.2f} zł**")

            # 3. Kantówki poziome (pod dodatkową izolację)
            st.markdown("**Kantówki 45x45 mm**")
            rozstaw_kant = 0.60  # dla wełny 60 cm
            rzedy = math.ceil(st.session_state.wys / 100 / rozstaw_kant) + 1
            mb_kant = rzedy * obwod_scian()
            cena_kant_dom = 6.0
            col_a3, col_b3 = st.columns([1,2])
            own_k = col_a3.checkbox("Własna cena", key='use_wlasna_cena_kantowki')
            if own_k:
                cena_k = col_b3.number_input("Cena za mb", value=st.session_state.cena_kantowki, key='cena_kantowki')
            else:
                cena_k = cena_kant_dom
                col_b3.write(f"Cena domyślna: {cena_kant_dom:.2f} zł/mb")
            st.write(f"Długość: **{mb_kant:.1f} mb**")
            st.write(f"Koszt: **{mb_kant * cena_k:.2f} zł**")

            # 4. OSB wewn.
            st.markdown("**Płyta OSB-3 wewn.**")
            grubosci = [8,9,10,12]
            st.selectbox("Grubość (mm)", grubosci, key='osb_wew')
            cena_osb_dom = 18.0
            col_a4, col_b4 = st.columns([1,2])
            own_osb = col_a4.checkbox("Własna cena", key='use_wlasna_cena_osb_wew')
            if own_osb:
                cena_osb = col_b4.number_input("Cena za m²", value=st.session_state.cena_osb_wew, key='cena_osb_wew')
            else:
                cena_osb = cena_osb_dom
                col_b4.write(f"Cena domyślna: {cena_osb_dom:.2f} zł/m²")
            st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
            st.write(f"Koszt: **{pow_netto * cena_osb:.2f} zł**")

            # 5. Płyta GK
            st.markdown("**Płyta gipsowo-kartonowa 12,5 mm**")
            cena_gk_dom = 15.0
            col_a5, col_b5 = st.columns([1,2])
            own_gk = col_a5.checkbox("Własna cena", key='use_wlasna_cena_gk')
            if own_gk:
                cena_gk = col_b5.number_input("Cena za m²", value=st.session_state.cena_gk, key='cena_gk')
            else:
                cena_gk = cena_gk_dom
                col_b5.write(f"Cena domyślna: {cena_gk_dom:.2f} zł/m²")
            st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
            st.write(f"Koszt: **{pow_netto * cena_gk:.2f} zł**")

            # 6. Paroizolacja
            st.markdown("**Paroizolacja**")
            paro_opcje = {"Folia PE 0,2mm":3.5, "Folia PE 0,3mm":4.8, "Folia aluminiowa":8.2, "Membrana paroszczelna":6.5}
            wybor_paro = st.selectbox("Rodzaj", list(paro_opcje.keys()), key='paroizolacja')
            cena_paro_dom = paro_opcje[wybor_paro]
            col_a6, col_b6 = st.columns([1,2])
            own_paro = col_a6.checkbox("Własna cena", key='use_wlasna_cena_paro')
            if own_paro:
                cena_paro = col_b6.number_input("Cena za m²", value=st.session_state.cena_paro, key='cena_paro')
            else:
                cena_paro = cena_paro_dom
                col_b6.write(f"Cena domyślna: {cena_paro_dom:.2f} zł/m²")
            st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
            st.write(f"Koszt: **{pow_netto * cena_paro:.2f} zł**")

        # POSZYCIE ZEWNĘTRZNE
        st.markdown("## Poszycie zewnętrzne")
        pow_netto = pow_scian_netto()
        st.markdown("**Płyta OSB-3 zewn.**")
        st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_zew')
        cena_osb_zew_dom = 18.0
        col_az, col_bz = st.columns([1,2])
        own_osz = col_az.checkbox("Własna cena", key='use_wlasna_cena_osb_zew')
        if own_osz:
            cena_osz = col_bz.number_input("Cena za m²", value=st.session_state.cena_osb_zew, key='cena_osb_zew')
        else:
            cena_osz = cena_osb_zew_dom
            col_bz.write(f"Cena domyślna: {cena_osb_zew_dom:.2f} zł/m²")
        st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
        st.write(f"Koszt: **{pow_netto * cena_osz:.2f} zł**")

        st.markdown("**Wiatroizolacja**")
        wiatro_opcje = {"Membrana Standard 120g":120, "Membrana Premium 160g":160, "Folia wiatrochronna 100g":100}
        wybor_w = st.selectbox("Rodzaj", list(wiatro_opcje.keys()), key='wiatro')
        pow_zapas = pow_netto * 1.1
        cena_w_dom = 8.0
        col_aw, col_bw = st.columns([1,2])
        own_w = col_aw.checkbox("Własna cena", key='use_wlasna_cena_wiatro')
        if own_w:
            cena_w = col_bw.number_input("Cena za m²", value=st.session_state.cena_wiatro, key='cena_wiatro')
        else:
            cena_w = cena_w_dom
            col_bw.write(f"Cena domyślna: {cena_w_dom:.2f} zł/m²")
        st.write(f"Powierzchnia (z 10% zapasem): **{pow_zapas:.2f} m²**")
        st.write(f"Koszt: **{pow_zapas * cena_w:.2f} zł**")

# ==================== DACH ====================
elif wybor == "Dach":
    st.header("🔺 Dach")
    dach_opcje = st.radio("", ["Konstrukcja dachu", "Wykończenie dachu"], key='dach_podstrona', horizontal=True)

    if dach_opcje == "Konstrukcja dachu":
        st.subheader("Rozstaw belek")
        st.selectbox("Rozstaw (cm)", [30,40,60], key='rozstaw_dach')
        st.markdown("---")
        st.subheader("Kąt nachylenia")
        kat = st.slider("Kąt (°)", 0,45, key='kat')
        nachyl = nachylenie_procent()
        st.markdown(f"<h2 style='text-align:center; color:#e74c3c;'>{nachyl:.1f}%</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Okapy")
        st.markdown("<div style='font-size:1.2em'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Przód (cm)", 0,100, key='okap_przod')
            st.slider("Lewo (cm)", 0,100, key='okap_lewo')
        with c2:
            st.slider("Tył (cm)", 0,100, key='okap_tyl')
            st.slider("Prawo (cm)", 0,100, key='okap_prawo')
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h3 style='text-align:center;'>Powierzchnia dachu: {pow_dachu():.2f} m²</h3>", unsafe_allow_html=True)

    else:
        st.subheader("Wykończenie dachu")
        st.selectbox("Pokrycie", ["Papa", "Blachodachówka", "Gont bitumiczny", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")
        st.markdown("---")

        if st.session_state.pokrycie == "Papa":
            st.subheader("Papa – parametry rolki")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.number_input("Długość rolki (m)", min_value=5.0, value=st.session_state.dlugosc_rolki_papa, key='dlugosc_rolki_papa')
            with col_p2:
                st.number_input("Szerokość rolki (m)", min_value=0.5, value=st.session_state.szerokosc_rolki_papa, key='szerokosc_rolki_papa')
            with col_p3:
                st.number_input("Zakład (m)", min_value=0.05, value=st.session_state.zaklad_papa, step=0.01, key='zaklad_papa')
            szer_efekt = st.session_state.szerokosc_rolki_papa - st.session_state.zaklad_papa
            dl_polaci = dlugosc_polaci()
            liczba_pasow = math.ceil(dl_polaci / szer_efekt)
            pow_rolki = st.session_state.dlugosc_rolki_papa * st.session_state.szerokosc_rolki_papa
            rolki_na_pas = math.ceil(pow_dach / pow_rolki) * liczba_pasow  # uproszczenie
            st.write(f"Efektywna szerokość: **{szer_efekt:.2f} m** → liczba pasów na połaci: **{liczba_pasow}**")
            # Porada optymalizacyjna
            opt_okap = dl_polaci - liczba_pasow * szer_efekt
            if opt_okap > 0.01:
                st.info(f"💡 Zmniejszając okap o **{opt_okap*100:.1f} cm**, idealnie wypełnisz {liczba_pasow} pasów, bez odpadów na szerokości.")
            elif opt_okap < -0.01:
                st.info(f"💡 Zwiększ okap o **{-opt_okap*100:.1f} cm**, aby pokryć dokładnie {liczba_pasow} pasów.")
            else:
                st.success("✅ Okapy idealnie dopasowane – zero odpadów na szerokości papy.")
            # Oszacowanie liczby rolek
            calkowite_m2 = pow_dach * 1.15
            rolki = math.ceil(calkowite_m2 / pow_rolki)
            st.write(f"**Papa podkładowa:** {rolki} rolki ({pow_rolki:.1f} m²/rolka)")
            st.write(f"**Papa wierzchnia:** {rolki} rolki")
            masa_kg = pow_dach * 0.5
            st.write(f"**Masa bitumiczna:** ok. {masa_kg:.1f} kg ({math.ceil(masa_kg/5)} wiader 5 kg)")

        elif st.session_state.pokrycie == "Blachodachówka":
            st.subheader("Blachodachówka")
            arkusze = math.ceil(pow_dach / 0.8)
            st.write(f"**Arkusze:** {arkusze} szt.")
            st.selectbox("Wiatroizolacja", ["Membrana Standard 120g","Membrana Premium 160g"], key='wiatro_dach')
            rolki_w = math.ceil(pow_dach * 1.1 / 50)
            st.write(f"**Wiatroizolacja:** {rolki_w} rolek")
            l_kr = liczba_krokwi()
            dl_pol = dlugosc_polaci()
            szer_pol = (st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl)/100
            kontr = l_kr * dl_pol * 2
            laty = math.ceil(dl_pol / 0.35 + 1) * szer_pol * 2
            st.write(f"**Kontrłaty:** {kontr:.1f} mb, **Łaty:** {laty:.1f} mb")
            st.write(f"**Wkręty farmerskie:** ok. {arkusze*8} szt.")

        elif st.session_state.pokrycie == "Gont bitumiczny":
            st.subheader("Gont bitumiczny")
            st.write(f"**Papa podkładowa:** {math.ceil(pow_dach*1.1/10)} rolek")
            st.write(f"**Gonty:** {math.ceil(pow_dach/3)} op.")
            st.write(f"**Masa bitumiczna:** {math.ceil(pow_dach/5)} tubek")

        else:
            st.subheader("EPDM")
            st.write(f"**Membrana:** {pow_dach:.1f} m², **Klej:** {math.ceil(pow_dach/5)} l, **Primer:** {pow_dach*0.3:.1f} l")
            st.write(f"**Taśma:** {math.ceil(obwod_dachu()/10)} rolek")  # wymaga funkcji

# ==================== PODŁOGA ====================
elif wybor == "Podłoga":
    st.header("🏠 Podłoga")
    st.radio("Technika", ["Standardowa","Ze stołem roboczym"], key='technika_podlogi')
    pow_p = pow_podlogi()
    st.write(f"Powierzchnia: **{pow_p:.2f} m²**")
    if st.session_state.technika_podlogi == "Ze stołem roboczym":
        st.write(f"**Płyty OSB 22 mm:** {math.ceil(pow_p*1.1/3)} szt.")
        krot = min(st.session_state.szer, st.session_state.dlug)
        dluz = max(st.session_state.szer, st.session_state.dlug)
        ile_leg = math.ceil(dluz/60)+1
        st.write(f"**Legary:** {ile_leg*krot/100:.1f} mb ({ile_leg} szt.)")

# ==================== AKCESORIA ====================
elif wybor == "Akcesoria":
    st.header("🔩 Akcesoria")
    pow_osb = pow_scian_netto()
    wkrety_osb = math.ceil(pow_osb * 25 * 1.15)
    op_osb = math.ceil(wkrety_osb / 200)
    wkrety_gk = math.ceil(pow_osb * 20 * 1.15) if st.session_state.get('gk_wew',0)>0 else 0
    op_gk = math.ceil(wkrety_gk / 1000) if wkrety_gk else 0
    wkr_cies = liczba_slupkow() * 4
    op_cies = math.ceil(wkr_cies / 100)
    mb_tasm = obwod_scian() * 2
    rolki_tasm = math.ceil(mb_tasm / 10)
    kat = liczba_slupkow() * 2

    html_tabela = f"""
    <table style="width:100%; border-collapse:collapse;">
    <tr style="background:#ddd;"><th>Produkt</th><th>Ilość</th><th>Opakowania</th><th>Cena jedn.</th><th>Koszt</th></tr>
    <tr><td>Wkręty OSB (Klimas 4,5x60)</td><td>{wkrety_osb} szt.</td><td>{op_osb} op. (200 szt.)</td><td>35 zł/op.</td><td>{op_osb*35:.0f} zł</td></tr>
    {f'<tr><td>Wkręty GK (Klimas 3,5x25)</td><td>{wkrety_gk} szt.</td><td>{op_gk} op. (1000 szt.)</td><td>20 zł/op.</td><td>{op_gk*20:.0f} zł</td></tr>' if wkrety_gk else ''}
    <tr><td>Wkręty ciesielskie (6x80)</td><td>{wkr_cies} szt.</td><td>{op_cies} op. (100 szt.)</td><td>45 zł/op.</td><td>{op_cies*45:.0f} zł</td></tr>
    <tr><td>Taśma butylowa</td><td>{mb_tasm:.1f} mb</td><td>{rolki_tasm} rolki (10 m)</td><td>25 zł/rolka</td><td>{rolki_tasm*25:.0f} zł</td></tr>
    <tr><td>Kątowniki 60x60x40</td><td>{kat} szt.</td><td>-</td><td>3,5 zł/szt.</td><td>{kat*3.5:.0f} zł</td></tr>
    </table>
    """
    st.markdown(html_tabela, unsafe_allow_html=True)
    if st.session_state.pokrycie == "Blachodachówka":
        wkr_farm = math.ceil(pow_dachu() / 0.8) * 8
        op_farm = math.ceil(wkr_farm / 250)
        st.markdown(f"**Wkręty farmerskie:** {wkr_farm} szt. → {op_farm} op. × 55 zł = {op_farm*55:.0f} zł")

# ==================== KOSZTORYS ====================
elif wybor == "Kosztorys":
    st.header("📊 Kosztorys zbiorczy")
    st.info("Funkcja zostanie rozbudowana po ustaleniu wszystkich cen i modułów.")
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
        'dlugosc_rolki_papa_podklad': 10.0,
        'szerokosc_rolki_papa_podklad': 1.0,
        'zaklad_papa_podklad': 0.10,
        'dlugosc_rolki_papa_wierzch': 10.0,
        'szerokosc_rolki_papa_wierzch': 1.0,
        'zaklad_papa_wierzch': 0.10,
        'dodatkowa_izolacja': False,
        'rozstaw_kantowek': 60,
        'cena_osb_wew': 18.0, 'cena_gk': 15.0, 'cena_paro': 3.5,
        'cena_welna_glowna': 35.0, 'cena_welna_dod': 25.0, 'cena_kantowki': 6.0,
        'cena_osb_zew': 18.0, 'cena_wiatro': 8.0,
        'use_wlasna_cena_osb_wew': False, 'use_wlasna_cena_gk': False,
        'use_wlasna_cena_paro': False, 'use_wlasna_cena_welna_glowna': False,
        'use_wlasna_cena_welna_dod': False, 'use_wlasna_cena_kantowki': False,
        'use_wlasna_cena_osb_zew': False, 'use_wlasna_cena_wiatro': False,
        'uzyj_osb_wew': True,
        'uzyj_gk_wew': True,
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
    return math.ceil(dlugosc_calkowita_m / (dlugosc_handlowa_cm / 100))

def objetosc_drewna():
    przekroje = {"95x45": 0.095*0.045, "145x45": 0.145*0.045, "195x45": 0.195*0.045}
    pole = przekroje[st.session_state.slupki]
    return pole * dlugosc_listwy()

def pow_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    return (szer * dlug) / 10_000 / math.cos(math.radians(st.session_state.kat))

def nachylenie_procent():
    return math.tan(math.radians(st.session_state.kat)) * 100

def dlugosc_polaci():
    polowa = (st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo) / 200
    return polowa / math.cos(math.radians(st.session_state.kat))

def liczba_krokwi():
    dl_cm = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    return math.ceil(dl_cm / st.session_state.get('rozstaw_dach', 60)) + 1

def obwod_dachu():
    szer = st.session_state.szer + st.session_state.okap_lewo + st.session_state.okap_prawo
    dlug = st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl
    return 2 * (szer + dlug) / 100

# ---------- MENU ----------
st.title("🏗️ Inżynier Szkieletowy Pro")
zakladki = ["Geometria", "Ściany", "Dach", "Podłoga", "Akcesoria", "Kosztorys"]
wybor = st.radio("", zakladki, key='active_tab', horizontal=True)

# ==================== GEOMETRIA ====================
if wybor == "Geometria":
    st.header("📐 Geometria")
    c1, c2 = st.columns(2)
    with c1:
        wys = st.slider("Wysokość (cm)", 200, 600, value=st.session_state.wys, key='wys_slider', on_change=lambda: st.session_state.update(wys=st.session_state.wys_slider))
        st.number_input("Dokładna wysokość (cm)", 200, 600, value=st.session_state.wys, key='wys', on_change=lambda: st.session_state.update(wys_slider=st.session_state.wys))
        szer = st.slider("Szerokość (cm)", 200, 1500, value=st.session_state.szer, key='szer_slider', on_change=lambda: st.session_state.update(szer=st.session_state.szer_slider))
        st.number_input("Dokładna szerokość (cm)", 200, 1500, value=st.session_state.szer, key='szer', on_change=lambda: st.session_state.update(szer_slider=st.session_state.szer))
        dlug = st.slider("Długość (cm)", 200, 2000, value=st.session_state.dlug, key='dlug_slider', on_change=lambda: st.session_state.update(dlug=st.session_state.dlug_slider))
        st.number_input("Dokładna długość (cm)", 200, 2000, value=st.session_state.dlug, key='dlug', on_change=lambda: st.session_state.update(dlug_slider=st.session_state.dlug))
    with c2:
        st.subheader("Parametry")
        st.metric("Powierzchnia podłogi", f"{pow_podlogi():.2f} m²")
        st.metric("Kubatura", f"{kubatura():.2f} m³")
        st.metric("Pow. ścian brutto", f"{pow_scian_brutto():.2f} m²")

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
            dl_desek = st.slider("Dł. handlowa desek (cm)", 200, 1200, step=50, value=st.session_state.dlugosc_desek, key='dlugosc_desek_slider', on_change=lambda: st.session_state.update(dlugosc_desek=st.session_state.dlugosc_desek_slider))
            st.number_input("Dokładna długość (cm)", 200, 1200, value=st.session_state.dlugosc_desek, step=5, key='dlugosc_desek', on_change=lambda: st.session_state.update(dlugosc_desek_slider=st.session_state.dlugosc_desek))

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

    else:
        st.subheader("🧵 Wykończenie ścian")
        st.checkbox("Dodatkowa izolacja termiczna 5 cm + kantówki", key='dodatkowa_izolacja')
        pow_netto = pow_scian_netto()

        st.markdown("### Poszycie wewnętrzne")
        grub_map = {"95x45":100, "145x45":150, "195x45":200}
        gr = grub_map[st.session_state.slupki]
        st.write(f"**Wełna Knauf Ecose {gr} mm**")
        pokrycie_map = {100:5.76, 150:4.32, 200:2.88}
        paczki = math.ceil(pow_netto / pokrycie_map[gr])
        st.write(f"Powierzchnia: {pow_netto:.1f} m² → {paczki} paczek")
        cena_dom = 35.0
        own = st.checkbox("Własna cena", key='use_wlasna_cena_welna_glowna')
        if own:
            cena = st.number_input("Cena za m²", value=st.session_state.cena_welna_glowna, key='cena_welna_glowna')
        else:
            cena = cena_dom
            st.caption(f"Cena domyślna: {cena_dom:.2f} zł/m²")
        st.write(f"Koszt: **{pow_netto * cena:.2f} zł**")

        if st.session_state.dodatkowa_izolacja:
            st.write("**Wełna 50 mm (dodatkowa)**")
            paczki5 = math.ceil(pow_netto / 8.64)
            st.write(f"Powierzchnia: {pow_netto:.1f} m² → {paczki5} paczek")
            own5 = st.checkbox("Własna cena", key='use_wlasna_cena_welna_dod')
            if own5:
                cena5 = st.number_input("Cena za m²", value=st.session_state.cena_welna_dod, key='cena_welna_dod')
            else:
                cena5 = 25.0
                st.caption("Cena domyślna: 25.00 zł/m²")
            st.write(f"Koszt: **{pow_netto * cena5:.2f} zł**")

            st.write("**Kantówki 45x45 mm**")
            rozstaw = st.slider("Rozstaw (cm)", 30, 80, step=5, value=st.session_state.rozstaw_kantowek, key='rozstaw_kantowek')
            rzedy = math.ceil(st.session_state.wys / 100 / (rozstaw/100)) + 1
            mb_kant = rzedy * obwod_scian()
            st.write(f"Długość: {mb_kant:.1f} mb")
            own_k = st.checkbox("Własna cena", key='use_wlasna_cena_kantowki')
            if own_k:
                cena_k = st.number_input("Cena za mb", value=st.session_state.cena_kantowki, key='cena_kantowki')
            else:
                cena_k = 6.0
                st.caption("Cena domyślna: 6.00 zł/mb")
            st.write(f"Koszt: **{mb_kant * cena_k:.2f} zł**")

        # Checkboxy dla OSB i GK
        uzyj_osb = st.checkbox("Płyta OSB-3 wewnętrzna", value=st.session_state.uzyj_osb_wew, key='uzyj_osb_wew')
        if uzyj_osb:
            st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_wew')
            own_osb = st.checkbox("Własna cena", key='use_wlasna_cena_osb_wew')
            if own_osb:
                cena_osb = st.number_input("Cena za m²", value=st.session_state.cena_osb_wew, key='cena_osb_wew')
            else:
                cena_osb = 18.0
                st.caption("Cena domyślna: 18.00 zł/m²")
            st.write(f"Powierzchnia: {pow_netto:.1f} m², Koszt: **{pow_netto * cena_osb:.2f} zł**")

        uzyj_gk = st.checkbox("Płyta gipsowo-kartonowa 12,5 mm", value=st.session_state.uzyj_gk_wew, key='uzyj_gk_wew')
        if uzyj_gk:
            own_gk = st.checkbox("Własna cena", key='use_wlasna_cena_gk')
            if own_gk:
                cena_gk = st.number_input("Cena za m²", value=st.session_state.cena_gk, key='cena_gk')
            else:
                cena_gk = 15.0
                st.caption("Cena domyślna: 15.00 zł/m²")
            st.write(f"Powierzchnia: {pow_netto:.1f} m², Koszt: **{pow_netto * cena_gk:.2f} zł**")

        st.write("**Paroizolacja**")
        paro_opcje = {"Folia PE 0,2mm":3.5, "Folia PE 0,3mm":4.8, "Folia aluminiowa":8.2, "Membrana paroszczelna":6.5}
        wybor_paro = st.selectbox("Rodzaj", list(paro_opcje.keys()), key='paroizolacja')
        own_paro = st.checkbox("Własna cena", key='use_wlasna_cena_paro')
        if own_paro:
            cena_paro = st.number_input("Cena za m²", value=st.session_state.cena_paro, key='cena_paro')
        else:
            cena_paro = paro_opcje[wybor_paro]
            st.caption(f"Cena domyślna: {cena_paro:.2f} zł/m²")
        st.write(f"Powierzchnia: {pow_netto:.1f} m², Koszt: **{pow_netto * cena_paro:.2f} zł**")

        # Poszycie zewnętrzne
        st.markdown("### Poszycie zewnętrzne")
        st.write("**Płyta OSB-3 zewnętrzna**")
        st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_zew')
        own_osz = st.checkbox("Własna cena", key='use_wlasna_cena_osb_zew')
        if own_osz:
            cena_osz = st.number_input("Cena za m²", value=st.session_state.cena_osb_zew, key='cena_osb_zew')
        else:
            cena_osz = 18.0
            st.caption("Cena domyślna: 18.00 zł/m²")
        st.write(f"Powierzchnia: {pow_netto:.1f} m², Koszt: **{pow_netto * cena_osz:.2f} zł**")

        st.write("**Wiatroizolacja**")
        wiatro_opcje = {"Membrana Standard 120g":120, "Membrana Premium 160g":160, "Folia wiatrochronna 100g":100}
        wybor_w = st.selectbox("Rodzaj", list(wiatro_opcje.keys()), key='wiatro')
        pow_zapas = pow_netto * 1.1
        own_w = st.checkbox("Własna cena", key='use_wlasna_cena_wiatro')
        if own_w:
            cena_w = st.number_input("Cena za m²", value=st.session_state.cena_wiatro, key='cena_wiatro')
        else:
            cena_w = 8.0
            st.caption("Cena domyślna: 8.00 zł/m²")
        st.write(f"Powierzchnia (z 10% zapasem): {pow_zapas:.2f} m², Koszt: **{pow_zapas * cena_w:.2f} zł**")

# ==================== DACH ====================
elif wybor == "Dach":
    st.header("🔺 Dach")
    dach_opcje = st.radio("", ["Konstrukcja dachu", "Wykończenie dachu"], key='dach_podstrona', horizontal=True)

    if dach_opcje == "Konstrukcja dachu":
        st.subheader("Rozstaw belek")
        st.selectbox("Rozstaw (cm)", [30,40,60], key='rozstaw_dach')
        st.subheader("Kąt nachylenia")
        kat = st.slider("Kąt (°)", 0, 45, value=st.session_state.kat, key='kat')
        st.markdown(f"<h2 style='text-align:center; color:#e74c3c;'>{nachylenie_procent():.1f}%</h2>", unsafe_allow_html=True)
        st.subheader("Okapy")
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Przód (cm)", 0, 100, value=st.session_state.okap_przod, key='okap_przod')
            st.slider("Lewo (cm)", 0, 100, value=st.session_state.okap_lewo, key='okap_lewo')
        with c2:
            st.slider("Tył (cm)", 0, 100, value=st.session_state.okap_tyl, key='okap_tyl')
            st.slider("Prawo (cm)", 0, 100, value=st.session_state.okap_prawo, key='okap_prawo')
        st.divider()
        st.markdown(f"<h3 style='text-align:center;'>Powierzchnia dachu: {pow_dachu():.2f} m²</h3>", unsafe_allow_html=True)

    else:
        st.subheader("Wykończenie dachu")
        st.selectbox("Pokrycie", ["Papa", "Blachodachówka", "Gont bitumiczny", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")
        st.markdown("---")

        if st.session_state.pokrycie == "Papa":
            st.markdown("#### Papa podkładowa")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                dl_pod = st.slider("Długość (m)", 5.0, 20.0, step=0.5, value=st.session_state.dlugosc_rolki_papa_podklad, key='dl_pod_slider', on_change=lambda: st.session_state.update(dlugosc_rolki_papa_podklad=st.session_state.dl_pod_slider))
                st.number_input("Dokładna długość (m)", 5.0, 20.0, value=st.session_state.dlugosc_rolki_papa_podklad, step=0.5, key='dlugosc_rolki_papa_podklad', on_change=lambda: st.session_state.update(dl_pod_slider=st.session_state.dlugosc_rolki_papa_podklad))
            with col_p2:
                szer_pod = st.slider("Szerokość (m)", 0.5, 2.0, step=0.1, value=st.session_state.szerokosc_rolki_papa_podklad, key='szer_pod_slider', on_change=lambda: st.session_state.update(szerokosc_rolki_papa_podklad=st.session_state.szer_pod_slider))
                st.number_input("Dokładna szerokość (m)", 0.5, 2.0, value=st.session_state.szerokosc_rolki_papa_podklad, step=0.1, key='szerokosc_rolki_papa_podklad', on_change=lambda: st.session_state.update(szer_pod_slider=st.session_state.szerokosc_rolki_papa_podklad))
                zakl_pod = st.slider("Zakład (m)", 0.05, 0.30, step=0.01, value=st.session_state.zaklad_papa_podklad, key='zakl_pod_slider', on_change=lambda: st.session_state.update(zaklad_papa_podklad=st.session_state.zakl_pod_slider))
                st.number_input("Dokładny zakład (m)", 0.05, 0.30, value=st.session_state.zaklad_papa_podklad, step=0.01, key='zaklad_papa_podklad', on_change=lambda: st.session_state.update(zakl_pod_slider=st.session_state.zaklad_papa_podklad))

            st.markdown("#### Papa wierzchnia")
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                dl_w = st.slider("Długość (m)", 5.0, 20.0, step=0.5, value=st.session_state.dlugosc_rolki_papa_wierzch, key='dl_w_slider', on_change=lambda: st.session_state.update(dlugosc_rolki_papa_wierzch=st.session_state.dl_w_slider))
                st.number_input("Dokładna długość (m)", 5.0, 20.0, value=st.session_state.dlugosc_rolki_papa_wierzch, step=0.5, key='dlugosc_rolki_papa_wierzch', on_change=lambda: st.session_state.update(dl_w_slider=st.session_state.dlugosc_rolki_papa_wierzch))
            with col_w2:
                szer_w = st.slider("Szerokość (m)", 0.5, 2.0, step=0.1, value=st.session_state.szerokosc_rolki_papa_wierzch, key='szer_w_slider', on_change=lambda: st.session_state.update(szerokosc_rolki_papa_wierzch=st.session_state.szer_w_slider))
                st.number_input("Dokładna szerokość (m)", 0.5, 2.0, value=st.session_state.szerokosc_rolki_papa_wierzch, step=0.1, key='szerokosc_rolki_papa_wierzch', on_change=lambda: st.session_state.update(szer_w_slider=st.session_state.szerokosc_rolki_papa_wierzch))
                zakl_w = st.slider("Zakład (m)", 0.05, 0.30, step=0.01, value=st.session_state.zaklad_papa_wierzch, key='zakl_w_slider', on_change=lambda: st.session_state.update(zaklad_papa_wierzch=st.session_state.zakl_w_slider))
                st.number_input("Dokładny zakład (m)", 0.05, 0.30, value=st.session_state.zaklad_papa_wierzch, step=0.01, key='zaklad_papa_wierzch', on_change=lambda: st.session_state.update(zakl_w_slider=st.session_state.zaklad_papa_wierzch))

            szer_efekt_w = st.session_state.szerokosc_rolki_papa_wierzch - st.session_state.zaklad_papa_wierzch
            szer_polaci = (st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl) / 100
            pasy_w = math.ceil(szer_polaci / szer_efekt_w)
            opt_szer = pasy_w * szer_efekt_w
            roznica = opt_szer - szer_polaci
            if abs(roznica) < 0.001:
                st.success("✅ Okapy są optymalne.")
            else:
                st.error(f"⚠️ Różnica: {roznica*100:.1f} cm")
                if st.button("🎯 Dopasuj okapy", use_container_width=True):
                    st.session_state.pokaz_wybor = True
                if st.session_state.get('pokaz_wybor'):
                    przod = st.checkbox("Przód", True, key='opt_przod')
                    tyl = st.checkbox("Tył", True, key='opt_tyl')
                    lewo = st.checkbox("Lewo", False, key='opt_lewo')
                    prawo = st.checkbox("Prawo", False, key='opt_prawo')
                    rowno = st.checkbox("Równomiernie", True, key='opt_rownomiernie')
                    if st.button("✅ Zastosuj"):
                        zmiana = roznica * 100
                        liczba = sum([przod, tyl, lewo, prawo])
                        if liczba:
                            delta = zmiana / (liczba if rowno else 1)
                            if przod: st.session_state.okap_przod = max(0, min(100, st.session_state.okap_przod + delta))
                            if tyl: st.session_state.okap_tyl = max(0, min(100, st.session_state.okap_tyl + delta))
                            if lewo: st.session_state.okap_lewo = max(0, min(100, st.session_state.okap_lewo + delta))
                            if prawo: st.session_state.okap_prawo = max(0, min(100, st.session_state.okap_prawo + delta))
                            st.session_state.pokaz_wybor = False
                            st.rerun()
        else:
            st.write("Materiały dla " + st.session_state.pokrycie)

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
    wkr_cies = liczba_slupkow() * 4
    op_cies = math.ceil(wkr_cies / 100)
    mb_tasm = obwod_scian() * 2
    rolki_tasm = math.ceil(mb_tasm / 10)
    kat = liczba_slupkow() * 2
    st.markdown(f"""
    | Produkt | Ilość | Opakowania | Koszt |
    |---------|-------|------------|-------|
    | Wkręty OSB | {wkrety_osb} szt. | {op_osb} op. | {op_osb*35:.0f} zł |
    | Wkręty ciesielskie | {wkr_cies} szt. | {op_cies} op. | {op_cies*45:.0f} zł |
    | Taśma butylowa | {mb_tasm:.1f} mb | {rolki_tasm} rolki | {rolki_tasm*25:.0f} zł |
    | Kątowniki | {kat} szt. | - | {kat*3.5:.0f} zł |
    """)

# ==================== KOSZTORYS ====================
elif wybor == "Kosztorys":
    st.header("📊 Kosztorys zbiorczy")
    cena_drewna = st.session_state.cena_drewna_m3 if st.session_state.use_wlasna_cena else 1600.0
    m3 = objetosc_drewna()
    pow_netto = pow_scian_netto()
    # ... (reszta kosztorysu analogiczna jak wcześniej)
    st.write("Pełny kosztorys – funkcja w przygotowaniu.")
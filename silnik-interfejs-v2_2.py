"""
Inżynier Szkieletowy Pro — silnik_interfejs
Wersja: v2.2

CHANGELOG:
v2.2 (UI/UX)
  - Nowy, spójny motyw wizualny: ciemne, "inżynierskie" tło + jednolita paleta akcentów
    (czerwony=ostrzeżenie/mniej, pomarańczowy=standard, niebieski=więcej/info, zielony=OK)
  - Helper sekcja() -- każdy blok funkcjonalny (materiał, otwory, papa, wełna, itd.)
    jest teraz w jednolitej "karcie" z tytułem i wyraźną ramką, zamiast ręcznie
    stylowanych <hr> o różnej grubości/kolorze w różnych miejscach
  - FIX: tabela "Pełna lista odległości" w zakładce Fundamenty nie renderowała się
    poprawnie (markdown-table wrzucona w div flexbox). Zastąpiona natywnym układem
    3 kolumn Streamlit z wyśrodkowanym tekstem w każdej komórce
  - Ujednolicone odstępy między sekcjami w całej appce (Geometria, Ściany, Dach,
    Podłoga, Akcesoria, Kosztorys, Fundamenty)
  - Tabela w Akcesoriach dopasowana kolorystycznie do reszty motywu (był hardkodowany
    jasny styl niepasujący do pozostałych zakładek)
v2.1 (refaktor)
  - FIX: edycja wymiarów otworu (okno/drzwi) nie zapisywała się do obliczeń
    (powierzchnia netto ścian i kosztorys liczyły się zawsze na wartościach domyślnych)
  - Nowe funkcje pomocnicze UI: slider_z_wpisem(), pole_ceny(), pobierz_cene(), oblicz_papa()
  - Usunięcie duplikacji: logika liczby rolek papy scalona (Dach + Kosztorys korzystają
    teraz z jednego źródła prawdy zamiast dwóch kopii tego samego kodu)
  - Usunięte zdublowane importy i śmieciowe komentarze
  - Dodane brakujące klucze domyślne w init_state (rozstaw_dach, fundament_liczba_rzedow)
v2.0 (baza)
  - Wersja wyjściowa: geometria, ściany, dach, podłoga, akcesoria, kosztorys, fundamenty
"""
import streamlit as st
import math
import base64
import uuid
from fpdf import FPDF
import tempfile
import os
from contextlib import contextmanager

st.set_page_config(layout="wide", page_title="Inżynier Szkieletowy Pro")

# ---------- MOTYW WIZUALNY: ciemny, inżynierski ----------
# Jedna paleta i jeden zestaw odstępów dla całej appki -- zamiast stylowania
# każdej sekcji z osobna (jak było wcześniej), żeby wszystko wyglądało spójnie.
st.markdown("""
<style>
:root {
    --bg-glowne: #171c26;
    --bg-karta: #232a37;
    --brzeg-karty: #3a4455;
    --tekst: #e8eaed;
    --tekst-przygaszony: #9aa4b5;
    --akcent-czerwony: #e74c3c;   /* ostrzeżenia / "mniej" / krytyczne */
    --akcent-pomaranczowy: #f39c12; /* stan standardowy / neutralny */
    --akcent-niebieski: #2980b9;  /* informacje / "więcej" / bezpieczne */
    --akcent-zielony: #27ae60;    /* potwierdzenia / OK */
}

.stApp { background-color: var(--bg-glowne); color: var(--tekst); }

h1, h2, h3, h4, p, span, label, .stMarkdown { color: var(--tekst); }

/* Karta sekcji -- podstawowa jednostka wizualna całej appki */
.sekcja-karta {
    background-color: var(--bg-karta);
    border: 1px solid var(--brzeg-karty);
    border-radius: 10px;
    padding: 4px 18px 14px 18px;
    margin: 0 0 20px 0;
}
.sekcja-tytul {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--tekst);
    margin: 10px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--brzeg-karty);
}

/* Natywne kontenery Streamlit z border=True -- dopasowanie do motywu */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--bg-karta);
    border-color: var(--brzeg-karty) !important;
    border-radius: 10px !important;
    margin-bottom: 18px;
}

/* Metryki */
div[data-testid="stMetric"] {
    background-color: var(--bg-karta);
    border: 1px solid var(--brzeg-karty);
    border-radius: 8px;
    padding: 10px 14px;
}

/* Przyciski */
.stButton button {
    border-radius: 6px;
    border: 1px solid var(--brzeg-karty);
}

/* Zakładki główne (radio horizontal) jako "pigułki" */
div[role="radiogroup"] { gap: 6px; }

hr { border-color: var(--brzeg-karty) !important; margin: 18px 0 !important; }
</style>
""", unsafe_allow_html=True)


@contextmanager
def sekcja(tytul):
    """
    Jednolita 'karta' sekcji -- używana w całej appce zamiast ręcznie
    stylowanych <hr> i nagłówków. Grupuje powiązane ze sobą kontrolki
    i wizualnie oddziela je od reszty widoku.
    Użycie:
        with sekcja("🧱 Materiał i rozstaw"):
            st.selectbox(...); st.slider(...)
    """
    with st.container(border=True):
        st.markdown(f"<div class='sekcja-tytul'>{tytul}</div>", unsafe_allow_html=True)
        yield


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
        'uzyj_osb_wew': True, 'uzyj_gk_wew': True,
        'poszycie_wew': False,
        'pokaz_wybor': False,
        # Fundamenty
        'fundament_grunt': 'Piasek średniozagęszczony',
        'fundament_glebokosc': 100,
        'fundament_srednica': 60,
        'fundament_rozstaw': 150,
        'fundament_liczba_rzedow': 0,
        'rozstaw_dach': 60,
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

def update_poszycie_wew():
    st.session_state.poszycie_wew = st.session_state.poszycie_wew_widget

def update_dodatkowa_izolacja():
    st.session_state.dodatkowa_izolacja = st.session_state.dodatkowa_izolacja_widget

# ---------- FUNKCJE POMOCNICZE UI (żeby nie powtarzać kodu) ----------

def slider_z_wpisem(etykieta, minv, maxv, klucz, step=1, etykieta_liczby="Dokładna wartość"):
    """
    Jeden wiersz zamiast dwóch powtarzanych widżetów: slider + number_input
    zsynchronizowane dwukierunkowo przez wspólny 'kanoniczny' klucz stanu sesji.
    Ostateczna wartość zawsze dostępna pod st.session_state[klucz].
    """
    klucz_slider = f"{klucz}_slider"
    if klucz not in st.session_state:
        st.session_state[klucz] = minv
    if klucz_slider not in st.session_state:
        st.session_state[klucz_slider] = st.session_state[klucz]

    def _ze_slidera():
        st.session_state[klucz] = st.session_state[klucz_slider]

    def _z_wpisu():
        st.session_state[klucz_slider] = st.session_state[klucz]

    st.slider(etykieta, minv, maxv, step=step, key=klucz_slider, on_change=_ze_slidera)
    st.number_input(etykieta_liczby, minv, maxv, step=step, key=klucz, on_change=_z_wpisu)
    return st.session_state[klucz]

def pole_ceny(cena_domyslna, klucz_wlasna, klucz_cena, jednostka="zł/m²", cols_ratio=(1, 2)):
    """Checkbox 'Własna cena' + number_input albo info o cenie domyślnej. Zwraca aktualną cenę."""
    if klucz_cena not in st.session_state:
        st.session_state[klucz_cena] = cena_domyslna
    col_a, col_b = st.columns(list(cols_ratio))
    wlasna = col_a.checkbox("Własna cena", key=klucz_wlasna)
    if wlasna:
        cena = col_b.number_input(f"Cena ({jednostka})", value=st.session_state[klucz_cena], key=klucz_cena)
    else:
        cena = cena_domyslna
        col_b.write(f"Cena domyślna: {cena_domyslna:.2f} {jednostka}")
    return cena

def pobierz_cene(klucz_wlasna, klucz_cena, cena_domyslna):
    """Wersja bez renderowania widżetów – do użycia w Kosztorysie, gdzie tylko odczytujemy ustawienia z innych zakładek."""
    return st.session_state[klucz_cena] if st.session_state.get(klucz_wlasna) else cena_domyslna

def oblicz_papa():
    """Wspólna logika liczby rolek papy podkładowej/wierzchniej – używana w zakładce Dach i w Kosztorysie,
    żeby te dwa miejsca nigdy się nie rozjechały."""
    szer_polaci = (st.session_state.dlug + st.session_state.okap_przod + st.session_state.okap_tyl) / 100
    dl_pol = dlugosc_polaci()

    szer_ef_pod = st.session_state.szerokosc_rolki_papa_podklad - st.session_state.zaklad_papa_podklad
    pasy_pod = math.ceil(szer_polaci / szer_ef_pod)
    laczna_dl_pod = 2 * pasy_pod * dl_pol
    rolki_pod = math.ceil(laczna_dl_pod / st.session_state.dlugosc_rolki_papa_podklad)

    szer_ef_w = st.session_state.szerokosc_rolki_papa_wierzch - st.session_state.zaklad_papa_wierzch
    pasy_w = math.ceil(szer_polaci / szer_ef_w)
    laczna_dl_w = 2 * pasy_w * dl_pol
    rolki_w = math.ceil(laczna_dl_w / st.session_state.dlugosc_rolki_papa_wierzch)

    return {
        'szer_polaci': szer_polaci, 'dl_pol': dl_pol,
        'szer_efekt_w': szer_ef_w, 'pasy_pod': pasy_pod, 'rolki_pod': rolki_pod,
        'pasy_w': pasy_w, 'rolki_w': rolki_w,
    }

# ---------- MENU ----------
st.title("🏗️ Inżynier Szkieletowy Pro")

# ========== SŁOWNIK FUNKCJI (dodajemy nowe moduły TUTAJ) ==========
def geometria_tab():
    st.header("📐 Geometria")
    c1, c2 = st.columns(2)
    with c1:
        with sekcja("📏 Wymiary budynku"):
            slider_z_wpisem("Wysokość (cm)", 200, 600, 'wys', etykieta_liczby="Dokładna wysokość (cm)")
            slider_z_wpisem("Szerokość (cm)", 200, 1500, 'szer', etykieta_liczby="Dokładna szerokość (cm)")
            slider_z_wpisem("Długość (cm)", 200, 2000, 'dlug', etykieta_liczby="Dokładna długość (cm)")
    with c2:
        with sekcja("📊 Parametry"):
            st.metric("Powierzchnia podłogi", f"{pow_podlogi():.2f} m²")
            st.metric("Kubatura", f"{kubatura():.2f} m³")
            st.metric("Pow. ścian brutto", f"{pow_scian_brutto():.2f} m²")

def sciany_tab():
    st.header("🧱 Ściany")
    sciany_opcje = st.radio("", ["Konstrukcja ścian", "Wykończenie ścian"], key='sciany_podstrona', horizontal=True)
    if sciany_opcje == "Konstrukcja ścian":
        with sekcja("🧱 Materiał i rozstaw"):
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Przekrój słupków", ["95x45", "145x45", "195x45"], key='slupki')
                st.selectbox("Rozstaw słupków (cm)", [60, 120], key='rozstaw')
            with col2:
                slider_z_wpisem("Dł. handlowa desek (cm)", 200, 1200, 'dlugosc_desek', step=50, etykieta_liczby="Dokładna długość (cm)")

        with sekcja("🚪 Otwory"):
            for o in st.session_state.otwory:
                oid = o['id']
                cols = st.columns([2,2,2,1])
                o['nazwa'] = cols[0].text_input("Nazwa", o.get('nazwa',''), key=f"nazwa_{oid}")
                o['szer'] = cols[1].number_input("Szer (cm)", 30, 500, o.get('szer',100), key=f"szer_{oid}")
                o['wys'] = cols[2].number_input("Wys (cm)", 30, 500, o.get('wys',120), key=f"wys_{oid}")
                if cols[3].button("❌", key=f"del_{oid}"):
                    st.session_state.otwory = [x for x in st.session_state.otwory if x['id'] != oid]
                    st.rerun()
            if st.button("➕ Dodaj otwór"):
                st.session_state.otwory.append({'id': str(uuid.uuid4()), 'nazwa':'Okno', 'szer':100, 'wys':120})
                st.rerun()

        with sekcja("🪵 Zapotrzebowanie na drewno"):
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

        with sekcja("💰 Koszt drewna"):
            use_wlasna = st.checkbox("Użyj własnej ceny za m³", key='use_wlasna_cena')
            if use_wlasna:
                st.number_input("Twoja cena za m³", value=st.session_state.cena_drewna_m3, step=100.0, key='cena_drewna_m3')
                koszt = m3 * st.session_state.cena_drewna_m3
                st.write(f"Koszt wg Twojej ceny: **{koszt:.2f} zł**")
            else:
                koszt = m3 * 1600.0
                st.write(f"Koszt (cena domyślna 1600 zł/m³): **{koszt:.2f} zł**")
    else:
        st.markdown("<h2 style='text-align: center;'>Wykończenie ścian</h2>", unsafe_allow_html=True)
        pow_netto = pow_scian_netto()
        st.markdown("""<style>div[data-testid="stCheckbox"] label {font-size:1.8em;font-weight:bold;display:flex;justify-content:center;width:100%;}</style>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.checkbox("Poszycie wewnętrzne", value=st.session_state.poszycie_wew, key='poszycie_wew_widget', on_change=update_poszycie_wew)
        if st.session_state.poszycie_wew:
            grub_map = {"95x45":100, "145x45":150, "195x45":200}
            gr = grub_map[st.session_state.slupki]
            pokrycie_map = {100:5.76, 150:4.32, 200:2.88}
            with sekcja(f"🧶 Wełna Knauf Ecose {gr} mm"):
                paczki = math.ceil(pow_netto / pokrycie_map[gr])
                cena = pole_ceny(35.0, 'use_wlasna_cena_welna_glowna', 'cena_welna_glowna')
                st.write(f"Powierzchnia: **{pow_netto:.1f} m²** → **{paczki} paczek** (razem {paczki*pokrycie_map[gr]:.1f} m²)")
                st.write(f"Koszt: **{pow_netto * cena:.2f} zł**")

            with sekcja("🧶 Dodatkowa izolacja termiczna"):
                st.checkbox("Dodatkowa izolacja termiczna 5 cm + kantówki", value=st.session_state.dodatkowa_izolacja, key='dodatkowa_izolacja_widget', on_change=update_dodatkowa_izolacja)
                if st.session_state.dodatkowa_izolacja:
                    st.markdown("**Wełna Knauf Ecose 50 mm (dodatkowa)**")
                    paczki5 = math.ceil(pow_netto / 8.64)
                    cena5 = pole_ceny(25.0, 'use_wlasna_cena_welna_dod', 'cena_welna_dod')
                    st.write(f"Powierzchnia: **{pow_netto:.1f} m²** → **{paczki5} paczek**")
                    st.write(f"Koszt: **{pow_netto * cena5:.2f} zł**")
                    st.divider()
                    st.markdown("**Kantówki 45x45 mm (poprzeczne)**")
                    rozstaw = st.slider("Rozstaw kantówek (cm)", 30, 80, step=5, value=st.session_state.rozstaw_kantowek, key='rozstaw_kantowek')
                    rzedy = math.ceil(st.session_state.wys / 100 / (rozstaw/100)) + 1
                    mb_kant = rzedy * obwod_scian()
                    cena_k = pole_ceny(6.0, 'use_wlasna_cena_kantowki', 'cena_kantowki', jednostka="zł/mb")
                    st.write(f"Długość: **{mb_kant:.1f} mb**")
                    st.write(f"Koszt: **{mb_kant * cena_k:.2f} zł**")

            with sekcja("🌫️ Paroizolacja"):
                paro_opcje = {"Folia PE 0,2mm":3.5, "Folia PE 0,3mm":4.8, "Folia aluminiowa":8.2, "Membrana paroszczelna":6.5}
                wybor_paro = st.selectbox("Rodzaj", list(paro_opcje.keys()), key='paroizolacja')
                cena_paro_dom = paro_opcje[wybor_paro]
                cena_paro = pole_ceny(cena_paro_dom, 'use_wlasna_cena_paro', 'cena_paro')
                st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
                st.write(f"Koszt: **{pow_netto * cena_paro:.2f} zł**")

            with sekcja("📋 Płyta OSB-3 wewnętrzna"):
                uzyj_osb = st.checkbox("Płyta OSB-3 wewnętrzna", value=st.session_state.uzyj_osb_wew, key='uzyj_osb_wew')
                if uzyj_osb:
                    st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_wew')
                    cena_osb = pole_ceny(18.0, 'use_wlasna_cena_osb_wew', 'cena_osb_wew')
                    st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
                    st.write(f"Koszt: **{pow_netto * cena_osb:.2f} zł**")

            with sekcja("📋 Płyta gipsowo-kartonowa 12,5 mm"):
                uzyj_gk = st.checkbox("Płyta gipsowo-kartonowa 12,5 mm", value=st.session_state.uzyj_gk_wew, key='uzyj_gk_wew')
                if uzyj_gk:
                    cena_gk = pole_ceny(15.0, 'use_wlasna_cena_gk', 'cena_gk')
                    st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
                    st.write(f"Koszt: **{pow_netto * cena_gk:.2f} zł**")

        st.markdown("<h2 style='text-align: center;'>Poszycie zewnętrzne</h2>", unsafe_allow_html=True)
        pow_netto = pow_scian_netto()
        with sekcja("📋 Płyta OSB-3 zewnętrzna"):
            st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_zew')
            cena_osz = pole_ceny(18.0, 'use_wlasna_cena_osb_zew', 'cena_osb_zew')
            st.write(f"Powierzchnia: **{pow_netto:.1f} m²**")
            st.write(f"Koszt: **{pow_netto * cena_osz:.2f} zł**")

        with sekcja("🍃 Wiatroizolacja"):
            wiatro_opcje = {"Membrana Standard 120g":120, "Membrana Premium 160g":160, "Folia wiatrochronna 100g":100}
            wybor_w = st.selectbox("Rodzaj", list(wiatro_opcje.keys()), key='wiatro')
            pow_zapas = pow_netto * 1.1
            cena_w = pole_ceny(8.0, 'use_wlasna_cena_wiatro', 'cena_wiatro')
            st.write(f"Powierzchnia (z 10% zapasem): **{pow_zapas:.2f} m²**")
            st.write(f"Koszt: **{pow_zapas * cena_w:.2f} zł**")

def dach_tab():
    st.header("🔺 Dach")
    dach_opcje = st.radio("", ["Konstrukcja dachu", "Wykończenie dachu"], key='dach_podstrona', horizontal=True)
    if dach_opcje == "Konstrukcja dachu":
        with sekcja("📐 Rozstaw belek i kąt nachylenia"):
            st.selectbox("Rozstaw (cm)", [30,40,60], key='rozstaw_dach')
            st.slider("Kąt (°)", 0, 45, value=st.session_state.kat, key='kat')
            st.markdown(f"<h2 style='text-align:center; color:var(--akcent-czerwony);'>{nachylenie_procent():.1f}%</h2>", unsafe_allow_html=True)

        with sekcja("🏠 Okapy"):
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Przód (cm)", 0, 100, value=st.session_state.okap_przod, key='okap_przod')
                st.number_input("Lewo (cm)", 0, 100, value=st.session_state.okap_lewo, key='okap_lewo')
            with c2:
                st.number_input("Tył (cm)", 0, 100, value=st.session_state.okap_tyl, key='okap_tyl')
                st.number_input("Prawo (cm)", 0, 100, value=st.session_state.okap_prawo, key='okap_prawo')
            st.markdown(f"<h3 style='text-align:center;'>Powierzchnia dachu: {pow_dachu():.2f} m²</h3>", unsafe_allow_html=True)
    else:
        st.subheader("Wykończenie dachu")
        st.selectbox("Pokrycie", ["Papa", "Blachodachówka", "Gont bitumiczny", "EPDM"], key='pokrycie')
        pow_dach = pow_dachu()
        st.write(f"Powierzchnia do pokrycia: **{pow_dach:.2f} m²**")
        if st.session_state.pokrycie == "Papa":
            with sekcja("🧾 Papa podkładowa"):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    slider_z_wpisem("Długość (m)", 5.0, 20.0, 'dlugosc_rolki_papa_podklad', step=0.5, etykieta_liczby="Dokładna długość (m)")
                with col_p2:
                    slider_z_wpisem("Szerokość (m)", 0.5, 2.0, 'szerokosc_rolki_papa_podklad', step=0.1, etykieta_liczby="Dokładna szerokość (m)")
                    slider_z_wpisem("Zakład (m)", 0.05, 0.30, 'zaklad_papa_podklad', step=0.01, etykieta_liczby="Dokładny zakład (m)")

            with sekcja("🧾 Papa wierzchnia"):
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    slider_z_wpisem("Długość (m)", 5.0, 20.0, 'dlugosc_rolki_papa_wierzch', step=0.5, etykieta_liczby="Dokładna długość (m)")
                with col_w2:
                    slider_z_wpisem("Szerokość (m)", 0.5, 2.0, 'szerokosc_rolki_papa_wierzch', step=0.1, etykieta_liczby="Dokładna szerokość (m)")
                    slider_z_wpisem("Zakład (m)", 0.05, 0.30, 'zaklad_papa_wierzch', step=0.01, etykieta_liczby="Dokładny zakład (m)")

            papa = oblicz_papa()
            szer_efekt_w = papa['szer_efekt_w']
            szer_polaci = papa['szer_polaci']
            pasy_w = papa['pasy_w']
            opt_szer = pasy_w * szer_efekt_w
            roznica = opt_szer - szer_polaci
            with sekcja("📦 Zapotrzebowanie na papę"):
                if abs(roznica) < 0.001:
                    st.success("✅ Okapy są optymalne.")
                else:
                    st.error(f"⚠️ Różnica: {roznica*100:.1f} cm")
                    if st.button("🎯 Dopasuj okapy", use_container_width=True):
                        st.session_state.pokaz_wybor = True
                    if st.session_state.pokaz_wybor:
                        przod = st.checkbox("Przód", True, key='opt_przod')
                        tyl = st.checkbox("Tył", True, key='opt_tyl')
                        lewo = st.checkbox("Lewo", False, key='opt_lewo')
                        prawo = st.checkbox("Prawo", False, key='opt_prawo')
                        rowno = st.checkbox("Równomiernie", True, key='opt_rownomiernie')
                        if st.button("✅ Zastosuj", key='zastosuj_opt'):
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
                # jeśli zmienialiśmy okapy powyżej, liczymy jeszcze raz na świeżych wartościach
                papa = oblicz_papa()
                st.write(f"**Papa podkładowa:** {papa['rolki_pod']} rolki")
                st.write(f"**Papa wierzchnia:** {papa['rolki_w']} rolki")
        elif st.session_state.pokrycie == "Blachodachówka":
            with sekcja("🔩 Blachodachówka"):
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
            with sekcja("🧱 Gont bitumiczny"):
                st.write(f"**Papa podkładowa:** {math.ceil(pow_dach*1.1/10)} rolek")
                st.write(f"**Gonty:** {math.ceil(pow_dach/3)} op.")
                st.write(f"**Masa bitumiczna:** {math.ceil(pow_dach/5)} tubek")
        else:
            with sekcja("🧴 EPDM"):
                st.write(f"**Membrana:** {pow_dach:.1f} m²")
                st.write(f"**Klej kontaktowy:** {math.ceil(pow_dach/5)} l")
                st.write(f"**Primer:** {pow_dach*0.3:.1f} l")
                st.write(f"**Taśma EPDM:** {math.ceil(obwod_dachu()/10)} rolek (10 m/rolka)")

def podloga_tab():
    st.header("🏠 Podłoga")
    with sekcja("🧰 Technika i zapotrzebowanie"):
        st.radio("Technika", ["Standardowa","Ze stołem roboczym"], key='technika_podlogi')
        pow_p = pow_podlogi()
        st.write(f"Powierzchnia: **{pow_p:.2f} m²**")
        if st.session_state.technika_podlogi == "Ze stołem roboczym":
            st.write(f"**Płyty OSB 22 mm:** {math.ceil(pow_p*1.1/3)} szt.")
            krot = min(st.session_state.szer, st.session_state.dlug)
            dluz = max(st.session_state.szer, st.session_state.dlug)
            ile_leg = math.ceil(dluz/60)+1
            st.write(f"**Legary:** {ile_leg*krot/100:.1f} mb ({ile_leg} szt.)")

def akcesoria_tab():
    st.header("🔩 Akcesoria")
    pow_osb = pow_scian_netto()
    wkrety_osb = math.ceil(pow_osb * 25 * 1.15)
    op_osb = math.ceil(wkrety_osb / 200)
    wkrety_gk = math.ceil(pow_osb * 20 * 1.15) if st.session_state.get('uzyj_gk_wew', False) else 0
    op_gk = math.ceil(wkrety_gk / 1000) if wkrety_gk else 0
    wkr_cies = liczba_slupkow() * 4
    op_cies = math.ceil(wkr_cies / 100)
    mb_tasm = obwod_scian() * 2
    rolki_tasm = math.ceil(mb_tasm / 10)
    kat = liczba_slupkow() * 2
    html_tabela = f"""
    <table style="width:100%; border-collapse:collapse; color:#e8eaed;">
    <tr style="background:#171c26; font-weight:bold;">
        <th style="padding:8px; text-align:left;">Produkt</th><th style="padding:8px;">Ilość</th><th style="padding:8px;">Opakowania</th><th style="padding:8px;">Cena jedn.</th><th style="padding:8px;">Koszt</th>
    </tr>
    <tr><td style="padding:6px;">Wkręty OSB (Klimas 4,5x60)</td><td style="padding:6px; text-align:center;">{wkrety_osb} szt.</td><td style="padding:6px; text-align:center;">{op_osb} op. (200 szt.)</td><td style="padding:6px; text-align:center;">35 zł/op.</td><td style="padding:6px; text-align:center;">{op_osb*35:.0f} zł</td></tr>
    {f'<tr><td style="padding:6px;">Wkręty GK (Klimas 3,5x25)</td><td style="padding:6px; text-align:center;">{wkrety_gk} szt.</td><td style="padding:6px; text-align:center;">{op_gk} op. (1000 szt.)</td><td style="padding:6px; text-align:center;">20 zł/op.</td><td style="padding:6px; text-align:center;">{op_gk*20:.0f} zł</td></tr>' if wkrety_gk else ''}
    <tr><td style="padding:6px;">Wkręty ciesielskie (6x80)</td><td style="padding:6px; text-align:center;">{wkr_cies} szt.</td><td style="padding:6px; text-align:center;">{op_cies} op. (100 szt.)</td><td style="padding:6px; text-align:center;">45 zł/op.</td><td style="padding:6px; text-align:center;">{op_cies*45:.0f} zł</td></tr>
    <tr><td style="padding:6px;">Taśma butylowa</td><td style="padding:6px; text-align:center;">{mb_tasm:.1f} mb</td><td style="padding:6px; text-align:center;">{rolki_tasm} rolki (10 m)</td><td style="padding:6px; text-align:center;">25 zł/rolka</td><td style="padding:6px; text-align:center;">{rolki_tasm*25:.0f} zł</td></tr>
    <tr><td style="padding:6px;">Kątowniki 60x60x40</td><td style="padding:6px; text-align:center;">{kat} szt.</td><td style="padding:6px; text-align:center;">-</td><td style="padding:6px; text-align:center;">3,5 zł/szt.</td><td style="padding:6px; text-align:center;">{kat*3.5:.0f} zł</td></tr>
    </table>
    """
    with sekcja("🛒 Lista zakupów"):
        st.markdown(html_tabela, unsafe_allow_html=True)
        if st.session_state.pokrycie == "Blachodachówka":
            wkr_farm = math.ceil(pow_dachu() / 0.8) * 8
            op_farm = math.ceil(wkr_farm / 250)
            st.markdown(f"**Wkręty farmerskie:** {wkr_farm} szt. → {op_farm} op. × 55 zł = {op_farm*55:.0f} zł")

def kosztorys_tab():
    st.header("📊 Kosztorys zbiorczy")
    cena_drewna_m3 = pobierz_cene('use_wlasna_cena', 'cena_drewna_m3', 1600.0)
    poszycie_wew_active = st.session_state.poszycie_wew
    if poszycie_wew_active:
        cena_welna_gl = pobierz_cene('use_wlasna_cena_welna_glowna', 'cena_welna_glowna', 35.0)
        if st.session_state.dodatkowa_izolacja:
            cena_welna_dod = pobierz_cene('use_wlasna_cena_welna_dod', 'cena_welna_dod', 25.0)
            cena_kant = pobierz_cene('use_wlasna_cena_kantowki', 'cena_kantowki', 6.0)
            rozstaw_kant = st.session_state.rozstaw_kantowek / 100
            rzedy = math.ceil(st.session_state.wys / 100 / rozstaw_kant) + 1
            mb_kant = rzedy * obwod_scian()
        else:
            cena_welna_dod = 0.0; cena_kant = 0.0; mb_kant = 0.0
        cena_osb_wew = pobierz_cene('use_wlasna_cena_osb_wew', 'cena_osb_wew', 18.0)
        cena_gk = pobierz_cene('use_wlasna_cena_gk', 'cena_gk', 15.0)
        paro_opcje = {"Folia PE 0,2mm":3.5, "Folia PE 0,3mm":4.8, "Folia aluminiowa":8.2, "Membrana paroszczelna":6.5}
        cena_paro = pobierz_cene('use_wlasna_cena_paro', 'cena_paro', paro_opcje[st.session_state.paroizolacja])
    else:
        cena_welna_gl = cena_welna_dod = cena_kant = cena_osb_wew = cena_gk = cena_paro = 0.0
        mb_kant = 0.0
    cena_osb_zew = pobierz_cene('use_wlasna_cena_osb_zew', 'cena_osb_zew', 18.0)
    cena_wiatro = pobierz_cene('use_wlasna_cena_wiatro', 'cena_wiatro', 8.0)
    m3_drewna = objetosc_drewna()
    pow_netto = pow_scian_netto()
    pow_dach = pow_dachu()
    koszt_drewno = m3_drewna * cena_drewna_m3
    koszt_welna_gl = pow_netto * cena_welna_gl if poszycie_wew_active else 0.0
    koszt_welna_dod = pow_netto * cena_welna_dod if (poszycie_wew_active and st.session_state.dodatkowa_izolacja) else 0.0
    koszt_kantowki = mb_kant * cena_kant if (poszycie_wew_active and st.session_state.dodatkowa_izolacja) else 0.0
    koszt_osb_wew = pow_netto * cena_osb_wew if (poszycie_wew_active and st.session_state.uzyj_osb_wew) else 0.0
    koszt_gk = pow_netto * cena_gk if (poszycie_wew_active and st.session_state.uzyj_gk_wew) else 0.0
    koszt_paro = pow_netto * cena_paro if poszycie_wew_active else 0.0
    koszt_osb_zew = pow_netto * cena_osb_zew
    koszt_wiatro = pow_netto * 1.1 * cena_wiatro
    if st.session_state.pokrycie == "Papa":
        papa = oblicz_papa()
        koszt_dach = papa['rolki_pod'] * 120 + papa['rolki_w'] * 130 + math.ceil(pow_dach * 0.5 / 5) * 30
    elif st.session_state.pokrycie == "Blachodachówka":
        koszt_dach = math.ceil(pow_dach / 0.8) * 85
    elif st.session_state.pokrycie == "Gont bitumiczny":
        koszt_dach = math.ceil(pow_dach / 3) * 120
    else:
        koszt_dach = pow_dach * 90
    koszt_podloga = pow_podlogi() * 50 if st.session_state.technika_podlogi == "Ze stołem roboczym" else 0.0
    koszt_akc = 150
    suma = (koszt_drewno + koszt_welna_gl + koszt_welna_dod + koszt_kantowki + koszt_osb_wew + koszt_gk + koszt_paro + koszt_osb_zew + koszt_wiatro + koszt_dach + koszt_podloga + koszt_akc)
    with sekcja("💰 Podsumowanie kosztów"):
        st.markdown(f"""
| Kategoria | Koszt |
|-----------|-------|
| Drewno konstrukcyjne | **{koszt_drewno:.2f} zł** |
| Wełna główna | {koszt_welna_gl:.2f} zł |
| Dodatkowa wełna 5 cm | {koszt_welna_dod:.2f} zł |
| Kantówki | {koszt_kantowki:.2f} zł |
| OSB wewnętrzne | {koszt_osb_wew:.2f} zł |
| Płyty GK | {koszt_gk:.2f} zł |
| Paroizolacja | {koszt_paro:.2f} zł |
| OSB zewnętrzne | {koszt_osb_zew:.2f} zł |
| Wiatroizolacja | {koszt_wiatro:.2f} zł |
| Pokrycie dachu | **{koszt_dach:.2f} zł** |
| Podłoga | {koszt_podloga:.2f} zł |
| Akcesoria | {koszt_akc:.2f} zł |
| **SUMA** | **{suma:.2f} zł** |
""")

# ========== MODUŁ: FUNDAMENTY (funkcje pomocnicze) ==========
def usun_polskie_znaki(text):
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def generuj_slupki_obwodowe(szer_m, dlug_m, rozstaw_cm):
    def slupki_na_boku(dlugosc_m, rozstaw_cm):
        if dlugosc_m <= 0.01:
            return []
        max_przesel = max(1, int(dlugosc_m * 100 / rozstaw_cm))
        for n in range(max_przesel, 0, -1):
            if dlugosc_m / n >= rozstaw_cm / 100:
                krok = dlugosc_m / n
                return [i * krok for i in range(1, n)]
        return []

    punkty = []
    for x in (0, szer_m):
        for y in (0, dlug_m):
            punkty.append({'x': x, 'y': y, 'typ': 'narozny'})
    for y in (0, dlug_m):
        for x in slupki_na_boku(szer_m, rozstaw_cm):
            punkty.append({'x': x, 'y': y, 'typ': 'obwodowy'})
    for x in (0, szer_m):
        for y in slupki_na_boku(dlug_m, rozstaw_cm):
            punkty.append({'x': x, 'y': y, 'typ': 'obwodowy'})
    return punkty

def dodaj_slupki_poprzeczne(punkty, szer_m, dlug_m, liczba_rzedow, rozstaw_cm):
    if liczba_rzedow <= 0:
        return punkty
    x_na_krawedziach = set()
    for p in punkty:
        if p['typ'] in ('narozny', 'obwodowy'):
            x_na_krawedziach.add(round(p['x'], 6))
    x_na_krawedziach.discard(0.0)
    x_na_krawedziach.discard(round(szer_m, 6))
    x_na_krawedziach = sorted(list(x_na_krawedziach))
    for i in range(1, liczba_rzedow + 1):
        y = dlug_m * i / (liczba_rzedow + 1)
        for x in x_na_krawedziach:
            if not any(abs(p['x']-x)<0.001 and abs(p['y']-y)<0.001 for p in punkty):
                punkty.append({'x': x, 'y': y, 'typ': 'poprzeczny'})
    return punkty

def sortuj_slupki(punkty, szer_m, dlug_m):
    obwodowe = [p for p in punkty if p['typ'] in ('narozny', 'obwodowy')]
    unikalne = []
    for p in obwodowe:
        if not any(abs(p['x']-u['x'])<0.001 and abs(p['y']-u['y'])<0.001 for u in unikalne):
            unikalne.append(p)

    dol = sorted([p for p in unikalne if abs(p['y']) < 0.001], key=lambda p: p['x'])
    prawa = sorted([p for p in unikalne if abs(p['x'] - szer_m) < 0.001 and p['y'] > 0.001 and p['y'] < dlug_m - 0.001], key=lambda p: p['y'])
    gora = sorted([p for p in unikalne if abs(p['y'] - dlug_m) < 0.001], key=lambda p: -p['x'])
    lewa = sorted([p for p in unikalne if abs(p['x']) < 0.001 and p['y'] > 0.001 and p['y'] < dlug_m - 0.001], key=lambda p: -p['y'])

    unikalne_obwodowe = dol + prawa + gora + lewa
    poprzeczne = sorted([p for p in punkty if p['typ'] == 'poprzeczny'], key=lambda p: (p['y'], p['x']))
    return unikalne_obwodowe + poprzeczne

def rysuj_odleglosci_na_rysunku(svg, punkty, szer_m, dlug_m, skala):
    def dodaj_odleglosci_dla_pary(p1, p2, orientacja):
        nonlocal svg
        cx1 = 40 + p1['x'] * skala
        cy1 = 40 + (dlug_m - p1['y']) * skala
        cx2 = 40 + p2['x'] * skala
        cy2 = 40 + (dlug_m - p2['y']) * skala
        odl = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2) * 100
        if odl < 0.5:
            return
        if orientacja == 'dol':
            x = (cx1 + cx2) / 2
            y = 40 + dlug_m * skala - 12
        elif orientacja == 'gora':
            x = (cx1 + cx2) / 2
            y = 40 + 15
        elif orientacja == 'lewo':
            x = 40 + 15
            y = (cy1 + cy2) / 2
        elif orientacja == 'prawo':
            x = 40 + szer_m * skala - 15
            y = (cy1 + cy2) / 2
        elif orientacja == 'poprzeczny':
            x = (cx1 + cx2) / 2
            y = cy1 - 10
        svg += f'<text x="{x}" y="{y}" font-size="8" fill="black" text-anchor="middle">{odl:.0f} cm</text>'

    dolne = sorted([p for p in punkty if abs(p['y']) < 0.001], key=lambda p: p['x'])
    for i in range(len(dolne)-1):
        dodaj_odleglosci_dla_pary(dolne[i], dolne[i+1], 'dol')
    gorne = sorted([p for p in punkty if abs(p['y'] - dlug_m) < 0.001], key=lambda p: p['x'])
    for i in range(len(gorne)-1):
        dodaj_odleglosci_dla_pary(gorne[i], gorne[i+1], 'gora')
    lewe = sorted([p for p in punkty if abs(p['x']) < 0.001], key=lambda p: p['y'])
    for i in range(len(lewe)-1):
        dodaj_odleglosci_dla_pary(lewe[i], lewe[i+1], 'lewo')
    prawe = sorted([p for p in punkty if abs(p['x'] - szer_m) < 0.001], key=lambda p: p['y'])
    for i in range(len(prawe)-1):
        dodaj_odleglosci_dla_pary(prawe[i], prawe[i+1], 'prawo')

    poprzeczne = [p for p in punkty if p['typ'] == 'poprzeczny']
    if poprzeczne:
        grupy = {}
        for p in poprzeczne:
            y_r = round(p['y'], 6)
            if y_r not in grupy:
                grupy[y_r] = []
            grupy[y_r].append(p)
        for lista in grupy.values():
            lista.sort(key=lambda p: p['x'])
            for i in range(len(lista)-1):
                dodaj_odleglosci_dla_pary(lista[i], lista[i+1], 'poprzeczny')
    return svg

def create_pdf(szer_m, dlug_m, wybrany_grunt_ascii, glebokosc_cm, srednica_mm, rozstaw_cm,
               liczba_rzedow, ile_final, obc_final, Ndop_final, zapas_final,
               smuklosc, szansa_wyboczenia, punkty_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Tytuł
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Raport - Fundamenty", ln=True, align='C')
    pdf.ln(10)

    # Parametry
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Parametry budynku i gruntu", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, txt=f"Wymiary: {szer_m:.2f} x {dlug_m:.2f} m", ln=True)
    pdf.cell(0, 6, txt=f"Grunt: {wybrany_grunt_ascii}", ln=True)
    pdf.cell(0, 6, txt=f"Glebokosc: {glebokosc_cm} cm, Srednica: {srednica_mm} mm", ln=True)
    pdf.cell(0, 6, txt=f"Rozstaw obwodowy: {rozstaw_cm} cm, Rzedy poprzeczne: {liczba_rzedow}", ln=True)
    pdf.ln(5)

    # Wyniki
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Wyniki obliczen", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, txt=f"Liczba slupkow: {ile_final}", ln=True)
    pdf.cell(0, 6, txt=f"Obciazenie na slupek: {obc_final:.2f} kN", ln=True)
    pdf.cell(0, 6, txt=f"Noscnosc dopuszczalna: {Ndop_final:.2f} kN", ln=True)
    pdf.cell(0, 6, txt=f"Zapas nosci: {zapas_final:.0f}%", ln=True)
    pdf.cell(0, 6, txt=f"Smuklosc: {smuklosc:.0f}, Szansa wyboczenia: {szansa_wyboczenia:.0f}%", ln=True)
    pdf.ln(8)

    # Rysunek schematyczny (proporcjonalny, mieszczący się na A4)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Schemat fundamentu", ln=True)
    pdf.ln(1)

    # --- Stałe geometrii strony A4 i marginesów rysunku ---
    PAGE_H = 297
    PAGE_W = 210
    BOTTOM_PAGE_MARGIN = 15   # margines dolny strony
    TOP_GAP = 12              # miejsce nad rysunkiem na wymiar górnej krawędzi
    BOTTOM_GAP = 20           # miejsce pod rysunkiem na wymiar dolny + przekątną
    SIDE_GAP = 20             # miejsce po bokach na wymiary lewej/prawej krawędzi
    MIN_WYS_RYSUNKU = 60      # jeśli zostało mniej miejsca niż to na stronie -> nowa strona

    margines_x = 25

    # Ile realnie zostało miejsca w pionie na TEJ stronie
    y_start = pdf.get_y() + TOP_GAP
    dostepna_wys = (PAGE_H - BOTTOM_PAGE_MARGIN) - y_start - BOTTOM_GAP

    # Jeśli nad rysunkiem jest za dużo tekstu i rysunek by się nie zmieścił -> nowa strona
    if dostepna_wys < MIN_WYS_RYSUNKU:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Schemat fundamentu (cd.)", ln=True)
        pdf.ln(1)
        y_start = pdf.get_y() + TOP_GAP
        dostepna_wys = (PAGE_H - BOTTOM_PAGE_MARGIN) - y_start - BOTTOM_GAP

    dostepna_szer = PAGE_W - margines_x - SIDE_GAP

    # Skala licz z FAKTYCZNIE dostępnego miejsca (a nie ze sztywnych 190x250)
    skala_pdf = min(dostepna_szer / szer_m, dostepna_wys / dlug_m, 30)  # max 30 mm/m
    skala_pdf = max(skala_pdf, 1)  # zabezpieczenie dla bardzo dużych budynków

    margines_y = y_start
    szer_px = szer_m * skala_pdf
    dlug_px = dlug_m * skala_pdf

    def pdf_xy(p):
        x = margines_x + p['x'] * skala_pdf
        y = margines_y + (dlug_m - p['y']) * skala_pdf
        return x, y

    def dodaj_wymiar_pdf(p1, p2, orientacja):
        x1, y1 = pdf_xy(p1)
        x2, y2 = pdf_xy(p2)
        odl = math.sqrt((p2['x'] - p1['x']) ** 2 + (p2['y'] - p1['y']) ** 2) * 100
        if odl < 0.5:
            return
        pdf.set_font("Arial", size=6)
        if orientacja == 'dol':
            y_l = margines_y + dlug_px + 6
            pdf.line(x1, y_l, x2, y_l)
            pdf.text((x1 + x2) / 2 - 5, y_l + 4, f"{odl:.0f} cm")
        elif orientacja == 'gora':
            y_l = margines_y - 6
            pdf.line(x1, y_l, x2, y_l)
            pdf.text((x1 + x2) / 2 - 5, y_l - 1.5, f"{odl:.0f} cm")
        elif orientacja == 'lewo':
            x_l = margines_x - 6
            pdf.line(x_l, y1, x_l, y2)
            pdf.text(x_l - 14, (y1 + y2) / 2 + 1, f"{odl:.0f}cm")
        elif orientacja == 'prawo':
            x_l = margines_x + szer_px + 6
            pdf.line(x_l, y1, x_l, y2)
            pdf.text(x_l + 2, (y1 + y2) / 2 + 1, f"{odl:.0f}cm")
        elif orientacja == 'poprzeczny':
            pdf.line(x1, y1, x2, y2)
            pdf.text((x1 + x2) / 2 - 5, min(y1, y2) - 2, f"{odl:.0f} cm")
        pdf.set_font("Arial", size=9)

    # Obrys fundamentu
    pdf.rect(margines_x, margines_y, szer_px, dlug_px)

    # Słupki (kwadraciki)
    for p in punkty_final:
        cx, cy = pdf_xy(p)
        pdf.rect(cx - 1.5, cy - 1.5, 3, 3, 'D')

    # --- Wymiary na WSZYSTKICH krawędziach (a nie tylko dolnej) ---
    dolne = sorted([p for p in punkty_final if abs(p['y']) < 0.001], key=lambda p: p['x'])
    for i in range(len(dolne) - 1):
        dodaj_wymiar_pdf(dolne[i], dolne[i + 1], 'dol')

    gorne = sorted([p for p in punkty_final if abs(p['y'] - dlug_m) < 0.001], key=lambda p: p['x'])
    for i in range(len(gorne) - 1):
        dodaj_wymiar_pdf(gorne[i], gorne[i + 1], 'gora')

    lewe = sorted([p for p in punkty_final if abs(p['x']) < 0.001], key=lambda p: p['y'])
    for i in range(len(lewe) - 1):
        dodaj_wymiar_pdf(lewe[i], lewe[i + 1], 'lewo')

    prawe = sorted([p for p in punkty_final if abs(p['x'] - szer_m) < 0.001], key=lambda p: p['y'])
    for i in range(len(prawe) - 1):
        dodaj_wymiar_pdf(prawe[i], prawe[i + 1], 'prawo')

    # --- Wymiary między słupkami poprzecznymi (wewnętrznymi) ---
    poprzeczne = [p for p in punkty_final if p['typ'] == 'poprzeczny']
    if poprzeczne:
        grupy = {}
        for p in poprzeczne:
            y_r = round(p['y'], 6)
            grupy.setdefault(y_r, []).append(p)
        for lista in grupy.values():
            lista.sort(key=lambda p: p['x'])
            for i in range(len(lista) - 1):
                dodaj_wymiar_pdf(lista[i], lista[i + 1], 'poprzeczny')

    # Przekątna (lewy dolny – prawy górny)
    x1_diag = margines_x
    y1_diag = margines_y + dlug_px
    x2_diag = margines_x + szer_px
    y2_diag = margines_y
    pdf.line(x1_diag, y1_diag, x2_diag, y2_diag)
    przekatna_odl = math.sqrt(szer_m ** 2 + dlug_m ** 2) * 100
    pdf.set_font("Arial", size=8)
    pdf.text((x1_diag + x2_diag) / 2 + 2, (y1_diag + y2_diag) / 2, f"{przekatna_odl:.0f} cm")
    pdf.set_font("Arial", size=10)

    # Ustaw kursor DOKŁADNIE pod całym rysunkiem (rect + wymiar dolny), a nie "na oko"
    pdf.set_y(margines_y + dlug_px + BOTTOM_GAP)

    # Tabela odległości
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Odleglosci miedzy slupkami (cm)", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(20, 6, "Start", 1, 0, 'C', True)
    pdf.cell(20, 6, "Koniec", 1, 0, 'C', True)
    pdf.cell(30, 6, "Odleglosc", 1, 1, 'C', True)
    for i in range(len(punkty_final)-1):
        p1 = punkty_final[i]
        p2 = punkty_final[i+1]
        odl = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)*100
        pdf.cell(20, 6, str(i+1), 1, 0, 'C')
        pdf.cell(20, 6, str(i+2), 1, 0, 'C')
        pdf.cell(30, 6, f"{odl:.0f} cm", 1, 1, 'C')

    pdf.ln(5)

    # Klauzula prawna
    klauzula = (
        "Uwaga prawna: Obliczenia wykonano zgodnie z uproszczonymi zasadami Eurokodu 7 (PN-EN 1997). "
        "Wyniki maja charakter orientacyjny i nie stanowia podstawy do wykonania fundamentow bez konsultacji "
        "z uprawnionym konstruktorem lub architektem. Ostateczna decyzje o liczbie, srednicy i glebokosci slupkow "
        "nalezy powierzyc specjaliście posiadajacemu odpowiednie uprawnienia budowlane."
    )
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, txt=usun_polskie_znaki(klauzula))

    return pdf.output(dest='S').encode('latin-1')


# ---------- MODUŁ FUNDAMENTY ----------
def fundamenty_tab():
    st.header("🏛️ Fundamenty – słupki betonowe")

    szer_m = st.session_state.szer / 100
    dlug_m = st.session_state.dlug / 100
    obwod_m = obwod_scian()

    st.info(f"📐 Automatycznie pobrano wymiary budynku: **{szer_m:.2f} × {dlug_m:.2f} m** (obwód: {obwod_m:.1f} m)")

    pow_dach = pow_dachu()
    ciezar_dach = pow_dach * 0.5
    ciezar_scian = obwod_m * (st.session_state.wys / 100) * 0.35
    ciezar_stropu = pow_podlogi() * 0.4
    obciazenie_snieg = pow_dach * 0.5
    calkowite_kn = ciezar_dach + ciezar_scian + ciezar_stropu + obciazenie_snieg

    with sekcja("🔍 Rodzaj podłoża"):
        grunty_wyswietlane = {
            "Piasek luźny": 100,
            "Piasek średniozagęszczony": 200,
            "Piasek zagęszczony": 350,
            "Piasek gliniasty": 150,
            "Glina plastyczna": 100,
            "Glina twardoplastyczna": 200,
            "Żwir zagęszczony": 400,
            "Posadzka skalista": 500,
        }
        wybrany_grunt_wyswietlany = st.selectbox("Wybierz rodzaj gruntu", list(grunty_wyswietlane.keys()), key='fundament_grunt')
        wybrany_grunt_ascii = usun_polskie_znaki(wybrany_grunt_wyswietlany)
        nosnosc_gruntu_kpa = grunty_wyswietlane[wybrany_grunt_wyswietlany]

        with st.expander("🧪 Jak sprawdzić rodzaj gruntu? (test butelkowy)"):
            st.markdown("""
            **Test butelkowy – jak w prosty sposób ocenić grunt na działce:**
            1. Wykop niewielką dziurę na głębokość **80–100 cm** (poniżej warstwy humusu).
            2. Z dna dziury pobierz około **pół szklanki ziemi**.
            3. Wsyp ziemię do przezroczystej butelki (np. 0,5 l) do **⅓ wysokości**.
            4. Dolej **wody do ¾ butelki** i mocno wstrząśnij przez 1 minutę.
            5. Odstaw butelkę na **24 godziny** w nieruchome miejsce.

            **Jak odczytać wynik:**
            - **Piasek**: osad opada szybko (w ciągu kilku minut), woda nad osadem jest prawie przejrzysta. Warstwy: na dnie piasek gruboziarnisty, wyżej drobny.
            - **Glina**: woda pozostaje mętna przez wiele godzin, osad jest jednolity, zbity i tłusty w dotyku (po zlaniu wody).
            - **Piasek gliniasty**: drobne cząstki długo utrzymują się w wodzie, ale na dnie widać warstwę piasku. Po 24 h woda może być lekko mętna.

            Dla budownictwa szkieletowego **najlepsze są piaski i żwiry** – gliny wymagają większych średnic i głębokości słupków.
            """)

    with sekcja("📏 Parametry słupka i rozstaw"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            glebokosc_cm = st.slider("Głębokość słupka (cm)", 60, 150, value=st.session_state.fundament_glebokosc, step=5, key='fundament_glebokosc')
        with col_f2:
            srednica_mm = st.slider("Średnica słupka (mm)", 60, 250, value=st.session_state.fundament_srednica, step=10, key='fundament_srednica')

        st.markdown("**Rozstaw słupków obwodowych**")
        rozstaw_cm = st.slider("Odległość między słupkami (cm)", 60, 250,
                               value=st.session_state.fundament_rozstaw, step=10, key='fundament_rozstaw')

        st.markdown("**Słupki poprzeczne (wewnętrzne)**")
        liczba_rzedow = st.radio(
            "Liczba rzędów poprzecznych",
            [0, 1, 2],
            format_func=lambda x: "Brak" if x == 0 else f"{x} rząd(y)" if x == 1 else f"{x} rzędy",
            horizontal=True,
            key='fundament_liczba_rzedow'
        )

    rozstaw_mniej = rozstaw_cm + 30
    rozstaw_wiecej = max(40, rozstaw_cm - 20)

    def generuj_wariant(rozstaw):
        punkty = generuj_slupki_obwodowe(szer_m, dlug_m, rozstaw)
        punkty = dodaj_slupki_poprzeczne(punkty, szer_m, dlug_m, liczba_rzedow, rozstaw)
        return punkty

    punkty_standard = generuj_wariant(rozstaw_cm)
    punkty_mniej = generuj_wariant(rozstaw_mniej)
    punkty_wiecej = generuj_wariant(rozstaw_wiecej)

    def oblicz_wariant(punkty):
        ile = len(punkty)
        obc = calkowite_kn / ile if ile else 1e9
        r = (srednica_mm / 1000) / 2
        pole = math.pi * r * r
        obwod_sl = 2 * math.pi * r
        h = glebokosc_cm / 100
        N_podst = pole * nosnosc_gruntu_kpa
        N_tarcie = obwod_sl * h * nosnosc_gruntu_kpa * 0.15
        N_calk = N_podst + N_tarcie
        N_dop = N_calk / 2.0
        zapas = ((N_dop / obc) - 1) * 100 if obc > 0 else 999
        smuklosc = (2 * h) / (r / 2) if r > 0 else 0
        szansa_wyboczenia = max(0, min(100, (smuklosc - 50) * 2))
        return ile, obc, N_dop, zapas, smuklosc, szansa_wyboczenia

    ile_std, obc_std, Ndop_std, zapas_std, sm_std, wyb_std = oblicz_wariant(punkty_standard)
    ile_mniej, obc_mniej, Ndop_mniej, zapas_mniej, sm_mniej, wyb_mniej = oblicz_wariant(punkty_mniej)
    ile_wiecej, obc_wiecej, Ndop_wiecej, zapas_wiecej, sm_wiecej, wyb_wiecej = oblicz_wariant(punkty_wiecej)

    if zapas_std >= 15:
        zalecany = "standard"
    elif zapas_mniej >= 10 and zapas_mniej < 40:
        zalecany = "mniej"
    elif zapas_wiecej > zapas_std:
        zalecany = "wiecej"
    else:
        zalecany = "standard"

    st.markdown("---")
    st.subheader("⚙️ Optymalizacja liczby słupków")

    col_o1, col_o2, col_o3 = st.columns(3)

    with col_o1:
        kolor = "#e74c3c"
        if zalecany == "mniej":
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white;">
            <h3 style="margin:0; color:white;">🔴 Mniej słupków</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_mniej} szt.</b> | obc. {obc_mniej:.1f} kN | zapas {zapas_mniej:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_mniej:.0f} | Wyboczenie {wyb_mniej:.0f}%</p>
            <span style="background:white; color:{kolor}; padding:3px 14px; border-radius:8px; font-weight:bold;">✅ ZALECANE</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white; opacity:0.8;">
            <h3 style="margin:0; color:white;">🔴 Mniej słupków</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_mniej} szt.</b> | obc. {obc_mniej:.1f} kN | zapas {zapas_mniej:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_mniej:.0f} | Wyboczenie {wyb_mniej:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)

    with col_o2:
        kolor = "#f39c12"
        if zalecany == "standard":
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white;">
            <h3 style="margin:0; color:white;">🟠 Standard</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_std} szt.</b> | obc. {obc_std:.1f} kN | zapas {zapas_std:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_std:.0f} | Wyboczenie {wyb_std:.0f}%</p>
            <span style="background:white; color:{kolor}; padding:3px 14px; border-radius:8px; font-weight:bold;">✅ ZALECANE</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white; opacity:0.8;">
            <h3 style="margin:0; color:white;">🟠 Standard</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_std} szt.</b> | obc. {obc_std:.1f} kN | zapas {zapas_std:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_std:.0f} | Wyboczenie {wyb_std:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)

    with col_o3:
        kolor = "#2980b9"
        if zalecany == "wiecej":
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white;">
            <h3 style="margin:0; color:white;">🔵 Więcej słupków</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_wiecej} szt.</b> | obc. {obc_wiecej:.1f} kN | zapas {zapas_wiecej:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_wiecej:.0f} | Wyboczenie {wyb_wiecej:.0f}%</p>
            <span style="background:white; color:{kolor}; padding:3px 14px; border-radius:8px; font-weight:bold;">✅ ZALECANE</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color:{kolor}; padding:12px; border-radius:12px; text-align:center; color:white; opacity:0.8;">
            <h3 style="margin:0; color:white;">🔵 Więcej słupków</h3>
            <p style="font-size:16px; margin:8px 0;"><b>{ile_wiecej} szt.</b> | obc. {obc_wiecej:.1f} kN | zapas {zapas_wiecej:.0f}%</p>
            <p style="font-size:16px; margin:4px 0;">Smukłość {sm_wiecej:.0f} | Wyboczenie {wyb_wiecej:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)

    wybor = st.radio(
        "Wybierz wariant:",
        ["mniej", "standard", "wiecej"],
        index=["mniej", "standard", "wiecej"].index(zalecany),
        horizontal=True,
        key='fundament_wariant_wybor'
    )

    if wybor == "mniej":
        punkty_final = punkty_mniej
        ile_final, obc_final, Ndop_final, zapas_final, sm_final, wyb_final = ile_mniej, obc_mniej, Ndop_mniej, zapas_mniej, sm_mniej, wyb_mniej
    elif wybor == "wiecej":
        punkty_final = punkty_wiecej
        ile_final, obc_final, Ndop_final, zapas_final, sm_final, wyb_final = ile_wiecej, obc_wiecej, Ndop_wiecej, zapas_wiecej, sm_wiecej, wyb_wiecej
    else:
        punkty_final = punkty_standard
        ile_final, obc_final, Ndop_final, zapas_final, sm_final, wyb_final = ile_std, obc_std, Ndop_std, zapas_std, sm_std, wyb_std

    punkty_final = sortuj_slupki(punkty_final, szer_m, dlug_m)

    with st.expander("📖 Jak interpretować wyniki?"):
        st.markdown("""
        **Liczba słupków** – im więcej, tym obciążenie na jeden słupek jest mniejsze, co zwiększa bezpieczeństwo, ale zwiększa koszty betonu i robocizny.

        ---

        **Obciążenie na słupek (kN)** – siła, jaką budynek wywiera na jeden słupek. Powinna być mniejsza niż nośność dopuszczalna słupka.

        ---

        **Nośność dopuszczalna (kN)** – maksymalne obciążenie, jakie słupek może bezpiecznie przenieść (z zapasem).

        ---

        **Zapas nośności (%)** – o ile procent nośność dopuszczalna przewyższa obciążenie. Zalecany zapas to **15–40%**. Poniżej 10% ryzyko przeciążenia; powyżej 50% – konstrukcja przewymiarowana (nieekonomiczna).

        ---

        **Smukłość** – stosunek długości wyboczeniowej do promienia bezwładności. Dla słupków fundamentowych bezpieczna smukłość to **40–60**. Powyżej 70 ryzyko wyboczenia gwałtownie rośnie.

        ---

        **Szansa wyboczenia (%)** – orientacyjny wskaźnik ryzyka wygięcia słupka pod obciążeniem. Wartości poniżej 5% są bezpieczne, 5–15% – akceptowalne, powyżej 15% – zalecane zwiększenie średnicy.
        """)

    with sekcja("🗺️ Rysunek fundamentu z wymiarami"):
        st.caption("📏 Odległości liczone od środka słupka do środka słupka.")

        max_wymiar = max(szer_m, dlug_m)
        skala = 450 / max_wymiar if max_wymiar > 0 else 50
        szer_px = szer_m * skala
        dlug_px = dlug_m * skala
        promien = 10

        kolory_wariantow = {"mniej": "#e74c3c", "standard": "#f39c12", "wiecej": "#2980b9"}
        kolor_slupkow = kolory_wariantow[wybor]

        svg = f'<svg width="{szer_px + 80}" height="{dlug_px + 80}" xmlns="http://www.w3.org/2000/svg">'
        svg += f'<rect x="40" y="40" width="{szer_px}" height="{dlug_px}" fill="#f9f9f9" stroke="black" stroke-width="2"/>'
        svg = rysuj_odleglosci_na_rysunku(svg, punkty_final, szer_m, dlug_m, skala)
        for i, p in enumerate(punkty_final):
            cx = 40 + p['x'] * skala
            cy = 40 + (dlug_m - p['y']) * skala
            svg += f'<circle cx="{cx}" cy="{cy}" r="{promien}" fill="{kolor_slupkow}" stroke="black" stroke-width="1"/>'
            svg += f'<text x="{cx}" y="{cy+3}" text-anchor="middle" font-size="8" fill="white" font-weight="bold">{i+1}</text>'
        svg += '</svg>'
        st.markdown(svg, unsafe_allow_html=True)

    # --- TABELA ODLEGŁOŚCI ---
    narozne = [p for p in punkty_final if p['typ'] == 'narozny']
    odleglosci_narozne = []
    for i in range(len(narozne)):
        for j in range(i+1, len(narozne)):
            p1 = narozne[i]
            p2 = narozne[j]
            if (abs(p1['x'] - p2['x']) < 0.001 or abs(p1['y'] - p2['y']) < 0.001):
                odl = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)*100
                if 0.5 < odl < max(szer_m, dlug_m)*100+10:
                    idx1 = punkty_final.index(p1) + 1
                    idx2 = punkty_final.index(p2) + 1
                    odleglosci_narozne.append((idx1, idx2, odl))

    odleglosci_sasiednie = []
    for i in range(len(punkty_final) - 1):
        p1 = punkty_final[i]
        p2 = punkty_final[i+1]
        odl = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)*100
        if odl > 0.5:
            odleglosci_sasiednie.append((i+1, i+2, odl))

    with sekcja("📋 Odległości pomiędzy słupkami"):
        if odleglosci_narozne:
            st.markdown("**Odległości między słupkami narożnymi:**")
            for (i, j, odl) in odleglosci_narozne:
                st.write(f"- {i} ↔ {j}: **{odl:.0f} cm**")
            st.divider()

        st.markdown("**Pełna lista odległości (kolejno od słupka 1):**")
        if odleglosci_sasiednie:
            # Trzy kolumny obok siebie, treść wyśrodkowana w każdej -- zamiast
            # łamanej tabeli markdown wrzuconej w div flexbox (nie renderowała się poprawnie).
            n = len(odleglosci_sasiednie)
            na_kolumne = math.ceil(n / 3)
            grupy = [odleglosci_sasiednie[k:k + na_kolumne] for k in range(0, n, na_kolumne)]
            kolumny = st.columns(3)
            for kol, grupa in zip(kolumny, grupy):
                with kol:
                    wiersze = "".join(
                        f"<div style='text-align:center; padding:4px 0; border-bottom:1px solid var(--brzeg-karty);'>"
                        f"{i} → {j} &nbsp;<b>{odl:.0f} cm</b></div>"
                        for i, j, odl in grupa
                    )
                    st.markdown(wiersze, unsafe_allow_html=True)
        else:
            st.write("*Brak odległości do wyświetlenia.*")

    # --- EKSPORT PDF ---
    st.markdown("---")
    if st.button("📄 Eksportuj raport do PDF"):
        try:
            pdf_bytes = create_pdf(szer_m, dlug_m, wybrany_grunt_ascii, glebokosc_cm, srednica_mm, rozstaw_cm,
                                  liczba_rzedow, ile_final, obc_final, Ndop_final, zapas_final,
                                  sm_final, wyb_final, punkty_final)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="raport_fundamenty.pdf">Pobierz raport PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Nie udało się wygenerować PDF: {e}")

    st.markdown("---")
    st.warning(
        "⚠️ **Uwaga prawna:** Obliczenia wykonano zgodnie z uproszczonymi zasadami Eurokodu 7 (PN-EN 1997). "
        "Wyniki mają charakter orientacyjny i **nie stanowią podstawy do wykonania fundamentów** bez konsultacji "
        "z uprawnionym konstruktorem lub architektem. Ostateczną decyzję o liczbie, średnicy i głębokości słupków "
        "należy powierzyć specjaliście posiadającemu odpowiednie uprawnienia budowlane."
    )
     
            
# Na końcu pliku zaktualizuj słownik zakładek (dodaj, jeśli nie ma)
# zakladki_funkcje["🏛️ Fundamenty"] = fundamenty_tab
# ========== SŁOWNIK ZAKŁADEK (dodajemy nowe TUTAJ) ==========
zakladki_funkcje = {
    "Geometria": geometria_tab,
    "Ściany": sciany_tab,
    "Dach": dach_tab,
    "Podłoga": podloga_tab,
    "Akcesoria": akcesoria_tab,
    "Kosztorys": kosztorys_tab,
    "🏛️ Fundamenty": fundamenty_tab,   # <-- NOWA ZAKŁADKA
}

# ========== GŁÓWNA PĘTLA ==========
wybor = st.radio("", list(zakladki_funkcje.keys()), key='active_tab', horizontal=True)
zakladki_funkcje[wybor]()
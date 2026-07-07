# ... (początek aplikacji bez zmian aż do sekcji Wykończenie ścian)

    else:  # Wykończenie ścian
        st.markdown("<h2 style='text-align: center;'>Wykończenie ścian</h2>", unsafe_allow_html=True)
        pow_netto = pow_scian_netto()

        # Poszycie wewnętrzne – oddzielone grubą szarą linią, checkbox wyśrodkowany
        st.markdown("<hr style='border:2px solid #666; margin: 20px 0;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            poszycie_wew = st.checkbox("Poszycie wewnętrzne", key='poszycie_wew')
        if poszycie_wew:
            # 1. Wełna główna
            grub_map = {"95x45":100, "145x45":150, "195x45":200}
            gr = grub_map[st.session_state.slupki]
            st.markdown(f"<h3 style='margin:0'>Wełna Knauf Ecose {gr} mm</h3>", unsafe_allow_html=True)
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
            st.markdown("<hr style='border:1px solid #555; margin:10px 0;'>", unsafe_allow_html=True)

            # 2. Dodatkowa izolacja (opcjonalna)
            if st.checkbox("Dodatkowa izolacja termiczna 5 cm + kantówki", key='dodatkowa_izolacja'):
                st.markdown(f"<h3 style='margin:0'>Wełna Knauf Ecose 50 mm (dodatkowa)</h3>", unsafe_allow_html=True)
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
                st.markdown("<hr style='border:1px solid #555; margin:10px 0;'>", unsafe_allow_html=True)

                st.markdown(f"<h3 style='margin:0'>Kantówki 45x45 mm (poprzeczne)</h3>", unsafe_allow_html=True)
                rozstaw = st.slider("Rozstaw kantówek (cm)", 30, 80, step=5, value=st.session_state.rozstaw_kantowek, key='rozstaw_kantowek')
                rzedy = math.ceil(st.session_state.wys / 100 / (rozstaw/100)) + 1
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
                st.markdown("<hr style='border:1px solid #555; margin:10px 0;'>", unsafe_allow_html=True)

            # 3. OSB wewn. (opcjonalne)
            uzyj_osb = st.checkbox("Płyta OSB-3 wewnętrzna", value=st.session_state.uzyj_osb_wew, key='uzyj_osb_wew')
            if uzyj_osb:
                st.markdown(f"<h3 style='margin:0'>Płyta OSB-3 wewnętrzna</h3>", unsafe_allow_html=True)
                st.selectbox("Grubość (mm)", [8,9,10,12], key='osb_wew')
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
                st.markdown("<hr style='border:1px solid #555; margin:10px 0;'>", unsafe_allow_html=True)

            # 4. Płyta GK (opcjonalna)
            uzyj_gk = st.checkbox("Płyta gipsowo-kartonowa 12,5 mm", value=st.session_state.uzyj_gk_wew, key='uzyj_gk_wew')
            if uzyj_gk:
                st.markdown(f"<h3 style='margin:0'>Płyta gipsowo-kartonowa 12,5 mm</h3>", unsafe_allow_html=True)
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
                st.markdown("<hr style='border:1px solid #555; margin:10px 0;'>", unsafe_allow_html=True)

            # 5. Paroizolacja (zawsze w poszyciu wewn.)
            st.markdown(f"<h3 style='margin:0'>Paroizolacja</h3>", unsafe_allow_html=True)
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

        # Czerwona linia oddzielająca i poszycie zewnętrzne (bez zmian)
        st.markdown("<hr style='border:2px solid #e74c3c; margin:25px 0;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Poszycie zewnętrzne</h2>", unsafe_allow_html=True)
        # ... (reszta poszycia zewnętrznego)

# ... (dalsza część kodu aplikacji)
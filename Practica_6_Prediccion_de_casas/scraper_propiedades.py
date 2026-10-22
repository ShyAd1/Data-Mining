# -*- coding: utf-8 -*-
import os
import re
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

PAGINAS = 16  # Total de páginas a extraer
ARCHIVO_SALIDA = "raw_propiedades.csv"
URL_BASE = "https://propiedades.com/gustavo-a-madero/casas-venta"
PATH_PERFIL = os.path.join(os.getcwd(), "perfil_chrome_propiedades")

def limpiar_precio(texto):
    if not texto: return None
    match = re.search(r'\$\s*([\d\.,]+)', str(texto))
    if not match: return None
    raw = match.group(1)
    if '.' in raw:
        parts = raw.split('.')
        if len(parts[-1]) == 2 and parts[-1].isdigit():
            main_part = "".join(parts[:-1]).replace(',', '')
            return float(main_part + "." + parts[-1])
        else:
            return float(raw.replace('.', '').replace(',', ''))
    return float(raw.replace(',', ''))

def extraer_calle_colonia_propiedades(texto_card):
    t = re.sub(r'PRIME|DESTACADO|CASA VENTA', '', texto_card, flags=re.IGNORECASE)
    t = re.sub(r'\$\s*[\d\.,]+\s*(?:MXN)?', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(?:Casa disponible en venta en|Se vende casa en|Venta de casa en|Venta de casa|Casa en venta en|Casa en|En venta)\b', '', t, flags=re.IGNORECASE)
    
    parts = [p.strip() for p in t.split(',') if p.strip()]
    calle = "Sin calle"
    colonia = "Gustavo A. Madero"
    
    for i, p in enumerate(parts):
        if re.search(r'\d+|Lt|Mz|#|Chiclayo|Arequipa|Guantánamo|Nte\.|Av\.|Calle|Privada|Cda\.', p, re.I):
            if not re.search(r'Recám|Baños|m²|m2|Mascota|Lavande|Teléfono|Contactar|Consultar', p, re.I) and len(p) < 90:
                calle = p
                if i + 1 < len(parts):
                    next_p = re.sub(r'^(?:Col\.|Colonia|Col)\s*', '', parts[i+1], flags=re.IGNORECASE).strip()
                    if not re.search(r'Gustavo A\. Madero|Ciudad de México|DF|\d{5}', next_p, re.I):
                        colonia = next_p
                break
                
    if colonia == "Gustavo A. Madero":
        for i, p in enumerate(parts):
            if re.search(r'Gustavo A\. Madero|Ciudad de México|DF', p, re.I) and i > 0:
                prev_p = re.sub(r'^(?:Col\.|Colonia|Col)\s*', '', parts[i-1], flags=re.IGNORECASE).strip()
                if len(prev_p) > 2 and 'venta' not in prev_p.lower():
                    colonia = prev_p
                    break

    return calle, colonia

def extraer_m2_propiedades(txt_clean):
    if not txt_clean: return None
    txt_norm = txt_clean.replace('\xa0', ' ').replace('&sup2;', '²')
    
    m_const = re.search(r'(\d+[\d\.,]*)\s*(?:m\u00b2|m2|m²|mts|m)?\s*(?:const|cubierto|cubiertos|c\b)', txt_norm, re.I)
    if m_const:
        val = float(m_const.group(1).replace(',', ''))
        if 15 <= val <= 3000: return val

    matches = re.findall(r'(\d+[\d\.,]*)\s*(?:m\u00b2|m2|m²|mts|m\b)', txt_norm, re.I)
    for m in matches:
        try:
            val = float(m.replace(',', ''))
            if 15 <= val <= 3000: return val
        except ValueError: continue
    return None

def ejecutar():
    registros = []
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PATH_PERFIL}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    try:
        driver = uc.Chrome(options=options, version_main=155)
    except Exception:
        driver = uc.Chrome(options=options)

    try:
        print(f"[Propiedades.com] Abriendo página inicial: {URL_BASE}")
        driver.get(URL_BASE)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("[!] PAUSA INICIAL DE VERIFICACIÓN")
        print(" -> Revisa la ventana de Chrome.")
        print(" -> Si hay CAPTCHA, resuélvelo hasta ver las casas.")
        print("="*70)
        input("\n>>> Cuando VEAS LAS CASAS cargadas en Chrome, presiona ENTER para iniciar... <<<\n")

        p = 1
        while p <= PAGINAS:
            url_pagina = f"{URL_BASE}?pagina={p}" if p > 1 else URL_BASE
            print(f"\n[Propiedades.com] Procesando página {p}/{PAGINAS}: {url_pagina}")
            
            if p > 1:
                driver.execute_script(f"window.location.href = '{url_pagina}';")
                time.sleep(random.uniform(4.0, 6.0))

            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            driver.execute_script(f"window.scrollTo(0, {total_height / 3});")
            time.sleep(1)
            driver.execute_script(f"window.scrollTo(0, {(total_height / 3) * 2});")
            time.sleep(1)
            driver.execute_script(f"window.scrollTo(0, {total_height});")
            time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            links = soup.select('a[href*="/inmuebles/"], a[href*="/propiedades/"]')
            card_containers = []
            cards_seen = set()

            for a in links:
                curr = a.parent
                best_container = None
                while curr is not None and curr.name != 'body':
                    txt = curr.get_text(separator=' ', strip=True)
                    txt_l = txt.lower()
                    has_price = '$' in txt
                    has_features = any(k in txt_l for k in ['m²', 'm2', 'recá', 'recam', 'baño', 'bano', 'm\u00b2'])
                    classes = " ".join(curr.get('class', []))
                    is_card = bool(re.search(r'card|propertycard|boxproperty', classes, re.I))

                    if has_price and (has_features or is_card) and len(txt) < 2500:
                        best_container = curr
                        parent = curr.parent
                        if parent and re.search(r'card|propertycard|boxproperty', " ".join(parent.get('class', [])), re.I) and len(parent.get_text()) < 2500:
                            best_container = parent
                        break
                    curr = curr.parent

                if best_container and best_container not in cards_seen:
                    cards_seen.add(best_container)
                    card_containers.append(best_container)

            if len(card_containers) == 0:
                print("\n" + "!"*70)
                print(f"[!] DETECCIÓN DE BLOQUEO EN PÁGINA {p}/{PAGINAS}")
                print(" -> Resuelve la verificación en la ventana de Chrome.")
                print("!"*70)
                input(f"\n>>> Cuando veas las casas, presiona ENTER para REINTENTAR... <<<\n")
                continue

            print(f" -> {len(card_containers)} tarjetas completas identificadas.")

            nuevos_en_pagina = 0
            for t in card_containers:
                try:
                    txt_completo = t.get_text(separator=' ', strip=True)
                    txt_lower = txt_completo.lower()

                    precio = limpiar_precio(txt_completo)
                    calle, colonia = extraer_calle_colonia_propiedades(txt_completo)
                    m2 = extraer_m2_propiedades(txt_completo)

                    rec_match = re.search(r'(\d+)\s*(?:rec\u00e1m|recam|rec|hab|dorm)', txt_lower)
                    ban_match = re.search(r'(\d+)\s*(?:ba\u00f1|bano)', txt_lower)

                    recs = float(rec_match.group(1)) if rec_match else None
                    banos = float(ban_match.group(1)) if ban_match else None

                    if precio or m2:
                        registros.append({
                            'fuente': 'Propiedades.com',
                            'alcaldia': 'Gustavo A. Madero',
                            'colonia': colonia,
                            'calle': calle,
                            'precio_mxn': precio,
                            'm2_construidos': m2,
                            'recamaras': recs,
                            'banos': banos
                        })
                        nuevos_en_pagina += 1
                except Exception:
                    continue

            print(f" -> {nuevos_en_pagina} propiedades procesadas correctamente en la página {p}.")

            df_temp = pd.DataFrame(registros).drop_duplicates()
            df_temp.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')

            p += 1

    finally:
        try:
            driver.quit()
        except Exception: pass

    df = pd.DataFrame(registros).drop_duplicates()
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')
    print(f"\n[✓] Extracción finalizada: '{ARCHIVO_SALIDA}' ({len(df)} registros guardados)")

if __name__ == "__main__":
    ejecutar()
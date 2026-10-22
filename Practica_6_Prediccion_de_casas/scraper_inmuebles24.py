# -*- coding: utf-8 -*-
import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

PAGINAS = 5
ARCHIVO_SALIDA = "raw_inmuebles24.csv"
URL_BASE = "https://www.inmuebles24.com/casas-en-venta-en-gustavo-a.-madero"
PATH_PERFIL = os.path.join(os.getcwd(), "perfil_chrome_i24")

COLONIAS_GAM = [
    "Lindavista Sur", "Lindavista Norte", "Lindavista Nte.", "Lindavista",
    "Torres Lindavista", "Villa de Aragón", "Santa Maria Ticoman", "Santa María Ticomán",
    "Nueva Atzacoalco", "Ferrocarrilera", "Industrial", "San Felipe de Jesús",
    "San Felipe De Jesús", "Casas Alemán", "Aragón La Villa", "Guadalupe Tepeyac",
    "Cuchilla del Tesoro", "Nueva Vallejo", "Residencial Zacatenco", "Acueducto de Guadalupe",
    "Pradera", "Pradera I Secc", "Pradera II Secc", "Vallejo", "Estrella",
    "Cuautepec", "Cuautepec de Madero", "San Juan de Aragón", "San Juan de Aragón III",
    "Valle Del Tepeyac", "La Joya", "Providencia", "Campestre Aragón", "Tepeyac Insurgentes"
]

def verificar_y_esperar_captcha(driver):
    url = driver.current_url.lower()
    page_text = driver.page_source.lower()
    if "challenge" in url or "captcha" in url or "just a moment" in page_text or "bloqueo" in page_text:
        print("\n" + "!"*70)
        print("[!] VERIFICACIÓN DE CLOUDFLARE EN INMUEBLES24")
        print(" -> Resuelve la verificación en la ventana de Chrome.")
        print("!"*70)
        input("\n>>> Una vez que veas las casas, presiona ENTER aquí... <<<\n")
        time.sleep(2)

def limpiar_num(texto):
    if not texto: return None
    match = re.search(r'(\d+)', str(texto).replace(',', '').replace('.', ''))
    return float(match.group(1)) if match else None

def extraer_calle_colonia_i24(col_elem):
    if not col_elem:
        return "Sin calle", "Gustavo A. Madero"
    
    raw_text = ", ".join([s.strip() for s in col_elem.stripped_strings if s.strip()])
    text_clean = re.sub(r',?\s*(?:Gustavo A\.? Madero|Distrito Federal|CDMX|Ciudad de México).*', '', raw_text, flags=re.IGNORECASE).strip()

    calle = "Sin calle"
    colonia = "Gustavo A. Madero"

    for col_known in sorted(COLONIAS_GAM, key=len, reverse=True):
        if col_known.lower() in text_clean.lower():
            colonia = col_known
            idx = text_clean.lower().find(col_known.lower())
            calle_part = text_clean[:idx].strip(' ,.-')
            if calle_part and len(calle_part) > 1:
                calle = calle_part
            return calle, colonia

    parts = [p.strip() for p in text_clean.split(',') if p.strip()]
    if len(parts) >= 2:
        calle = parts[0]
        colonia = parts[1]
    elif len(parts) == 1:
        txt = parts[0]
        split_camel = re.split(r'(?<=\d)(?=[A-Z])|(?<=[a-z])(?=[A-Z][a-z]+)', txt)
        if len(split_camel) >= 2:
            calle = split_camel[0].strip()
            colonia = " ".join(split_camel[1:]).strip()
        elif re.search(r'\d+|Lt|Mz|#', txt):
            calle = txt
            colonia = "Gustavo A. Madero"
        else:
            calle = "Sin calle"
            colonia = txt

    return calle, colonia

def extraer_m2_i24(txt):
    if not txt: return None
    
    # 1. Eliminar cifras del precio para evitar fusiones de números
    txt_noprice = re.sub(r'(?:MN|\$)\s*[\d\.,]+', '', txt, flags=re.IGNORECASE)
    txt_norm = txt_noprice.replace('\xa0', ' ').replace('&sup2;', '²').replace('&#178;', '²')
    
    # Prioridad A: Metros de construcción explícitos en el texto o descripción
    m_const = re.search(r'(\d+[\d\.,]*)\s*(?:m\u00b2|m2|m²|mts|m)?\s*(?:de\s+)?(?:construcci\u00f3n|construccion|const|cubierto|cubiertos|c\b)', txt_norm, re.I)
    if m_const:
        val = float(m_const.group(1).replace(',', ''))
        if 15 <= val <= 3000: return val

    # Prioridad B: Etiquetas de lote, terreno o total (e.g. "156 m² lote", "485 m² lote")
    m_badge = re.search(r'(\d+[\d\.,]*)\s*(?:m\u00b2|m2|m²|mts|m\b)\s*(?:lote|terreno|tot|ter\b)?', txt_norm, re.I)
    if m_badge:
        val = float(m_badge.group(1).replace(',', ''))
        if 15 <= val <= 3000: return val

    # Prioridad C: Cualquier coincidencia directa de m²
    matches = re.findall(r'(\d+[\d\.,]*)\s*(?:m\u00b2|m2|m²|mts)', txt_norm, re.I)
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
        for p in range(1, PAGINAS + 1):
            url = f"{URL_BASE}-pagina-{p}.html" if p > 1 else f"{URL_BASE}.html"
            print(f"[Inmuebles24] Extrayendo página {p}/{PAGINAS}: {url}")
            driver.get(url)
            time.sleep(3)
            
            verificar_y_esperar_captcha(driver)

            height = int(driver.execute_script("return document.body.scrollHeight"))
            driver.execute_script(f"window.scrollTo(0, {height / 2});")
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tarjetas = soup.select('div[data-qa="posting card"], div.postingCard, div[class*="PostingCard"]')
            
            if not tarjetas:
                links = soup.select('a[href*="/propiedades/"]')
                contenedores = []
                for a in links:
                    parent = a.find_parent('div', class_=re.compile(r'posting|card', re.I))
                    if parent and parent not in contenedores:
                        contenedores.append(parent)
                tarjetas = contenedores

            print(f" -> Encontradas {len(tarjetas)} propiedades.")

            for t in tarjetas:
                try:
                    precio_elem = t.select_one('div[data-qa="POSTING_CARD_PRICE"], [class*="Price"], [class*="price"]')
                    col_elem = t.select_one('div[data-qa="POSTING_CARD_LOCATION"], [class*="Location"], [class*="location"]')
                    
                    precio = limpiar_num(precio_elem.text) if precio_elem else None
                    calle, colonia = extraer_calle_colonia_i24(col_elem)

                    txt = t.get_text(separator=' ', strip=True)
                    m2 = extraer_m2_i24(txt)
                    
                    recs, banos = None, None
                    rec_match = re.search(r'(\d+)\s*(?:rec|hab|dorm)', txt, re.I)
                    ban_match = re.search(r'(\d+)\s*(?:bañ|bano)', txt, re.I)
                    
                    if rec_match: recs = float(rec_match.group(1))
                    if ban_match: banos = float(ban_match.group(1))

                    registros.append({
                        'fuente': 'Inmuebles24',
                        'alcaldia': 'Gustavo A. Madero',
                        'colonia': colonia,
                        'calle': calle,
                        'precio_mxn': precio,
                        'm2_construidos': m2,
                        'recamaras': recs,
                        'banos': banos
                    })
                except Exception: 
                    continue
    finally:
        try:
            driver.quit()
        except Exception: pass

    df = pd.DataFrame(registros).drop_duplicates()
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')
    print(f"[✓] Guardado: '{ARCHIVO_SALIDA}' ({len(df)} registros)")

if __name__ == "__main__":
    ejecutar()
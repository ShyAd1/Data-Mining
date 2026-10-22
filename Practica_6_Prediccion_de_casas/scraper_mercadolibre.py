import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

PAGINAS = 6
ARCHIVO_SALIDA = "raw_mercadolibre.csv"
URL_INICIAL = "https://inmuebles.mercadolibre.com.mx/casas/venta/gustavo-a-madero-distrito-federal/"
PATH_PERFIL = os.path.join(os.getcwd(), "perfil_chrome_meli")

def limpiar_num(texto):
    if not texto: return None
    match = re.search(r'(\d+)', str(texto).replace(',', '').replace('.', ''))
    return float(match.group(1)) if match else None

def separar_calle_colonia(texto_loc):
    if not texto_loc:
        return "Sin calle", "Gustavo A. Madero"
    
    partes = [p.strip() for p in str(texto_loc).split(',') if p.strip()]
    pri = partes[0]
    
    # Detectar si el primer fragmento contiene números o nomenclatura de calle/lote/manzana
    tiene_num_o_calle = re.search(r'\d+|Lt|Mz|#|Cda\.|Privada|Calle|Av\.|Avenida', pri, re.IGNORECASE)
    es_eje_o_norte = re.fullmatch(r'Norte\s*\d+|Eje\s*\d+\s*Norte', pri, re.IGNORECASE)
    
    if tiene_num_o_calle and not es_eje_o_norte:
        calle = pri
        colonia = partes[1] if len(partes) > 1 and "gustavo" not in partes[1].lower() else "Gustavo A. Madero"
    else:
        calle = "Sin calle"
        colonia = pri if pri.lower() != "gustavo a. madero" else "Gustavo A. Madero"
        
    return calle, colonia

def ejecutar():
    registros = []
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PATH_PERFIL}")
    options.add_argument("--start-maximized")
    
    try:
        driver = uc.Chrome(options=options, version_main=155)
    except Exception:
        driver = uc.Chrome(options=options)

    try:
        driver.get(URL_INICIAL)
        time.sleep(3)

        for p in range(1, PAGINAS + 1):
            print(f"[MercadoLibre] Extrayendo página {p}/{PAGINAS}...")
            height = int(driver.execute_script("return document.body.scrollHeight"))
            driver.execute_script(f"window.scrollTo(0, {height / 2});")
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tarjetas = soup.select('div.poly-card, li.ui-search-layout__item')

            for t in tarjetas:
                try:
                    precio = limpiar_num(t.select_one('.poly-price__current .andes-money-amount__fraction, .andes-money-amount__fraction').text)
                    loc_text = t.select_one('.poly-component__location, .ui-search-item__location').get_text(strip=True)
                    
                    calle, colonia = separar_calle_colonia(loc_text)

                    m2, recs, banos = None, None, None
                    for attr in t.select('.poly-component__attributes-list li, .ui-search-card-attributes__attribute'):
                        txt = attr.get_text(strip=True).lower()
                        if 'm²' in txt or 'm2' in txt: m2 = limpiar_num(txt)
                        elif 'rec' in txt: recs = limpiar_num(txt)
                        elif 'baño' in txt or 'bano' in txt: banos = limpiar_num(txt)

                    registros.append({
                        'fuente': 'MercadoLibre',
                        'alcaldia': 'Gustavo A. Madero',
                        'colonia': colonia,
                        'calle': calle,
                        'precio_mxn': precio,
                        'm2_construidos': m2,
                        'recamaras': recs,
                        'banos': banos
                    })
                except Exception: continue

            if p < PAGINAS:
                try:
                    btn = driver.find_element(By.CSS_SELECTOR, 'a.andes-pagination__link[title="Siguiente"]')
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    btn.click()
                    time.sleep(2)
                except Exception: break
    finally:
        try:
            driver.quit()
        except Exception: pass

    df = pd.DataFrame(registros).drop_duplicates()
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')
    print(f"[✓] Guardado: '{ARCHIVO_SALIDA}' ({len(df)} registros)")

if __name__ == "__main__":
    ejecutar()
# -*- coding: utf-8 -*-
import os
import re
import numpy as np
import pandas as pd

# Archivos de entrada y salida
ARCHIVOS_ENTRADA = [
    ("Practica_6_Prediccion_de_casas/raw_mercadolibre.csv", "Practica_6_Prediccion_de_casas/enriched_mercadolibre.csv"),
    ("Practica_6_Prediccion_de_casas/raw_inmuebles24.csv", "Practica_6_Prediccion_de_casas/enriched_inmuebles24.csv"),
    ("Practica_6_Prediccion_de_casas/raw_propiedades.csv", "Practica_6_Prediccion_de_casas/enriched_propiedades.csv")
]

# Centroide por defecto de Gustavo A. Madero (GAM)
DEFAULT_GAM_COORDS = (19.4820, -99.1150)

# Catálogo de coordenadas de colonias y zonas clave de Gustavo A. Madero
GAM_COLONIAS_COORDS = {
    "lindavista norte": (19.4880, -99.1280),
    "lindavista nte": (19.4880, -99.1280),
    "lindavista sur": (19.4810, -99.1290),
    "lindavista": (19.4840, -99.1285),
    "torres lindavista": (19.5050, -99.1380),
    "industrial": (19.4750, -99.1180),
    "guadalupe tepeyac": (19.4690, -99.1170),
    "guadalupe insurgentes": (19.4740, -99.1210),
    "tepeyac insurgentes": (19.4830, -99.1220),
    "san felipe de jesús": (19.5015, -99.0735),
    "san felipe de jesus": (19.5015, -99.0735),
    "casas alemán": (19.4746, -99.0885),
    "casas aleman": (19.4746, -99.0885),
    "aragón la villa": (19.4820, -99.1150),
    "san juan de aragón": (19.4580, -99.0820),
    "san juan de aragón i secc": (19.4620, -99.0860),
    "san juan de aragón ii sección": (19.4590, -99.0820),
    "san juan de aragón iii sección": (19.4550, -99.0780),
    "villa de aragón": (19.4520, -99.0680),
    "campestre aragón": (19.4720, -99.0750),
    "cuchilla del tesoro": (19.4550, -99.0580),
    "nueva atzacoalco": (19.4920, -99.0980),
    "atzacoalco ctm": (19.4950, -99.0920),
    "ctm aragón": (19.4600, -99.0650),
    "nueva vallejo": (19.4820, -99.1420),
    "vallejo": (19.4720, -99.1410),
    "panamericana": (19.4830, -99.1390),
    "defensores de la república": (19.4730, -99.1380),
    "capultitla": (19.4780, -99.1310),
    "magdalena de las salinas": (19.4820, -99.1400),
    "residencial zacatenco": (19.5060, -99.1240),
    "san pedro zacatenco": (19.5080, -99.1200),
    "acueducto de guadalupe": (19.5280, -99.1410),
    "santa maría ticomán": (19.5120, -99.1350),
    "santa maria ticoman": (19.5120, -99.1350),
    "san josé ticomán": (19.5180, -99.1320),
    "la laguna ticomán": (19.5220, -99.1290),
    "cuautepec de madero": (19.5480, -99.1320),
    "cuautepec barrio alto": (19.5580, -99.1290),
    "zona escolar": (19.5420, -99.1350),
    "zona escolar oriente": (19.5430, -99.1310),
    "la palma": (19.5520, -99.1380),
    "cocoyotes": (19.5590, -99.1320),
    "juventino rosas": (19.5380, -99.1390),
    "valle del tepeyac": (19.4950, -99.1380),
    "la joya": (19.4980, -99.1280),
    "estrella": (19.4790, -99.1170),
    "martín carrera": (19.4860, -99.1080),
    "ferrocarrilera": (19.4820, -99.1110),
    "providencia": (19.4780, -99.0820),
    "ampliación providencia": (19.4800, -99.0800),
    "la pradera": (19.4820, -99.0880),
    "pradera": (19.4820, -99.0880),
    "pradera i secc": (19.4830, -99.0860),
    "pradera ii secc": (19.4810, -99.0890),
    "granjas modernas": (19.4780, -99.1020),
    "guadalupe victoria": (19.4850, -99.1020),
    "salvador díaz mirón": (19.4810, -99.1010),
    "eva sámano de lópez mateos": (19.5020, -99.0960),
    "adolfo ruiz cortínez": (19.5320, -99.1400),
    "progreso nacional": (19.5220, -99.1510),
    "ampliación progreso nacional": (19.5250, -99.1490),
    "villas de aragón": (19.4580, -99.0620),
    "ampliación gabriel hernández": (19.5020, -99.1020),
    "gabriel hernández": (19.4980, -99.1050),
    "constituyentes de querétaro": (19.4920, -99.0890),
    "triunfo de la república": (19.4860, -99.1140),
    "25 de julio": (19.4980, -99.0820),
    "la esmeralda": (19.4880, -99.0820),
    "15 de agosto": (19.4830, -99.1020),
    "7 de noviembre": (19.4750, -99.1050),
    "ahuehuetes": (19.5350, -99.1350),
    "ampliación guadalupe proletaria": (19.5250, -99.1480),
    "ampliación mártires de río blanco": (19.4680, -99.1220),
    "aragón inguarán": (19.4720, -99.1100),
    "bondojito": (19.4650, -99.1120),
    "buenavista": (19.4980, -99.1250),
    "chalma de guadalupe": (19.5520, -99.1450),
    "churubusco tepeyac": (19.4880, -99.1220),
    "constitución de la república": (19.4800, -99.0950),
    "cuautepec alto centro": (19.5550, -99.1280),
    "del obrero": (19.4820, -99.1080),
    "educadores mexicanos": (19.5150, -99.1320),
    "el coyol": (19.4820, -99.0780),
    "faja de oro": (19.4710, -99.1150),
    "gertrudis sánchez": (19.4680, -99.0980),
    "guadalupe proletaria": (19.5220, -99.1460),
    "héroes de cerro prieto": (19.4720, -99.0900),
    "héroes de chapultepec": (19.4750, -99.1050),
    "jorge negrete": (19.5450, -99.1410),
    "la malinche": (19.4650, -99.1020),
    "malinche": (19.4650, -99.1020),
    "la pastora": (19.5380, -99.1280),
    "mártires de río blanco": (19.4650, -99.1200),
    "nueva tenochtitlan": (19.4680, -99.1280),
    "palmatitla": (19.5620, -99.1350),
    "pascual ortiz rubio": (19.4820, -99.1050),
    "santiago atzacoalco": (19.5020, -99.1050),
    "rosas del tepeyac": (19.4880, -99.1180),
    "san bartolo atepehuacan": (19.4850, -99.1350),
    "san josé de la escalera": (19.5150, -99.1520),
    "san pedro el chico": (19.4720, -99.0980),
    "santa isabel tola": (19.4920, -99.1180),
    "santa rosa": (19.5220, -99.1600),
    "santiago atepetlac": (19.5120, -99.1480),
    "tablas de san agustín": (19.4720, -99.1050),
    "vasco de quiroga": (19.4920, -99.0950),
    "villa gustavo a. madero": (19.4820, -99.1150),
    "riobamba": (19.4860, -99.1280),
    "coquimbo": (19.4870, -99.1270),
    "chiclayo": (19.4880, -99.1290),
    "cienfuegos": (19.4840, -99.1280),
    "cuzco": (19.4850, -99.1290),
    "pernambuco": (19.4830, -99.1300),
    "mollendo": (19.4890, -99.1280),
    "puno": (19.4870, -99.1290),
    "arequipa": (19.4820, -99.1290),
    "huancayo": (19.4840, -99.1270),
    "managua": (19.4880, -99.1260)
}

# Principales Avenidas y Autopistas de GAM
AVENIDAS_AUTOPISTAS_GAM = [
    {"nombre": "Insurgentes Norte", "coords": (19.4850, -99.1250)},
    {"nombre": "Autopista México-Pachuca", "coords": (19.5280, -99.1080)},
    {"nombre": "Calzada Vallejo", "coords": (19.4750, -99.1550)},
    {"nombre": "Eje Central Lázaro Cárdenas", "coords": (19.4900, -99.1350)},
    {"nombre": "Eje 5 Norte", "coords": (19.4800, -99.1450)},
    {"nombre": "Eje 3 Norte", "coords": (19.4700, -99.1000)},
    {"nombre": "Eje 1 Oriente (Ferrocarril Hidalgo)", "coords": (19.4800, -99.1100)},
    {"nombre": "Calzada de los Misterios", "coords": (19.4900, -99.1200)},
    {"nombre": "Calzada de Guadalupe", "coords": (19.4780, -99.1180)},
    {"nombre": "Av. Gran Canal", "coords": (19.4680, -99.1100)},
    {"nombre": "Av. Instituto Politécnico Nacional", "coords": (19.5200, -99.1450)},
    {"nombre": "Av. Montevideo", "coords": (19.5050, -99.1300)},
    {"nombre": "Eje 4 Norte", "coords": (19.4600, -99.0700)},
    {"nombre": "Av. Centenario", "coords": (19.4650, -99.0850)}
]

# Estaciones de Transporte Público en GAM (Metro, Metrobús, Cablebús)
TRANSPORTE_PUBLICO_GAM = [
    {"nombre": "Metro Indios Verdes", "coords": (19.5217, -99.1197)},
    {"nombre": "Metro Deportivo 18 de Marzo", "coords": (19.4839, -99.1264)},
    {"nombre": "Metro Potrero", "coords": (19.4717, -99.1317)},
    {"nombre": "Metro La Raza", "coords": (19.4700, -99.1367)},
    {"nombre": "Metro Lindavista", "coords": (19.4872, -99.1342)},
    {"nombre": "Metro Instituto del Petróleo", "coords": (19.4894, -99.1439)},
    {"nombre": "Metro Politécnico", "coords": (19.5008, -99.1492)},
    {"nombre": "Metro Autobuses del Norte", "coords": (19.4792, -99.1408)},
    {"nombre": "Metro Martín Carrera", "coords": (19.4853, -99.1044)},
    {"nombre": "Metro Talismán", "coords": (19.4725, -99.1086)},
    {"nombre": "Metro Bondojito", "coords": (19.4639, -99.1119)},
    {"nombre": "Metro Consulado", "coords": (19.4578, -99.1139)},
    {"nombre": "Metro La Villa-Basílica", "coords": (19.4811, -99.1181)},
    {"nombre": "Metro Misterios", "coords": (19.4631, -99.1308)},
    {"nombre": "Metro San Juan de Aragón", "coords": (19.4514, -99.0881)},
    {"nombre": "Metro Río de los Remedios", "coords": (19.4456, -99.0872)},
    {"nombre": "Cablebús Indios Verdes", "coords": (19.5217, -99.1197)},
    {"nombre": "Cablebús Cuautepec", "coords": (19.5580, -99.1350)}
]

def haversine_meters(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos coordenadas geográficas."""
    R = 6371000.0  # Radio de la Tierra en metros
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return R * c

def obtener_coordenadas(colonia, calle):
    """Obtiene latitud y longitud basándose en la colonia y calle de la propiedad."""
    texto_combinado = f"{calle} {colonia}".lower().strip()
    
    # 1. Búsqueda por coincidencia en combinación calle + colonia
    for key, coords in GAM_COLONIAS_COORDS.items():
        if key in texto_combinado:
            return coords
            
    # 2. Búsqueda limpia por colonia
    col_clean = str(colonia).lower().strip()
    col_clean = re.sub(r'^(?:col\.|colonia|col|usd|sn|se vende casa)\s*', '', col_clean).strip()
    
    if col_clean in GAM_COLONIAS_COORDS:
        return GAM_COLONIAS_COORDS[col_clean]
        
    for key, coords in GAM_COLONIAS_COORDS.items():
        if key in col_clean or col_clean in key:
            return coords
            
    return DEFAULT_GAM_COORDS

def calcular_distancias_minimas(lat, lon):
    """Calcula la distancia mínima en metros hacia avenidas principales y transporte público."""
    dist_av = min([haversine_meters(lat, lon, x["coords"][0], x["coords"][1]) for x in AVENIDAS_AUTOPISTAS_GAM])
    dist_trans = min([haversine_meters(lat, lon, x["coords"][0], x["coords"][1]) for x in TRANSPORTE_PUBLICO_GAM])
    return round(dist_av, 2), round(dist_trans, 2)

def procesar_datasets():
    print("Iniciando enriquecimiento espacial de datasets...")
    
    for input_file, output_file in ARCHIVOS_ENTRADA:
        if not os.path.exists(input_file):
            print(f"[!] Archivo {input_file} no encontrado. Omitiendo...")
            continue
            
        df = pd.read_csv(input_file)
        print(f"\nProcesando '{input_file}' ({len(df)} registros)...")
        
        lats, lons, dist_avs, dist_trans = [], [], [], []
        
        for idx, row in df.iterrows():
            colonia = row.get('colonia', '')
            calle = row.get('calle', '')
            
            lat, lon = obtener_coordenadas(colonia, calle)
            d_av, d_tr = calcular_distancias_minimas(lat, lon)
            
            lats.append(lat)
            lons.append(lon)
            dist_avs.append(d_av)
            dist_trans.append(d_tr)
            
        # Asignar las 4 nuevas variables espaciales sin modificar los datos originales
        df['latitud'] = lats
        df['longitud'] = lons
        df['dist_avenida_principal_m'] = dist_avs
        df['dist_transporte_m'] = dist_trans
        
        # Guardar en nuevo CSV
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[✓] Guardado exitoso: '{output_file}' con columnas adicionales: latitud, longitud, dist_avenida_principal_m, dist_transporte_m")

if __name__ == "__main__":
    procesar_datasets()
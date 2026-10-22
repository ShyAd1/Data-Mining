# -*- coding: utf-8 -*-
import re
import numpy as np
import pandas as pd

# Archivo de entrada y salida
ARCHIVO_ENTRADA = 'Practica_6_Prediccion_de_casas/dataset_casas_gam_unificado.csv'
ARCHIVO_SALIDA = 'Practica_6_Prediccion_de_casas/dataset_casas_gam_limpio.csv'


def limpiar_colonia(c):
  if pd.isna(c):
    return 'Gustavo A. Madero'

  txt = str(c).strip()
  # Eliminar prefijos comunes
  txt_clean = re.sub(
      r'^(?:Se vende casa Col\.|Colonia|Col\.|Col|USD|Venta Casa En La'
      r' Colonia|Venta DE Casa EN\s*Gustavo\s*A\s*Madero Colonia|Casa EN Venta'
      r' EN Gustavo A\. Madero|Oficinas O Departamentos EN)\s*',
      '',
      txt,
      flags=re.I,
  ).strip()
  txt_lower = txt_clean.lower()

  # 1. Lindavista
  if 'torres lindavista' in txt_lower or txt_lower == 'tores':
    return 'Torres Lindavista'
  elif 'planetario lindavista' in txt_lower:
    return 'Planetario Lindavista'
  elif 'lindavista vallejo' in txt_lower:
    return 'Lindavista Vallejo'
  elif 'lindavista nte' in txt_lower or 'lindavista norte' in txt_lower:
    return 'Lindavista Norte'
  elif 'lindavista sur' in txt_lower:
    return 'Lindavista Sur'
  elif 'lindaviista' in txt_lower or 'lindavista' in txt_lower:
    return 'Lindavista'

  # Calles de Lindavista usadas como colonia
  if txt_lower in [
      'riobamba',
      'c. riobamba',
      'coquimbo',
      'chiclayo',
      'cienfuegoses',
      'cuzco',
      'pernambuco',
      'mollendo',
      'puno',
      'arequipa',
      'huancayo',
      'lima',
      'managua',
      'montevideo',
  ]:
    return 'Lindavista Norte'

  # 2. San Felipe de Jesús
  if 'san felipe' in txt_lower or txt_lower == 'sn felipe':
    return 'San Felipe de Jesús'

  # 3. San Juan de Aragón por secciones
  if (
      'san juan de aragón i ' in txt_lower
      or 'san juan de aragon i ' in txt_lower
  ):
    return 'San Juan de Aragón 1a Sección'
  elif (
      'san juan de aragón ii' in txt_lower
      or 'san juan de aragon ii' in txt_lower
  ):
    return 'San Juan de Aragón 2a Sección'
  elif (
      'san juan de aragón iii' in txt_lower
      or 'san juan de aragon iii' in txt_lower
  ):
    return 'San Juan de Aragón 3a Sección'
  elif (
      'san juan de aragón iv' in txt_lower
      or 'san juan de aragon iv' in txt_lower
  ):
    return 'San Juan de Aragón 4a Sección'
  elif (
      'san juan de aragón v ' in txt_lower
      or 'san juan de aragon v ' in txt_lower
      or 'san juan de aragón v secc' in txt_lower
  ):
    return 'San Juan de Aragón 5a Sección'
  elif (
      'san juan de aragón vi' in txt_lower
      or 'san juan de aragon vi' in txt_lower
  ):
    return 'San Juan de Aragón 6a Sección'
  elif (
      'san juan de aragón vii' in txt_lower
      or 'san juan de aragon vii' in txt_lower
  ):
    return 'San Juan de Aragón 7a Sección'
  elif 'san juan de aragón' in txt_lower or 'san juan de aragon' in txt_lower:
    return 'San Juan de Aragón'

  # 4. Aragón y CTM
  if (
      'c.t.m. aragón' in txt_lower
      or 'ctm aragón' in txt_lower
      or 'c. t. m. aragón' in txt_lower
  ):
    return 'CTM Aragón'
  elif 'c.t.m. atzacoalco' in txt_lower or 'atzacoalco ctm' in txt_lower:
    return 'CTM Atzacoalco'
  elif 'c.t.m. el risco' in txt_lower or 'el risco ctm' in txt_lower:
    return 'CTM El Risco'
  elif 'aragón la villa' in txt_lower or 'aragon la villa' in txt_lower:
    return 'Aragón La Villa'
  elif 'aragón inguarán' in txt_lower or 'aragon inguarán' in txt_lower:
    return 'Aragón Inguarán'
  elif (
      'villa de aragón' in txt_lower
      or 'villa de aragon' in txt_lower
      or 'villa nezahualcóyotl' in txt_lower
  ):
    return 'Villa de Aragón'
  elif 'campestre aragón' in txt_lower or 'campestre aragon' in txt_lower:
    return 'Campestre Aragón'

  # 5. Casas Alemán
  if 'casas alem' in txt_lower:
    return 'Casas Alemán'

  # 6. Gertrudis Sánchez
  if 'gertrudis sánchez 1' in txt_lower or 'gertrudis sanchez 1' in txt_lower:
    return 'Gertrudis Sánchez 1a Sección'
  elif (
      'gertrudis sánchez 2' in txt_lower
      or 'gertrudis sanchez 2' in txt_lower
      or 'gertrudis sánchez ii' in txt_lower
  ):
    return 'Gertrudis Sánchez 2a Sección'
  elif (
      'gertrudis sánchez 3' in txt_lower
      or 'gertrudis sanchez 3' in txt_lower
      or 'gertrudis sánchez iii' in txt_lower
  ):
    return 'Gertrudis Sánchez 3a Sección'
  elif 'gertrudis' in txt_lower:
    return 'Gertrudis Sánchez'

  # 7. Pradera y Ticomán
  if 'pradera' in txt_lower:
    return 'Pradera'
  elif 'purísima ticom' in txt_lower or 'purisima ticom' in txt_lower:
    return 'La Purísima Ticomán'
  elif (
      'santa maría ticom' in txt_lower
      or 'santa maria ticom' in txt_lower
      or 'guadalupe ticomán' in txt_lower
  ):
    return 'Santa María Ticomán'
  elif (
      'san josé ticom' in txt_lower
      or 'san jose ticom' in txt_lower
      or 'la laguna ticom' in txt_lower
  ):
    return 'San José Ticomán'
  elif 'cuautepec' in txt_lower:
    return 'Cuautepec'
  elif 'zona escolar' in txt_lower:
    return 'Zona Escolar'
  elif 'cocoyotes' in txt_lower:
    return 'Cocoyotes'
  elif 'loma la palma' in txt_lower or 'la palma' in txt_lower:
    return 'La Palma'

  # 8. Guadalupe / Tepeyac / Industrial / Vallejo
  if 'guadalupe tepeyac' in txt_lower:
    return 'Guadalupe Tepeyac'
  elif 'guadalupe insurgentes' in txt_lower:
    return 'Guadalupe Insurgentes'
  elif 'tepeyac insurgentes' in txt_lower:
    return 'Tepeyac Insurgentes'
  elif 'valle del tepeyac' in txt_lower:
    return 'Valle del Tepeyac'
  elif 'guadalupe victoria' in txt_lower:
    return 'Guadalupe Victoria'
  elif 'guadalupe proletaria' in txt_lower:
    return 'Guadalupe Proletaria'
  elif 'nueva vallejo' in txt_lower:
    return 'Nueva Vallejo'
  elif 'vallejo' in txt_lower:
    return 'Vallejo'
  elif (
      'defensores de la república' in txt_lower
      or 'defensores de la republica' in txt_lower
  ):
    return 'Defensores de la República'
  elif (
      'constitución de la república' in txt_lower
      or 'constitucion de la republica' in txt_lower
  ):
    return 'Constitución de la República'

  # 9. Otras colonias de GAM
  if (
      'mártires de río blanco' in txt_lower
      or 'martires de rio blanco' in txt_lower
  ):
    return 'Mártires de Río Blanco'
  elif 'providencia' in txt_lower:
    return 'Providencia'
  elif 'san pedro el chico' in txt_lower:
    return 'San Pedro El Chico'
  elif 'gabriel hern' in txt_lower:
    return 'Gabriel Hernández'
  elif 'progreso nacional' in txt_lower:
    return 'Progreso Nacional'
  elif 'la escalera' in txt_lower:
    return 'San José de la Escalera'
  elif 'acueducto de guadalupe' in txt_lower or 'acueducto' in txt_lower:
    return 'Acueducto de Guadalupe'
  elif '15 de agosto' in txt_lower:
    return '15 de Agosto'
  elif '25 de julio' in txt_lower:
    return '25 de Julio'
  elif '7 de noviembre' in txt_lower or 'siete de noviembre' in txt_lower:
    return '7 de Noviembre'
  elif 'san bartolo atepehuacan' in txt_lower:
    return 'San Bartolo Atepehuacan'
  elif 'ex escuela de tiro' in txt_lower or 'exescuela' in txt_lower:
    return 'Ex Escuela de Tiro'
  elif 'salvador d' in txt_lower:
    return 'Salvador Díaz Mirón'
  elif 'villa gustavo a. madero' in txt_lower or txt_lower == 'villa':
    return 'Villa Gustavo A. Madero'

  if txt_lower in [
      'cdmx',
      'ciudad de méxico',
      'gustavo a. madero',
      'gustavo a madero',
      'cdmx #s/n',
      'cdmx #000',
      '596',
      'norte',
      's/c s/n',
      'entre martha y lidia',
      'mz. 18',
      'lt 7',
      'otilia',
      'manuel morales',
      'maria grever',
      'sucre norte s/n',
  ]:
    return 'Gustavo A. Madero'

  return txt_clean.title()


def limpiar_calle(calle):
  if pd.isna(calle):
    return 'Sin calle'

  c = str(calle).strip()

  # Prefijos de texto publicitario
  c = re.sub(
      r'^(?:PRIME|DESTACADO|CASA VENTA|CASA|VENTA|Venta CON Potencial Para|Venta'
      r' Cuchilla DEL Tesoro)\s*',
      '',
      c,
      flags=re.I,
  ).strip()
  c = re.sub(
      r'^(?:Casa disponible en venta en|Se vende casa en|Se vende casa|Venta de'
      r' casa en|Venta de casa|Casa en venta en|Casa en venta|Casa en|En'
      r' venta|Venta disponible en|venta disponible en|Venta)\s*',
      '',
      c,
      flags=re.I,
  ).strip()

  # Precios o montos numéricos al inicio
  c = re.sub(r'^\$\s*[\d\.,]+\s*(?:MXN)?\s*', '', c, flags=re.I).strip()
  c = re.sub(r'^\d+\s*mil(?:lones)?\s*', '', c, flags=re.I).strip()

  # Códigos postales o prefijos de colonia
  c = re.sub(r'^(?:Col\.|Colonia|Col)\s+.*$', '', c, flags=re.I).strip()
  c = re.sub(
      r'\b(?:Gustavo A\.? Madero|Ciudad de México|DF|CDMX)\b.*$',
      '',
      c,
      flags=re.I,
  ).strip()
  c = re.sub(r'\bC\.P\.\s*\d{5}\b', '', c, flags=re.I).strip()
  c = re.sub(r'^\b07\d{3}\b.*$', '', c, flags=re.I).strip()

  c = c.strip(' ,.-#')

  if len(c) < 2 or re.match(
      r'^(?:sin calle|sin nombre|sin nombre de calle|calle|s/n|sn|c\.p\.|c\.p|07\d{3}|cdmx|df)$',
      c,
      re.I,
  ):
    return 'Sin calle'

  return c


def ejecutar_limpieza_completa():
  df = pd.read_csv(ARCHIVO_ENTRADA)
  print(f'Cargados {len(df)} registros iniciales de "{ARCHIVO_ENTRADA}".')

  # 1. Homogeneización de Colonias y Calles
  df['colonia'] = df['colonia'].apply(limpiar_colonia)
  df['calle'] = df['calle'].apply(limpiar_calle)

  # 2. Eliminación de registros sin m2_construidos (Garantía de calidad para el modelo)
  inicial_rows = len(df)
  df = df.dropna(subset=['m2_construidos']).copy()
  df = df[df['m2_construidos'] > 0].copy()
  eliminados_m2 = inicial_rows - len(df)
  print(
      f' -> Eliminados {eliminados_m2} registros por no contar con'
      ' m2_construidos.'
  )

  # 3. Imputación de recámaras y baños basada en rangos de m2 construidos
  bins = [0, 120, 180, 250, 350, 500, 750, 5000]
  labels = [
      '<120m2',
      '120-180m2',
      '180-250m2',
      '250-350m2',
      '350-500m2',
      '500-750m2',
      '>750m2',
  ]
  df['m2_bin'] = pd.cut(df['m2_construidos'], bins=bins, labels=labels)

  # Tablas de medianas por rango de m2
  medianas_rec = (
      df.groupby('m2_bin', observed=False)['recamaras']
      .median()
      .round()
      .to_dict()
  )
  medianas_ban = (
      df.groupby('m2_bin', observed=False)['banos'].median().round().to_dict()
  )

  # Tablas condicionales de soporte
  rec_por_ban = (
      df.groupby('banos', observed=False)['recamaras']
      .median()
      .round()
      .to_dict()
  )
  ban_por_rec = (
      df.groupby('recamaras', observed=False)['banos'].median().round().to_dict()
  )

  imputados_rec, imputados_ban = 0, 0

  for idx, row in df.iterrows():
    # Imputar Recámaras
    if pd.isna(row['recamaras']):
      b_val = row['banos']
      m_bin = row['m2_bin']
      if pd.notna(b_val) and b_val in rec_por_ban:
        df.at[idx, 'recamaras'] = float(rec_por_ban[b_val])
      else:
        df.at[idx, 'recamaras'] = float(medianas_rec.get(m_bin, 3.0))
      imputados_rec += 1

    # Imputar Baños
    if pd.isna(row['banos']):
      r_val = df.at[idx, 'recamaras']
      m_bin = row['m2_bin']
      if pd.notna(r_val) and r_val in ban_por_rec:
        df.at[idx, 'banos'] = float(ban_por_rec[r_val])
      else:
        df.at[idx, 'banos'] = float(medianas_ban.get(m_bin, 2.0))
      imputados_ban += 1

  # Recalcular métricas cuantitativas
  df['precio_m2'] = np.round(df['precio_mxn'] / df['m2_construidos'], 2)
  df['relacion_banos_rec'] = np.round(df['banos'] / df['recamaras'], 2)

  # Eliminar columna auxiliar
  df.drop(columns=['m2_bin'], inplace=True)

  # Guardar el dataset limpio final
  df.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')

  print(f' -> Recámaras imputadas correctamente: {imputados_rec} registros.')
  print(f' -> Baños imputados correctamente: {imputados_ban} registros.')
  print(
      f"[✓] Proceso finalizado. Dataset limpio guardado en '{ARCHIVO_SALIDA}'"
      f' ({len(df)} inmuebles listos para el modelo).'
  )


if __name__ == '__main__':
  ejecutar_limpieza_completa()
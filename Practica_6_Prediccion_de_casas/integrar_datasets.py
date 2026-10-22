# -*- coding: utf-8 -*-
import re
import numpy as np
import pandas as pd


def integrar_y_limpiar_datasets():
  # 1. Cargar conjuntos enriquecidos
  df_prop = pd.read_csv('Practica_6_Prediccion_de_casas/enriched_propiedades.csv')
  df_i24 = pd.read_csv('Practica_6_Prediccion_de_casas/enriched_inmuebles24.csv')
  df_ml = pd.read_csv('Practica_6_Prediccion_de_casas/enriched_mercadolibre.csv')

  # 2. Concatenación vertical
  df_unificado = pd.concat([df_prop, df_i24, df_ml], ignore_index=True)
  total_inicial = len(df_unificado)

  # 3. Funciones de estandarización
  def estandarizar_colonia(c):
    if pd.isna(c):
      return 'sin colonia'
    txt = str(c).lower().strip()
    txt = re.sub(r'^(?:col\.|colonia|col|usd|sn|se vende casa)\s*', '', txt)
    return (
        txt.replace('nte.', 'norte')
        .replace('secc', 'sección')
        .replace('de jesús', 'de jesus')
    )

  def estandarizar_calle(calle):
    if pd.isna(calle):
      return 'Sin calle'
    c = str(calle).strip()
    if re.search(r'^(?:sin calle|sin nombre|c\.p\.|07\d{3}|cdmx)', c, re.I):
      return 'Sin calle'
    return c

  df_unificado['colonia_norm'] = df_unificado['colonia'].apply(
      estandarizar_colonia
  )
  df_unificado['calle_limpia'] = df_unificado['calle'].apply(estandarizar_calle)

  # 4. Agrupamiento de fuentes y desduplicación cruzada
  dup_cols = [
      'colonia_norm',
      'precio_mxn',
      'm2_construidos',
      'recamaras',
      'banos',
  ]

  fuentes_agrupadas = (
      df_unificado.groupby(dup_cols, dropna=False)['fuente']
      .apply(lambda x: ', '.join(sorted(set(x))))
      .reset_index()
  )
  fuentes_agrupadas.rename(
      columns={'fuente': 'portales_publicados'}, inplace=True
  )

  df_dedup = df_unificado.drop_duplicates(subset=dup_cols, keep='first').copy()
  df_dedup = df_dedup.merge(fuentes_agrupadas, on=dup_cols, how='left')

  # 5. Cálculo de métricas derivadas
  df_dedup['precio_m2'] = np.where(
      df_dedup['m2_construidos'] > 0,
      np.round(df_dedup['precio_mxn'] / df_dedup['m2_construidos'], 2),
      np.nan,
  )

  df_dedup['relacion_banos_rec'] = np.where(
      df_dedup['recamaras'] > 0,
      np.round(df_dedup['banos'] / df_dedup['recamaras'], 2),
      np.nan,
  )

  # Identificador correlativo
  df_dedup['id_propiedad'] = [
      f'GAM-CASAS-{i+1:04d}' for i in range(len(df_dedup))
  ]

  # 6. Reordenamiento y guardado
  cols_orden = [
      'id_propiedad',
      'fuente',
      'portales_publicados',
      'alcaldia',
      'colonia',
      'calle_limpia',
      'precio_mxn',
      'm2_construidos',
      'precio_m2',
      'recamaras',
      'banos',
      'relacion_banos_rec',
      'latitud',
      'longitud',
      'dist_avenida_principal_m',
      'dist_transporte_m',
  ]

  df_final = df_dedup[cols_orden].rename(columns={'calle_limpia': 'calle'})

  archivo_salida = 'Practica_6_Prediccion_de_casas/dataset_casas_gam_unificado.csv'
  df_final.to_csv(archivo_salida, index=False, encoding='utf-8-sig')

  print(
      f'[✓] Proceso de unificación completado.\n'
      f' - Publicaciones analizadas: {total_inicial}\n'
      f' - Duplicados cruzados consolidados: {total_inicial - len(df_final)}\n'
      f' - Dataset final unificado: {len(df_final)} inmuebles en'
      f' "{archivo_salida}"'
  )


if __name__ == '__main__':
  integrar_y_limpiar_datasets()
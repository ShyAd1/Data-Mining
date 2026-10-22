# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler


def preparar_datos_para_modelado():
  # 1. Cargar dataset limpio
  df = pd.read_csv('Practica_6_Prediccion_de_casas/dataset_casas_gam_limpio.csv')
  print(f'Registros cargados: {len(df)}')

  # 2. Corrección de los 3 casos atípicos específicos
  df.loc[df['id_propiedad'] == 'GAM-CASAS-0091', 'precio_mxn'] = 6290000.0
  df.loc[df['id_propiedad'] == 'GAM-CASAS-0736', 'precio_mxn'] = 14950000.0

  # Recalcular precio por m2 para los corregidos
  df['precio_m2'] = np.round(df['precio_mxn'] / df['m2_construidos'], 2)

  # 3. Filtrado de Outliers (Límites comerciales realistas en GAM)
  # Precios entre $800,000 y $35,000,000 MXN | m2 entre 40 y 1,200 | recámaras y baños <= 12
  df_model = df[
      (df['precio_mxn'] >= 800000)
      & (df['precio_mxn'] <= 35000000)
      & (df['m2_construidos'] >= 40)
      & (df['m2_construidos'] <= 1200)
      & (df['recamaras'] <= 12)
      & (df['banos'] <= 12)
      & (df['precio_m2'] >= 6000)
      & (df['precio_m2'] <= 85000)
  ].copy()

  print(f'Registros tras filtrado de outliers de mercado: {len(df_model)}')

  # 4. Transformación Logarítmica del Precio (Target Transformation)
  df_model['precio_log'] = np.log1p(df_model['precio_mxn'])

  # 5. Target Encoding para 'colonia' (Precio medio por m2 por colonia)
  colonia_target_map = df_model.groupby('colonia')['precio_m2'].mean().to_dict()
  df_model['colonia_precio_medio_m2'] = df_model['colonia'].map(
      colonia_target_map
  )

  # 6. Selección de Variables para los Modelos
  features = [
      'm2_construidos',
      'recamaras',
      'banos',
      'relacion_banos_rec',
      'colonia_precio_medio_m2',
      'dist_avenida_principal_m',
      'dist_transporte_m',
      'latitud',
      'longitud',
  ]

  X = df_model[features]
  y = df_model['precio_log']
  y_raw = df_model['precio_mxn']

  # 7. División Train / Test (80% / 20%)
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.20, random_state=42
  )

  # 8. Escalamiento de Atributos
  scaler = RobustScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)

  # Guardar datasets procesados para la fase de Modelado
  df_model.to_csv('Practica_6_Prediccion_de_casas/dataset_gam_preparado_modelo.csv', index=False)

  print('\n[✓] FASE 3 CRISP-DM (PREPARACIÓN DE DATOS) COMPLETADA:')
  print(
      f' - Muestras de entrenamiento (X_train): {X_train_scaled.shape[0]}'
      ' filas'
  )
  print(f' - Muestras de prueba (X_test): {X_test_scaled.shape[0]} filas')
  print(f' - Atributos de entrada seleccionados: {len(features)}')
  print(
      " - Dataset preparado guardado como: 'dataset_gam_preparado_modelo.csv'"
  )


if __name__ == '__main__':
  preparar_datos_para_modelado()
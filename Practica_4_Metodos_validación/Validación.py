# %% [markdown]
# # Validación para regresión
# 
# Usar los siguientes datasets para regresión:
# 
# - California Housing
# - Diabetes Regression
# - Auto MPG
# - Bike Sharing
# 
# Y para cada dataset aplicar los siguientes modelos:
# 
# - Regresión Lineal
# - Ridge Regression
# - KNN Regressor
# - Decision Tree Regressor
# - Random Forest Regressor
# - SVR
# 
# Metricas para cada modelo de regresión:
# 
# - MSE
# - RMSE
# - MAE
# - R2
# - MAPE
# - MSLE
# 
# Y a cada modelo se le aplicaran los cinco metodos de validación siguientes:
# 
# 1. Hold-Out / Train-Test Split:
# 	Se divide el conjunto de datos una sola vez. El modelo se entrena con una parte y se evalúa con la otra.
# 2. K-Fold Cross Validation:
# 	El dataset se divide en K partes. En cada iteración, una parte se usa para validar y las demás para entrenar. Al final se promedian los resultados.
# 	Usado en base de datos medianas.
# 3. Stratified K-Fold:
# 	Variante de K-Fold que conserva aproximadamente la proporción de clases en cada partición de clases en cada partición.
# 	Busca que en cada K (grupo) estén lo mas balanceados respecto a clases.
# 4. Leave-One-Out:
# 	Caso extremo de K-Fold cada observación se usa una vez como prueba y el resto como entrenamiento.
# 5. Bootstrap:
# 	Se generan múltiples muestras con remplazo. Algunos registros se repiten y otros quedan fuera. Permitiendo estimar el rendimiento del modelo.
# 
# 

# %%
"""
Importar modelos de regresión, metricas y metodos de validación
"""

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, LeaveOneOut

# Utilidades para escalar los datos y clonar los modelos en cada validación
from sklearn.base import clone
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import TransformedTargetRegressor

# %% [markdown]
# #### Consideraciones
# 
# - **Escalado:** Regresión Lineal, Ridge, KNN y SVR se entrenan dentro de un `Pipeline` con `StandardScaler`, de modo que el escalado se ajusta solo con los datos de entrenamiento de cada partición (sin fuga de información). Los árboles y el Random Forest no lo necesitan.
# - **SVR:** además se escala la variable objetivo (`TransformedTargetRegressor`), porque con objetivos de gran magnitud (p. ej. `cnt` o `MedHouseVal`) el SVR con parámetros por defecto rinde muy mal. Las métricas se calculan siempre en la escala original.
# - **Stratified K-Fold en regresión:** como no hay clases, la variable objetivo se divide en 10 intervalos por cuantiles y se estratifica sobre esos intervalos.
# - **Leave-One-Out:** entrena un modelo por observación, por lo que es inviable en datasets grandes. Con más de 500 observaciones (California Housing y Bike Sharing) se aplica sobre una muestra aleatoria de 500. Las predicciones de todas las iteraciones se juntan y las métricas se calculan una sola vez (con una sola observación por iteración, el R2 no está definido).
# - **Bootstrap:** en cada iteración se entrena con una muestra con reemplazo y se evalúa con las observaciones que quedaron fuera (out-of-bag). Se promedian las métricas de todas las iteraciones.
# - **Gráficas de regresión (30 por dataset):** para cada modelo y método se grafican valores reales vs predicciones. Hold-Out usa el 20 % de prueba; K-Fold y Stratified K-Fold usan la predicción de cada observación cuando estuvo en el fold de prueba; Leave-One-Out usa las predicciones individuales; Bootstrap usa la predicción promedio de cada observación en las iteraciones donde quedó fuera. El R2 de cada gráfica se calcula sobre esas predicciones juntas, por lo que puede diferir ligeramente del R2 de la tabla (promedio por fold o por iteración).
# - **Hold-Out:** 80 % entrenamiento y 20 % prueba. **K-Fold y Stratified K-Fold:** K = 5.

# %%
"""
Importar y cargar datasets
"""

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing, load_diabetes
from ucimlrepo import fetch_ucirepo

# California Housing (variable objetivo: MedHouseVal)
california = fetch_california_housing(as_frame=True)
df_california = california.frame

# Diabetes Regression (variable objetivo: target)
diabetes = load_diabetes(as_frame=True)
df_diabetes = diabetes.frame

# Auto MPG (variable objetivo: mpg)
auto_mpg = fetch_ucirepo(id=9)
df_auto = pd.concat([auto_mpg.data.features, auto_mpg.data.targets], axis=1)

# Bike Sharing (variable objetivo: cnt)
bike = fetch_ucirepo(id=275)
df_bike = pd.concat([bike.data.features, bike.data.targets], axis=1)

# %%
"""
Preprocesar los datasets: quitar columnas que no aportan, eliminar nulos y convertir variables categóricas a numéricas
"""

def preparar_dataset(df, columna_objetivo, columnas_ignorar=None):
    """
    Devuelve X (características numéricas) y y (variable objetivo numérica).
    """
    # 1. Hacer una copia para no alterar el dataset original
    datos = df.copy()

    # 2. Eliminar columnas que no aportan (IDs, fechas) o que filtran la respuesta
    if columnas_ignorar:
        columnas_existentes = [col for col in columnas_ignorar if col in datos.columns]
        datos = datos.drop(columns=columnas_existentes)

    # 3. Eliminar filas con valores nulos
    datos = datos.dropna()

    # 4. Separar la variable objetivo y forzarla a numérica
    y = pd.to_numeric(datos[columna_objetivo], errors='coerce')
    X = datos.drop(columns=[columna_objetivo])

    # 5. Convertir variables categóricas (texto) a numéricas
    X = pd.get_dummies(X, drop_first=True, dtype=float)

    # 6. Eliminar filas cuyo objetivo no se pudo convertir
    mascara = y.notna()
    X = X.loc[mascara].reset_index(drop=True)
    y = y.loc[mascara].reset_index(drop=True)

    return X, y

datasets = {
    "California Housing": preparar_dataset(df_california, 'MedHouseVal'),
    "Diabetes Regression": preparar_dataset(df_diabetes, 'target'),
    "Auto MPG": preparar_dataset(df_auto, 'mpg'),
    # casual y registered suman exactamente cnt, por lo que se eliminan para evitar fuga de información
    "Bike Sharing": preparar_dataset(df_bike, 'cnt', columnas_ignorar=['instant', 'dteday', 'casual', 'registered']),
}

# Resumen de los datasets ya trabajados
resumen = pd.DataFrame({
    nombre: {
        "Observaciones": X.shape[0],
        "Características": X.shape[1],
        "Objetivo mínimo": y.min(),
        "Objetivo máximo": y.max(),
        "Objetivo media": y.mean(),
    }
    for nombre, (X, y) in datasets.items()
}).T
print(resumen)

# %%
"""
Funcion para crear los modelos de regresión
"""

def crear_modelos():
    """
    Devuelve un diccionario con los 6 modelos de regresión.
    Los modelos sensibles a la escala se envuelven en un Pipeline con StandardScaler.
    """
    return {
        "Regresión Lineal": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "KNN": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5, n_jobs=-1)),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        # SVR: se escala también la variable objetivo
        "SVR": TransformedTargetRegressor(
            regressor=make_pipeline(StandardScaler(), SVR()),
            transformer=StandardScaler()
        ),
    }

# %%
"""
Funcion para calcular las metricas de regresión: MSE, RMSE, MAE, R2, MAPE y MSLE
"""

def calcular_metricas(y_real, y_pred):
    y_real = np.asarray(y_real, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mse = mean_squared_error(y_real, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_real, y_pred)
    r2 = r2_score(y_real, y_pred) if len(y_real) > 1 else np.nan

    # Evitar división por cero en MAPE
    y_real_safe = np.where(y_real == 0, 1e-10, y_real)
    mape = np.mean(np.abs((y_real - y_pred) / y_real_safe)) * 100

    # MSLE real (usando logaritmos); se recortan negativos porque log1p no los admite
    msle = np.mean(np.square(np.log1p(np.maximum(y_real, 0)) - np.log1p(np.maximum(y_pred, 0))))

    return {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2,
        "MAPE": mape,
        "MSLE": msle
    }

def promediar_metricas(lista_metricas):
    """
    Promedia las metricas obtenidas en cada iteración de la validación.
    """
    return pd.DataFrame(lista_metricas).mean().to_dict()

# %%
"""
Funciones para los cinco metodos de validación
Cada función devuelve: las metricas, los valores reales y las predicciones (para graficar la regresión)
"""

# 1. Hold-Out / Train-Test Split
def validacion_holdout(modelo, X, y, test_size=0.2, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    m = clone(modelo)
    m.fit(X_train, y_train)
    predicciones = m.predict(X_test)
    return calcular_metricas(y_test, predicciones), y_test.to_numpy(), predicciones


# 2. K-Fold Cross Validation
def validacion_kfold(modelo, X, y, k=5, random_state=42):
    cv = KFold(n_splits=k, shuffle=True, random_state=random_state)
    resultados = []
    predicciones = np.zeros(len(y))
    for idx_train, idx_test in cv.split(X):
        m = clone(modelo)
        m.fit(X.iloc[idx_train], y.iloc[idx_train])
        pred_fold = m.predict(X.iloc[idx_test])
        predicciones[idx_test] = pred_fold
        resultados.append(calcular_metricas(y.iloc[idx_test], pred_fold))
    # Metricas: promedio de los K folds. Predicciones: cada observación predicha cuando estuvo en prueba
    return promediar_metricas(resultados), y.to_numpy(), predicciones


# 3. Stratified K-Fold
def validacion_stratified_kfold(modelo, X, y, k=5, bins=10, random_state=42):
    # En regresión no hay clases: se discretiza el objetivo en intervalos por cuantiles
    y_estratos = pd.qcut(y, q=bins, labels=False, duplicates='drop')
    cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=random_state)
    resultados = []
    predicciones = np.zeros(len(y))
    for idx_train, idx_test in cv.split(X, y_estratos):
        m = clone(modelo)
        m.fit(X.iloc[idx_train], y.iloc[idx_train])
        pred_fold = m.predict(X.iloc[idx_test])
        predicciones[idx_test] = pred_fold
        resultados.append(calcular_metricas(y.iloc[idx_test], pred_fold))
    return promediar_metricas(resultados), y.to_numpy(), predicciones


# 4. Leave-One-Out
def validacion_leave_one_out(modelo, X, y, max_muestras=500, random_state=42):
    # Si el dataset es grande se trabaja con una muestra aleatoria para que el tiempo sea razonable
    if len(X) > max_muestras:
        idx = np.random.RandomState(random_state).choice(len(X), max_muestras, replace=False)
        X = X.iloc[idx].reset_index(drop=True)
        y = y.iloc[idx].reset_index(drop=True)

    predicciones = np.zeros(len(y))
    for idx_train, idx_test in LeaveOneOut().split(X):
        m = clone(modelo)
        m.fit(X.iloc[idx_train], y.iloc[idx_train])
        predicciones[idx_test] = m.predict(X.iloc[idx_test])

    # Las metricas se calculan con todas las predicciones juntas
    return calcular_metricas(y, predicciones), y.to_numpy(), predicciones


# 5. Bootstrap
def validacion_bootstrap(modelo, X, y, n_iteraciones=30, random_state=42):
    rng = np.random.RandomState(random_state)
    n = len(X)
    resultados = []
    suma_pred = np.zeros(n)
    conteo = np.zeros(n)
    for _ in range(n_iteraciones):
        # Muestra con reemplazo para entrenar; lo que no se eligió (out-of-bag) sirve para evaluar
        idx_train = rng.choice(n, size=n, replace=True)
        idx_test = np.setdiff1d(np.arange(n), idx_train)
        if len(idx_test) == 0:
            continue
        m = clone(modelo)
        m.fit(X.iloc[idx_train], y.iloc[idx_train])
        pred = m.predict(X.iloc[idx_test])
        suma_pred[idx_test] += pred
        conteo[idx_test] += 1
        resultados.append(calcular_metricas(y.iloc[idx_test], pred))

    # Para graficar: predicción promedio de cada observación en las iteraciones donde quedó fuera
    vistas = conteo > 0
    predicciones = suma_pred[vistas] / conteo[vistas]
    return promediar_metricas(resultados), y.to_numpy()[vistas], predicciones

# %%
"""
Funcion para aplicar los 6 modelos con los 5 metodos de validación a un dataset
"""

import time

def evaluar_validaciones(X, y, nombre_dataset, k=5, n_bootstrap=30, max_loo=500):
    """
    Devuelve:
    - un DataFrame con las metricas de cada modelo y cada metodo de validación
    - un diccionario {(modelo, metodo): (y_real, y_pred)} para graficar la regresión
    """
    metodos = {
        "Hold-Out": lambda m: validacion_holdout(m, X, y),
        "K-Fold": lambda m: validacion_kfold(m, X, y, k=k),
        "Stratified K-Fold": lambda m: validacion_stratified_kfold(m, X, y, k=k),
        "Leave-One-Out": lambda m: validacion_leave_one_out(m, X, y, max_muestras=max_loo),
        "Bootstrap": lambda m: validacion_bootstrap(m, X, y, n_iteraciones=n_bootstrap),
    }

    filas = []
    predicciones = {}
    for nombre_modelo, modelo in crear_modelos().items():
        for nombre_metodo, aplicar in metodos.items():
            inicio = time.time()
            metricas, y_real, y_pred = aplicar(modelo)
            print(f"{nombre_dataset} | {nombre_modelo} | {nombre_metodo} ({time.time() - inicio:.1f} s)")
            filas.append({
                "Dataset": nombre_dataset,
                "Modelo": nombre_modelo,
                "Validación": nombre_metodo,
                **metricas
            })
            predicciones[(nombre_modelo, nombre_metodo)] = (y_real, y_pred)

    return pd.DataFrame(filas), predicciones

# %%
"""
Funcion para mostrar graficamente la comparación de modelos y metodos de validación (MSE, RMSE, MAE, R2, MAPE y MSLE)
"""
import matplotlib.pyplot as plt

def graficar_comparacion(df_resultados, nombre_dataset):
    """
    Toma el DataFrame de resultados y genera 6 subgráficos (Metricas: MSE, RMSE, MAE, R2, MAPE y MSLE)
    con barras agrupadas por modelo y coloreadas por método de validación.
    """
    modelos = df_resultados['Modelo'].unique()
    metodos = df_resultados['Validación'].unique()

    fig, axes = plt.subplots(2, 3, figsize=(20, 10))
    fig.suptitle(f'Comparación de Modelos y Métodos de Validación: {nombre_dataset}', fontsize=16)

    # axes es una matriz de 2x3, se aplana para poder recorrerla con un solo ciclo
    for ax, metrica in zip(axes.flatten(), ['MSE', 'RMSE', 'MAE', 'R2', 'MAPE', 'MSLE']):
        tabla = df_resultados.pivot(index='Modelo', columns='Validación', values=metrica)
        tabla = tabla.loc[modelos, metodos]
        tabla.plot(kind='bar', ax=ax, width=0.85)

        ax.set_title(metrica)
        ax.set_xlabel('Modelo')
        ax.set_ylabel(metrica)
        ax.tick_params(axis='x', rotation=30)
        ax.legend(title='Validación', fontsize=8)

    plt.tight_layout()
    plt.show()

# %%
"""
Funcion para mostrar graficamente que tan bien predice cada modelo con cada metodo de validación (valores reales vs predicciones)
"""

def graficar_regresion(predicciones, nombre_dataset):
    """
    Genera una cuadricula de 6 modelos (filas) x 5 metodos de validación (columnas) = 30 graficas.
    Mientras más cerca estén los puntos de la línea roja, mejor predice el modelo.
    """
    modelos = list(dict.fromkeys(m for m, _ in predicciones))
    metodos = list(dict.fromkeys(v for _, v in predicciones))

    fig, axes = plt.subplots(len(modelos), len(metodos), figsize=(5 * len(metodos), 4 * len(modelos)))
    fig.suptitle(f'Regresión: Valores Reales vs Predicciones - {nombre_dataset}', fontsize=18, y=1.0)

    for i, nombre_modelo in enumerate(modelos):
        for j, nombre_metodo in enumerate(metodos):
            ax = axes[i, j]
            y_real, y_pred = predicciones[(nombre_modelo, nombre_metodo)]
            r2 = r2_score(y_real, y_pred)

            ax.scatter(y_real, y_pred, alpha=0.5, s=12)
            ax.plot([y_real.min(), y_real.max()], [y_real.min(), y_real.max()], 'r--', lw=2)
            ax.set_title(f'{nombre_modelo} | {nombre_metodo}\nR2 = {r2:.3f}', fontsize=10)
            ax.set_xlabel('Valores Reales')
            ax.set_ylabel('Predicciones')

    plt.tight_layout()
    plt.show()

# %% [markdown]
# #### California Housing

# %%
"""
Aplicar los modelos y metodos de validación a California Housing (dataset grande: 10 iteraciones de Bootstrap)
"""
from IPython.display import display

X, y = datasets["California Housing"]
resultados_california, predicciones_california = evaluar_validaciones(X, y, "California Housing", n_bootstrap=10)
display(resultados_california)
graficar_comparacion(resultados_california, "California Housing")
graficar_regresion(predicciones_california, "California Housing")

# %% [markdown]
# #### Diabetes Regression

# %%
"""
Aplicar los modelos y metodos de validación a Diabetes Regression
"""

X, y = datasets["Diabetes Regression"]
resultados_diabetes, predicciones_diabetes = evaluar_validaciones(X, y, "Diabetes Regression", n_bootstrap=30)
display(resultados_diabetes)
graficar_comparacion(resultados_diabetes, "Diabetes Regression")
graficar_regresion(predicciones_diabetes, "Diabetes Regression")

# %% [markdown]
# #### Auto MPG

# %%
"""
Aplicar los modelos y metodos de validación a Auto MPG
"""

X, y = datasets["Auto MPG"]
resultados_auto, predicciones_auto = evaluar_validaciones(X, y, "Auto MPG", n_bootstrap=30)
display(resultados_auto)
graficar_comparacion(resultados_auto, "Auto MPG")
graficar_regresion(predicciones_auto, "Auto MPG")

# %% [markdown]
# #### Bike Sharing

# %%
"""
Aplicar los modelos y metodos de validación a Bike Sharing (dataset grande: 10 iteraciones de Bootstrap)
"""

X, y = datasets["Bike Sharing"]
resultados_bike, predicciones_bike = evaluar_validaciones(X, y, "Bike Sharing", n_bootstrap=10)
display(resultados_bike)
graficar_comparacion(resultados_bike, "Bike Sharing")
graficar_regresion(predicciones_bike, "Bike Sharing")

# %% [markdown]
# #### Resumen

# %%
"""
Resumen: mejor modelo (menor RMSE) por dataset y metodo de validación
"""

resultados_totales = pd.concat(
    [resultados_california, resultados_diabetes, resultados_auto, resultados_bike],
    ignore_index=True
)

indices_mejores = resultados_totales.groupby(['Dataset', 'Validación'])['RMSE'].idxmin()
mejores_modelos = resultados_totales.loc[indices_mejores, ['Dataset', 'Validación', 'Modelo', 'RMSE', 'R2']]
display(mejores_modelos.reset_index(drop=True))



# Práctica 7: Reglas de Asociación

Sistema de recomendaciones basado en reglas de asociación con el dataset **Instacart Market Basket Analysis**. El análisis compara Apriori, FP-Growth y Eclat, genera reglas y permite consultarlas mediante una aplicación Streamlit.

## Requisitos

- Python 3.10 o superior.
- Los archivos del dataset de Instacart.
- Jupyter Notebook o Visual Studio Code para ejecutar `main.ipynb`.

## Instalación

Desde la carpeta de la práctica, cree y active un entorno virtual (opcional, pero recomendado):

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Instale las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requeriments.txt
```

## Descarga del dataset

Descargue los datos desde Kaggle:

<https://www.kaggle.com/competitions/instacart-market-basket-analysis/data>

Coloque estos cinco archivos dentro de una carpeta llamada `Dataset` en la raíz del proyecto:

```text
Practica_7_Reglas_Asociación/
├── Dataset/
│   ├── aisles.csv
│   ├── departments.csv
│   ├── orders.csv
│   ├── order_products__prior.csv
│   └── products.csv
├── main.ipynb
├── app.py
├── requeriments.txt
└── README.md
```

La ruta debe ser exactamente `Dataset/`, ya que el notebook y la aplicación utilizan rutas relativas como `Dataset/orders.csv`.

## Ejecución del análisis

Abra `main.ipynb` en Jupyter o VS Code, seleccione el entorno virtual como kernel y ejecute las celdas en orden.

El notebook:

1. Carga y prepara los archivos de Instacart.
2. Construye la matriz transaccional.
3. Ejecuta los algoritmos de minería y genera las reglas.
4. Guarda las reglas en `Dataset/reglas_asociacion.csv`.
5. Genera o actualiza `app.py` mediante la celda con `%%writefile app.py`.
6. Ejecuta la evaluación de precisión, cobertura y robustez.

> El procesamiento puede requerir varios minutos y bastante memoria, especialmente al ejecutar FP-Growth sobre la muestra completa.

## Ejecución de la aplicación

Después de ejecutar el notebook y generar `Dataset/reglas_asociacion.csv`, inicie Streamlit desde la raíz del proyecto:

```bash
streamlit run app.py
```

Se abrirá la aplicación en:

<http://localhost:8501>

En la aplicación podrá:

- Seleccionar de uno a cinco productos para formar una canasta.
- Ajustar los umbrales de soporte, confianza y lift.
- Consultar recomendaciones basadas en reglas.
- Ver la regla utilizada y la explicación de cada recomendación.
- Recibir una recomendación por popularidad cuando no exista una regla aplicable.

## Solución de problemas

- **`FileNotFoundError` para un CSV:** confirme que los cinco archivos estén directamente dentro de `Dataset/`.
- **Falta `reglas_asociacion.csv`:** ejecute primero las celdas del notebook correspondientes a la generación de reglas.
- **No se encuentra `streamlit`:** active el entorno virtual y vuelva a ejecutar `pip install -r requeriments.txt`.
- **Problemas de memoria:** reduzca el número de órdenes muestreadas o aumente el soporte mínimo en el notebook.

## Reproducibilidad

El notebook fija la semilla aleatoria en `42`. Los resultados pueden variar si se modifica la muestra, los umbrales o la versión de las dependencias.

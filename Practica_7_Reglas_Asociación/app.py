# ==============================================================================
# PARTE 6: SISTEMA STREAMLIT CON FALLBACK DINÁMICO
# ==============================================================================
import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Recomendador Instacart", layout="wide")
st.title("Recomendador con Fallback Dinámico")

@st.cache_data
def load_data():
    rules = pd.read_csv('Dataset/reglas_asociacion.csv')
    rules['antecedents'] = rules['antecedents'].apply(eval).apply(frozenset)
    rules['consequents'] = rules['consequents'].apply(eval).apply(frozenset)
    # Cargar TODOS los productos del catálogo, no solo los de las reglas
    try:
        prods_df = pd.read_csv('Dataset/products.csv')
        prods = sorted(prods_df['product_name'].dropna().unique().tolist())
    except Exception:
        prods = sorted({i for s in rules['antecedents'] for i in s}
                       .union({i for s in rules['consequents'] for i in s}))
    top_popular_item = rules['consequents'].explode().value_counts().idxmax() if not rules.empty else 'Banana'
    return rules, prods, top_popular_item

try:
    rules, prods, popular = load_data()

    st.sidebar.header("Umbrales")
    sup  = st.sidebar.slider("Soporte",    0.001, 0.05, 0.002)
    conf = st.sidebar.slider("Confianza",  0.01,  1.0,  0.10)
    lift = st.sidebar.slider("Lift",       1.0,   5.0,  1.2)

    sel = st.multiselect("Tu canasta (1-5 productos):", prods, max_selections=5)

    if st.button("Recomendar") and sel:
        basket = frozenset(sel)
        sub = rules[(rules['support'] >= sup) &
                    (rules['confidence'] >= conf) &
                    (rules['lift'] >= lift)]
        sub = sub[sub['antecedents'].apply(lambda a: a.issubset(basket))]

        if sub.empty:
            st.warning(f"No se encontraron reglas que cumplan los umbrales. "
                       f"Recomendación por popularidad: **{popular}**")
        else:
            sub = sub.sort_values(['lift', 'confidence'], ascending=[False, False])
            seen = set()
            st.success("Recomendaciones:")
            for _, r in sub.iterrows():
                for c in r['consequents']:
                    if c not in basket and c not in seen:
                        seen.add(c)
                        ant_str = ' + '.join(sorted(r['antecedents']))
                        st.markdown(f"### {c}")
                        st.markdown(
                            f"- **Regla utilizada:** `{{{ant_str}}} → {{{c}}}`\n"
                            f"- **Soporte:** {r['support']:.4f} | "
                            f"**Confianza:** {r['confidence']:.2%} | "
                            f"**Lift:** {r['lift']:.2f}\n"
                            f"- **¿Por qué se recomienda?** Porque {r['confidence']:.0%} de "
                            f"las canastas que contienen `{ant_str}` también incluyen `{c}`, "
                            f"lo que es **{r['lift']:.1f}×** más frecuente que la probabilidad "
                            f"base de comprar `{c}`."
                        )
                if len(seen) >= 5: break
            if len(seen) < 5:
                st.info(f"Solo se encontraron {len(seen)} recomendaciones con reglas. "
                        f"Completa con popularidad: **{popular}**")
except FileNotFoundError:
    st.error("Archivo reglas_asociacion.csv faltante.")

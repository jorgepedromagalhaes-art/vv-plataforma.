import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="VV - Vigilância Educacional", page_icon="📚", layout="wide")

st.title("📚 VV - Vigilância Educacional")
st.markdown("### Monitoramento do Diário Oficial da União")

def carregar_dados():
    if os.path.exists('dados.json'):
        with open('dados.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

dados = carregar_dados()

if not dados:
    st.info("Aguardando a primeira varredura do sistema...")
else:
    df = pd.DataFrame(dados)
    termo = st.sidebar.multiselect("Filtrar por Programa:", df['palavra_chave'].unique())
    
    df_final = df[df['palavra_chave'].isin(termo)] if termo else df
    df_final = df_final.iloc[::-1] # Mostrar mais recentes primeiro

    for _, row in df_final.iterrows():
        with st.expander(f"{row['data']} - {row['palavra_chave']}: {row['titulo']}"):
            st.write(row['extrato'])
            st.link_button("Abrir no DOU", row['link'])

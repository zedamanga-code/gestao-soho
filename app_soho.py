import streamlit as st
import pandas as pd

# 1. Configuração Visual
st.set_page_config(page_title="Manutenção Soho", page_icon="🛠️")

st.title("🛠️ Sistema de Manutenção Soho")
st.subheader("Registro de Atividades e Laudos")
st.divider()

# 2. Link da sua Planilha (Formato CSV)
url = "https://docs.google.com/spreadsheets/d/12OAsmeEE9DcDbvLlQhI_Tw85UYTa6dk2Tn7YhN-sjs4/export?format=csv"

try:
    # Lendo os dados da aba EQUIPAMENTOS
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    
    if 'TAG' in df.columns:
        lista_tags = df['TAG'].dropna().unique().tolist()
        st.success("✅ Equipamentos carregados com sucesso!")
    else:
        st.error("Coluna 'TAG' não encontrada.")
        lista_tags = ["Erro na planilha"]
except Exception as e:
    st.error(f"Erro de conexão: {e}")
    lista_tags = ["Bomba 01", "Bomba 02"]

# --- FORMULÁRIO DE ENTRADA ---

# Seleção do equipamento
equipamento = st.selectbox("Selecione o Equipamento:", lista_tags)

# Novo campo: Upload de PDF
st.write("---")
st.subheader("Documentação")
arquivo_pdf = st.file_uploader("Fazer upload de relatório (Somente PDF)", type=["pdf"])

if arquivo_pdf is not None:
    st.info(f"Arquivo selecionado: {arquivo_pdf.name}")

# Relato em texto
relato = st.text_area("Descrição resumida do serviço:")

# Botão de salvar
if st.button("Finalizar e Registrar"):
    if relato and arquivo_pdf:
        st.success(f"✅ Registro e PDF de '{equipamento}' prontos para envio!")
        st.balloons()
        # Aqui entra a lógica de salvar o arquivo no Google Drive ou Servidor
    elif not arquivo_pdf:
        st.warning("⚠️ Por favor, anexe o relatório em PDF.")
    else:
        st.warning("⚠️ Por favor, preencha a descrição do serviço.")

st.divider()
st.caption("Versão 1.2 - Suporte a anexos PDF")
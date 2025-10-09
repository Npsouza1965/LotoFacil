import streamlit as st
import pandas as pd
import os

CSV_PATH = 'dados/lotofacil.csv'

def exibir_dados_loto():
    st.header("📁 Dados da Lotofácil")
    
    if not os.path.exists(CSV_PATH):
        st.warning("📝 Nenhum arquivo carregado ainda.")
        st.info("Vá para a aba 'Análise de Jogos' para fazer upload do arquivo CSV.")
        return
    
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        
        # Estatísticas rápidas
        st.subheader("📊 Estatísticas")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Concursos", len(df))
        with col2:
            st.metric("Período", f"{df['Concurso'].min()} - {df['Concurso'].max()}")
        with col3:
            st.metric("Primeira Data", df.iloc[0]['Data Sorteio'] if 'Data Sorteio' in df.columns else 'N/A')
        with col4:
            st.metric("Última Data", df.iloc[-1]['Data Sorteio'] if 'Data Sorteio' in df.columns else 'N/A')
        
        st.markdown("---")
        
        # Visualização dos dados
        st.subheader("📋 Últimos 10 Concursos")
        
        # Simplificar colunas para exibição
        colunas_exibicao = ['Concurso', 'Data Sorteio']
        colunas_bolas = [f'Bola{i}' for i in range(1, 16) if f'Bola{i}' in df.columns]
        colunas_exibicao.extend(colunas_bolas[:5])  # Mostrar apenas 5 bolas para não ficar muito largo
        
        st.dataframe(
            df[colunas_exibicao].tail(10), 
            use_container_width=True,
            hide_index=True
        )
        
        # Download do arquivo processado
        st.markdown("---")
        st.subheader("💾 Exportar Dados")
        
        csv = df.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label="📥 Baixar CSV Processado",
            data=csv,
            file_name="lotofacil_processed.csv",
            mime="text/csv",
            help="Baixar arquivo CSV com todos os dados"
        )
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
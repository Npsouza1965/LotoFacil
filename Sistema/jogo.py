import streamlit as st
import pandas as pd
import os
import io
from collections import Counter
from datetime import datetime

# PARA STREAMLIT CLOUD - caminho relativo
CSV_PATH = 'dados/lotofacil.csv'

def exibir_jogo():
    st.header("📊 Análise de Jogos - Lotofácil")
    
    # Seção de upload de arquivo
    if not os.path.exists(CSV_PATH):
        exibir_secao_upload()
        return
    
    # Se arquivo existe, carregar e mostrar análise
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        
        # Informações básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Total de Concursos", len(df))
        with col2:
            st.metric("🎯 Primeiro Concurso", df['Concurso'].min())
        with col3:
            st.metric("🔥 Último Concurso", df['Concurso'].max())
        
        st.markdown("---")
        
        # Análise de frequência (exemplo)
        st.subheader("📈 Frequência dos Números")
        todos_numeros = []
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in df.columns:
                todos_numeros.extend(df[coluna].dropna().astype(int).tolist())
        
        if todos_numeros:
            frequencia = Counter(todos_numeros)
            
            # Mostrar os 15 números mais frequentes
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Números Mais Sorteados:**")
                for num, freq in frequencia.most_common(15):
                    st.write(f"🎯 Número {num}: {freq} vezes")
            
            with col2:
                st.write("**Números Menos Sorteados:**")
                for num, freq in frequencia.most_common()[-15:]:
                    st.write(f"⚡ Número {num}: {freq} vezes")
        
        # Sugestão de jogo (exemplo simples)
        st.markdown("---")
        st.subheader("💡 Sugestão de Jogo")
        
        if st.button("🔄 Gerar Sugestão"):
            if todos_numeros:
                numeros_mais_frequentes = [num for num, freq in frequencia.most_common(15)]
                sugestao = sorted(numeros_mais_frequentes[:15])
                
                st.success("Sugestão baseada nos números mais frequentes:")
                st.info(f"**{' - '.join(map(str, sugestao))}**")
                
                # Mostrar em formato de cartela
                st.write("**Cartela:**")
                cols = st.columns(5)
                for i, num in enumerate(sugestao):
                    with cols[i % 5]:
                        st.markdown(f"<div style='text-align: center; padding: 10px; border: 2px solid #1E88E5; border-radius: 10px; margin: 5px;'><strong>{num}</strong></div>", 
                                  unsafe_allow_html=True)
        
        # Botão para recarregar arquivo
        st.markdown("---")
        if st.button("🔄 Carregar Novo Arquivo CSV"):
            if os.path.exists(CSV_PATH):
                os.remove(CSV_PATH)
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.info("💡 Tente fazer upload novamente com um arquivo válido.")

def exibir_secao_upload():
    st.warning("📁 Arquivo de dados não encontrado")
    
    st.info("""
    ### 📋 Para começar, faça upload do arquivo CSV com os dados da Lotofácil
    
    **Requisitos do arquivo:**
    - Formato: CSV com separador ponto e vírgula (;)
    - Colunas: Concurso, Data Sorteio, Bola1, Bola2, ..., Bola15
    - Encoding: UTF-8 (recomendado)
    
    **Exemplo das primeiras linhas:**
    ```
    Concurso;Data Sorteio;Bola1;Bola2;Bola3;...;Bola15
    1;31/03/2024;1;2;3;...;15
    2;01/04/2024;2;4;6;...;20
    ```
    """)
    
    uploaded_file = st.file_uploader(
        "📤 Faça upload do arquivo Lotofacil.csv", 
        type=['csv'],
        help="Arquivo CSV com dados históricos da Lotofácil"
    )
    
    if uploaded_file is not None:
        try:
            # Ler o arquivo para validar
            content = uploaded_file.getvalue().decode('utf-8')
            df = pd.read_csv(io.StringIO(content), sep=';')
            
            # Validar colunas básicas
            colunas_necessarias = ['Concurso', 'Data Sorteio']
            colunas_bolas = [f'Bola{i}' for i in range(1, 16)]
            colunas_validas = all(col in df.columns for col in colunas_necessarias)
            
            if colunas_validas:
                # Criar diretório se não existir
                os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
                
                # Salvar arquivo
                with open(CSV_PATH, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                st.success("✅ Arquivo carregado com sucesso!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Arquivo inválido. Verifique as colunas necessárias.")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
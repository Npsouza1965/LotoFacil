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
        
        # Análise de frequência
        st.subheader("📈 Frequência dos Números")
        todos_numeros = []
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in df.columns:
                todos_numeros.extend(df[coluna].dropna().astype(int).tolist())
        
        if todos_numeros:
            frequencia = Counter(todos_numeros)
            total_sorteios = len(todos_numeros)
            
            # Calcular percentuais
            frequencia_com_percentual = {}
            for num in range(1, 26):
                freq = frequencia.get(num, 0)
                percentual = (freq / total_sorteios) * 100
                frequencia_com_percentual[num] = {
                    'frequencia': freq,
                    'percentual': percentual
                }
            
            # Exibir frequência em 5 colunas com 5 números cada
            st.write("**Frequência de Todos os Números (1-25):**")
            
            # Criar 5 colunas
            cols = st.columns(5)
            
            # Dividir os números em 5 grupos de 5
            grupos = []
            for i in range(5):
                grupo = list(range(i*5 + 1, i*5 + 6))
                grupos.append(grupo)
            
            # Exibir cada grupo em uma coluna
            for col_idx, col in enumerate(cols):
                with col:
                    for num in grupos[col_idx]:
                        if num <= 25:  # Garantir que só vai até 25
                            dados = frequencia_com_percentual[num]
                            st.markdown(
                                f"""
                                <div style='
                                    text-align: center; 
                                    padding: 8px; 
                                    border: 2px solid #1E88E5; 
                                    border-radius: 8px; 
                                    margin: 4px; 
                                    background-color: #f8f9fa;
                                    font-size: 0.9em;
                                '>
                                    <strong>Nº {num}</strong><br>
                                    <span style='font-size: 0.8em;'>
                                    {dados['frequencia']} vezes<br>
                                    {dados['percentual']:.1f}%
                                    </span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
            
            # Estatísticas adicionais
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Estatísticas Gerais:**")
                st.write(f"• Total de sorteios analisados: {total_sorteios}")
                st.write(f"• Número mais frequente: {frequencia.most_common(1)[0][0]} ({frequencia.most_common(1)[0][1]} vezes)")
                st.write(f"• Número menos frequente: {frequencia.most_common()[-1][0]} ({frequencia.most_common()[-1][1]} vezes)")
                
            with col2:
                st.write("**🎯 Ranking Top 5:**")
                for i, (num, freq) in enumerate(frequencia.most_common(5), 1):
                    percentual = (freq / total_sorteios) * 100
                    st.write(f"{i}º - Número {num}: {freq} vezes ({percentual:.1f}%)")
        
        # Sugestão de jogo (exemplo simples)
        st.markdown("---")
        st.subheader("💡 Sugestão de Jogo")
        
        if st.button("🔄 Gerar Sugestão"):
            if todos_numeros:
                numeros_mais_frequentes = [num for num, freq in frequencia.most_common(15)]
                sugestao = sorted(numeros_mais_frequentes[:15])
                
                st.success("Sugestão baseada nos números mais frequentes:")
                st.info(f"**{' - '.join(map(str, sugestao))}**")
                
                # Mostrar em formato de cartela responsiva
                st.write("**Cartela:**")
                cols_cartela = st.columns(5)
                for i, num in enumerate(sugestao):
                    with cols_cartela[i % 5]:
                        st.markdown(
                            f"""
                            <div style='
                                text-align: center; 
                                padding: 12px; 
                                border: 2px solid #4CAF50; 
                                border-radius: 10px; 
                                margin: 5px; 
                                background-color: #e8f5e8;
                                font-size: 1.1em;
                            '>
                                <strong>{num}</strong>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
        
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
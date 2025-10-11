import streamlit as st
import pandas as pd
import os
import io
from collections import Counter
from datetime import datetime
import numpy as np

# Caminho do arquivo CSV
CSV_PATH = 'dados/lotofacil.csv'

# -------------------------------------------------------------
# Criação de arquivo de teste
# -------------------------------------------------------------
def criar_arquivo_teste():
    """Cria um arquivo de dados de exemplo para teste"""
    try:
        os.makedirs('dados', exist_ok=True)
        
        np.random.seed(42)
        num_concursos = 100
        concursos = []
        
        for i in range(1, num_concursos + 1):
            numeros = np.random.choice(range(1, 26), 15, replace=False)
            numeros.sort()
            
            concurso = {
                'Concurso': i,
                'Data Sorteio': (datetime.now() - pd.Timedelta(days=num_concursos - i)).strftime('%d/%m/%Y')
            }
            
            for j, num in enumerate(numeros, 1):
                concurso[f'Bola{j}'] = num
                
            concursos.append(concurso)
        
        df = pd.DataFrame(concursos)
        df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
        
        st.success(f"✅ Arquivo de teste criado com {num_concursos} concursos!")
        st.dataframe(df.head(3))
        return True
        
    except Exception as e:
        st.error(f"Erro ao criar arquivo de teste: {e}")
        return False

# -------------------------------------------------------------
# Verificação de estrutura
# -------------------------------------------------------------
def verificar_estrutura():
    """Verifica e cria a estrutura de pastas necessária"""
    if not os.path.exists('dados'):
        os.makedirs('dados', exist_ok=True)

# -------------------------------------------------------------
# Exibição principal do jogo
# -------------------------------------------------------------
def exibir_jogo():
    verificar_estrutura()
    st.header("📊 Análise de Jogos - Lotofácil")
    
    if not os.path.exists(CSV_PATH):
        st.warning("📁 Arquivo de dados não encontrado")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Criar Dados de Teste", type="primary", use_container_width=True):
                if criar_arquivo_teste():
                    st.rerun()
        
        with col2:
            if st.button("📤 Fazer Upload", use_container_width=True):
                pass
        
        st.markdown("---")
        exibir_secao_upload()
        return
    
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        
        with st.expander("🔍 DEBUG - Informações do DataFrame"):
            st.write(f"• Shape: {df.shape}")
            st.write(f"• Colunas: {list(df.columns)}")
            st.dataframe(df.head(3))
            
            colunas_bola = [f'Bola{i}' for i in range(1, 16)]
            colunas_existentes = [col for col in colunas_bola if col in df.columns]
            st.write(f"• Colunas Bola encontradas: {colunas_existentes}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Total de Concursos", len(df))
        with col2:
            st.metric("🎯 Primeiro Concurso", df['Concurso'].min())
        with col3:
            st.metric("🔥 Último Concurso", df['Concurso'].max())
        
        st.markdown("---")
        st.subheader("📈 Frequência dos Números")
        
        todos_numeros = []
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in df.columns:
                numeros_coluna = pd.to_numeric(df[coluna], errors='coerce').dropna().astype(int).tolist()
                todos_numeros.extend(numeros_coluna)
        
        with st.expander("🔍 DEBUG - Números Coletados"):
            st.write(f"Total coletados: {len(todos_numeros)}")
            st.write(f"Números únicos: {len(set(todos_numeros))}")
        
        if todos_numeros:
            frequencia = Counter(todos_numeros)
            total_sorteios = len(todos_numeros)
            
            frequencia_com_percentual = {}
            for num in range(1, 26):
                freq = frequencia.get(num, 0)
                percentual = (freq / total_sorteios) * 100 if total_sorteios > 0 else 0
                frequencia_com_percentual[num] = {
                    'frequencia': freq,
                    'percentual': percentual
                }
            
            st.write("**Frequência de Todos os Números (1-25):**")
            cols = st.columns(5)
            grupos = [list(range(i*5 + 1, i*5 + 6)) for i in range(5)]
            
            for col_idx, col in enumerate(cols):
                with col:
                    for num in grupos[col_idx]:
                        if num <= 25:
                            dados = frequencia_com_percentual[num]
                            cor_borda = "#1E88E5"
                            if dados['frequencia'] > frequencia.most_common(1)[0][1] * 0.8:
                                cor_borda = "#FF6B6B"
                            elif dados['frequencia'] < frequencia.most_common()[-1][1] * 1.2:
                                cor_borda = "#4ECDC4"
                            
                            st.markdown(
                                f"""
                                <div style='
                                    text-align: center; 
                                    padding: 10px; 
                                    border: 3px solid {cor_borda}; 
                                    border-radius: 10px; 
                                    margin: 5px; 
                                    background-color: #f8f9fa;
                                    font-size: 1em;
                                    color: #000000;
                                '>
                                    <div style='font-weight: bold; font-size: 1.1em;'>Nº {num}</div>
                                    <div style='font-size: 0.85em; margin-top: 5px;'>
                                        {dados['frequencia']} vezes<br>
                                        <strong>{dados['percentual']:.1f}%</strong>
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Estatísticas Gerais:**")
                st.write(f"• Total sorteios: {total_sorteios:,}")
                st.write(f"• Concursos: {len(df):,}")
                if frequencia.most_common(1):
                    num_mais_freq, freq_mais = frequencia.most_common(1)[0]
                    percent_mais = (freq_mais / total_sorteios) * 100
                    st.write(f"• Mais frequente: **{num_mais_freq}** ({freq_mais}x - {percent_mais:.1f}%)")
                if frequencia.most_common():
                    num_menos_freq, freq_menos = frequencia.most_common()[-1]
                    percent_menos = (freq_menos / total_sorteios) * 100
                    st.write(f"• Menos frequente: **{num_menos_freq}** ({freq_menos}x - {percent_menos:.1f}%)")
                
            with col2:
                st.write("**🎯 Ranking Top 5:**")
                for i, (num, freq) in enumerate(frequencia.most_common(5), 1):
                    percentual = (freq / total_sorteios) * 100
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "4️⃣" if i == 4 else "5️⃣"
                    st.write(f"{emoji} **Número {num}**: {freq} vezes ({percentual:.1f}%)")
        
        # -------------------------------------------------------------
        # Sugestões de jogos (9 melhores + 6 piores)
        # -------------------------------------------------------------
        st.markdown("---")
        st.subheader("💡 Sugestões de Jogos")

        if st.button("🎯 Gerar 6 Sugestões (9 melhores + 6 piores)", type="primary", use_container_width=True):
            if todos_numeros and len(todos_numeros) > 0:
                mais_frequentes = [num for num, _ in frequencia.most_common(9)]
                menos_frequentes = [num for num, _ in frequencia.most_common()[-6:]]

                st.success("🎉 **6 Sugestões de jogo (9 melhores + 6 piores):**")

                for i in range(6):
                    jogo = sorted(np.random.choice(mais_frequentes, 9, replace=False).tolist() +
                                  np.random.choice(menos_frequentes, 6, replace=False).tolist())

                    st.markdown(f"##### 💡 Sugestão {i+1}")
                    numeros_formatados = " - ".join([f"**{num:02d}**" for num in jogo])
                    st.markdown(
                        f"<div style='text-align: center; font-size: 1.2em; padding: 10px; background-color: #e8f5e8; border-radius: 10px; margin: 5px 0; color: #000000;'>{numeros_formatados}</div>",
                        unsafe_allow_html=True
                    )

                    cols_cartela = st.columns(5)
                    for j, num in enumerate(jogo):
                        with cols_cartela[j % 5]:
                            st.markdown(
                                f"""
                                <div style='
                                    text-align: center; 
                                    padding: 15px; 
                                    border: 3px solid #4CAF50; 
                                    border-radius: 12px; 
                                    margin: 5px; 
                                    background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
                                    font-size: 1.2em;
                                    font-weight: bold;
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                    color: #000000;
                                '>{num}</div>
                                """,
                                unsafe_allow_html=True
                            )
            else:
                st.error("❌ Não há dados suficientes para gerar sugestões")

        st.markdown("---")
        col_rec1, col_rec2, col_rec3 = st.columns([1, 1, 1])
        with col_rec2:
            if st.button("🔄 Carregar Novo Arquivo CSV", use_container_width=True):
                if os.path.exists(CSV_PATH):
                    os.remove(CSV_PATH)
                st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.info("💡 Tente fazer upload novamente com um arquivo válido.")

# -------------------------------------------------------------
# Upload manual do arquivo CSV
# -------------------------------------------------------------
def exibir_secao_upload():
    st.info("""
    ### 📋 Para começar, faça upload do arquivo CSV com os dados da Lotofácil
    
    **Requisitos:**
    - Formato: CSV com separador `;`
    - Colunas: Concurso, Data Sorteio, Bola1...Bola15
    - Encoding: UTF-8
    
    Exemplo:
    ```
    Concurso;Data Sorteio;Bola1;...;Bola15
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
            content = uploaded_file.getvalue().decode('utf-8')
            df = pd.read_csv(io.StringIO(content), sep=';')
            
            colunas_necessarias = ['Concurso', 'Data Sorteio']
            colunas_validas = all(col in df.columns for col in colunas_necessarias)
            
            if colunas_validas:
                os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
                with open(CSV_PATH, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                st.success("✅ Arquivo carregado com sucesso!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Arquivo inválido. Verifique as colunas necessárias.")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

# -------------------------------------------------------------
# Execução principal
# -------------------------------------------------------------
if __name__ == "__main__":
    exibir_jogo()

import streamlit as st
import pandas as pd
import os
import io
from collections import Counter
from datetime import datetime
import numpy as np
import random

# PARA STREAMLIT CLOUD - caminho relativo
CSV_PATH = 'dados/lotofacil.csv'

def criar_arquivo_teste():
    """Cria um arquivo de dados de exemplo para teste"""
    try:
        os.makedirs('dados', exist_ok=True)
        
        # Criar dados de exemplo CORRETOS
        np.random.seed(42)
        num_concursos = 100
        
        # Criar lista de concursos
        concursos = []
        
        for i in range(1, num_concursos + 1):
            # Gerar 15 números únicos entre 1 e 25
            numeros = np.random.choice(range(1, 26), 15, replace=False)
            numeros.sort()
            
            concurso = {
                'Concurso': i,
                'Data Sorteio': (datetime.now() - pd.Timedelta(days=num_concursos - i)).strftime('%d/%m/%Y')
            }
            
            # Adicionar cada número em sua coluna
            for j, num in enumerate(numeros, 1):
                concurso[f'Bola{j}'] = num
                
            concursos.append(concurso)
        
        # Criar DataFrame
        df = pd.DataFrame(concursos)
        
        # Salvar arquivo
        df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
        
        st.success(f"✅ Arquivo de teste criado com {num_concursos} concursos!")
        st.dataframe(df.head(3))
        return True
        
    except Exception as e:
        st.error(f"Erro ao criar arquivo de teste: {e}")
        return False

def verificar_estrutura():
    """Verifica e cria a estrutura de pastas necessária"""
    if not os.path.exists('dados'):
        os.makedirs('dados', exist_ok=True)

def intercalar_melhores_piores(melhores_sorted, piores_sorted):
    """Intercala elementos: melhor, pior, melhor, pior... e depois os restantes"""
    resultado = []
    max_len = max(len(melhores_sorted), len(piores_sorted))
    for i in range(max_len):
        if i < len(melhores_sorted):
            resultado.append(melhores_sorted[i])
        if i < len(piores_sorted):
            resultado.append(piores_sorted[i])
    return resultado

def exibir_jogo():
    verificar_estrutura()
    st.header("📊 Análise de Jogos - Lotofácil")
    
    # Se arquivo não existe, mostrar opções
    if not os.path.exists(CSV_PATH):
        st.warning("📁 Arquivo de dados não encontrado")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Criar Dados de Teste", type="primary", use_container_width=True):
                if criar_arquivo_teste():
                    st.rerun()
        
        with col2:
            if st.button("📤 Fazer Upload", use_container_width=True):
                pass  # Vai mostrar o upload abaixo
        
        st.markdown("---")
        exibir_secao_upload()
        return
    
    # Se arquivo existe, carregar e mostrar análise
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        
        # DEBUG: Verificar os dados
        with st.expander("🔍 DEBUG - Informações do DataFrame"):
            st.write(f"• Shape: {df.shape}")
            st.write(f"• Colunas: {list(df.columns)}")
            st.write(f"• Primeiras linhas:")
            st.dataframe(df.head(3))
            
            # Verificar se as colunas de bola existem
            colunas_bola = [f'Bola{i}' for i in range(1, 16)]
            colunas_existentes = [col for col in colunas_bola if col in df.columns]
            st.write(f"• Colunas Bola encontradas: {colunas_existentes}")
        
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
        
        # Coletar todos os números de todas as bolas
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in df.columns:
                # Converter para numérico e remover NaN
                numeros_coluna = pd.to_numeric(df[coluna], errors='coerce').dropna().astype(int).tolist()
                todos_numeros.extend(numeros_coluna)
        
        # DEBUG: Verificar números coletados
        with st.expander("🔍 DEBUG - Números Coletados"):
            st.write(f"Total de números coletados: {len(todos_numeros)}")
            st.write(f"Números únicos: {len(set(todos_numeros))}")
            st.write(f"Range dos números: {min(todos_numeros) if todos_numeros else 'N/A'} - {max(todos_numeros) if todos_numeros else 'N/A'}")
        
        if todos_numeros:
            frequencia = Counter(todos_numeros)
            total_sorteios = len(todos_numeros)
            
            # Calcular percentuais (para exibição)
            frequencia_com_percentual = {}
            for num in range(1, 26):
                freq = frequencia.get(num, 0)
                percentual = (freq / total_sorteios) * 100 if total_sorteios > 0 else 0
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
                        if num <= 25:
                            dados = frequencia_com_percentual[num]
                            # Cor baseada na frequência (opcional)
                            cor_borda = "#1E88E5"  # Azul padrão
                            if dados['frequencia'] > frequencia.most_common(1)[0][1] * 0.8:
                                cor_borda = "#FF6B6B"  # Vermelho para muito frequentes
                            elif dados['frequencia'] < frequencia.most_common()[-1][1] * 1.2:
                                cor_borda = "#4ECDC4"  # Verde para pouco frequentes
                            
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
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    color: #000000;
                                '>
                                    <div style='font-weight: bold; font-size: 1.1em; color: #000000;'>Nº {num}</div>
                                    <div style='font-size: 0.85em; margin-top: 5px; color: #000000;'>
                                        {dados['frequencia']} vezes<br>
                                        <strong style='color: #000000;'>{dados['percentual']:.1f}%</strong>
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
            
            # Estatísticas adicionais
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Estatísticas Gerais:**")
                st.write(f"• Total de sorteios analisados: {total_sorteios:,}")
                st.write(f"• Total de concursos: {len(df):,}")
                if frequencia.most_common(1):
                    num_mais_freq, freq_mais = frequencia.most_common(1)[0]
                    percent_mais = (freq_mais / total_sorteios) * 100
                    st.write(f"• Número mais frequente: **{num_mais_freq}** ({freq_mais} vezes - {percent_mais:.1f}%)")
                if frequencia.most_common():
                    num_menos_freq, freq_menos = frequencia.most_common()[-1]
                    percent_menos = (freq_menos / total_sorteios) * 100
                    st.write(f"• Número menos frequente: **{num_menos_freq}** ({freq_menos} vezes - {percent_menos:.1f}%)")
                
            with col2:
                st.write("**🎯 Ranking Top 5:**")
                for i, (num, freq) in enumerate(frequencia.most_common(5), 1):
                    percentual = (freq / total_sorteios) * 100
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "4️⃣" if i == 4 else "5️⃣"
                    st.write(f"{emoji} **Número {num}**: {freq} vezes ({percentual:.1f}%)")
        
        # Sugestão de jogos: usar 15 melhores e 10 piores como pools
        st.markdown("---")
        st.subheader("💡 Sugestões de Jogos (15 melhores → escolher 9 / 10 piores → escolher 6)")
        
        col_sug1, col_sug2 = st.columns([2, 1])
        
        with col_sug1:
            if st.button("🎯 Gerar 6 Sugestões (9 melhores + 6 piores)", type="primary", use_container_width=True):
                if not todos_numeros or len(todos_numeros) == 0:
                    st.error("❌ Não há dados suficientes para gerar sugestões")
                else:
                    # Montar pools garantido 1..25 considerado
                    # Ordena números de 1..25 por frequência descendente
                    sorted_by_freq_desc = sorted(range(1, 26), key=lambda n: frequencia.get(n, 0), reverse=True)
                    top15 = sorted_by_freq_desc[:15]
                    bottom10 = sorted_by_freq_desc[-10:]
                    
                    # Tentar gerar 6 combinações únicas (ou o máximo possível)
                    suggestions = []
                    unique_keys = set()
                    attempts = 0
                    max_attempts = 500
                    
                    while len(suggestions) < 6 and attempts < max_attempts:
                        attempts += 1
                        # escolher aleatoriamente 9 dos 15 melhores e 6 dos 10 piores
                        escolha_top = random.sample(top15, 9)
                        escolha_bottom = random.sample(bottom10, 6)
                        
                        jogo = sorted(escolha_top + escolha_bottom)
                        key = tuple(jogo)
                        if key not in unique_keys:
                            unique_keys.add(key)
                            # armazenar as partes para permitir intercalamento na exibição
                            suggestions.append({
                                'top': sorted(escolha_top),
                                'bottom': sorted(escolha_bottom),
                                'jogo_sorted': jogo
                            })
                    
                    if len(suggestions) == 0:
                        st.error("❌ Não foi possível gerar sugestões únicas com os dados atuais.")
                    else:
                        if len(suggestions) < 6:
                            st.warning(f"⚠️ Só foi possível gerar {len(suggestions)} combinações únicas após {attempts} tentativas.")
                        
                        st.success("🎉 Sugestões geradas:")
                        # Exibir cada sugestão intercalando melhores/piores
                        for i, s in enumerate(suggestions, start=1):
                            melhores_s = s['top']
                            piores_s = s['bottom']
                            intercalado = intercalar_melhores_piores(melhores_s, piores_s)
                            
                            st.markdown(f"##### 💡 Sugestão {i}")
                            numeros_formatados = " - ".join([f"**{num:02d}**" for num in intercalado])
                            st.markdown(
                                f"<div style='text-align: center; font-size: 1.15em; padding: 10px; background-color: #e8f5e8; border-radius: 10px; margin: 8px 0; color: #000000;'>{numeros_formatados}</div>",
                                unsafe_allow_html=True
                            )
                            
                            # Mostrar em formato de cartela responsiva (distribuir em 5 colunas)
                            cols_cartela = st.columns(5)
                            for idx_num, num in enumerate(intercalado):
                                with cols_cartela[idx_num % 5]:
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
        
        with col_sug2:
            if st.button("🔄 Gerar Aleatório", use_container_width=True):
                if todos_numeros:
                    # Gerar uma sugestão aleatória (15 números únicos entre 1-25)
                    sugestao_aleatoria = sorted(np.random.choice(range(1, 26), 15, replace=False))
                    st.info("🎲 **Sugestão aleatória:**")
                    st.markdown(f"<div style='text-align: center; font-size: 1.2em; padding: 10px; background-color: #e3f2fd; border-radius: 8px; color: #000000;'>{' - '.join(map(str, sugestao_aleatoria))}</div>", unsafe_allow_html=True)
        
        # Botão para recarregar arquivo
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

def exibir_secao_upload():
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

# Executar o aplicativo
if __name__ == "__main__":
    exibir_jogo()

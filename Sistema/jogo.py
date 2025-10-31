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

# ---------------------------- Funções auxiliares ----------------------------

def criar_arquivo_teste():
    """Cria um arquivo de dados de exemplo para teste com distribuições variadas"""
    try:
        os.makedirs('dados', exist_ok=True)
        
        np.random.seed(42)
        num_concursos = 300  # Garantir que temos pelo menos 150 concursos para análise
        
        distribuicoes = [
            (10, 5),
            (9, 6),
            (8, 7),
            (11, 4),
            (7, 8)
        ]
        
        pesos = [35, 30, 20, 10, 5]
        
        concursos = []
        for i in range(1, num_concursos + 1):
            dist_idx = np.random.choice(len(distribuicoes), p=np.array(pesos)/100)
            melhores_count, piores_count = distribuicoes[dist_idx]
            
            numeros_melhores = np.random.choice(range(1, 16), melhores_count, replace=False)
            numeros_piores = np.random.choice(range(16, 26), piores_count, replace=False)
            
            numeros = np.concatenate([numeros_melhores, numeros_piores])
            numeros.sort()
            
            concurso = {
                'Concurso': i,
                'Data Sorteio': (datetime.now() - pd.Timedelta(days=num_concursos - i)).strftime('%d/%m/%Y')
            }
            
            for j, num in enumerate(numeros, 1):
                concurso[f'Bola{j}'] = int(num)
            concursos.append(concurso)
        
        df = pd.DataFrame(concursos)
        df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
        
        st.success(f"✅ Arquivo de teste criado com {num_concursos} concursos!")
        return True
        
    except Exception as e:
        st.error(f"Erro ao criar arquivo de teste: {e}")
        return False

def verificar_estrutura():
    if not os.path.exists('dados'):
        os.makedirs('dados', exist_ok=True)

def intercalar_melhores_piores(melhores_sorted, piores_sorted):
    resultado = []
    max_len = max(len(melhores_sorted), len(piores_sorted))
    for i in range(max_len):
        if i < len(melhores_sorted):
            resultado.append(melhores_sorted[i])
        if i < len(piores_sorted):
            resultado.append(piores_sorted[i])
    return resultado

def analisar_distribuicao_grupos(df):
    todos_numeros = []
    for i in range(1, 16):
        coluna = f'Bola{i}'
        if coluna in df.columns:
            numeros_coluna = pd.to_numeric(df[coluna], errors='coerce').dropna().astype(int).tolist()
            todos_numeros.extend(numeros_coluna)
    frequencia = Counter(todos_numeros)
    
    numeros_ordenados = sorted(range(1, 26), key=lambda x: frequencia.get(x, 0), reverse=True)
    
    grupos_melhores = [
        numeros_ordenados[0:5],
        numeros_ordenados[5:10],
        numeros_ordenados[10:15]
    ]
    grupos_piores = [
        numeros_ordenados[15:20],
        numeros_ordenados[20:25]
    ]
    return grupos_melhores, grupos_piores, frequencia

def analisar_padrao_concursos(df, grupos_melhores, grupos_piores):
    padroes = []
    for idx, row in df.iterrows():
        numeros_concurso = []
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in row and pd.notna(row[coluna]):
                try:
                    numeros_concurso.append(int(row[coluna]))
                except (ValueError, TypeError):
                    continue
        if len(numeros_concurso) != 2000:
            continue
        
        contagem_grupos = {
            'melhores_g1': len(set(numeros_concurso) & set(grupos_melhores[0])),
            'melhores_g2': len(set(numeros_concurso) & set(grupos_melhores[1])),
            'melhores_g3': len(set(numeros_concurso) & set(grupos_melhores[2])),
            'piores_g1': len(set(numeros_concurso) & set(grupos_piores[0])),
            'piores_g2': len(set(numeros_concurso) & set(grupos_piores[1]))
        }
        
        total_melhores = contagem_grupos['melhores_g1'] + contagem_grupos['melhores_g2'] + contagem_grupos['melhores_g3']
        total_piores = contagem_grupos['piores_g1'] + contagem_grupos['piores_g2']
        
        padroes.append({
            'concurso': row['Concurso'],
            'melhores_g1': contagem_grupos['melhores_g1'],
            'melhores_g2': contagem_grupos['melhores_g2'],
            'melhores_g3': contagem_grupos['melhores_g3'],
            'piores_g1': contagem_grupos['piores_g1'],
            'piores_g2': contagem_grupos['piores_g2'],
            'total_melhores': total_melhores,
            'total_piores': total_piores,
            'distribuicao': f"{total_melhores}m x {total_piores}p"
        })
    return padroes

def calcular_media_ultimos(padroes_recentes, n=150):
    """Calcula médias dos últimos N concursos"""
    if len(padroes_recentes) < n:
        concursos_analisados = padroes_recentes
    else:
        concursos_analisados = padroes_recentes[:n]
    
    # Calcular médias reais dos últimos concursos
    media_melhores_g1 = np.mean([p['melhores_g1'] for p in concursos_analisados])
    media_melhores_g2 = np.mean([p['melhores_g2'] for p in concursos_analisados])
    media_melhores_g3 = np.mean([p['melhores_g3'] for p in concursos_analisados])
    media_piores_g1 = np.mean([p['piores_g1'] for p in concursos_analisados])
    media_piores_g2 = np.mean([p['piores_g2'] for p in concursos_analisados])
    
    return {
        'media_melhores_g1': media_melhores_g1,
        'media_melhores_g2': media_melhores_g2,
        'media_melhores_g3': media_melhores_g3,
        'media_piores_g1': media_piores_g1,
        'media_piores_g2': media_piores_g2,
        'concursos_analisados': len(concursos_analisados)
    }

def exibir_estatisticas_concursos(padroes_recentes, n_analise):
    """Exibe estatísticas dos últimos N concursos de forma otimizada"""
    
    # Determinar quantos concursos analisar
    n = min(n_analise, len(padroes_recentes))
    padroes_analise = padroes_recentes[:n]
    
    # Calcular estatísticas
    dist_melhores_piores = Counter([p['distribuicao'] for p in padroes_analise])
    analise = calcular_media_ultimos(padroes_recentes, n=n)
    
    # Exibir informações
    if n < n_analise:
        st.warning(f"⚠️ Apenas {n} concursos disponíveis (ideal: {n_analise} para análise completa)")
        st.write(f"**📈 Estatísticas dos {n} Concursos Disponíveis:**")
    else:
        st.write(f"**📈 Estatísticas dos Últimos {n} Concursos:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Total de concursos analisados: {n}**")
        
        st.write("**Distribuições mais comuns:**")
        for dist, count in dist_melhores_piores.most_common(5):
            st.write(f"• {dist}: {count} vezes")
    
    with col2:
        st.write("**Médias por grupo:**")
        st.write(f"• Melhores G1: {analise['media_melhores_g1']:.2f}")
        st.write(f"• Melhores G2: {analise['media_melhores_g2']:.2f}")
        st.write(f"• Melhores G3: {analise['media_melhores_g3']:.2f}")
        st.write(f"• Piores G1: {analise['media_piores_g1']:.2f}")
        st.write(f"• Piores G2: {analise['media_piores_g2']:.2f}")

# ---------------------------- Função principal corrigida ----------------------------

def gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes):
    sugestoes = []
    
    # Analisar os últimos 150 concursos
    ultimos_150 = padroes_recentes[:150] if len(padroes_recentes) >= 150 else padroes_recentes

    # Contar distribuições nos últimos 150 concursos
    dist_counter_150 = Counter([p['distribuicao'] for p in ultimos_150])
    distribuicoes_mais_comuns_150 = dist_counter_150.most_common(5)
    total_ocorrencias_150 = sum(dist_counter_150.values())

    st.write("📈 **Estatísticas dos Últimos 150 Concursos:**")
    for i, (dist, count) in enumerate(distribuicoes_mais_comuns_150, 1):
        st.write(f"{i} - {dist}: {count} vezes")
    st.write(f"**Total:** {total_ocorrencias_150} vezes")
    st.write("---")

    # Verificar se temos pelo menos 3 distribuições
    if len(distribuicoes_mais_comuns_150) < 3:
        st.error(f"❌ Apenas {len(distribuicoes_mais_comuns_150)} distribuições distintas encontradas.")
        return []

    # Pegar as 3 distribuições mais comuns
    top3_distribuicoes = [dist for dist, _ in distribuicoes_mais_comuns_150[:3]]

    # Gerar 2 jogos para cada uma das 3 distribuições mais comuns
    for dist_idx, distribuicao in enumerate(top3_distribuicoes):
        st.write(f"🎯 **Gerando 2 jogos para: {distribuicao}** ({dist_idx + 1}ª distribuição mais comum)")
        
        jogos_gerados = 0
        tentativas = 0
        max_tentativas = 2000

        while jogos_gerados < 2 and tentativas < max_tentativas:
            tentativas += 1

            # Extrair m_count e p_count da distribuição
            try:
                partes = distribuicao.replace('m', '').replace('p', '').split(' x ')
                m_count = int(partes[0])
                p_count = int(partes[1])
            except Exception:
                m_count, p_count = 10, 5

            # Distribuição mais inteligente entre grupos
            if m_count == 10 and p_count == 5:
                targets = (4, 3, 3, 3, 2)  # G1, G2, G3, P1, P2
            elif m_count == 9 and p_count == 6:
                targets = (3, 3, 3, 3, 3)  # G1, G2, G3, P1, P2
            elif m_count == 8 and p_count == 7:
                targets = (3, 3, 2, 4, 3)  # G1, G2, G3, P1, P2
            elif m_count == 11 and p_count == 4:
                targets = (4, 4, 3, 2, 2)  # G1, G2, G3, P1, P2
            else:
                # Distribuição genérica
                targets = (
                    max(1, min(5, (m_count + 1) // 3)),
                    max(1, min(5, m_count // 3)),
                    max(1, min(5, m_count - ((m_count + 1) // 3) - (m_count // 3))),
                    max(1, min(5, (p_count + 1) // 2)),
                    max(1, min(5, p_count - ((p_count + 1) // 2)))
                )

            target_melhores_g1, target_melhores_g2, target_melhores_g3, target_piores_g1, target_piores_g2 = targets

            try:
                selecao_melhores_g1 = random.sample(grupos_melhores[0], target_melhores_g1)
                selecao_melhores_g2 = random.sample(grupos_melhores[1], target_melhores_g2)
                selecao_melhores_g3 = random.sample(grupos_melhores[2], target_melhores_g3)
                selecao_piores_g1 = random.sample(grupos_piores[0], target_piores_g1)
                selecao_piores_g2 = random.sample(grupos_piores[1], target_piores_g2)
            except ValueError:
                continue

            jogo = selecao_melhores_g1 + selecao_melhores_g2 + selecao_melhores_g3 + selecao_piores_g1 + selecao_piores_g2

            if len(jogo) == 15 and len(set(jogo)) == 15:
                jogo_ordenado = sorted(jogo)
                chave = tuple(jogo_ordenado)

                # Verificar se já não geramos esta combinação
                if all(s['chave'] != chave for s in sugestoes):
                    sugestoes.append({
                        'chave': chave,
                        'jogo': jogo_ordenado,
                        'distribuicao_origem': distribuicao,
                        'posicao_distribuicao': dist_idx + 1,
                        'melhores_g1': selecao_melhores_g1,
                        'melhores_g2': selecao_melhores_g2,
                        'melhores_g3': selecao_melhores_g3,
                        'piores_g1': selecao_piores_g1,
                        'piores_g2': selecao_piores_g2
                    })
                    jogos_gerados += 1

        st.write(f"✅ **{jogos_gerados} jogos gerados para {distribuicao}**")

    st.write("---")
    st.write("🎉 **Resumo Final das Sugestões:**")
    for i, s in enumerate(sugestoes, 1):
        total_m = len(s['melhores_g1']) + len(s['melhores_g2']) + len(s['melhores_g3'])
        total_p = len(s['piores_g1']) + len(s['piores_g2'])
        st.write(f"{i}️⃣ {s['distribuicao_origem']} (posição {s['posicao_distribuicao']}ª distribuição) - Real: {total_m}M + {total_p}P")

    return sugestoes

def exibir_jogo():
    verificar_estrutura()
    st.header("📊 Análise de Jogos - Lotofácil")
    
    # Se arquivo não existe, mostrar opções
    if not os.path.exists(CSV_PATH):
        st.warning("📁 Arquivo de dados não encontrado")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Criar Dados de Teste", type="primary", key='criar_teste'):
                if criar_arquivo_teste():
                    st.rerun()
        
        with col2:
            if st.button("📤 Fazer Upload", key='fazer_upload'):
                pass
        
        st.markdown("---")
        exibir_secao_upload()
        return
    
    # Se arquivo existe, carregar e mostrar análise
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        
        # Ordenar por concurso (mais recentes primeiro)
        df = df.sort_values('Concurso', ascending=False).reset_index(drop=True)
        
        # Informações básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Total de Concursos", len(df))
        with col2:
            st.metric("🎯 Primeiro Concurso", df['Concurso'].min())
        with col3:
            st.metric("🔥 Último Concurso", df['Concurso'].max())
        
        st.markdown("---")
        
        # ANÁLISE AVANÇADA POR GRUPOS
        st.subheader("🎯 Análise Avançada por Grupos de 5")
        
        # Calcular grupos
        grupos_melhores, grupos_piores, frequencia = analisar_distribuicao_grupos(df)
        
        # Exibir grupos
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Grupos de Melhores Números:**")
            for i, grupo in enumerate(grupos_melhores, 1):
                numeros_com_freq = [f"{num} ({frequencia[num]}x)" for num in grupo]
                st.write(f"**Grupo {i}:** {', '.join(numeros_com_freq)}")
        
        with col2:
            st.write("**📉 Grupos de Piores Números:**")
            for i, grupo in enumerate(grupos_piores, 1):
                numeros_com_freq = [f"{num} ({frequencia[num]}x)" for num in grupo]
                st.write(f"**Grupo {i+3}:** {', '.join(numeros_com_freq)}")
        
        # Analisar padrões recentes
        padroes_recentes = analisar_padrao_concursos(df, grupos_melhores, grupos_piores)
        
        # Mostrar análise dos últimos concursos
        st.markdown("---")
        st.subheader("📊 Análise dos Últimos Concursos")
        
        if padroes_recentes:
            # Criar DataFrame para exibição (apenas primeiros 30 padrões para visualização)
            df_padroes = pd.DataFrame(padroes_recentes[:150])
            
            # Exibir tabela
            st.dataframe(
                df_padroes[['concurso', 'melhores_g1', 'melhores_g2', 'melhores_g3', 
                           'piores_g1', 'piores_g2', 'distribuicao']].rename(
                    columns={
                        'concurso': 'Concurso',
                        'melhores_g1': 'M-G1',
                        'melhores_g2': 'M-G2', 
                        'melhores_g3': 'M-G3',
                        'piores_g1': 'P-G1',
                        'piores_g2': 'P-G2',
                        'distribuicao': 'Distribuição'
                    }
                ),
                width='stretch',
                height=400
            )
            
            # ESTATÍSTICAS DOS ÚLTIMOS CONCURSOS (CÓDIGO OTIMIZADO)
            exibir_estatisticas_concursos(padroes_recentes, 150)

        # SUGESTÕES INTELIGENTES
        st.markdown("---")
        st.subheader("💡 Sugestões Inteligentes Baseadas nas 3 Distribuições Mais Comuns")

        if st.button("🎯 Gerar 6 Sugestões (2 para cada das 3 distribuições mais comuns)", type="primary", key='gerar_sugestoes'):
            if not padroes_recentes:
                st.error("❌ Não há dados suficientes para análise")
            else:
                sugestoes = gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes)
                
                if sugestoes:
                    st.success(f"🎉 {len(sugestoes)} sugestões geradas com base nas 3 distribuições mais comuns dos últimos 150 concursos!")
                    
                    for i, sugestao in enumerate(sugestoes, 1):
                        st.markdown(f"##### 💡 Sugestão {i} - {sugestao['distribuicao_origem']} ({sugestao['posicao_distribuicao']}ª distribuição mais comum)")
                        
                        # Mostrar distribuição por grupos
                        cols_dist = st.columns(5)
                        grupos_info = [
                            (f"🏆 G1", sugestao['melhores_g1']),
                            (f"🥈 G2", sugestao['melhores_g2']),
                            (f"🥉 G3", sugestao['melhores_g3']),
                            (f"📉 G4", sugestao['piores_g1']),
                            (f"📊 G5", sugestao['piores_g2'])
                        ]
                        
                        for col_idx, (nome, numeros) in enumerate(grupos_info):
                            with cols_dist[col_idx]:
                                st.markdown(f"**{nome}**")
                                st.write(", ".join(map(str, sorted(numeros))))
                        
                        # Mostrar resumo
                        total_m = len(sugestao['melhores_g1']) + len(sugestao['melhores_g2']) + len(sugestao['melhores_g3'])
                        total_p = len(sugestao['piores_g1']) + len(sugestao['piores_g2'])
                        st.write(f"**📊 Distribuição Real: {total_m}M + {total_p}P**")
                        
                        # Calcular jogo intercalado
                        melhores_todos = sugestao['melhores_g1'] + sugestao['melhores_g2'] + sugestao['melhores_g3']
                        piores_todos = sugestao['piores_g1'] + sugestao['piores_g2']
                        jogo_intercalado = intercalar_melhores_piores(sorted(melhores_todos), sorted(piores_todos))
                        
                        st.markdown("**🎲 Jogo Intercalado:**")
                        numeros_formatados = " - ".join([f"**{num:02d}**" for num in jogo_intercalado])
                        st.markdown(
                            f"<div style='text-align: center; font-size: 1.1em; padding: 10px; background-color: #e8f5e8; border-radius: 10px; margin: 8px 0; color: #000000;'>{numeros_formatados}</div>",
                            unsafe_allow_html=True
                        )
                        
                        # Cartela visual
                        cols_cartela = st.columns(5)
                        for idx_num, num in enumerate(jogo_intercalado):
                            with cols_cartela[idx_num % 5]:
                                if num in grupos_melhores[0]:
                                    cor = "#FF6B6B"
                                elif num in grupos_melhores[1]:
                                    cor = "#4ECDC4"
                                elif num in grupos_melhores[2]:
                                    cor = "#45B7D1"
                                elif num in grupos_piores[0]:
                                    cor = "#F9A826"
                                else:
                                    cor = "#9966CC"
                                
                                st.markdown(
                                    f"""
                                    <div style='text-align: center; padding: 12px; border: 3px solid {cor}; border-radius: 10px; margin: 3px; background: white; font-size: 1.1em; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #000000;'>{num}</div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        
                        st.markdown("---")
                else:
                    st.error("❌ Não foi possível gerar sugestões com os padrões atuais")
        
        # Botão para recarregar arquivo
        st.markdown("---")
        col_rec1, col_rec2, col_rec3 = st.columns([1, 1, 1])
        
        with col_rec2:
            if st.button("🔄 Carregar Novo Arquivo CSV", key='recarregar_csv'):
                if os.path.exists(CSV_PATH):
                    os.remove(CSV_PATH)
                st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def exibir_secao_upload():
    st.info("""
    ### 📋 Para começar, faça upload do arquivo CSV com os dados da Lotofácil
    
    **Requisitos do arquivo:**
    - Formato: CSV com separador ponto e vírgula (;)
    - Colunas: Concurso, Data Sorteio, Bola1, Bola2, ..., Bola15
    - Encoding: UTF-8 (recomendado)
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

# Executar o aplicativo
if __name__ == "__main__":
    exibir_jogo()
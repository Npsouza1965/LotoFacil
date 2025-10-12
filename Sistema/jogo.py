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

def analisar_distribuicao_grupos(df):
    """Analisa a distribuição dos números nos grupos de 5"""
    # Calcular frequência de todos os números
    todos_numeros = []
    for i in range(1, 16):
        coluna = f'Bola{i}'
        if coluna in df.columns:
            numeros_coluna = pd.to_numeric(df[coluna], errors='coerce').dropna().astype(int).tolist()
            todos_numeros.extend(numeros_coluna)
    
    frequencia = Counter(todos_numeros)
    
    # Ordenar números por frequência (melhores = mais frequentes)
    numeros_ordenados = sorted(range(1, 26), key=lambda x: frequencia.get(x, 0), reverse=True)
    
    # Dividir em grupos de 5
    grupos_melhores = [
        numeros_ordenados[0:5],   # Grupo 1 - Top 5 melhores
        numeros_ordenados[5:10],  # Grupo 2 - Próximos 5 melhores  
        numeros_ordenados[10:15]  # Grupo 3 - Últimos 5 melhores
    ]
    
    grupos_piores = [
        numeros_ordenados[15:20], # Grupo 4 - Primeiros 5 piores
        numeros_ordenados[20:25]  # Grupo 5 - Últimos 5 piores
    ]
    
    return grupos_melhores, grupos_piores, frequencia

def analisar_padrao_concursos(df, grupos_melhores, grupos_piores):
    """Analisa o padrão de distribuição nos últimos concursos"""
    padroes = []
    
    # CORREÇÃO: Usar iterrows() normalmente e depois reverter a ordem se necessário
    # Mas como o DataFrame já está ordenado por concurso decrescente, vamos percorrer normalmente
    for idx, row in df.iterrows():
        # Coletar números do concurso
        numeros_concurso = []
        for i in range(1, 16):
            coluna = f'Bola{i}'
            if coluna in row and pd.notna(row[coluna]):
                try:
                    numeros_concurso.append(int(row[coluna]))
                except (ValueError, TypeError):
                    continue
        
        # Verificar se temos 15 números válidos
        if len(numeros_concurso) != 15:
            continue
        
        # Contar quantos números de cada grupo apareceram
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

def calcular_media_ultimos_30(padroes_recentes):
    """Calcula médias reais dos últimos 30 concursos"""
    if len(padroes_recentes) < 30:
        st.warning(f"⚠️ Apenas {len(padroes_recentes)} concursos disponíveis (ideal: 30)")
        concursos_analisados = padroes_recentes
    else:
        concursos_analisados = padroes_recentes[:30]
    
    # Calcular médias reais dos últimos concursos
    media_melhores_g1 = np.mean([p['melhores_g1'] for p in concursos_analisados])
    media_melhores_g2 = np.mean([p['melhores_g2'] for p in concursos_analisados])
    media_melhores_g3 = np.mean([p['melhores_g3'] for p in concursos_analisados])
    media_piores_g1 = np.mean([p['piores_g1'] for p in concursos_analisados])
    media_piores_g2 = np.mean([p['piores_g2'] for p in concursos_analisados])
    
    # Calcular distribuição M x P dos últimos concursos
    dist_melhores_piores = Counter([p['distribuicao'] for p in concursos_analisados])
    distribuicao_mais_comum = dist_melhores_piores.most_common(1)[0][0] if dist_melhores_piores else "10m x 5p"
    
    # Extrair números da distribuição mais comum
    try:
        m_count = int(distribuicao_mais_comum.split('m')[0])
        p_count = int(distribuicao_mais_comum.split('x ')[1].split('p')[0])
    except:
        m_count = 10
        p_count = 5
    
    return {
        'media_melhores_g1': media_melhores_g1,
        'media_melhores_g2': media_melhores_g2,
        'media_melhores_g3': media_melhores_g3,
        'media_piores_g1': media_piores_g1,
        'media_piores_g2': media_piores_g2,
        'distribuicao_mais_comum': distribuicao_mais_comum,
        'target_melhores': m_count,
        'target_piores': p_count,
        'concursos_analisados': len(concursos_analisados)
    }

def gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes, num_sugestoes=6):
    """Gera sugestões baseadas na análise dos últimos 30 concursos - SEGUINDO O HISTÓRICO REAL"""
    sugestoes = []
    
    # Analisar os últimos 30 concursos
    analise_30 = calcular_media_ultimos_30(padroes_recentes)
    
    st.write(f"📊 **Análise dos Últimos {analise_30['concursos_analisados']} Concursos:**")
    st.write(f"• Distribuição mais comum: **{analise_30['distribuicao_mais_comum']}**")
    st.write(f"• Médias reais por grupo:")
    st.write(f"  - Melhores G1: {analise_30['media_melhores_g1']:.2f}")
    st.write(f"  - Melhores G2: {analise_30['media_melhores_g2']:.2f}")
    st.write(f"  - Melhores G3: {analise_30['media_melhores_g3']:.2f}")
    st.write(f"  - Piores G1: {analise_30['media_piores_g1']:.2f}")
    st.write(f"  - Piores G2: {analise_30['media_piores_g2']:.2f}")
    
    # Usar a distribuição mais comum dos últimos concursos
    target_melhores = analise_30['target_melhores']
    target_piores = analise_30['target_piores']
    
    st.write(f"🎯 **Distribuição Baseada no Histórico:** {target_melhores}M x {target_piores}P")
    
    # Distribuir os melhores entre os grupos baseado nas médias reais
    total_melhores_float = (analise_30['media_melhores_g1'] + 
                           analise_30['media_melhores_g2'] + 
                           analise_30['media_melhores_g3'])
    
    # Calcular proporções baseadas nas médias reais
    prop_g1 = analise_30['media_melhores_g1'] / total_melhores_float if total_melhores_float > 0 else 0.33
    prop_g2 = analise_30['media_melhores_g2'] / total_melhores_float if total_melhores_float > 0 else 0.33
    prop_g3 = analise_30['media_melhores_g3'] / total_melhores_float if total_melhores_float > 0 else 0.34
    
    # Distribuir os piores entre os grupos baseado nas médias reais
    total_piores_float = analise_30['media_piores_g1'] + analise_30['media_piores_g2']
    prop_p1 = analise_30['media_piores_g1'] / total_piores_float if total_piores_float > 0 else 0.5
    prop_p2 = analise_30['media_piores_g2'] / total_piores_float if total_piores_float > 0 else 0.5
    
    # Calcular targets por grupo (arredondando para manter proporções)
    target_melhores_g1 = max(1, min(5, round(prop_g1 * target_melhores)))
    target_melhores_g2 = max(1, min(5, round(prop_g2 * target_melhores)))
    target_melhores_g3 = max(1, min(5, target_melhores - target_melhores_g1 - target_melhores_g2))
    
    target_piores_g1 = max(1, min(5, round(prop_p1 * target_piores)))
    target_piores_g2 = max(1, min(5, target_piores - target_piores_g1))
    
    # Ajuste final para garantir que totalize 15
    total_atual = (target_melhores_g1 + target_melhores_g2 + target_melhores_g3 + 
                  target_piores_g1 + target_piores_g2)
    
    if total_atual != 15:
        diferenca = 15 - total_atual
        # Ajustar nos grupos com mais flexibilidade
        if diferenca > 0:
            # Adicionar aos grupos que podem receber mais
            if target_melhores_g1 < 5:
                target_melhores_g1 += diferenca
            elif target_melhores_g2 < 5:
                target_melhores_g2 += diferenca
            elif target_melhores_g3 < 5:
                target_melhores_g3 += diferenca
        else:
            # Remover dos grupos que podem ceder
            if target_melhores_g3 > 1:
                target_melhores_g3 += diferenca  # diferenca é negativo
            elif target_melhores_g2 > 1:
                target_melhores_g2 += diferenca
            elif target_melhores_g1 > 1:
                target_melhores_g1 += diferenca
    
    st.write(f"📋 **Distribuição Final por Grupos:**")
    st.write(f"• Melhores G1: {target_melhores_g1} números")
    st.write(f"• Melhores G2: {target_melhores_g2} números")
    st.write(f"• Melhores G3: {target_melhores_g3} números")
    st.write(f"• Piores G1: {target_piores_g1} números")
    st.write(f"• Piores G2: {target_piores_g2} números")
    st.write(f"• **Total: {target_melhores}M + {target_piores}P = 15 números**")
    
    # Gerar sugestões
    tentativas = 0
    max_tentativas = 1000
    
    while len(sugestoes) < num_sugestoes and tentativas < max_tentativas:
        tentativas += 1
        
        try:
            # Selecionar números de cada grupo conforme as metas baseadas no histórico
            selecao_melhores_g1 = random.sample(grupos_melhores[0], target_melhores_g1)
            selecao_melhores_g2 = random.sample(grupos_melhores[1], target_melhores_g2)
            selecao_melhores_g3 = random.sample(grupos_melhores[2], target_melhores_g3)
            selecao_piores_g1 = random.sample(grupos_piores[0], target_piores_g1)
            selecao_piores_g2 = random.sample(grupos_piores[1], target_piores_g2)
            
            # Combinar todas as seleções
            jogo = selecao_melhores_g1 + selecao_melhores_g2 + selecao_melhores_g3 + selecao_piores_g1 + selecao_piores_g2
            
            # Verificar se temos exatamente 15 números únicos
            if len(jogo) == 15 and len(set(jogo)) == 15:
                jogo_ordenado = sorted(jogo)
                chave = tuple(jogo_ordenado)
                
                # Verificar se já não geramos esta combinação
                if not any(s['chave'] == chave for s in sugestoes):
                    sugestoes.append({
                        'chave': chave,
                        'jogo': jogo_ordenado,
                        'melhores_g1': selecao_melhores_g1,
                        'melhores_g2': selecao_melhores_g2,
                        'melhores_g3': selecao_melhores_g3,
                        'piores_g1': selecao_piores_g1,
                        'piores_g2': selecao_piores_g2,
                        'total_melhores': target_melhores,
                        'total_piores': target_piores
                    })
        
        except ValueError:
            # Pode acontecer se tentarmos sample mais números do que existem no grupo
            continue
    
    return sugestoes

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
            # Criar DataFrame para exibição
            df_padroes = pd.DataFrame(padroes_recentes[:30])  # Últimos 30
            
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
                use_container_width=True,
                height=400
            )
            
            # Estatísticas dos últimos 30
            if len(padroes_recentes) >= 30:
                analise_30 = calcular_media_ultimos_30(padroes_recentes)
                
                st.write("**📈 Estatísticas dos Últimos 30 Concursos:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    dist_melhores_piores = Counter([p['distribuicao'] for p in padroes_recentes[:30]])
                    st.write("**Distribuições mais comuns:**")
                    for dist, count in dist_melhores_piores.most_common(5):
                        st.write(f"• {dist}: {count} vezes")
                
                with col2:
                    st.write("**Médias por grupo:**")
                    st.write(f"• Melhores G1: {analise_30['media_melhores_g1']:.2f}")
                    st.write(f"• Melhores G2: {analise_30['media_melhores_g2']:.2f}")
                    st.write(f"• Melhores G3: {analise_30['media_melhores_g3']:.2f}")
                    st.write(f"• Piores G1: {analise_30['media_piores_g1']:.2f}")
                    st.write(f"• Piores G2: {analise_30['media_piores_g2']:.2f}")
        
        # SUGESTÕES INTELIGENTES
        st.markdown("---")
        st.subheader("💡 Sugestões Inteligentes Baseadas nos Últimos 30 Concursos")
        
        if st.button("🎯 Gerar Sugestões com Análise de 30 Concursos", type="primary", use_container_width=True):
            if not padroes_recentes:
                st.error("❌ Não há dados suficientes para análise")
            else:
                sugestoes = gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes)
                
                if sugestoes:
                    st.success(f"🎉 {len(sugestoes)} sugestões geradas com base nos últimos 30 concursos!")
                    
                    for i, sugestao in enumerate(sugestoes, 1):
                        st.markdown(f"##### 💡 Sugestão {i} ({sugestao['total_melhores']}M + {sugestao['total_piores']}P)")
                        
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
                        
                        # Mostrar jogo completo intercalado
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
                                # Definir cor baseada no grupo
                                if num in grupos_melhores[0]:
                                    cor = "#FF6B6B"  # Vermelho - Grupo 1 melhores
                                elif num in grupos_melhores[1]:
                                    cor = "#4ECDC4"  # Verde - Grupo 2 melhores
                                elif num in grupos_melhores[2]:
                                    cor = "#45B7D1"  # Azul - Grupo 3 melhores
                                elif num in grupos_piores[0]:
                                    cor = "#F9A826"  # Laranja - Grupo 4 piores
                                else:
                                    cor = "#9966CC"  # Roxo - Grupo 5 piores
                                
                                st.markdown(
                                    f"""
                                    <div style='
                                        text-align: center; 
                                        padding: 12px; 
                                        border: 3px solid {cor}; 
                                        border-radius: 10px; 
                                        margin: 3px; 
                                        background: white;
                                        font-size: 1.1em;
                                        font-weight: bold;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                        color: #000000;
                                    '>{num}</div>
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
            if st.button("🔄 Carregar Novo Arquivo CSV", use_container_width=True):
                if os.path.exists(CSV_PATH):
                    os.remove(CSV_PATH)
                st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
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
import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from collections import Counter
import numpy as np
import random

CSV_PATH = 'dados/lotofacil.csv'

# Configuração da página
st.set_page_config(
    page_title="Lotofácil Analyzer", 
    layout="wide",
    page_icon="🎯"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-msg {
        padding: 10px;
        background-color: #E8F5E8;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
    .numero-cartela {
        text-align: center; 
        padding: 12px; 
        border-radius: 10px; 
        margin: 3px; 
        background: white;
        font-size: 1.1em;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🎯 Lotofácil Analyzer</h1>', unsafe_allow_html=True)

# ========== FUNÇÕES DO SISTEMA ==========
def verificar_estrutura():
    """Verifica e cria a estrutura de pastas necessária"""
    if not os.path.exists('dados'):
        os.makedirs('dados', exist_ok=True)

def carregar_dados():
    """Carrega os dados do arquivo CSV"""
    try:
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def salvar_dados(df):
    """Salva os dados no arquivo CSV"""
    try:
        df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def criar_arquivo_base():
    """Cria um arquivo base vazio se não existir"""
    if not os.path.exists(CSV_PATH):
        colunas = ['Concurso', 'Data Sorteio'] + [f'Bola{i}' for i in range(1, 16)]
        df_base = pd.DataFrame(columns=colunas)
        salvar_dados(df_base)
        return True
    return False

def criar_arquivo_teste():
    """Cria um arquivo de dados de exemplo para teste"""
    try:
        os.makedirs('dados', exist_ok=True)
        
        # Criar dados de exemplo CORRETOS
        np.random.seed(42)
        num_concursos = 200  # Aumentado para ter pelo menos 150 concursos
        
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

def calcular_media_ultimos_150(padroes_recentes):
    """Calcula médias reais dos últimos 150 concursos"""
    if len(padroes_recentes) < 150:
        st.warning(f"⚠️ Apenas {len(padroes_recentes)} concursos disponíveis (ideal: 150)")
        concursos_analisados = padroes_recentes
    else:
        concursos_analisados = padroes_recentes[:150]
    
    # Calcular médias reais dos últimos concursos
    media_melhores_g1 = np.mean([p['melhores_g1'] for p in concursos_analisados])
    media_melhores_g2 = np.mean([p['melhores_g2'] for p in concursos_analisados])
    media_melhores_g3 = np.mean([p['melhores_g3'] for p in concursos_analisados])
    media_piores_g1 = np.mean([p['piores_g1'] for p in concursos_analisados])
    media_piores_g2 = np.mean([p['piores_g2'] for p in concursos_analisados])
    
    # Calcular distribuição M x P dos últimos concursos
    dist_melhores_piores = Counter([p['distribuicao'] for p in concursos_analisados])
    distribuicoes_mais_comuns = dist_melhores_piores.most_common(10)  # Mostrar mais distribuições
    
    # Calcular total para verificação
    total_concursos = sum(dist_melhores_piores.values())
    
    return {
        'media_melhores_g1': media_melhores_g1,
        'media_melhores_g2': media_melhores_g2,
        'media_melhores_g3': media_melhores_g3,
        'media_piores_g1': media_piores_g1,
        'media_piores_g2': media_piores_g2,
        'distribuicoes_mais_comuns': distribuicoes_mais_comuns,
        'total_concursos': total_concursos,
        'concursos_analisados': len(concursos_analisados)
    }

def calcular_distribuicao_por_grupo(distribuicao):
    """Calcula a distribuição por grupo baseada na distribuição M x P"""
    try:
        partes = distribuicao.replace('m', '').replace('p', '').split(' x ')
        m_count = int(partes[0])
        p_count = int(partes[1])
    except:
        m_count = 10
        p_count = 5
    
    # Distribuição inteligente baseada na experiência
    if m_count == 10 and p_count == 5:
        # 10M x 5P: Distribuição mais comum
        return (4, 3, 3, 3, 2)  # G1, G2, G3, P1, P2
    elif m_count == 9 and p_count == 6:
        # 9M x 6P: Distribuição equilibrada
        return (3, 3, 3, 3, 3)  # G1, G2, G3, P1, P2
    elif m_count == 8 and p_count == 7:
        # 8M x 7P: Mais números dos piores
        return (3, 3, 2, 4, 3)  # G1, G2, G3, P1, P2
    elif m_count == 11 and p_count == 4:
        # 11M x 4P: Mais números dos melhores
        return (4, 4, 3, 2, 2)  # G1, G2, G3, P1, P2
    elif m_count == 7 and p_count == 8:
        # 7M x 8P: Predominância dos piores
        return (3, 2, 2, 4, 4)  # G1, G2, G3, P1, P2
    else:
        # Distribuição genérica para outros casos
        return (
            max(1, min(5, (m_count + 1) // 3)),
            max(1, min(5, m_count // 3)),
            max(1, min(5, m_count - ((m_count + 1) // 3) - (m_count // 3))),
            max(1, min(5, (p_count + 1) // 2)),
            max(1, min(5, p_count - ((p_count + 1) // 2)))
        )

def gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes):
    """Gera 6 sugestões baseadas nas 3 distribuições mais comuns dos últimos 150 concursos"""
    sugestoes = []
    
    # Analisar os últimos 150 concursos
    analise_150 = calcular_media_ultimos_150(padroes_recentes)
    
    st.write(f"📊 **Análise dos Últimos {analise_150['concursos_analisados']} Concursos:**")
    
    # Mostrar distribuições mais comuns
    st.write("**🎯 Distribuições Mais Comuns:**")
    distribuicoes_mais_comuns = analise_150['distribuicoes_mais_comuns']
    
    for i, (distribuicao, count) in enumerate(distribuicoes_mais_comuns[:5], 1):  # Mostrar apenas top 5
        st.write(f"{i}º - {distribuicao}: {count} vezes")
    
    # Mostrar total para verificação
    total_exibido = sum(count for _, count in distribuicoes_mais_comuns[:5])
    outros = analise_150['total_concursos'] - total_exibido
    if outros > 0:
        st.write(f"• Outras distribuições: {outros} vezes")
    
    st.write(f"**📈 Médias por grupo (últimos 150):**")
    st.write(f"• Melhores G1: {analise_150['media_melhores_g1']:.2f}")
    st.write(f"• Melhores G2: {analise_150['media_melhores_g2']:.2f}")
    st.write(f"• Melhores G3: {analise_150['media_melhores_g3']:.2f}")
    st.write(f"• Piores G1: {analise_150['media_piores_g1']:.2f}")
    st.write(f"• Piores G2: {analise_150['media_piores_g2']:.2f}")
    
    # Verificar se temos pelo menos 3 distribuições
    if len(distribuicoes_mais_comuns) < 3:
        st.error(f"❌ Apenas {len(distribuicoes_mais_comuns)} distribuições distintas encontradas (necessário: 3)")
        return []
    
    # Gerar 2 jogos para cada uma das 3 distribuições mais comuns
    for dist_idx, (distribuicao, count) in enumerate(distribuicoes_mais_comuns[:3], 1):
        st.write(f"---")
        st.write(f"🎯 **Gerando 2 jogos para: {distribuicao}** ({dist_idx}ª distribuição mais comum - {count} vezes)")
        
        # Calcular distribuição por grupos
        target_melhores_g1, target_melhores_g2, target_melhores_g3, target_piores_g1, target_piores_g2 = calcular_distribuicao_por_grupo(distribuicao)
        
        # Extrair totais
        try:
            partes = distribuicao.replace('m', '').replace('p', '').split(' x ')
            total_melhores = int(partes[0])
            total_piores = int(partes[1])
        except:
            total_melhores = target_melhores_g1 + target_melhores_g2 + target_melhores_g3
            total_piores = target_piores_g1 + target_piores_g2
        
        st.write(f"📋 **Distribuição por grupos:**")
        st.write(f"• Melhores G1: {target_melhores_g1} números")
        st.write(f"• Melhores G2: {target_melhores_g2} números")
        st.write(f"• Melhores G3: {target_melhores_g3} números")
        st.write(f"• Piores G1: {target_piores_g1} números")
        st.write(f"• Piores G2: {target_piores_g2} números")
        st.write(f"• **Total: {total_melhores}M + {total_piores}P = 15 números**")
        
        # Validar se os grupos têm números suficientes
        for i, (grupo, qtd) in enumerate([
            (grupos_melhores[0], target_melhores_g1),
            (grupos_melhores[1], target_melhores_g2),
            (grupos_melhores[2], target_melhores_g3),
            (grupos_piores[0], target_piores_g1),
            (grupos_piores[1], target_piores_g2)
        ], 1):
            if len(grupo) < qtd:
                st.error(f"❌ Grupo {i} tem apenas {len(grupo)} números, mas precisa de {qtd}")
                return []
        
        # Gerar 2 jogos para esta distribuição
        jogos_gerados = 0
        tentativas = 0
        max_tentativas = 1000
        
        with st.spinner(f"Gerando 2 jogos para {distribuicao}..."):
            while jogos_gerados < 2 and tentativas < max_tentativas:
                tentativas += 1
                
                try:
                    # Selecionar números de cada grupo conforme as metas
                    selecao_melhores_g1 = random.sample(grupos_melhores[0], target_melhores_g1)
                    selecao_melhores_g2 = random.sample(grupos_melhores[1], target_melhores_g2)
                    selecao_melhores_g3 = random.sample(grupos_melhores[2], target_melhores_g3)
                    selecao_piores_g1 = random.sample(grupos_piores[0], target_piores_g1)
                    selecao_piores_g2 = random.sample(grupos_piores[1], target_piores_g2)
                    
                    # Combinar todas as seleções
                    jogo = (selecao_melhores_g1 + selecao_melhores_g2 + selecao_melhores_g3 + 
                            selecao_piores_g1 + selecao_piores_g2)
                    
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
                                'total_melhores': total_melhores,
                                'total_piores': total_piores,
                                'distribuicao_origem': distribuicao,
                                'posicao_distribuicao': dist_idx
                            })
                            jogos_gerados += 1
                
                except ValueError:
                    # Log silencioso para erros de sample
                    continue
            
            if jogos_gerados < 2:
                st.warning(f"⚠️ Apenas {jogos_gerados} jogo(s) gerado(s) para {distribuicao}")
    
    return sugestoes

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

# ========== FUNÇÕES PRINCIPAIS DE INTERFACE ==========
def exibir_jogo():
    """Função principal para análise de jogos - VERSÃO COMPLETA"""
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
            # Criar DataFrame para exibição (últimos 30 para visualização)
            df_padroes = pd.DataFrame(padroes_recentes[:30])
            
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
            
            # Estatísticas dos últimos 150
            if len(padroes_recentes) >= 150:
                analise_150 = calcular_media_ultimos_150(padroes_recentes)
                
                st.write("**📈 Estatísticas dos Últimos 150 Concursos:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Total de concursos analisados: {analise_150['total_concursos']}**")
                    
                    st.write("**Distribuições mais comuns:**")
                    for dist, count in analise_150['distribuicoes_mais_comuns'][:5]:  # Mostrar apenas top 5
                        st.write(f"• {dist}: {count} vezes")
                    
                    # Mostrar outras distribuições se houver
                    outros = analise_150['total_concursos'] - sum(count for _, count in analise_150['distribuicoes_mais_comuns'][:5])
                    if outros > 0:
                        st.write(f"• **Outras distribuições: {outros} vezes**")
                
                with col2:
                    st.write("**Médias por grupo:**")
                    st.write(f"• Melhores G1: {analise_150['media_melhores_g1']:.2f}")
                    st.write(f"• Melhores G2: {analise_150['media_melhores_g2']:.2f}")
                    st.write(f"• Melhores G3: {analise_150['media_melhores_g3']:.2f}")
                    st.write(f"• Piores G1: {analise_150['media_piores_g1']:.2f}")
                    st.write(f"• Piores G2: {analise_150['media_piores_g2']:.2f}")
            else:
                st.warning(f"⚠️ Apenas {len(padroes_recentes)} concursos disponíveis (ideal: 150 para análise completa)")
        
        # SUGESTÕES INTELIGENTES
        st.markdown("---")
        st.subheader("💡 Sugestões Inteligentes Baseadas nas 3 Distribuições Mais Comuns dos Últimos 150 Concursos")
        
        if st.button("🎯 Gerar 6 Sugestões (2 para cada das 3 distribuições mais comuns)", type="primary", use_container_width=True):
            if not padroes_recentes:
                st.error("❌ Não há dados suficientes para análise")
            else:
                sugestoes = gerar_sugestoes_inteligentes(grupos_melhores, grupos_piores, padroes_recentes)
                
                if sugestoes:
                    st.success(f"🎉 {len(sugestoes)} sugestões geradas com base nas 3 distribuições mais comuns dos últimos 150 concursos!")
                    
                    # Resumo das sugestões geradas
                    st.write("---")
                    st.write("**📋 Resumo das Sugestões Geradas:**")
                    for i, s in enumerate(sugestoes, 1):
                        st.write(f"{i}️⃣ {s['distribuicao_origem']} (posição {s['posicao_distribuicao']}ª distribuição) - Real: {s['total_melhores']}M + {s['total_piores']}P")
                    
                    st.write("---")
                    
                    # Exibir cada sugestão em detalhes
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
                                    <div class='numero-cartela' style='border: 3px solid {cor};'>{num}</div>
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

def tela_atualizacao_dados():
    """Tela para atualizar dados manualmente"""
    st.header("🔄 Atualização de Dados da Lotofácil")
    
    verificar_estrutura()
    criar_arquivo_base()
    
    df = carregar_dados()
    
    # Informações atuais
    col1, col2, col3 = st.columns(3)
    with col1:
        total_concursos = len(df) if not df.empty else 0
        st.metric("Concursos Cadastrados", total_concursos)
    with col2:
        ultimo_concurso = df['Concurso'].max() if not df.empty and 'Concurso' in df.columns else 0
        st.metric("Último Concurso", ultimo_concurso)
    with col3:
        if not df.empty and 'Data Sorteio' in df.columns:
            ultima_data = df.iloc[-1]['Data Sorteio']
            st.metric("Última Data", ultima_data)
        else:
            st.metric("Última Data", "N/A")
    
    st.markdown("---")
    
    # FORMULÁRIO PRINCIPAL
    st.subheader("📝 Formulário para Adicionar Novo Concurso")
    
    with st.form("form_novo_concurso", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            numero_concurso = st.number_input(
                "Número do Concurso*",
                min_value=1,
                max_value=5000,
                value=int(ultimo_concurso) + 1 if ultimo_concurso > 0 else 1,
                step=1
            )
        
        with col_form2:
            data_sorteio = st.date_input(
                "Data do Sorteio*",
                value=datetime.now()
            )
        
        st.markdown("---")
        st.write("**🎯 Números Sorteados (15 números entre 1 e 25)**")
        
        col_bola1, col_bola2, col_bola3 = st.columns(3)
        numeros = []
        
        with col_bola1:
            for i in range(1, 6):
                numero = st.number_input(f"Bola {i}*", min_value=1, max_value=25, key=f"bola_{i}", value=i)
                numeros.append(numero)
        
        with col_bola2:
            for i in range(6, 11):
                numero = st.number_input(f"Bola {i}*", min_value=1, max_value=25, key=f"bola_{i}", value=i)
                numeros.append(numero)
        
        with col_bola3:
            for i in range(11, 16):
                numero = st.number_input(f"Bola {i}*", min_value=1, max_value=25, key=f"bola_{i}", value=i)
                numeros.append(numero)
        
        submitted = st.form_submit_button("💾 Salvar Concurso", type="primary", use_container_width=True)
        
        if submitted:
            # Validações
            erros = []
            if not df.empty and numero_concurso in df['Concurso'].values:
                erros.append(f"Concurso {numero_concurso} já existe!")
            if len(numeros) != 15:
                erros.append("São necessários 15 números!")
            if len(numeros) != len(set(numeros)):
                erros.append("Números devem ser únicos!")
            if any(num < 1 or num > 25 for num in numeros):
                erros.append("Números devem estar entre 1 e 25!")
            
            if not erros:
                novo_concurso = {'Concurso': numero_concurso, 'Data Sorteio': data_sorteio.strftime('%d/%m/%Y')}
                for i, num in enumerate(numeros, 1):
                    novo_concurso[f'Bola{i}'] = num
                
                if df.empty:
                    df = pd.DataFrame([novo_concurso])
                else:
                    df = pd.concat([df, pd.DataFrame([novo_concurso])], ignore_index=True)
                
                df = df.sort_values('Concurso').reset_index(drop=True)
                
                if salvar_dados(df):
                    st.success(f"✅ Concurso {numero_concurso} salvo com sucesso!")
                    st.balloons()
                    
                    # Mostrar resumo do concurso salvo
                    with st.expander("📋 Ver Detalhes do Concurso Salvo", expanded=True):
                        st.write(f"**Concurso:** {numero_concurso}")
                        st.write(f"**Data:** {data_sorteio.strftime('%d/%m/%Y')}")
                        st.write(f"**Números:** {', '.join(map(str, sorted(numeros)))}")
            else:
                for erro in erros:
                    st.error(f"❌ {erro}")

def exibir_dados_loto():
    """Exibe os dados cadastrados"""
    st.header("📁 Dados da Lotofácil")
    
    verificar_estrutura()
    
    if not os.path.exists(CSV_PATH):
        st.warning("📝 Arquivo não encontrado.")
        st.info("Vá para 'Atualizar Dados' para criar o arquivo.")
        return
    
    df = carregar_dados()
    
    if df.empty:
        st.warning("📝 Nenhum concurso cadastrado.")
        st.info("Use 'Atualizar Dados' para adicionar concursos.")
        return
    
    # Estatísticas rápidas
    st.subheader("📊 Estatísticas")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Concursos", len(df))
    with col2:
        st.metric("Primeiro Concurso", df['Concurso'].min())
    with col3:
        st.metric("Último Concurso", df['Concurso'].max())
    with col4:
        if 'Data Sorteio' in df.columns:
            ultima_data = df.iloc[-1]['Data Sorteio']
            st.metric("Última Data", ultima_data)
        else:
            st.metric("Data", "N/A")
    
    st.markdown("---")
    
    # Filtros
    st.subheader("🔍 Filtros")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        if not df.empty:
            min_conc = int(df['Concurso'].min())
            max_conc = int(df['Concurso'].max())
            concursos_range = st.slider(
                "Intervalo de Concursos",
                min_conc, max_conc, (min_conc, max_conc)
            )
            
            df_filtrado = df[
                (df['Concurso'] >= concursos_range[0]) & 
                (df['Concurso'] <= concursos_range[1])
            ]
        else:
            df_filtrado = df
    
    with col_f2:
        linhas_por_pagina = st.selectbox(
            "Linhas por página",
            [10, 25, 50, 100],
            index=0
        )
    
    st.markdown("---")
    
    # Tabela de dados
    st.subheader("📋 Concursos Cadastrados")
    st.write(f"**Mostrando {len(df_filtrado)} de {len(df)} concursos**")
    
    if not df_filtrado.empty:
        # Formatar a exibição
        df_display = df_filtrado.copy()
        if 'Data Sorteio' in df_display.columns:
            df_display = df_display[['Concurso', 'Data Sorteio'] + [f'Bola{i}' for i in range(1, 16)]]
        
        st.dataframe(
            df_display.head(linhas_por_pagina),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download
        st.markdown("---")
        st.subheader("💾 Exportar Dados")
        csv_data = df_filtrado.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label="📥 Baixar Dados Filtrados",
            data=csv_data,
            file_name=f"lotofacil_concursos_{concursos_range[0]}_{concursos_range[1]}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Nenhum concurso encontrado com os filtros selecionados.")

# ========== MENU PRINCIPAL ==========
st.sidebar.title("🔍 Menu Lotofácil")
opcao = st.sidebar.selectbox(
    "Selecione a análise:", 
    ["📊 Análise de Jogos", "📁 Ver Dados", "🔄 Atualizar Dados", "ℹ️ Sobre"]
)

if opcao == "📊 Análise de Jogos":
    exibir_jogo()  # ← FUNÇÃO PRINCIPAL COMPLETA
elif opcao == "📁 Ver Dados":
    exibir_dados_loto()
elif opcao == "🔄 Atualizar Dados":
    tela_atualizacao_dados()
elif opcao == "ℹ️ Sobre":
    st.info("""
    ### 📋 Sobre o App:
    
    **Lotofácil Analyzer**
    
    **Funcionalidades:**
    - 📊 Análise avançada de jogos e estatísticas (últimos 150 concursos)
    - 🎯 6 sugestões inteligentes (2 para cada das 3 distribuições mais comuns)
    - 📁 Visualização completa de dados históricos  
    - 🔄 Atualização de dados via formulário
    - 💾 Exportação de dados
    
    **Como usar:**
    1. Comece pela aba 'Atualizar Dados' para adicionar concursos
    2. Use 'Ver Dados' para visualizar e filtrar os concursos
    3. Use 'Análise de Jogos' para ver estatísticas avançadas e gerar sugestões
    
    **Análises disponíveis:**
    - Frequência de números por grupos
    - Padrões dos últimos 150 concursos
    - Distribuição Melhores x Piores
    - 6 sugestões baseadas nas 3 distribuições mais comuns
    
    **Formato dos dados:**
    - Concurso, Data Sorteio, Bola1 a Bola15
    - Separador: Ponto e vírgula (;)
    - Encoding: UTF-8
    """)

# Executar o aplicativo
if __name__ == "__main__":
    # O app já está rodando via Streamlit, esta parte é para execução direta
    pass
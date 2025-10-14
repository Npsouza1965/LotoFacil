import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

CSV_PATH = 'dados/lotofacil.csv'

def verificar_estrutura():
    """Verifica e cria a estrutura de pastas necessária"""
    if not os.path.exists('dados'):
        os.makedirs('dados', exist_ok=True)

def criar_arquivo_base():
    """Cria um arquivo base vazio se não existir"""
    if not os.path.exists(CSV_PATH):
        colunas = ['Concurso', 'Data Sorteio'] + [f'Bola{i}' for i in range(1, 16)]
        df_base = pd.DataFrame(columns=colunas)
        df_base.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
        return True
    return False

def carregar_dados():
    """Carrega os dados do arquivo CSV"""
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8')
            return df
        else:
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

def tela_atualizacao_dados():
    """Tela para atualizar dados manualmente"""
    st.header("🔄 Atualização de Dados da Lotofácil")
    
    verificar_estrutura()
    criar_arquivo_base()
    
    # Carregar dados existentes
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
    
    # FORMULÁRIO PARA ALIMENTAR O ARQUIVO
    st.subheader("📝 Formulário para Adicionar Novo Concurso")
    
    with st.form("form_novo_concurso", clear_on_submit=True):
        st.write("**Informações do Concurso**")
        
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            numero_concurso = st.number_input(
                "Número do Concurso*",
                min_value=1,
                max_value=5000,
                value=int(ultimo_concurso) + 1 if ultimo_concurso > 0 else 1,
                step=1,
                help="Número sequencial do concurso"
            )
        
        with col_form2:
            data_sorteio = st.date_input(
                "Data do Sorteio*",
                value=datetime.now(),
                help="Data em que o concurso foi realizado"
            )
        
        st.markdown("---")
        st.write("**🎯 Números Sorteados (15 números entre 1 e 25)**")
        
        # Criar 3 colunas para organizar os 15 campos
        col_bola1, col_bola2, col_bola3 = st.columns(3)
        
        numeros = []
        
        with col_bola1:
            for i in range(1, 6):
                numero = st.number_input(
                    f"Bola {i}*",
                    min_value=1,
                    max_value=25,
                    key=f"bola_{i}",
                    value=i,
                    step=1
                )
                numeros.append(numero)
        
        with col_bola2:
            for i in range(6, 11):
                numero = st.number_input(
                    f"Bola {i}*",
                    min_value=1,
                    max_value=25,
                    key=f"bola_{i}",
                    value=i,
                    step=1
                )
                numeros.append(numero)
        
        with col_bola3:
            for i in range(11, 16):
                numero = st.number_input(
                    f"Bola {i}*",
                    min_value=1,
                    max_value=25,
                    key=f"bola_{i}",
                    value=i,
                    step=1
                )
                numeros.append(numero)
        
        # Botão de submit
        submitted = st.form_submit_button(
            "💾 Salvar Concurso no Arquivo", 
            width='stretch',
            type="primary"
        )
        
        if submitted:
            # VALIDAÇÕES
            erros = []
            
            # Validar se concurso já existe
            if not df.empty and numero_concurso in df['Concurso'].values:
                erros.append(f"Concurso {numero_concurso} já existe no arquivo!")
            
            # Validar quantidade de números
            if len(numeros) != 15:
                erros.append("São necessários exatamente 15 números!")
            
            # Validar números únicos
            if len(numeros) != len(set(numeros)):
                erros.append("Os números devem ser únicos! Há números repetidos.")
            
            # Validar faixa de números
            for num in numeros:
                if num < 1 or num > 25:
                    erros.append("Todos os números devem estar entre 1 e 25!")
                    break
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                # CRIAR NOVO REGISTRO
                novo_concurso = {
                    'Concurso': numero_concurso,
                    'Data Sorteio': data_sorteio.strftime('%d/%m/%Y')
                }
                
                # Adicionar números às colunas Bola1 a Bola15
                for i, num in enumerate(numeros, 1):
                    novo_concurso[f'Bola{i}'] = num
                
                # Adicionar ao DataFrame
                if df.empty:
                    df = pd.DataFrame([novo_concurso])
                else:
                    df_novo = pd.DataFrame([novo_concurso])
                    df = pd.concat([df, df_novo], ignore_index=True)
                
                # Ordenar por concurso
                df = df.sort_values('Concurso').reset_index(drop=True)
                
                # SALVAR NO ARQUIVO
                if salvar_dados(df):
                    st.success(f"✅ Concurso {numero_concurso} salvo com sucesso no arquivo lotofacil.csv!")
                    st.balloons()
                    
                    # Mostrar resumo
                    with st.expander("📋 Ver Resumo do Concurso Salvo", expanded=True):
                        st.write(f"**Concurso:** {numero_concurso}")
                        st.write(f"**Data:** {data_sorteio.strftime('%d/%m/%Y')}")
                        st.write(f"**Números Sorteados:**")
                        
                        # Mostrar números em formato de cartela
                        cols_nums = st.columns(5)
                        for idx, num in enumerate(sorted(numeros)):
                            with cols_nums[idx % 5]:
                                st.markdown(
                                    f"""
                                    <div style='
                                        text-align: center; 
                                        padding: 10px; 
                                        border: 2px solid #4CAF50; 
                                        border-radius: 8px; 
                                        margin: 2px; 
                                        background: #e8f5e8;
                                        font-weight: bold;
                                        color: #000000;
                                    '>{num:02d}</div>
                                    """, 
                                    unsafe_allow_html=True
                                )
    
    st.markdown("---")
    
    # UPLOAD EM LOTE
    st.subheader("📤 Upload em Lote (CSV)")
    
    with st.expander("💡 Importar Múltiplos Concursos via Arquivo CSV"):
        st.info("""
        **Formato esperado do arquivo CSV:**
        - Colunas: Concurso, Data Sorteio, Bola1, Bola2, ..., Bola15
        - Separador: Ponto e vírgula (;)
        - Formato da Data: DD/MM/AAAA
        - Encoding: UTF-8 (recomendado)
        
        **Exemplo:**
        ```
        Concurso;Data Sorteio;Bola1;Bola2;Bola3;Bola4;Bola5;Bola6;Bola7;Bola8;Bola9;Bola10;Bola11;Bola12;Bola13;Bola14;Bola15
        3001;15/01/2024;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15
        3002;16/01/2024;2;4;6;8;10;12;14;16;18;20;22;24;1;3;5
        ```
        """)
        
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV para importar",
            type=['csv'],
            help="Selecione o arquivo com os dados dos concursos"
        )
        
        if uploaded_file is not None:
            try:
                # Ler arquivo upload
                df_upload = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                
                # Validar colunas necessárias
                colunas_necessarias = ['Concurso', 'Data Sorteio'] + [f'Bola{i}' for i in range(1, 16)]
                colunas_faltantes = [col for col in colunas_necessarias if col not in df_upload.columns]
                
                if colunas_faltantes:
                    st.error(f"❌ Colunas faltantes no arquivo: {', '.join(colunas_faltantes)}")
                else:
                    st.success(f"✅ Arquivo válido! {len(df_upload)} concursos encontrados.")
                    
                    # Mostrar preview
                    with st.expander("👀 Visualizar Primeiras Linhas do Arquivo"):
                        st.dataframe(df_upload.head(3), width='stretch')
                    
                    # Verificar concursos duplicados
                    concursos_existentes = set(df['Concurso']) if not df.empty else set()
                    concursos_novos = set(df_upload['Concurso'])
                    concursos_duplicados = concursos_existentes.intersection(concursos_novos)
                    
                    if concursos_duplicados:
                        st.warning(f"⚠️ {len(concursos_duplicados)} concursos já existem e serão ignorados: {sorted(concursos_duplicados)[:5]}...")
                        df_upload = df_upload[~df_upload['Concurso'].isin(concursos_duplicados)]
                    
                    if len(df_upload) > 0:
                        # Combinar dados
                        if df.empty:
                            df_combinado = df_upload.copy()
                        else:
                            df_combinado = pd.concat([df, df_upload], ignore_index=True)
                        
                        # Ordenar e salvar
                        df_combinado = df_combinado.sort_values('Concurso').reset_index(drop=True)
                        
                        if salvar_dados(df_combinado):
                            st.success(f"✅ {len(df_upload)} novos concursos importados com sucesso!")
                            st.rerun()
                    else:
                        st.info("ℹ️ Nenhum concurso novo para importar.")
                        
            except Exception as e:
                st.error(f"❌ Erro ao importar arquivo: {e}")
                st.info("💡 Verifique o formato do arquivo e tente novamente.")
    
    st.markdown("---")
    
    # GESTÃO DE DADOS
    st.subheader("🗃️ Gestão do Arquivo de Dados")
    
    col_gest1, col_gest2, col_gest3 = st.columns(3)
    
    with col_gest1:
        if st.button("🔄 Recarregar Dados", width='stretch'):
            st.rerun()
    
    with col_gest2:
        if st.button("📊 Visualizar Arquivo Atual", width='stretch'):
            if not df.empty:
                with st.expander("📁 Conteúdo do Arquivo lotofacil.csv", expanded=True):
                    st.dataframe(df, width='stretch')
            else:
                st.info("Arquivo vazio. Use o formulário acima para adicionar concursos.")
    
    with col_gest3:
        if st.button("🗑️ Limpar Todos os Dados", width='stretch', type="secondary"):
            st.warning("⚠️ Esta ação irá remover TODOS os concursos do arquivo!")
            if st.checkbox("✅ Confirmar exclusão total de todos os dados"):
                df_limpo = pd.DataFrame(columns=df.columns) if not df.empty else pd.DataFrame()
                if salvar_dados(df_limpo):
                    st.success("✅ Todos os dados foram removidos do arquivo!")
                    st.rerun()

def exibir_dados_loto():
    st.header("📁 Dados da Lotofácil")
    
    verificar_estrutura()
    
    if not os.path.exists(CSV_PATH):
        st.warning("📝 Arquivo lotofacil.csv não encontrado.")
        st.info("Vá para a aba 'Atualização de Dados' para criar o arquivo e adicionar concursos.")
        return
    
    df = carregar_dados()
    
    if df.empty:
        st.warning("📝 Nenhum concurso cadastrado no arquivo.")
        st.info("Vá para a aba 'Atualização de Dados' para adicionar concursos usando o formulário.")
        return
    
    # Estatísticas rápidas
    st.subheader("📊 Estatísticas Gerais")
    
    # Layout responsivo para estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Concursos", len(df))
    with col2:
        st.metric("Período", f"{df['Concurso'].min()} - {df['Concurso'].max()}")
    with col3:
        primeira_data = df.iloc[0]['Data Sorteio'] if 'Data Sorteio' in df.columns else 'N/A'
        st.metric("Primeira Data", primeira_data)
    with col4:
        ultima_data = df.iloc[-1]['Data Sorteio'] if 'Data Sorteio' in df.columns else 'N/A'
        st.metric("Última Data", ultima_data)
    
    st.markdown("---")
    
    # Filtros interativos
    st.subheader("🔍 Filtros e Visualização")
    
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        # Filtro por intervalo de concursos
        min_concurso = df['Concurso'].min()
        max_concurso = df['Concurso'].max()
        concursos_selecionados = st.slider(
            "Intervalo de Concursos",
            min_value=int(min_concurso),
            max_value=int(max_concurso),
            value=(int(min_concurso), int(max_concurso)),
            help="Selecione o intervalo de concursos para visualizar"
        )
    
    with col_filtro2:
        # Quantidade de linhas a exibir
        num_linhas = st.selectbox(
            "Linhas por página",
            options=[10, 25, 50, 100],
            index=0,
            help="Quantidade de concursos a exibir por vez"
        )
    
    with col_filtro3:
        # Ordenação
        ordenacao = st.selectbox(
            "Ordenar por",
            options=["Concurso (Crescente)", "Concurso (Decrescente)", "Data (Mais Recente)", "Data (Mais Antiga)"],
            index=1,
            help="Ordenação dos concursos"
        )
    
    # Aplicar filtros
    df_filtrado = df[
        (df['Concurso'] >= concursos_selecionados[0]) & 
        (df['Concurso'] <= concursos_selecionados[1])
    ]
    
    # Aplicar ordenação
    if ordenacao == "Concurso (Crescente)":
        df_filtrado = df_filtrado.sort_values('Concurso', ascending=True)
    elif ordenacao == "Concurso (Decrescente)":
        df_filtrado = df_filtrado.sort_values('Concurso', ascending=False)
    elif ordenacao == "Data (Mais Recente)" and 'Data Sorteio' in df_filtrado.columns:
        # Converter datas para datetime para ordenação correta
        try:
            df_filtrado['Data_Sorteio_DT'] = pd.to_datetime(df_filtrado['Data Sorteio'], format='%d/%m/%Y')
            df_filtrado = df_filtrado.sort_values('Data_Sorteio_DT', ascending=False)
            df_filtrado = df_filtrado.drop('Data_Sorteio_DT', axis=1)
        except:
            df_filtrado = df_filtrado.sort_values('Data Sorteio', ascending=False)
    elif ordenacao == "Data (Mais Antiga)" and 'Data Sorteio' in df_filtrado.columns:
        try:
            df_filtrado['Data_Sorteio_DT'] = pd.to_datetime(df_filtrado['Data Sorteio'], format='%d/%m/%Y')
            df_filtrado = df_filtrado.sort_values('Data_Sorteio_DT', ascending=True)
            df_filtrado = df_filtrado.drop('Data_Sorteio_DT', axis=1)
        except:
            df_filtrado = df_filtrado.sort_values('Data Sorteio', ascending=True)
    
    st.markdown("---")
    
    # Visualização dos dados com abas
    st.subheader("📋 Visualização dos Dados")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Visualização Compacta", "📊 Visualização Completa", "📈 Estatísticas Detalhadas"])
    
    with tab1:
        st.write(f"**Concursos {concursos_selecionados[0]} a {concursos_selecionados[1]}** (Total: {len(df_filtrado)})")
        
        # Criar dataframe compacto
        df_compacto = df_filtrado[['Concurso']].copy()
        if 'Data Sorteio' in df_filtrado.columns:
            df_compacto['Data Sorteio'] = df_filtrado['Data Sorteio']
        
        # Adicionar coluna com números sorteados formatados
        colunas_bolas = [f'Bola{i}' for i in range(1, 16) if f'Bola{i}' in df_filtrado.columns]
        if colunas_bolas:
            df_compacto['Números Sorteados'] = df_filtrado[colunas_bolas].apply(
                lambda row: ' - '.join(f"{int(x):02d}" for x in row.astype(int).values), axis=1
            )
        
        st.dataframe(
            df_compacto.head(num_linhas),
            width='stretch',
            hide_index=True,
            height=400
        )
    
    with tab2:
        st.write(f"**Visualização Completa - {len(df_filtrado)} concursos**")
        
        # Mostrar todas as colunas disponíveis
        st.dataframe(
            df_filtrado.head(num_linhas),
            width='stretch',
            hide_index=True,
            height=500
        )
    
    with tab3:
        st.write("**📈 Análise Estatística dos Dados**")
        
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.write("**Informações do Dataset:**")
            st.write(f"• Total de Concursos: **{len(df)}**")
            st.write(f"• Período: **{df['Concurso'].min()}** a **{df['Concurso'].max()}**")
            st.write(f"• Colunas Disponíveis: **{len(df.columns)}**")
            
            # Contar números únicos
            todos_numeros = []
            for i in range(1, 16):
                coluna = f'Bola{i}'
                if coluna in df.columns:
                    todos_numeros.extend(df[coluna].dropna().astype(int).tolist())
            
            if todos_numeros:
                st.write(f"• Total de Números Sorteados: **{len(todos_numeros):,}**")
                st.write(f"• Números Únicos Sorteados: **{len(set(todos_numeros))}**")
        
        with col_stat2:
            st.write("**Colunas do Arquivo:**")
            for coluna in df.columns:
                tipo = str(df[coluna].dtype)
                st.write(f"• **{coluna}** ({tipo})")
    
    # Download do arquivo processado
    st.markdown("---")
    st.subheader("💾 Exportar Dados")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # Download do arquivo original filtrado
        csv_filtrado = df_filtrado.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label="📥 Baixar Dados Filtrados",
            data=csv_filtrado,
            file_name=f"lotofacil_filtrado_{concursos_selecionados[0]}_{concursos_selecionados[1]}.csv",
            mime="text/csv",
            width='stretch',
            help="Baixar apenas os concursos filtrados"
        )
    
    with col_dl2:
        # Download do arquivo completo
        csv_completo = df.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label="📥 Baixar Todos os Dados",
            data=csv_completo,
            file_name="lotofacil_completo.csv",
            mime="text/csv",
            width='stretch',
            help="Baixar todos os concursos disponíveis"
        )

# Aplicativo principal
def main():
    st.set_page_config(
        page_title="Lotofácil Analytics",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Lotofácil Analytics - Gerenciador de Dados")
    
    # Menu de navegação
    tab1, tab2 = st.tabs(["📁 Visualizar Dados", "🔄 Alimentar Dados"])
    
    with tab1:
        exibir_dados_loto()
    
    with tab2:
        tela_atualizacao_dados()

if __name__ == "__main__":
    main()
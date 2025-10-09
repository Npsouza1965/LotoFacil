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
            df_filtrado = df_filtrado.sort_values('Data Sorteio', ascending=False)
        elif ordenacao == "Data (Mais Antiga)" and 'Data Sorteio' in df_filtrado.columns:
            df_filtrado = df_filtrado.sort_values('Data Sorteio', ascending=True)
        
        st.markdown("---")
        
        # Visualização dos dados com abas
        st.subheader("📋 Visualização dos Dados")
        
        tab1, tab2, tab3 = st.tabs(["🎯 Visualização Compacta", "📊 Visualização Completa", "📈 Estatísticas Detalhadas"])
        
        with tab1:
            st.write(f"**Concursos {concursos_selecionados[0]} a {concursos_selecionados[1]}** (Total: {len(df_filtrado)})")
            
            # Visualização compacta - apenas informações essenciais
            colunas_compactas = ['Concurso', 'Data Sorteio'] if 'Data Sorteio' in df_filtrado.columns else ['Concurso']
            
            # Adicionar algumas bolas para referência
            if len([col for col in df_filtrado.columns if 'Bola' in col]) >= 3:
                colunas_compactas.extend(['Bola1', 'Bola2', 'Bola3', '...', 'Bola15'])
            
            # Criar dataframe compacto
            df_compacto = df_filtrado[['Concurso']].copy()
            if 'Data Sorteio' in df_filtrado.columns:
                df_compacto['Data Sorteio'] = df_filtrado['Data Sorteio']
            
            # Adicionar coluna com números sorteados formatados
            colunas_bolas = [f'Bola{i}' for i in range(1, 16) if f'Bola{i}' in df_filtrado.columns]
            if colunas_bolas:
                df_compacto['Números Sorteados'] = df_filtrado[colunas_bolas].apply(
                    lambda row: ' - '.join(row.astype(str).values), axis=1
                )
            
            st.dataframe(
                df_compacto.head(num_linhas),
                use_container_width=True,
                hide_index=True,
                height=400
            )
        
        with tab2:
            st.write(f"**Visualização Completa - {len(df_filtrado)} concursos**")
            
            # Mostrar todas as colunas disponíveis
            st.dataframe(
                df_filtrado.head(num_linhas),
                use_container_width=True,
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
        
        # Paginação simples
        st.markdown("---")
        st.write(f"**📄 Página 1 de 1** - Mostrando {min(num_linhas, len(df_filtrado))} de {len(df_filtrado)} concursos")
        
        # Informações adicionais
        with st.expander("💡 Dicas de Visualização"):
            st.write("""
            - **Visualização Compacta**: Ideal para telas menores, mostra apenas informações essenciais
            - **Visualização Completa**: Mostra todas as colunas do arquivo CSV
            - **Use os filtros**: Para analisar períodos específicos de concursos
            - **Ordenação**: Organize os dados por concurso ou data para melhor análise
            """)
        
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
                use_container_width=True,
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
                use_container_width=True,
                help="Baixar todos os concursos disponíveis"
            )
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.info("💡 Verifique se o arquivo CSV está no formato correto.")
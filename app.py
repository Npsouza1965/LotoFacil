import streamlit as st
from Sistema import jogo
from Sistema import dados

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
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🎯 Lotofácil Analyzer</h1>', unsafe_allow_html=True)

# Menu lateral
st.sidebar.title("🔍 Menu Lotofácil")
opcao = st.sidebar.selectbox(
    "Selecione a análise:", 
    ["📊 Análise de Jogos", "📁 Ver Dados", "ℹ️ Sobre"]
)

if opcao == "📊 Análise de Jogos":
    jogo.exibir_jogo()
elif opcao == "📁 Ver Dados":
    dados.exibir_dados_loto()
elif opcao == "ℹ️ Sobre":
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Sobre o App:**
    - Análise de dados da Lotofácil
    - Sugestões de jogos
    - Estatísticas históricas
    """)
    
    st.info("""
    ### 📋 Instruções:
    
    1. **Primeiro uso:** Faça upload do arquivo CSV na aba "Análise de Jogos"
    2. **Formato do CSV:** Deve conter colunas: Concurso, Data Sorteio, Bola1...Bola15
    3. **Separador:** Ponto e vírgula (;)
    4. **Encoding:** UTF-8
    
    ### 📊 Funcionalidades:
    - Análise de frequência de números
    - Sugestões baseadas em estatísticas
    - Visualização de dados históricos
    """)
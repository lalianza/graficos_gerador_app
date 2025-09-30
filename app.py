import streamlit as st
import pandas as pd
import os
import sys
import io
import matplotlib.pyplot as plt
from typing import Dict, Any, List

# ---------------------------------------------------------------------
# CORREÇÃO DA IMPORTAÇÃO
# ---------------------------------------------------------------------
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "functions"))
    # Assumindo que a classe AnaliseScoresQI está aqui e tem os métodos/atributos necessários
    from graph_functions import AnaliseScoresQI

except ImportError:
    st.error("ERRO: O arquivo 'graph_functions.py' não foi encontrado na pasta 'functions'.")
    st.stop()

analisador = AnaliseScoresQI()

# ---------------------------------------------------------------------
# DEFINIÇÃO UNIVERSAL DOS PARÂMETROS E INICIALIZAÇÃO ROBUSTA
# ---------------------------------------------------------------------

VARIAVEIS_INTERNAS = ['input_scores', 'validated_scores', 'score', 'resultado', 'dic']

def _get_filtered_params(func) -> List[str]:
    """Coleta parâmetros da função e remove variáveis internas (score, dic, etc.)."""
    params = func.__code__.co_varnames[1:]
    return [p for p in params if p not in VARIAVEIS_INTERNAS]

PARAMETROS_QI = _get_filtered_params(analisador.cria_df_qi)
PARAMETROS_INDICES = _get_filtered_params(analisador.cria_df_indices)

# --- REFORÇO CRÍTICO: CHAVES FALTANTES ---
# Garante a inicialização de chaves que estavam falhando na transição.
CHAVES_CRITICAS_FALTANDO = {
    'Compreensao',
    'Completar_Figuras',
}

# Cria o conjunto de todas as chaves de scores possíveis.
TODOS_PARAMETROS = set(PARAMETROS_QI) | set(PARAMETROS_INDICES) | CHAVES_CRITICAS_FALTANDO
# ------------------------------------

# INICIALIZAÇÃO DO SESSION STATE: Garante que TODAS as chaves existam
if 'scores_initialized' not in st.session_state:
    for param in TODOS_PARAMETROS:
        # Inicializa TODOS os scores.
        st.session_state[param] = analisador.VALOR_PADRAO

    st.session_state['media_referencia_ui'] = float(analisador.VALOR_PADRAO)
    st.session_state['margem_seguranca_ui'] = 2.0
    st.session_state['scores_initialized'] = True


# ---------------------------------------------------------------------
# LAYOUT E WIDGETS
# ---------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Análise Interativa de Scores de QI")
st.title("Calculadora e Visualizador de Scores de QI")
st.sidebar.header("Configuração dos Dados")

formato_df = st.sidebar.selectbox(
    "Escolha o Formato da Análise:",
    ("QI (Verbal/Executivo)", "Índice (ICV/IOP/IMO/IVP)")
)

if formato_df == "QI (Verbal/Executivo)":
    PARAMETROS_ATUAIS = PARAMETROS_QI
    st.header("Scores de 13 Subtestes (QI)")
    func_cria_df = analisador.cria_df_qi
else:
    PARAMETROS_ATUAIS = PARAMETROS_INDICES
    st.header("Scores de 11 Subtestes (Índices Fatoriais)")
    func_cria_df = analisador.cria_df_indices

# --- LOOP DE INPUTS (Solução Final Aplicada) ---
cols = st.columns(3)
score_inputs: Dict[str, Any] = {}

for i, param in enumerate(PARAMETROS_ATUAIS):

    # CORREÇÃO: Usa .get() para retornar o valor padrão se a chave não existir
    valor_inicial = st.session_state.get(param, analisador.VALOR_PADRAO)

    score_inputs[param] = cols[i % 3].number_input(
        f"Score de {param.replace('_', ' ')}:",
        min_value=analisador.MIN_SCORE,
        max_value=analisador.MAX_SCORE,
        value=valor_inicial,
        step=1,
        key=param
    )

st.sidebar.markdown("---")
st.sidebar.header("Configuração do Gráfico")

media = st.sidebar.number_input(
    "Média de Referência (Reta Principal):",
    min_value=0.0,
    max_value=18.0,
    value=st.session_state['media_referencia_ui'],
    step=0.5,
    key='media_referencia_ui'
)

margem = st.sidebar.number_input(
    "Margem de Segurança (+/-):",
    min_value=0.0,
    value=st.session_state['margem_seguranca_ui'],
    step=0.5,
    key='margem_seguranca_ui'
)

cores_hex_str = st.sidebar.text_area(
    "Paleta de Cores HEX (Opcional):",
    placeholder="#1f77b4, #ff7f0e, #2ca02c, #9467bd (Separar por vírgula)"
)

# ---------------------------------------------------------------------
# BOTÃO E EXIBIÇÃO DO GRÁFICO
# ---------------------------------------------------------------------
st.markdown("---")

if st.button("Gerar Gráfico"):

    # 1. Tentar criar o DataFrame
    parametros_validos = PARAMETROS_ATUAIS
    current_score_inputs = {}

    for param in parametros_validos:
        # Puxa o valor do st.session_state (salvo via 'key' do number_input)
        valor_stream = st.session_state[param]
        if valor_stream is not None:
             current_score_inputs[param] = int(valor_stream)
        else:
             current_score_inputs[param] = None

    df_ou_erro = func_cria_df(**current_score_inputs)

    if isinstance(df_ou_erro, str):
        st.error(f"⚠️ Erro de Validação: {df_ou_erro}")
    else:
        df_resultados = df_ou_erro

        # 2. Processar a paleta de cores
        paleta_hex = [c.strip() for c in cores_hex_str.split(',') if c.strip()] if cores_hex_str else None

        st.subheader("Resultado da Análise")

        # 3. Geração do Gráfico e Captura para Download

        analisador.plota_scores(
            df=df_resultados,
            media_referencia=media,
            margem_seguranca=margem,
            paleta_cores_hex=paleta_hex
        )

        # Renderiza o gráfico do Matplotlib no Streamlit
        st.pyplot(plt.gcf())

        # --- Lógica de Download ---
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format="png", bbox_inches='tight')

        st.download_button(
            label="Baixar Gráfico (PNG)",
            data=buf.getvalue(),
            file_name=f"Scores_QI_{formato_df.replace('/', '-')}.png",
            mime="image/png"
        )

        # Fecha a figura do Matplotlib para liberar memória e evitar sobreposição
        plt.close(plt.gcf())

        st.markdown("---")
        st.subheader("Dados Plotados")
        st.dataframe(df_resultados)

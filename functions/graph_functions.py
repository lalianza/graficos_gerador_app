import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Union, List, Any

# =========================================================================
# CLASSE PRINCIPAL
# =========================================================================

class AnaliseScoresQI:
    """
    Classe utilitária para criar DataFrames de scores de testes de QI
    (no formato QI Verbal/Executivo ou Índices Fatoriais) e gerar gráficos
    de barras personalizados com validação de dados.
    """

    # Constantes de Validação (Compartilhadas por todas as funções de criação)
    VALOR_PADRAO = 8
    MIN_SCORE = 0
    MAX_SCORE = 18

    def __init__(self):
        """Inicializa a classe."""
        print("Objeto AnaliseScoresQI criado. Pronto para criar DFs e gerar gráficos.")

    # ---------------------------------------------------------------------
    # MÉTODO DE VALIDAÇÃO (Helper interno)
    # ---------------------------------------------------------------------

    def _valida_score(self, score: Any) -> Union[int, str]:
        """
        Valida um único score. Retorna o int validado ou a string de erro.
        """

        if score is None:
            return self.VALOR_PADRAO

        if isinstance(score, float):
            return "Por favor, coloque um número inteiro."

        try:
            valor_int = int(score)

            # Checa se a string continha um ponto decimal (indicando float)
            if isinstance(score, str) and '.' in score.strip():
                if float(score) != valor_int:
                    return "Por favor, coloque um número inteiro."

        except (ValueError, TypeError):
            return "Por favor, coloque um número inteiro."

        if valor_int < self.MIN_SCORE or valor_int > self.MAX_SCORE:
            return f"Por favor, preencha com um valor entre {self.MIN_SCORE} e {self.MAX_SCORE}."

        return valor_int

    # ---------------------------------------------------------------------
    # MÉTODO 1: Criação de DF (QI Verbal/Executivo)
    # ---------------------------------------------------------------------

    def cria_df_qi(self,
        Vocabulario: Optional[Union[int, str]] = None, Semelhancas: Optional[Union[int, str]] = None,
        Aritmetica: Optional[Union[int, str]] = None, Digitos: Optional[Union[int, str]] = None,
        Informacao: Optional[Union[int, str]] = None, Compreensao: Optional[Union[int, str]] = None,
        Sequencia_de_Numeros_e_Letras: Optional[Union[int, str]] = None, Completar_Figuras: Optional[Union[int, str]] = None,
        Cadigos: Optional[Union[int, str]] = None, Cubos: Optional[Union[int, str]] = None,
        Raciocinio_Matricial: Optional[Union[int, str]] = None, Arranjo_de_Figuras: Optional[Union[int, str]] = None,
        Porcurar_Símbolos: Optional[Union[int, str]] = None
    ) -> Union[pd.DataFrame, str]:

        input_scores = [
            Vocabulario, Semelhancas, Aritmetica, Digitos, Informacao,
            Compreensao, Sequencia_de_Numeros_e_Letras, Completar_Figuras,
            Cadigos, Cubos, Raciocinio_Matricial, Arranjo_de_Figuras, Porcurar_Símbolos
        ]

        validated_scores: List[int] = []

        for score in input_scores:
            resultado = self._valida_score(score)
            if isinstance(resultado, str):
                return resultado # Retorna a mensagem de erro da validação
            validated_scores.append(resultado)

        dic = {
            'Inteligência': [
                'Vocabulário', 'Semelhanças', 'Aritmética', 'Dígitos', 'Informação',
                'Compreensão', 'Sequência de Números e Letras', 'Completar Figuras',
                'Códigos', 'Cubos', 'Raciocínio Matricial', 'Arranjo de Figuras',
                'Procurar Símbolos'
            ],
            'Scores': validated_scores,
            'QI': [
                'QI Verbal', 'QI Verbal', 'QI Verbal', 'QI Verbal', 'QI Verbal',
                'QI Verbal', 'QI Verbal', 'QI Executivo', 'QI Executivo', 'QI Executivo',
                'QI Executivo', 'QI Executivo', 'QI Executivo'
            ]
        }

        return pd.DataFrame(dic)

    # ---------------------------------------------------------------------
    # MÉTODO 2: Criação de DF (Índices Fatoriais ICV, IOP, IMO, IVP)
    # ---------------------------------------------------------------------

    def cria_df_indices(self,
        Vocabulario: Optional[Union[int, str]] = None, Semelhancas: Optional[Union[int, str]] = None,
        Informacao: Optional[Union[int, str]] = None, Completar_Figuras: Optional[Union[int, str]] = None,
        Cubos: Optional[Union[int, str]] = None, Raciocinio_Matricial: Optional[Union[int, str]] = None,
        Aritmetica: Optional[Union[int, str]] = None, Digitos: Optional[Union[int, str]] = None,
        Seq_Numeros_Letras: Optional[Union[int, str]] = None, Codigos: Optional[Union[int, str]] = None,
        Procurar_Simbolos: Optional[Union[int, str]] = None
    ) -> Union[pd.DataFrame, str]:

        input_scores = [
            Vocabulario, Semelhancas, Informacao,
            Completar_Figuras, Cubos, Raciocinio_Matricial,
            Aritmetica, Digitos, Seq_Numeros_Letras,
            Codigos, Procurar_Simbolos
        ]

        validated_scores: List[int] = []

        for score in input_scores:
            resultado = self._valida_score(score)
            if isinstance(resultado, str):
                return resultado # Retorna a mensagem de erro da validação
            validated_scores.append(resultado)

        dic = {
            'Inteligência': [
                'Vocabulário', 'Semelhanças', 'Informação', 'Completar Figuras',
                'Cubos', 'Raciocínio Matricial', 'Aritmética', 'Dígitos',
                'Seq. Números Letras', 'Códigos', 'Procurar Símbolos'
            ],
            'Scores': validated_scores,
            'Índice': [
                'ICV', 'ICV', 'ICV',
                'IOP', 'IOP', 'IOP',
                'IMO', 'IMO', 'IMO',
                'IVP', 'IVP' # 11 itens para corresponder aos 11 subtestes
            ]
        }

        return pd.DataFrame(dic)

    # ---------------------------------------------------------------------
    # MÉTODO 3: Criação do Gráfico
    # ---------------------------------------------------------------------

    def plota_scores(
        self,
        df: pd.DataFrame,
        media_referencia: Optional[float] = None,
        margem_seguranca: Optional[float] = None,
        paleta_cores_hex: Optional[List[str]] = None,
    ):
        """
        Gera um gráfico de barras flexível, usando 'QI' ou 'Índice' para agrupar (Hue).
        """

        # 1. Determinação da Coluna de Agrupamento (HUE)
        if 'QI' in df.columns:
            coluna_hue = 'QI'
            titulo_agrupamento = 'Categoria de QI'
        elif 'Índice' in df.columns:
            coluna_hue = 'Índice'
            titulo_agrupamento = 'Índices Fatoriais'
        else:
            coluna_hue = None
            titulo_agrupamento = 'Scores Individuais'
            print("Atenção: Colunas 'QI' ou 'Índice' não encontradas. Plotando sem agrupamento (Hue).")

        # Configuração inicial do estilo
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(14, 7))

        # Parâmetros base para o barplot
        barplot_params = {
            'data': df,
            'x': 'Inteligência',
            'y': 'Scores',
            'dodge': False
        }

        # Adiciona Hue e Paleta
        if coluna_hue:
            barplot_params['hue'] = coluna_hue

            if paleta_cores_hex and isinstance(paleta_cores_hex, list):
                barplot_params['palette'] = paleta_cores_hex
                # Aviso de cores insuficientes (opcional)
                num_categorias = df[coluna_hue].nunique()
                if len(paleta_cores_hex) < num_categorias:
                     print(f"AVISO: Paleta customizada tem {len(paleta_cores_hex)} cores, mas há {num_categorias} categorias. Cores serão recicladas.")
            else:
                barplot_params['palette'] = 'viridis'

        sns.barplot(**barplot_params)

        # 3. Adição das Retas de Referência
        if media_referencia is not None:

            plt.axhline(media_referencia, color='red', linestyle='--', linewidth=1.5,
                        label=f'Média ({media_referencia})')

            if margem_seguranca is not None and margem_seguranca > 0:
                limite_sup = media_referencia + margem_seguranca
                limite_inf = media_referencia - margem_seguranca
                plt.axhline(limite_sup, color='green', linestyle=':', linewidth=1,
                            label=f'Margem Sup. ({limite_sup})')
                plt.axhline(limite_inf, color='green', linestyle=':', linewidth=1,
                            label=f'Margem Inf. ({limite_inf})')

            plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

        # 4. Configurações Finais
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.title(f'Scores dos Subtestes de Inteligência por {titulo_agrupamento}', fontsize=16, pad=20)
        plt.xlabel('Subteste de Inteligência', fontsize=12)
        plt.ylabel('Score (0-18)', fontsize=12)

        plt.tight_layout(rect=[0, 0, 1, 1])
        plt.show()

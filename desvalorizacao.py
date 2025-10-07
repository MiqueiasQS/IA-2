import json
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter

def prever_valor_futuro_ml(
    codigo_fipe: str,
    anos_para_prever: int,
    arquivo_json: str = "dataset_byd_completo_custos.json",
    verbose: bool = False,
):
    """
    Prevê o valor futuro de um veículo.
    Se verbose=True, imprime os detalhes da previsão.
    Retorna um dicionário com os dados da previsão ou None em caso de erro.
    """
    try:
        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_json}' não foi encontrado.")
        return None
        
    df = pd.DataFrame(dados)

    df["Valor"] = (
        df["Valor"]
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["AnoModelo"] = pd.to_numeric(df["AnoModelo"], errors="coerce")
    df.dropna(subset=["AnoModelo", "Valor"], inplace=True)

    df_modelo = df[df["CodigoFipe"] == codigo_fipe].copy()
    if df_modelo.empty:
        print(f"Nenhum veículo encontrado com CodigoFipe {codigo_fipe}")
        return None

    df_real = df_modelo[df_modelo["AnoModelo"] < 32000]
    df_zero = df_modelo[df_modelo["AnoModelo"] == 32000]

    if len(df_real) < 2 or df_zero.empty:
        print("Faltam dados de histórico (mínimo 2) ou valor zero km para esse modelo.")
        return None

    df_real = df_real.groupby("AnoModelo")["Valor"].mean().reset_index()
    modelo_base = df_modelo["ModeloBase"].iloc[0]

    ano_atual = 2026
    df_real["IdadeVeiculo"] = ano_atual - df_real["AnoModelo"]
    
    df_real = df_real[(df_real["IdadeVeiculo"] >= 0) & (df_real["IdadeVeiculo"] < 30)]

    if len(df_real) < 2:
        print("Faltam dados de histórico suficientes (após filtro de idade) para esse modelo.")
        return None

    X = df_real[["IdadeVeiculo"]]
    y = df_real["Valor"]

    grau_polinomio = 2
    model = make_pipeline(PolynomialFeatures(degree=grau_polinomio), LinearRegression())
    
    model.fit(X, y)

    valor_zero = df_zero["Valor"].mean()
    idades_futuras = np.array(range(1, anos_para_prever + 1)).reshape(-1, 1)
    valores_previstos = model.predict(idades_futuras)

    desvalorizacao_total = valor_zero - valores_previstos[-1]
    desvalorizacao_total = max(0, desvalorizacao_total)

    if verbose:
        print(f"\nPrevisão de desvalorização para o modelo FIPE {codigo_fipe} ({modelo_base})")
        print(f"Modelo treinado com {len(df_real)} pontos de dados históricos.")
        print(f"Valor zero km: R$ {valor_zero:,.2f}\n")

        for i, idade in enumerate(idades_futuras.flatten()):
            valor_previsto = valores_previstos[i]
            desval_acumulada = (1 - valor_previsto / valor_zero) * 100 if valor_zero > 0 else 0
            print(f"Após {idade} ano(s): Valor Previsto R$ {valor_previsto:,.2f} | Desv. Acumulada: {desval_acumulada:.2f}%")

    return {
        "codigo_fipe": codigo_fipe,
        "modelo_base": modelo_base,
        "dados_historicos": df_real,
        "valor_zero": valor_zero,
        "idades_previsao": idades_futuras.flatten(),
        "valores_previstos": valores_previstos,
        "desvalorizacao_total": desvalorizacao_total,
        "anos_previsao": anos_para_prever,
        "modelo_regressao": model,
    }

def gerar_imagem_desvalorizacao(dados_previsao: dict, salvar_em: str):
    """Gera e salva uma imagem com a foto do carro e o gráfico de desvalorização."""
    if not dados_previsao:
        print("Dados de previsão inválidos.")
        return

    # --- Configurações do Plot ---
    plt.style.use("seaborn-v0_8-darkgrid")
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 4])

    # --- Título ---
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.text(0.5, 0.7, f"Análise de Desvalorização: {dados_previsao['modelo_base']}",
                  ha='center', va='center', fontsize=22, fontweight='bold')
    ax_title.text(0.5, 0.2, f"Previsão para {dados_previsao['anos_previsao']} anos | Código FIPE: {dados_previsao['codigo_fipe']}",
                  ha='center', va='center', fontsize=14)
    ax_title.axis('off')

    # --- Imagem do Carro ---
    ax_img = fig.add_subplot(gs[1, 0])
    img_path = f"images/{dados_previsao['modelo_base']}.png"
    try:
        if not os.path.exists("images"): os.makedirs("images")
        img = mpimg.imread(img_path)
        ax_img.imshow(img)
        ax_img.set_title("Modelo", fontsize=14, pad=10)
    except FileNotFoundError:
        ax_img.text(0.5, 0.5, f"Imagem não encontrada\n(coloque em {img_path})",
                    ha='center', va='center', fontsize=12, style='italic')
    ax_img.axis('off')

    # --- Gráfico de Desvalorização ---
    ax_graph = fig.add_subplot(gs[1, 1])
    
    # Dados históricos
    hist = dados_previsao["dados_historicos"]
    ax_graph.scatter(hist["IdadeVeiculo"], hist["Valor"], color='blue', label='Dados Históricos (FIPE)', zorder=5)

    # Valor 0km
    ax_graph.scatter([0], [dados_previsao["valor_zero"]], color='green', s=100, label=f'Valor 0km: R$ {dados_previsao["valor_zero"]:,.2f}', zorder=5, marker='*')

    # Curva de regressão
    idade_total = np.arange(0, dados_previsao['anos_previsao'] + 1).reshape(-1, 1)
    curva_valor = dados_previsao['modelo_regressao'].predict(idade_total)
    curva_valor[0] = dados_previsao['valor_zero'] # Força o início no valor 0km
    ax_graph.plot(idade_total.flatten(), curva_valor, 'r--', label='Curva de Desvalorização Prevista')

    # Formatação do gráfico
    formatter = FuncFormatter(lambda x, p: f'R$ {int(x/1000)}k')
    ax_graph.yaxis.set_major_formatter(formatter)
    ax_graph.set_xlabel("Idade do Veículo (Anos)", fontsize=12)
    ax_graph.set_ylabel("Valor do Veículo (R$)", fontsize=12)
    ax_graph.set_title("Valor vs. Idade do Veículo", fontsize=16, pad=10)
    ax_graph.legend(fontsize=10)
    ax_graph.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Adiciona texto com a desvalorização total
    desv_total = dados_previsao['desvalorizacao_total']
    ax_graph.text(0.95, 0.05, f"Desvalorização em {dados_previsao['anos_previsao']} anos: R$ {desv_total:,.2f}",
                  transform=ax_graph.transAxes, ha='right', va='bottom',
                  fontsize=12, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.7))

    plt.tight_layout(pad=3.0)
    plt.savefig(salvar_em, dpi=150)
    print(f"\nImagem da análise salva em '{salvar_em}'")

# if __name__ == "__main__":
    # codigo_fipe_exemplo = "095008-4" # Exemplo: BYD SEAL
    # dados = prever_valor_futuro_ml(codigo_fipe_exemplo, 3, verbose=True)
#     if dados:
#         gerar_imagem_desvalorizacao(dados, f"analise_desvalorizacao_{codigo_fipe_exemplo}.png")
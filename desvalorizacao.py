import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime

def prever_valor_futuro_ml(codigo_fipe: str, anos_para_prever: int, arquivo_json: str = "dataset_byd_completo_custos.json", verbose: bool = True):
    """
    Prevê o valor futuro de um veículo e calcula a desvalorização total.
    Retorna o valor total da desvalorização em R$ após o período.
    Se verbose=True, imprime os detalhes da previsão.
    """
    try:
        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        if verbose: print(f"Erro: O arquivo '{arquivo_json}' não foi encontrado.")
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
        if verbose: print(f"Nenhum veículo encontrado com CodigoFipe {codigo_fipe}")
        return None

    df_real = df_modelo[df_modelo["AnoModelo"] < 32000]
    df_zero = df_modelo[df_modelo["AnoModelo"] == 32000]

    # Precisamos de pelo menos 2 pontos históricos para uma regressão e o valor 0km
    if len(df_real) < 2 or df_zero.empty:
        if verbose: print("Faltam dados de histórico (mínimo 2) ou valor zero km para esse modelo.")
        return None

    df_real = df_real.groupby("AnoModelo")["Valor"].mean().reset_index()

    ano_atual = 2026
    df_real["IdadeVeiculo"] = ano_atual - df_real["AnoModelo"]
    
    df_real = df_real[(df_real["IdadeVeiculo"] >= 0) & (df_real["IdadeVeiculo"] < 30)]

    if len(df_real) < 2:
        if verbose: print("Faltam dados de histórico suficientes (após filtro de idade) para esse modelo.")
        return None

    X = df_real[["IdadeVeiculo"]]
    y = df_real["Valor"]

    grau_polinomio = 2
    model = make_pipeline(PolynomialFeatures(degree=grau_polinomio), LinearRegression())
    
    model.fit(X, y)

    valor_zero = df_zero["Valor"].mean()
    ano_lancamento = ano_atual + 1
    
    # Prever o valor para o último ano do período
    idade_final_previsao = np.array([[anos_para_prever]])
    valor_previsto_final = model.predict(idade_final_previsao)[0]

    desvalorizacao_total = valor_zero - valor_previsto_final
    desvalorizacao_total = max(0, desvalorizacao_total) # Garante que não seja negativa
    
    if verbose:
        print(f"\nPrevisão de desvalorização para o modelo FIPE {codigo_fipe}")
        print(f"Modelo treinado com {len(df_real)} pontos de dados históricos.")
        print(f"Valor zero km ({ano_lancamento-1}): R$ {valor_zero:,.2f}\n")
        idades_futuras = np.array(range(1, anos_para_prever + 1)).reshape(-1, 1)
        valores_previstos = model.predict(idades_futuras)

        for i, idade in enumerate(idades_futuras.flatten()):
            valor_previsto = valores_previstos[i]
            desval_acumulada = (1 - valor_previsto / valor_zero) * 100 if valor_zero > 0 else 0
            print(f"Após {idade} ano(s): Valor Previsto R$ {valor_previsto:,.2f} | Desv. Acumulada: {desval_acumulada:.2f}%")

    return desvalorizacao_total

if __name__ == "__main__":
    desvalorizacao = prever_valor_futuro_ml("095010-6", 3, verbose=True)
    if desvalorizacao is not None:
        print(f"\nDesvalorização total estimada em 3 anos: R$ {desvalorizacao:,.2f}")
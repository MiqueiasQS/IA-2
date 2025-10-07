import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime

def prever_valor_futuro_ml(codigo_fipe: str, anos_para_prever: int, arquivo_json: str = "dataset_byd_completo_custos.json"):
    try:
        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_json}' não foi encontrado.")
        return
        
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
        return

    df_real = df_modelo[df_modelo["AnoModelo"] < 32000]
    df_zero = df_modelo[df_modelo["AnoModelo"] == 32000]

    if df_real.empty or df_zero.empty:
        print("Faltam dados de histórico ou valor zero km para esse modelo.")
        return

    df_real = df_real.groupby("AnoModelo")["Valor"].mean().reset_index()

    ano_atual = 2026
    df_real["IdadeVeiculo"] = ano_atual - df_real["AnoModelo"]
    
    df_real = df_real[(df_real["IdadeVeiculo"] >= 0) & (df_real["IdadeVeiculo"] < 30)]

    X = df_real[["IdadeVeiculo"]]
    y = df_real["Valor"]

    grau_polinomio = 2
    model = make_pipeline(PolynomialFeatures(degree=grau_polinomio), LinearRegression())
    
    model.fit(X, y)

    valor_zero = df_zero["Valor"].mean()
    ano_lancamento = ano_atual + 1
    
    print(f"\nPrevisão de desvalorização para o modelo FIPE {codigo_fipe}")
    print(f"Modelo treinado com {len(df_real)} pontos de dados históricos.")
    print(f"Valor zero km ({ano_lancamento-1}): R$ {valor_zero:,.2f}\n")
    idades_futuras = np.array(range(1, anos_para_prever + 1)).reshape(-1, 1)
    
    valores_previstos = model.predict(idades_futuras)

    for i, idade in enumerate(idades_futuras.flatten()):
        valor_previsto = valores_previstos[i]
        ano_do_veiculo = ano_lancamento + idade - 1
        desval_total = (1 - valor_previsto / valor_zero) * 100
        
        print(f"Ano {ano_do_veiculo} (Idade: {idade} ano(s)): R$ {valor_previsto:,.2f}  |  Desvalorização acumulada: {desval_total:.2f}%")

if __name__ == "__main__":
    prever_valor_futuro_ml("095010-6", 3)
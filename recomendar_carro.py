import json
import pandas as pd
import numpy as np

# Importa a função de previsão de desvalorização do outro arquivo
from desvalorizacao import prever_valor_futuro_ml, gerar_imagem_desvalorizacao

# --- 1. CONFIGURAÇÕES E PREMISSAS DO MODELO ---

# Perfil do carro atual (para cálculo de economia) - ajuste para o seu carro
CARRO_ATUAL_PERFIL = {
    'consumo_km_por_litro': 12,
    'preco_gasolina_litro': 6.00
}

# --- 2. PERFIL DO USUÁRIO ---
# Estes são os inputs para o modelo. Altere com seus dados!
PERFIL_USUARIO = {
    'preco_carro_atual': 110000,
    'km_rodados_anual': 20000,
    'viagens_longas': 600,
}

def carregar_dados(filepath='dataset_byd_completo_custos.json'):
    try:
        df = pd.read_json(filepath)
        print(f"Dados carregados com sucesso de '{filepath}'.")
        
        df = df[df['CustoMedioPorKM_R$'] != 'N/A'].copy()
        df['Valor'] = df['Valor'].replace({'R\$ ': ''}, regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['CustoMedioPorKM_R$'] = pd.to_numeric(df['CustoMedioPorKM_R$'])
        df['AutonomiaTotalKM'] = pd.to_numeric(df['AutonomiaTotalKM'])
        
        return df
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{filepath}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")
        return None

def calcular_pontuacao_e_economia(df, perfil_usuario):
    """
    Calcula a pontuação de adequação e a economia anual para cada carro.
    Esta é a função principal do nosso "modelo".
    """
    scores = []
    economias = []
    
    custo_anual_atual = (perfil_usuario['km_rodados_anual'] / CARRO_ATUAL_PERFIL['consumo_km_por_litro']) * CARRO_ATUAL_PERFIL['preco_gasolina_litro']

    for index, carro in df.iterrows():
        preco_carro_byd = carro['Valor']
        orcamento = perfil_usuario['preco_carro_atual']
        std_dev = orcamento * 0.3
        score_orcamento = np.exp(-0.5 * ((preco_carro_byd - orcamento) / std_dev) ** 2)

        score_autonomia = 1.0
        if carro['AutonomiaTotalKM'] < PERFIL_USUARIO['viagens_longas']*0.5:
            score_autonomia *= 0.5
        if carro['AutonomiaTotalKM'] > PERFIL_USUARIO['viagens_longas']:
            score_autonomia *= 1.2
            
        custo_anual_byd = perfil_usuario['km_rodados_anual'] * carro['CustoMedioPorKM_R$']
        economia_anual = custo_anual_atual - custo_anual_byd
        economias.append(economia_anual)
        
        score_economia = economia_anual / 5000

        pontuacao_final = (score_orcamento * 0.4) + (score_autonomia * 0.2) + (score_economia * 0.4)
        scores.append(pontuacao_final)

    df['Pontuacao'] = scores
    df['EconomiaAnualEstimada_R$'] = economias
    return df.sort_values(by='Pontuacao', ascending=False)

def main():
    """Função principal para executar o processo de recomendação."""
    df_byd = carregar_dados()
    
    if df_byd is not None and not df_byd.empty:
        df_recomendacoes = calcular_pontuacao_e_economia(df_byd, PERFIL_USUARIO)
        
        if df_recomendacoes.empty:
            print("Não foi possível gerar recomendações com os dados disponíveis.")
            return

        melhor_opcao = df_recomendacoes.iloc[0]
        
        print("\n--- Modelo de Recomendação de Carro BYD ---")
        print("\nAnalisando seu perfil:")
        for chave, valor in PERFIL_USUARIO.items():
            print(f"  - {chave.replace('_', ' ').capitalize()}: {valor}")
        
        print("\n--- RECOMENDAÇÃO PRINCIPAL ---")
        print(f"Modelo Recomendado: {melhor_opcao['Modelo']}")
        print(f"Ano: {melhor_opcao['AnoModelo']}")
        print(f"Preço FIPE (aprox.): R$ {melhor_opcao['Valor']:,.2f}")
        print(f"Tipo: {melhor_opcao['TipoVeiculo'].capitalize()}")
        print(f"Autonomia Estimada: {melhor_opcao['AutonomiaTotalKM']} km")
        print(f"Pontuação de Adequação: {melhor_opcao['Pontuacao']:.2f}")

        print("\n--- ANÁLISE DE ECONOMIA ---")
        print(f"Custo Anual com carro atual (gasolina): R$ {(PERFIL_USUARIO['km_rodados_anual'] / CARRO_ATUAL_PERFIL['consumo_km_por_litro']) * CARRO_ATUAL_PERFIL['preco_gasolina_litro']:,.2f}")
        print(f"Custo Anual com o {melhor_opcao['ModeloBase']}: R$ {PERFIL_USUARIO['km_rodados_anual'] * melhor_opcao['CustoMedioPorKM_R$']:,.2f}")
        print("--------------------------------------------------")
        print(f">> ECONOMIA DE COMBUSTIVEL ANUAL ESTIMADA: R$ {melhor_opcao['EconomiaAnualEstimada_R$']:,.2f} <<")
        print(f">> ECONOMIA COM IMPOSTOS (IPVA) ANUAL ESTIMADA: R$ {melhor_opcao['Valor'] * 0.03:,.2f} <<")

        # --- CÁLCULO DA DESVALORIZAÇÃO E ECONOMIA LÍQUIDA ---
        print("\n--- ANÁLISE DE VALOR EM 3 ANOS (VISÃO REALISTA) ---")
        
        # Calcula a economia bruta em 3 anos (combustível + impostos)
        economia_bruta_3_anos = (melhor_opcao['EconomiaAnualEstimada_R$'] + (melhor_opcao['Valor'] * 0.03)) * 3

        # Pega o código FIPE do carro recomendado e chama o modelo de desvalorização
        codigo_fipe_rec = melhor_opcao['CodigoFipe']
        # Chama a previsão com verbose=True para imprimir os detalhes
        dados_desvalorizacao = prever_valor_futuro_ml(codigo_fipe_rec, 3, verbose=True)

        if dados_desvalorizacao:
            # Gera a imagem da análise
            nome_arquivo_imagem = f"images/analise_{melhor_opcao['ModeloBase'].replace(' ', '_')}_{codigo_fipe_rec}.png"
            gerar_imagem_desvalorizacao(dados_desvalorizacao, nome_arquivo_imagem)

            desvalorizacao_3_anos = dados_desvalorizacao['desvalorizacao_total']
            economia_liquida_3_anos = economia_bruta_3_anos - desvalorizacao_3_anos
            print(f"\nEconomia Bruta (Combustível + IPVA) em 3 anos: R$ {economia_bruta_3_anos:,.2f}")
            print(f"Desvalorização Total Estimada do Veículo em 3 anos: R$ -{desvalorizacao_3_anos:,.2f}")
            print("--------------------------------------------------")
            print(f">> BALANÇO FINANCEIRO LÍQUIDO EM 3 ANOS: R$ {economia_liquida_3_anos:,.2f} <<")
            print("--------------------------------------------------")
        else:
            print("Não foi possível calcular a desvalorização (dados insuficientes para o modelo).")
            print("--------------------------------------------------")
            print(f">> ECONOMIA BRUTA EM 3 ANOS (sem desvalorização): R$ {economia_bruta_3_anos:,.2f} <<")
            print("--------------------------------------------------")

if __name__ == '__main__':
    main()
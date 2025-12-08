import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def carregar_e_limpar_dados(caminho_arquivo):

    df = pd.read_json(caminho_arquivo)
    print("Dataset carregado com sucesso!")
    print(f"Formato inicial do dataset: {df.shape}")

    # Remove 'R$ ', troca '.' por '' e ',' por '.'
    df['Valor'] = (
        df['Valor']
        .str.replace('R$ ', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # 2. Tratar o valor '32000' na coluna 'AnoModelo'
    ano_maximo_valido = df[df['AnoModelo'] != 32000]['AnoModelo'].max()
    df['AnoModelo'] = df['AnoModelo'].replace(32000, ano_maximo_valido)
    print(f"Valor '32000' em 'AnoModelo' substituído por '{ano_maximo_valido}'.")

    # 3. Preencher valores ausentes em 'AutonomiaEletricaKM'
    df['AutonomiaEletricaKM'].fillna(0, inplace=True)

    df.info()
    return df

def analisar_estatisticas_descritivas(df):
    print("\n--- Estatísticas Descritivas ---")

    colunas_descritivas = ['Valor', 'AnoModelo', 'CapacidadeBateriaKWH', 'AutonomiaTotalKM', 'CustoMedioPorKM_R$']
    print(df[colunas_descritivas].describe().to_string())

def criar_visualizacoes(df, pasta_saida='graficos_AED'):

    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        print(f"\nPasta '{pasta_saida}' criada para salvar os gráficos.")

    sns.set_theme(style="whitegrid")

    # 1. Distribuição dos Tipos de Veículo
    plt.figure(figsize=(8, 6))
    sns.countplot(x='TipoVeiculo', data=df, palette='viridis', hue='TipoVeiculo', legend=False)
    plt.title('Contagem por Tipo de Veículo')
    plt.xlabel('Tipo de Veículo')
    plt.ylabel('Contagem')
    plt.savefig(os.path.join(pasta_saida, '01_contagem_tipo_veiculo.png'))
    plt.close()

    # 2. Distribuição de Preços (Valor)
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Valor'], kde=True, bins=20)
    plt.title('Distribuição de Preços dos Veículos')
    plt.xlabel('Valor (R$)')
    plt.ylabel('Frequência')
    plt.savefig(os.path.join(pasta_saida, '02_distribuicao_precos.png'))
    plt.close()

    # 3. Relação entre Ano do Modelo e Valor
    plt.figure(figsize=(12, 7))
    sns.scatterplot(x='AnoModelo', y='Valor', hue='TipoVeiculo', data=df, s=100, alpha=0.8)
    plt.title('Valor do Veículo vs. Ano do Modelo')
    plt.xlabel('Ano do Modelo')
    plt.ylabel('Valor (R$)')
    plt.legend(title='Tipo de Veículo')
    plt.savefig(os.path.join(pasta_saida, '03_valor_vs_ano.png'))
    plt.close()

    # 4. Custo Médio por KM por Modelo Base
    plt.figure(figsize=(14, 8))
    ordem_modelos = df.groupby('ModeloBase')['CustoMedioPorKM_R$'].mean().sort_values().index
    sns.boxplot(x='CustoMedioPorKM_R$', y='ModeloBase', data=df, orient='h', order=ordem_modelos, palette='coolwarm', hue='ModeloBase', legend=False)
    plt.title('Distribuição do Custo Médio por KM por Modelo Base')
    plt.xlabel('Custo Médio por KM (R$)')
    plt.ylabel('Modelo Base')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, '04_custo_km_por_modelo.png'))
    plt.close()

    # 5. Autonomia Total vs. Custo por KM
    plt.figure(figsize=(12, 7))
    sns.scatterplot(x='AutonomiaTotalKM', y='CustoMedioPorKM_R$', hue='TipoVeiculo', size='CapacidadeBateriaKWH', data=df, sizes=(50, 300), alpha=0.8)
    plt.title('Autonomia Total vs. Custo por KM')
    plt.xlabel('Autonomia Total (KM)')
    plt.ylabel('Custo Médio por KM (R$)')
    plt.legend(title='Legenda', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, '05_autonomia_vs_custo_km.png'))
    plt.close()

    # 6. Matriz de Correlação
    colunas_numericas = df.select_dtypes(include=np.number)
    matriz_corr = colunas_numericas.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(matriz_corr, annot=True, cmap='viridis', fmt='.2f', linewidths=.5)
    plt.title('Matriz de Correlação das Variáveis Numéricas')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, '06_matriz_correlacao.png'))
    plt.close()

    print(f"Gráficos salvos na pasta '{pasta_saida}'.")

if __name__ == "__main__":
    nome_arquivo_json = 'dataset_byd_completo_custos.json'

    if not os.path.exists(nome_arquivo_json):
        print(f"Erro: O arquivo '{nome_arquivo_json}' não foi encontrado no diretório.")
    else:
        df_byd = carregar_e_limpar_dados(nome_arquivo_json)
        analisar_estatisticas_descritivas(df_byd)

        print("\n--- Análise de Dados Categóricos ---")
        print("\nContagem por Modelo Base:")
        print(df_byd['ModeloBase'].value_counts().to_string())

        criar_visualizacoes(df_byd)

        print("\nAnálise Exploratória de Dados concluída.")
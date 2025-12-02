import google.generativeai as genai
import time
import json
import os

# --- 1. IMPORTAÇÃO DA CHAVE DE SEGURANÇA ---
try:
    from api_key import GOOGLE_API_KEY
except ImportError:
    print("⚠️  ERRO CRÍTICO: Arquivo 'api_key.py' não encontrado.")
    print("    Crie um arquivo chamado api_key.py e coloque: GOOGLE_API_KEY = 'sua_chave'")
    GOOGLE_API_KEY = None

def carregar_estoque_formatado():
    nome_arquivo = 'dataset_byd_completo_custos.json'
    
    if not os.path.exists(nome_arquivo):
        return "ERRO: O catálogo de carros (arquivo JSON) não foi encontrado."

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        texto_catalogo = "--- ESTOQUE COMPLETO (NOVOS E SEMINOVOS) ---\n"
        
        for carro in dados:
            # LÓGICA DE TRADUÇÃO DO ANO
            ano_bruto = carro.get('AnoModelo')
            if ano_bruto == 32000:
                condicao = "🌟 ZERO KM (Novo)"
            else:
                condicao = f"🔄 SEMINOVO (Ano {ano_bruto})"

            # Montagem do texto para a IA ler
            texto_catalogo += (
                f"MODELO: {carro['Modelo']}\n"
                f"   - Condição: {condicao}\n" # <--- AQUI ESTÁ A CHAVE
                f"   - Preço: {carro['Valor']}\n"
                f"   - Tipo: {carro['TipoVeiculo'].upper()}\n"
                f"   - Custo Km: R$ {carro['CustoMedioPorKM_R$']}\n"
                f"   - Autonomia: {carro['AutonomiaTotalKM']} km\n"
                "--------------------------------------------------\n"
            )
        
        return texto_catalogo

    except Exception as e:
        return f"Erro ao ler dataset: {str(e)}"

def configurar_ia():
    if not GOOGLE_API_KEY:
        return None

    genai.configure(api_key=GOOGLE_API_KEY)
    estoque_atual = carregar_estoque_formatado()

    instrucoes_sistema = f"""Você é uma VendedorAI, um sistema inteligente e um consultor de vendas experiente e carismático da concessionária BYD.
    
    SEU OBJETIVO:Conversar naturalmente com o cliente para entender o perfil dele e vender um carro do seu estoque.
    
    SEU ESTOQUE:
    {estoque_atual}
    
    REGRAS DE COMPORTAMENTO:
    1. NÃO faça um interrogatório. Faça no máximo UMA pergunta por vez.
    2. Seja breve, informal e simpático.
    3. Descubra discretamente: Nome, Uso diário (KM) e Orçamento.
    4. CÁLCULO MENTAL: Sempre calcule a economia de combustível (Gasolina vs Elétrico) e use isso como argumento forte.
    5. Se o cliente perguntar de um carro fora da lista, ofereça uma alternativa similar da BYD.
    6. Objetivo final: Convencer o cliente a agendar um "Test Drive".

    INICIO:
    Se apresente e pergunte como pode ajudar.
    """

    print(instrucoes_sistema)
    # Configuração do Modelo
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 500,
    }

    modelo_nome = "models/gemini-2.5-flash"

    model = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucoes_sistema
    )
    
    return model.start_chat(history=[])

def main():
    chat = configurar_ia()
    
    if not chat:
        print("Erro na Configuração da API Key.")
        return

    print("\n" + "="*50)
    print("CHAT COM VendedorAI BYD")
    print("(Digite 'sair' para encerrar)")
    print("="*50 + "\n")

    try:
        response = chat.send_message("O cliente entrou na loja. Cumprimente-o.")
        print(f"🤖 VendedorAI (BYD): {response.text}")
    except Exception as e:
        print(f"Erro ao conectar com a IA: {e}")

    while True:
        try:
            user_input = input("\n👤 Você: ")
            
            if user_input.lower() in ["sair", "tchau", "fim"]:
                print("\n🤖 VendedorAI (BYD): Até logo! Estamos te esperando para o café. ☕")
                break
            
            if not user_input.strip(): continue

            print("(digitando...)", end="\r")
            
            # Envia mensagem para a IA
            response = chat.send_message(user_input)
            
            print(" " * 20, end="\r") # Limpa o "(digitando...)"
            print(f"🤖 VendedorAI (BYD): {response.text}")

        except Exception as e:
            print(f"\n Erro: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
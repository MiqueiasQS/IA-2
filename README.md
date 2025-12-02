# VendedorAI - Assistente Virtual de Vendas para Concessionárias BYD

## Problema
Concessionárias de veículos enfrentam o desafio de oferecer um atendimento personalizado e eficiente para cada cliente, especialmente em um mercado competitivo. Muitos clientes têm dúvidas sobre qual carro escolher, considerando fatores como orçamento, uso diário e economia de combustível. Além disso, o processo de convencimento para agendar um test drive pode ser demorado e ineficiente.

## Abordagem
O **VendedorAI** é um assistente virtual baseado em inteligência artificial projetado para atuar como um consultor de vendas carismático e experiente. Ele utiliza um modelo generativo para interagir com os clientes de forma natural, entender suas necessidades e recomendar veículos disponíveis no estoque da concessionária. O objetivo final é convencer o cliente a agendar um test drive, destacando os benefícios dos carros elétricos da BYD.

### Funcionalidades
- Conversa natural e amigável com os clientes.
- Descoberta discreta de informações importantes: nome, uso diário do carro (em KM) e orçamento.
- Recomendação de veículos disponíveis no estoque.
- Argumentação baseada na economia de combustível entre carros elétricos e a gasolina.
- Sugestão de alternativas para carros fora do estoque.
- Convencimento do cliente para agendar um test drive.


### Componentes Principais
1. **`assistente_carro_rag.py`**: Contém a lógica principal do assistente, incluindo a configuração do modelo de IA e o fluxo de interação com o cliente.
2. **`utils.py`**: Fornece funções auxiliares, como o carregamento e formatação do estoque de carros.
3. **`estoque.json`**: Armazena os dados do estoque de veículos disponíveis na concessionária.
4. **Modelo Generativo**: Utiliza a API do Google Generative AI (modelo Gemini) para gerar respostas dinâmicas e personalizadas.

## Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior instalado.
- Uma chave de API válida para o Google Generative AI.

### Passo a Passo
1. **Clone o repositório**:
    git clone https://github.com/MiqueiasQS/IA-2
    cd IA-2

2. **Instale as dependências**: pip install -U google-generativeai

3. **Configure a chave de API do Google Generative AI**:

- Crie um arquivo api_key.py na raiz do projeto.
- Adicione a seguinte linha ao arquivo, substituindo SUA_API_KEY pela sua chave: GOOGLE_API_KEY = "SUA_API_KEY"

4. **Adicione o estoque de carros**:

- Certifique-se de que o arquivo estoque.json contém os dados do estoque no formato correto.

5. **Execute o projeto**: python assistente_carro_rag.py

6. **Interaja com o assistente**:
- O assistente irá se apresentar e começar a interação com o cliente.
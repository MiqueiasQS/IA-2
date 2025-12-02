# VendedorAI - Assistente Virtual de Vendas para Concessionárias BYD

Um assistente de vendas virtual, carismático e inteligente, desenvolvido com a API do Google Gemini para revolucionar o atendimento em concessionárias BYD.

## O Problema

O atendimento em concessionárias de veículos, especialmente em um mercado tão competitivo, exige personalização e eficiência. Clientes frequentemente chegam com dúvidas sobre o modelo ideal para suas necessidades, ponderando fatores como orçamento, rotina diária e economia. O processo para agendar um test drive, uma etapa crucial na jornada de compra, muitas vezes se torna longo e pouco eficaz.

## A Abordagem

O **VendedorAI** surge como a solução: um assistente virtual com IA, projetado para ser um consultor de vendas carismático e experiente. Utilizando um modelo generativo (Google Gemini), ele interage de forma natural, identifica as necessidades do cliente e recomenda o veículo BYD ideal disponível em estoque. O objetivo principal é claro: encantar o cliente, destacar os benefícios dos carros elétricos e agendar um test drive.

### Funcionalidades Principais

- **Conversa Natural:** Interage de forma amigável e humana com os clientes.
- **Descoberta de Necessidades:** Identifica de forma sutil informações cruciais como nome, orçamento e uso diário do veículo (KM).
- **Recomendação Inteligente:** Sugere veículos do estoque que se encaixam perfeitamente no perfil do cliente.
- **Análise de Economia:** Apresenta argumentos sólidos sobre a economia de combustível dos elétricos BYD em comparação com carros a gasolina.
- **Gestão de Estoque:** Oferece alternativas viáveis caso o carro desejado não esteja disponível.
- **Agendamento de Test Drive:** Conduz a conversa com o objetivo de agendar um test drive, aumentando as chances de conversão.

### Componentes do Projeto

- **`assistente_carro_rag.py`**: O cérebro do projeto. Contém a lógica principal do assistente, o fluxo da conversa e a integração com a IA.
- **`estoque.json`**: Um arquivo JSON que funciona como o banco de dados do estoque de carros da concessionária.
- **Modelo Generativo**: Utiliza a API do Google Generative AI (modelo Gemini) para dar vida e inteligência ao VendedorAI.

## Como Executar o Projeto

Siga os passos abaixo para colocar o VendedorAI em funcionamento.

### Pré-requisitos

- Python 3.8+ instalado.
- Uma chave de API válida para o Google Generative AI.

### Passo a Passo

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/MiqueiasQS/IA-2.git
    cd IA-2
    ```

2.  **Instale as dependências**:
    ```bash
    pip install -U google-generativeai
    ```

3. **Configure a chave de API do Google Generative AI**:

- Crie um arquivo `api_key.py` na raiz do projeto.
- Adicione a seguinte linha ao arquivo, substituindo SUA_API_KEY pela sua chave: `GOOGLE_API_KEY = "SUA_API_KEY"`

4. **Adicione o estoque de carros**:

- Certifique-se de que o arquivo estoque.json contém os dados do estoque no formato correto.

5. **Execute o projeto**: python assistente_carro_rag.py

6. **Interaja com o assistente**:
- O assistente irá se apresentar e começar a interação com o cliente.

# Como Configurar o Arquivo .env

## 1. Criar o arquivo .env

Crie um arquivo chamado `.env` na raiz do projeto (mesmo diretório onde está o `app.py`) com o seguinte conteúdo:

```bash
# Configuração da OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Configuração do Banco de Dados
DATABASE_URL=sqlite:///data/vale_refeicao.db
```

## 2. Substituir a API Key

Substitua `sk-your-openai-api-key-here` pela sua chave de API real da OpenAI.

### Como obter uma API Key:
1. Acesse https://platform.openai.com/
2. Faça login ou crie uma conta
3. Vá em "API keys" no menu lateral
4. Clique em "Create new secret key"
5. Copie a chave e cole no arquivo .env

## 3. Escolher o Modelo (Opcional)

Você pode usar um dos seguintes modelos:
- `gpt-4-turbo-preview` (recomendado - mais recente)
- `gpt-4`
- `gpt-3.5-turbo` (mais barato, mas menos capaz)

## 4. Verificar se está funcionando

Após configurar, a aplicação irá:
- Gerar código Python usando o LLM ao invés de templates
- Mostrar nos logs laterais: "🤖 Gerando código com LLM"

## 5. Se não tiver API Key

Se você não tiver uma API key da OpenAI, o sistema continuará funcionando usando templates predefinidos de código, que são seguros e eficazes para análises comuns.

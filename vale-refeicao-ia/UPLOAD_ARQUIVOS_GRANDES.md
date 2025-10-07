# 📁 Upload de Arquivos Grandes - Soluções

## ⚠️ Limitação do Cloud Run

O **Google Cloud Run** tem um limite fixo de **32MB** por requisição HTTP. Isso significa que arquivos maiores que ~30MB não podem ser uploadados diretamente pela interface web.

## 🚀 Soluções para Arquivos Grandes

### 1. **💻 Rodar Localmente (Recomendado)**

Para arquivos de até **200MB**:

```bash
# Clone o repositório
git clone https://github.com/jrbaragao/CRM-IA-VR.git
cd CRM-IA-VR/vale-refeicao-ia

# Configure a chave da OpenAI
echo "OPENAI_API_KEY=sk-sua-chave" > .env
echo "DATABASE_URL=sqlite:///./vale_refeicao.db" >> .env

# Instale as dependências
pip install -r requirements.txt

# Execute localmente
streamlit run app.py
```

**Vantagens:**
- ✅ Suporte a arquivos até 200MB
- ✅ Processamento mais rápido
- ✅ Dados ficam no seu computador
- ✅ Sem custos de nuvem

### 2. **📂 Dividir Arquivos em Partes**

Se seu arquivo é muito grande, divida-o:

#### **Excel/CSV:**
```python
import pandas as pd

# Ler arquivo grande
df = pd.read_csv('arquivo_grande.csv')

# Dividir em partes de 25MB (aproximadamente 100k linhas)
chunk_size = 100000
for i, chunk in enumerate(df.groupby(df.index // chunk_size)):
    chunk[1].to_csv(f'arquivo_parte_{i+1}.csv', index=False)
```

#### **Via PowerShell (Windows):**
```powershell
# Dividir CSV em partes (por número de linhas)
$lines = Get-Content arquivo_grande.csv
$chunkSize = 100000
$fileNumber = 1

for ($i = 0; $i -lt $lines.Count; $i += $chunkSize) {
    $end = [Math]::Min($i + $chunkSize - 1, $lines.Count - 1)
    $lines[$i..$end] | Out-File "arquivo_parte_$fileNumber.csv" -Encoding UTF8
    $fileNumber++
}
```

### 3. **☁️ Google Drive + Colab (Alternativa)**

Para análises complexas com arquivos muito grandes:

1. **Upload para Google Drive**
2. **Abra Google Colab**
3. **Clone o repositório no Colab**:
```python
!git clone https://github.com/jrbaragao/CRM-IA-VR.git
%cd CRM-IA-VR/vale-refeicao-ia

# Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Instalar dependências
!pip install -r requirements.txt

# Configurar OpenAI
import os
os.environ['OPENAI_API_KEY'] = 'sk-sua-chave'

# Importar e usar as funções
from src.agents.calculation_agent import CalculationAgent
```

### 4. **🔧 Upload Direto para Cloud Storage (Avançado)**

Para desenvolvedores que querem manter tudo na nuvem:

```bash
# 1. Upload manual para o bucket
gsutil cp arquivo_grande.csv gs://crmia-uploads-files/uploads/

# 2. Modificar código para ler diretamente do GCS
# (Requer alteração no código da aplicação)
```

## 📊 Limites por Ambiente

| Ambiente | Limite de Upload | Limite de Processamento | Recomendação |
|----------|------------------|-------------------------|--------------|
| **Cloud Run** | 30MB | 2GB RAM | Arquivos pequenos/médios |
| **Local** | 200MB | Conforme seu PC | Arquivos grandes |
| **Google Colab** | 25GB | 12GB RAM | Análises complexas |

## 🎯 Qual Escolher?

### **Arquivo até 30MB:**
- ✅ Use a versão Cloud Run (mais conveniente)

### **Arquivo 30MB - 200MB:**
- ✅ Use a versão local (melhor experiência)

### **Arquivo > 200MB:**
- ✅ Divida em partes menores
- ✅ Ou use Google Colab para análises pontuais

## 🔄 Implementação Futura

Estamos trabalhando em:
- **Upload direto para Cloud Storage** (bypass do limite HTTP)
- **Processamento em chunks** (streaming de arquivos)
- **Interface para arquivos muito grandes**

## 📞 Suporte

Para casos específicos de arquivos muito grandes ou integração empresarial, entre em contato para soluções customizadas.

---

**Dica**: Para uso regular, recomendamos a **versão local** para arquivos grandes e a **versão Cloud** para acesso rápido e compartilhamento.

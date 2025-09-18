# 🌐 Guia de Teste em Servidor Remoto - Vale Refeição IA

## 📋 Pré-requisitos do Servidor

- Ubuntu 20.04+ ou CentOS 7+
- Python 3.11+
- Acesso SSH com permissões sudo
- Mínimo 2GB RAM
- 10GB espaço em disco
- Porta 8501 liberada no firewall

## 🚀 Deploy Rápido via SSH

### 1. Conecte ao Servidor

```bash
# Windows PowerShell/CMD
ssh usuario@seu-servidor.com

# Ou com chave privada
ssh -i caminho/para/sua-chave.pem usuario@seu-servidor.com
```

### 2. Script de Instalação Automática

Crie e execute este script no servidor:

```bash
# Crie o arquivo deploy.sh
nano deploy.sh
```

Cole o seguinte conteúdo:

```bash
#!/bin/bash

echo "======================================"
echo "  Deploy Vale Refeição IA"
echo "======================================"

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt-get update -y

# Instalar Python 3.11 se necessário
echo "🐍 Verificando Python..."
if ! command -v python3.11 &> /dev/null; then
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -y
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
fi

# Instalar Git
echo "📥 Instalando Git..."
sudo apt-get install -y git

# Clonar repositório
echo "📂 Clonando repositório..."
if [ -d "vale-refeicao-ia" ]; then
    cd vale-refeicao-ia
    git pull
else
    git clone https://github.com/seu-usuario/vale-refeicao-ia.git
    cd vale-refeicao-ia
fi

# Criar ambiente virtual
echo "🔧 Criando ambiente virtual..."
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo .env
echo "⚙️ Configurando ambiente..."
if [ ! -f .env ]; then
    cat > .env << EOL
# Banco de Dados SQLite (para teste)
DATABASE_URL=sqlite:///vale_refeicao.db

# OpenAI - ADICIONE SUA CHAVE AQUI!
OPENAI_API_KEY=sk-...

# ChromaDB Local
CHROMA_PERSIST=True
CHROMA_PATH=./chroma_db

# Configurações de Vale Refeição
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
DIAS_UTEIS_MES=22

# Ambiente
ENVIRONMENT=production
DEBUG=False

# Configurações de Upload
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
EOL
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com sua chave OpenAI!"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p uploads exports chroma_db

# Configurar permissões
chmod +x venv/bin/activate
chmod 755 uploads exports chroma_db

echo "✅ Deploy concluído!"
echo "Para iniciar: ./iniciar_remoto.sh"
```

Torne o script executável e rode:

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Script de Inicialização para Servidor

Crie um script `iniciar_remoto.sh`:

```bash
nano iniciar_remoto.sh
```

Cole:

```bash
#!/bin/bash

# Ativar ambiente virtual
source venv/bin/activate

# Configurar para aceitar conexões externas
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_PORT=8501

# Iniciar aplicação
echo "🚀 Iniciando Vale Refeição IA..."
echo "📍 Acesse em: http://$(hostname -I | awk '{print $1}'):8501"
echo "Pressione Ctrl+C para parar"

streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true \
    --browser.serverAddress="$(hostname -I | awk '{print $1}')" \
    --browser.gatherUsageStats=false
```

Torne executável:

```bash
chmod +x iniciar_remoto.sh
```

### 4. Configurar Firewall

```bash
# Ubuntu/Debian com UFW
sudo ufw allow 8501/tcp
sudo ufw reload

# CentOS/RHEL com firewalld
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload

# Verificar portas abertas
sudo netstat -tlnp | grep 8501
```

## 🔧 Execução como Serviço (Systemd)

Para manter a aplicação rodando permanentemente:

### 1. Criar arquivo de serviço

```bash
sudo nano /etc/systemd/system/vale-refeicao.service
```

Cole:

```ini
[Unit]
Description=Vale Refeição IA
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vale-refeicao-ia
Environment="PATH=/home/ubuntu/vale-refeicao-ia/venv/bin"
ExecStart=/home/ubuntu/vale-refeicao-ia/venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Ativar e iniciar serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço
sudo systemctl enable vale-refeicao.service

# Iniciar serviço
sudo systemctl start vale-refeicao.service

# Verificar status
sudo systemctl status vale-refeicao.service

# Ver logs
sudo journalctl -u vale-refeicao.service -f
```

## 🐳 Opção Docker (Recomendado)

### 1. Instalar Docker no servidor

```bash
# Script de instalação do Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Deploy com Docker Compose

```bash
# No servidor, dentro da pasta do projeto
docker-compose up -d

# Verificar containers
docker ps

# Ver logs
docker-compose logs -f
```

## 🔒 Configurações de Segurança

### 1. Nginx como Proxy Reverso (Opcional)

```bash
# Instalar Nginx
sudo apt-get install -y nginx

# Criar configuração
sudo nano /etc/nginx/sites-available/vale-refeicao
```

Cole:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Ative:

```bash
sudo ln -s /etc/nginx/sites-available/vale-refeicao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com
```

## 📊 Monitoramento

### 1. Verificar uso de recursos

```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Logs da aplicação
tail -f ~/.streamlit/logs.txt
```

### 2. Script de monitoramento

Crie `monitor.sh`:

```bash
#!/bin/bash
echo "=== Status do Vale Refeição IA ==="
echo "Serviço: $(systemctl is-active vale-refeicao)"
echo "Porta 8501: $(netstat -tlnp 2>/dev/null | grep 8501 | wc -l) processo(s)"
echo "Uso de RAM: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "Uso de Disco: $(df -h / | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
```

## 🧪 Teste Rápido

### 1. Via Terminal (servidor)

```bash
# Testar se a aplicação responde
curl http://localhost:8501

# Verificar se a porta está aberta
nc -zv localhost 8501
```

### 2. Via Navegador (seu computador)

```
http://IP-DO-SERVIDOR:8501
```

## 🔄 Atualização

Para atualizar a aplicação:

```bash
cd vale-refeicao-ia
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart vale-refeicao
```

## 🆘 Troubleshooting

### Erro: "Connection refused"
```bash
# Verificar se está rodando
ps aux | grep streamlit

# Verificar firewall
sudo ufw status
```

### Erro: "Module not found"
```bash
# Reinstalar dependências
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Erro: "Permission denied"
```bash
# Corrigir permissões
sudo chown -R $USER:$USER vale-refeicao-ia/
chmod -R 755 vale-refeicao-ia/
```

## 📝 Checklist de Deploy

- [ ] Servidor com Python 3.11+
- [ ] Repositório clonado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Porta 8501 liberada
- [ ] Aplicação iniciada
- [ ] Acesso via navegador funcionando
- [ ] Serviço systemd configurado (opcional)
- [ ] Nginx + SSL configurado (opcional)

## 🎯 Comandos Úteis

```bash
# Iniciar aplicação
./iniciar_remoto.sh

# Parar aplicação
sudo systemctl stop vale-refeicao

# Reiniciar aplicação
sudo systemctl restart vale-refeicao

# Ver logs em tempo real
sudo journalctl -u vale-refeicao -f

# Status do serviço
sudo systemctl status vale-refeicao
```

Pronto! Sua aplicação está rodando no servidor remoto! 🚀


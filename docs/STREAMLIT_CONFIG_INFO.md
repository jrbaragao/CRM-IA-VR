# Configurações Válidas do Streamlit (v1.29.0)

## ⚠️ Configurações DEPRECIADAS (não use):
- `runner.installTracer` - Removida
- `runner.fixMatplotlib` - Removida
- `runner.fastReruns` - Removida
- `server.enableWebsocketCompression` - Removida

## ✅ Configurações VÁLIDAS e Recomendadas:

### [server]
- `port` - Porta do servidor (padrão: 8501)
- `address` - Endereço do servidor (padrão: localhost)
- `headless` - Modo headless para servidores (padrão: false)
- `enableCORS` - Habilitar CORS (padrão: true)
- `enableXsrfProtection` - Proteção XSRF (padrão: true)
- `maxUploadSize` - Tamanho máximo de upload em MB (padrão: 200)
- `maxMessageSize` - Tamanho máximo de mensagem em MB (padrão: 200)

### [browser]
- `gatherUsageStats` - Coletar estatísticas (padrão: true)
- `serverAddress` - Endereço do servidor para o browser
- `serverPort` - Porta do servidor para o browser

### [runner]
- `magicEnabled` - Habilitar comandos mágicos (padrão: true)

### [client]
- `showErrorDetails` - Mostrar detalhes de erros (padrão: true)
- `toolbarMode` - Modo da toolbar ("auto", "viewer", "minimal", "developer")

### [theme]
- `primaryColor` - Cor primária
- `backgroundColor` - Cor de fundo
- `secondaryBackgroundColor` - Cor de fundo secundária
- `textColor` - Cor do texto
- `font` - Fonte ("sans serif", "serif", "monospace")

## 📝 Dica para Cloud Run:
No Cloud Run, é melhor passar configurações via linha de comando do que usar config.toml:
```dockerfile
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
``` 
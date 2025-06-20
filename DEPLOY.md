# Guia de Deploy

Este documento contém instruções para fazer deploy da aplicação Fox Control em diferentes plataformas.

## 🚀 Railway (Recomendado)

### Pré-requisitos
- Conta no GitHub
- Conta no Railway (railway.app)
- Repositório no GitHub com o código

### Passos para Deploy

1. **Conectar GitHub ao Railway**
   - Acesse railway.app
   - Faça login com GitHub
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"

2. **Configurar Variáveis de Ambiente**
   ```
   DB_HOST=seu-host-postgresql
   DB_PORT=5432
   DB_USER=seu-usuario
   DB_PASSWORD=sua-senha
   DB_NAME=seu-banco
   ```

3. **Deploy Automático**
   - Railway detecta automaticamente o requirements.txt
   - Deploy acontece automaticamente a cada push

### Custo Estimado
- **Starter**: $5/mês
- **Pro**: $20/mês

## 🌐 Render

### Passos para Deploy

1. **Criar Web Service**
   - Acesse render.com
   - Clique em "New Web Service"
   - Conecte seu repositório GitHub

2. **Configurações**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Variáveis de Ambiente**
   - Adicione as mesmas variáveis do Railway

### Custo Estimado
- **Free**: $0 (limitado)
- **Starter**: $7/mês

## ☁️ Streamlit Community Cloud

### Pré-requisitos
- Repositório público no GitHub
- Conta no Streamlit

### Passos para Deploy

1. **Acessar Streamlit Cloud**
   - Vá para share.streamlit.io
   - Faça login com GitHub

2. **Deploy**
   - Clique em "New app"
   - Selecione seu repositório
   - Arquivo principal: `app.py`

3. **Configurar Secrets**
   - Vá em Settings > Secrets
   - Adicione suas credenciais do banco:
   ```toml
   [database]
   host = "seu-host"
   port = 5432
   user = "seu-usuario"
   password = "sua-senha"
   database = "seu-banco"
   ```

### Custo
- **Gratuito** para repositórios públicos

## 🐳 Docker (Opcional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build e Run
```bash
docker build -t fox-control .
docker run -p 8501:8501 fox-control
```

## 🔧 Configurações de Produção

### Streamlit Config
Crie `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Otimizações
- Use `@st.cache_data` para cache de dados
- Implemente connection pooling para PostgreSQL
- Configure logs para monitoramento

## 📊 Monitoramento

### Métricas Importantes
- Tempo de resposta da aplicação
- Uso de memória
- Conexões com banco de dados
- Erros de aplicação

### Ferramentas Recomendadas
- **Railway**: Métricas integradas
- **Render**: Logs e métricas básicas
- **Streamlit Cloud**: Logs básicos

## 🔒 Segurança

### Boas Práticas
- Nunca commite credenciais no código
- Use variáveis de ambiente
- Configure HTTPS (automático na maioria das plataformas)
- Implemente rate limiting se necessário

### Backup
- Configure backup automático do PostgreSQL
- Mantenha backup do código no GitHub
- Documente processo de recuperação

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de Conexão com Banco**
   - Verifique variáveis de ambiente
   - Confirme se o banco está acessível
   - Teste conexão localmente

2. **Aplicação Lenta**
   - Otimize queries do banco
   - Use cache do Streamlit
   - Considere upgrade do plano

3. **Deploy Falha**
   - Verifique requirements.txt
   - Confirme versão do Python
   - Analise logs de build

### Logs Úteis
```bash
# Railway
railway logs

# Render
# Acesse via dashboard

# Streamlit Cloud
# Acesse via interface web
```

## 📞 Suporte

Para problemas específicos de deploy:
- **Railway**: Documentação oficial + Discord
- **Render**: Suporte via ticket
- **Streamlit**: Fórum da comunidade

---

**Recomendação**: Para produção, use Railway pela facilidade de configuração e custo-benefício.


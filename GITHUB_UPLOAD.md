# 🚀 Instruções para Upload no GitHub

## Passo a Passo Completo

### 1. 📁 Baixar o Projeto
Primeiro, você precisa baixar o projeto do sandbox para sua máquina local:

```bash
# O projeto está localizado em:
/home/ubuntu/fox-control-agendamento/

# Estrutura do projeto:
fox-control-agendamento/
├── app.py                 # Aplicação principal
├── config.py             # Configurações
├── requirements.txt      # Dependências
├── README.md            # Documentação
├── DEPLOY.md           # Guia de deploy
├── LICENSE             # Licença MIT
├── .gitignore          # Arquivos ignorados
└── .git/               # Repositório Git
```

### 2. 🌐 Criar Repositório no GitHub

1. **Acesse GitHub.com**
   - Faça login na sua conta
   - Clique no botão "+" no canto superior direito
   - Selecione "New repository"

2. **Configurar Repositório**
   - **Repository name**: `fox-control-agendamento`
   - **Description**: `Sistema de gestão logística para transporte de grãos com agendamento`
   - **Visibility**: Escolha Public ou Private
   - **NÃO** marque "Add a README file" (já temos um)
   - **NÃO** marque "Add .gitignore" (já temos um)
   - **NÃO** marque "Choose a license" (já temos uma)

3. **Criar Repositório**
   - Clique em "Create repository"

### 3. 📤 Upload do Projeto

Após criar o repositório, você verá uma página com instruções. Use a opção **"push an existing repository from the command line"**:

```bash
# Navegar para o diretório do projeto
cd fox-control-agendamento

# Adicionar o repositório remoto (substitua SEU-USUARIO pelo seu username)
git remote add origin https://github.com/SEU-USUARIO/fox-control-agendamento.git

# Fazer push do código
git push -u origin main
```

### 4. ✅ Verificar Upload

Após o push, verifique se todos os arquivos foram enviados:
- ✅ app.py
- ✅ config.py  
- ✅ requirements.txt
- ✅ README.md
- ✅ DEPLOY.md
- ✅ LICENSE
- ✅ .gitignore

### 5. 🔧 Configurar Repositório

#### Adicionar Topics (Tags)
No GitHub, vá em Settings > General > Topics e adicione:
- `streamlit`
- `python`
- `postgresql`
- `logistics`
- `agronegocio`
- `dashboard`
- `fox-partners`

#### Configurar Branch Protection (Opcional)
Para projetos em equipe:
- Settings > Branches
- Add rule para branch `main`
- Require pull request reviews

### 6. 🚀 Deploy Automático

#### Opção 1: Railway (Recomendado)
1. Acesse [railway.app](https://railway.app)
2. Login com GitHub
3. "New Project" > "Deploy from GitHub repo"
4. Selecione `fox-control-agendamento`
5. Configure variáveis de ambiente:
   ```
   DB_HOST=24.199.75.66
   DB_PORT=5432
   DB_USER=myuser
   DB_PASSWORD=mypassword
   DB_NAME=mydb
   ```

#### Opção 2: Streamlit Community Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Login com GitHub
3. "New app"
4. Repository: `seu-usuario/fox-control-agendamento`
5. Main file path: `app.py`
6. Configure secrets em Advanced settings

### 7. 📝 Atualizar README (Opcional)

Após o upload, você pode editar o README.md diretamente no GitHub para:
- Adicionar link do deploy
- Incluir screenshots
- Atualizar informações específicas

### 8. 🔄 Workflow de Desenvolvimento

Para futuras atualizações:

```bash
# Fazer alterações no código
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

### 9. 🎯 Próximos Passos

Após o upload bem-sucedido:

1. **Testar Deploy**
   - Verificar se a aplicação funciona online
   - Testar conexão com banco de dados

2. **Documentar URL**
   - Adicionar link do deploy no README
   - Compartilhar com a equipe

3. **Configurar Monitoramento**
   - Verificar logs da aplicação
   - Configurar alertas se necessário

4. **Backup**
   - O código já está seguro no GitHub
   - Considerar backup do banco de dados

## 🆘 Troubleshooting

### Problema: "Permission denied"
```bash
# Configurar autenticação SSH ou usar token pessoal
git remote set-url origin https://TOKEN@github.com/SEU-USUARIO/fox-control-agendamento.git
```

### Problema: "Repository not found"
- Verificar se o nome do repositório está correto
- Verificar se você tem permissão de acesso

### Problema: "Large files"
- Verificar se não há arquivos grandes (>100MB)
- Usar Git LFS se necessário

## 📞 Suporte

Se encontrar problemas:
1. Verificar documentação do GitHub
2. Consultar logs de erro
3. Testar comandos Git localmente
4. Verificar permissões do repositório

---

**Sucesso!** 🎉 Seu projeto Fox Control estará disponível no GitHub e pronto para deploy!


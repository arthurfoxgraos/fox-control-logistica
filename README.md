# Fox Control - Sistema de Agendamento de Cargas

Sistema de gestão logística para transporte de grãos com funcionalidades de agendamento, ordenação e análise de custos de frete.

## 🚛 Funcionalidades

### 📊 Dashboard Principal
- **Métricas em tempo real**: Total de sacas, viagens, caminhões necessários
- **Análise financeira**: Receita total, frete total, frete médio por saca
- **Conexão com PostgreSQL**: Dados atualizados automaticamente

### 📅 Sistema de Agendamento
- **Agendamento de cargas** por data específica
- **Reagendamento** de cargas individuais
- **Filtros por período** (data início/fim)
- **Timeline visual** das cargas agendadas

### 🔄 Ordenação e Filtros
- **Ordenação por**: Data, Prioridade, Distância, Sacas, Margem de Lucro, Frete por Saca
- **Filtros múltiplos**: Grão, Comprador, Prioridade, Período
- **Sistema de prioridades** baseado em margem de lucro

### 💰 Análise de Custos
- **Frete por saca**: Cálculo automático e análise comparativa
- **Margem de lucro**: Análise por operação e comprador
- **Eficiência de rotas**: Score de otimização automático

### 📈 Analytics Avançados
- **Gráficos interativos**: Distribuição de frete, timeline de cargas
- **Análise de eficiência**: Frete vs distância, viagens por data
- **Otimização de rotas**: Sugestões baseadas em algoritmos

### ⚙️ Simulador de Cenários
- **Simulação de parâmetros**: Capacidade, velocidade, horas de trabalho
- **Comparação de cenários**: Atual vs simulado
- **Análise de impacto**: Viagens, caminhões, custos

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Streamlit**: Interface web interativa
- **PostgreSQL**: Banco de dados
- **Plotly**: Gráficos interativos
- **Pandas**: Manipulação de dados
- **psycopg2**: Conexão com PostgreSQL

## 📋 Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL com dados da tabela `provisioningsv2_best_scenario_distance`
- Conexão de internet para instalação de dependências

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/fox-control-agendamento.git
cd fox-control-agendamento
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o banco de dados
Edite o arquivo `config.py` com suas credenciais do PostgreSQL:
```python
DB_CONFIG = {
    'host': 'seu-host',
    'port': 5432,
    'user': 'seu-usuario',
    'password': 'sua-senha',
    'database': 'seu-banco'
}
```

### 4. Execute a aplicação
```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📊 Estrutura do Banco de Dados

O sistema espera uma tabela `provisioningsv2_best_scenario_distance` com as seguintes colunas:

- `id`: Identificador único
- `grain`: Tipo de grão
- `amount_allocated`: Quantidade de sacas
- `distance`: Distância em km
- `buyer`: Comprador
- `seller`: Vendedor
- `revenue`: Receita
- `cost`: Custo
- `freight`: Frete
- `profit_total`: Lucro total

## 🔧 Configuração

### Parâmetros do Sistema
- **Capacidade do Caminhão**: 900 sacas (configurável)
- **Velocidade Média**: 60 km/h (configurável)
- **Horas de Trabalho**: 10h/dia (configurável)
- **Tempo Carga/Descarga**: 2h por viagem (configurável)

### Cache de Dados
O sistema utiliza `@st.cache_data` para otimizar performance:
- Dados carregados apenas uma vez por sessão
- Conversão automática de tipos para compatibilidade

## 📱 Interface

### Tabs Principais
1. **📋 Agendamento**: Lista de cargas com reagendamento
2. **📈 Analytics**: Gráficos e análises de frete
3. **🗺️ Rotas**: Otimização e timeline de cargas
4. **⚙️ Simulador**: Cenários e comparações

### Métricas Principais
- Total de Sacas
- Total de Viagens
- Caminhões Necessários
- Receita Total
- Frete Total
- Frete Médio por Saca

## 🎯 Casos de Uso

### Gestão Logística
- Planejamento de frota de caminhões
- Otimização de rotas por distância
- Controle de custos de transporte

### Análise Financeira
- Comparação de frete por saca entre compradores
- Análise de margem de lucro por operação
- Projeção de custos logísticos

### Agendamento Operacional
- Cronograma de cargas por data
- Reagendamento de operações
- Priorização baseada em rentabilidade

## 🔄 Deploy em Produção

### Opções Recomendadas

1. **Railway** (Recomendado)
   - Custo: ~$5-10/mês
   - Deploy automático via GitHub
   - PostgreSQL integrado

2. **Render**
   - Custo: $7-25/mês
   - SSL automático
   - Domínio customizado

3. **Streamlit Community Cloud**
   - Gratuito
   - Ideal para demos
   - Limitado a repositórios públicos

### Variáveis de Ambiente
```bash
DB_HOST=seu-host
DB_PORT=5432
DB_USER=seu-usuario
DB_PASSWORD=sua-senha
DB_NAME=seu-banco
```

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Notificações automáticas de agendamento
- [ ] Integração com APIs de rastreamento
- [ ] Relatórios em PDF
- [ ] Dashboard mobile responsivo
- [ ] Integração com WhatsApp/Telegram

### Melhorias Técnicas
- [ ] Autenticação de usuários
- [ ] Logs de auditoria
- [ ] Backup automático
- [ ] Monitoramento de performance

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- **Email**: suporte@foxcontrol.com.br
- **WhatsApp**: (11) 99999-9999
- **Issues**: Use o sistema de issues do GitHub

## 🏢 Fox Partners

Desenvolvido por **Fox Partners** - Soluções tecnológicas para o agronegócio.

---

**Fox Control** - Transformando a gestão logística do agronegócio brasileiro 🌾


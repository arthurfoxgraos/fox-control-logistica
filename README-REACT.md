# Fox Control - Versão React

## 🚀 Sistema de Gestão Logística Modernizado

Esta é a versão **React** do Fox Control, uma aplicação web moderna para gestão de agendamento de cargas e transporte de grãos.

### 🎯 **Principais Funcionalidades**

- **📋 Agendamento com Edição Inline**: Edite datas e número de caminhões diretamente na tabela
- **🔍 Filtros Avançados**: Filtragem por período, grão, vendedor, comprador e ordenação
- **📊 Analytics Interativos**: Gráficos de barras, pizza e linha com dados em tempo real
- **🗺️ Visualização de Rotas**: Mapa interativo com filtro de distância e modo full screen
- **⚙️ Simulador de Cenários**: Teste diferentes parâmetros operacionais
- **🎨 Interface Moderna**: Design minimalista com cores preto e prata

### 🛠️ **Tecnologias Utilizadas**

- **React 18** - Framework frontend moderno
- **Vite** - Build tool rápido e eficiente
- **Tailwind CSS** - Estilização utilitária
- **shadcn/ui** - Componentes UI profissionais
- **Recharts** - Gráficos interativos
- **Lucide React** - Ícones modernos
- **date-fns** - Manipulação de datas

### 🚀 **Como Executar**

#### **Desenvolvimento:**
```bash
# Instalar dependências
pnpm install

# Executar em modo desenvolvimento
pnpm run dev

# Acessar: http://localhost:5173
```

#### **Produção:**
```bash
# Gerar build de produção
pnpm run build

# Servir arquivos estáticos
pnpm run preview
```

### 📁 **Estrutura do Projeto**

```
src/
├── components/           # Componentes React
│   ├── FiltrosGlobais.jsx   # Filtros e ordenação
│   ├── AgendamentoTab.jsx   # Tabela editável
│   ├── AnalyticsTab.jsx     # Gráficos e métricas
│   ├── RotasTab.jsx         # Otimização de rotas
│   ├── MapaTab.jsx          # Visualização em mapa
│   └── SimuladorTab.jsx     # Simulador de cenários
├── App.jsx              # Componente principal
└── main.jsx            # Ponto de entrada
```

### 🎨 **Design System**

- **Cores**: Esquema preto e prata (seguindo preferências)
- **Tipografia**: Inter (moderna e legível)
- **Componentes**: shadcn/ui (consistência e qualidade)
- **Layout**: Responsivo e mobile-first
- **Filosofia**: Minimalismo inspirado em Steve Jobs

### 📊 **Funcionalidades Detalhadas**

#### **Edição Inline**
- ✅ Clique para editar datas e caminhões
- ✅ Salvamento automático
- ✅ Feedback visual de confirmação
- ✅ Controle de estado robusto (sem loops)

#### **Filtros Inteligentes**
- ✅ Filtros por período, grão, vendedor, comprador
- ✅ Botões "Todos" funcionais
- ✅ Limpeza completa de filtros
- ✅ Ordenação customizável

#### **Analytics Avançados**
- ✅ Distribuição de sacas por grão
- ✅ Receita por tipo de grão
- ✅ Viagens necessárias por período
- ✅ Caminhões necessários por período

#### **Mapa Interativo**
- ✅ Filtro de distância com slider
- ✅ Modo full screen
- ✅ Estatísticas em tempo real
- ✅ Top 5 maiores volumes e distâncias

#### **Simulador de Cenários**
- ✅ Parâmetros ajustáveis (capacidade, velocidade, horas)
- ✅ Comparação atual vs simulado
- ✅ Métricas de impacto
- ✅ Interpretação automática dos resultados

### 🔄 **Migração do Streamlit**

Esta versão React substitui completamente a interface Streamlit, oferecendo:

- **Performance Superior**: Carregamento mais rápido
- **UX Moderna**: Interface mais fluida e responsiva
- **Manutenibilidade**: Código mais organizado e escalável
- **Customização**: Maior flexibilidade de design
- **Mobile-First**: Experiência otimizada para dispositivos móveis

### 📈 **Próximos Passos**

1. **Integração com Backend**: Conectar com APIs reais
2. **Autenticação**: Sistema de login e permissões
3. **Notificações**: Alertas em tempo real
4. **PWA**: Transformar em Progressive Web App
5. **Testes**: Implementar testes automatizados

### 🎯 **Experiência do Usuário**

- **Navegação Intuitiva**: Tabs organizadas por funcionalidade
- **Feedback Visual**: Confirmações e estados de loading
- **Responsividade**: Funciona em desktop, tablet e mobile
- **Acessibilidade**: Componentes acessíveis por padrão
- **Performance**: Otimizado para carregamento rápido

---

## 🚛 **Fox Control React - Gestão Logística do Futuro**

*Desenvolvido com foco na experiência do usuário e performance moderna.*


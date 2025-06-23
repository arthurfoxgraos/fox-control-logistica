import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Truck, Calendar, BarChart3, Map, Settings, Filter } from 'lucide-react'
import AgendamentoTab from './components/AgendamentoTab'
import AnalyticsTab from './components/AnalyticsTab'
import RotasTab from './components/RotasTab'
import MapaTab from './components/MapaTab'
import SimuladorTab from './components/SimuladorTab'
import FiltrosGlobais from './components/FiltrosGlobais'
import './App.css'

function App() {
  const [dados, setDados] = useState([])
  const [dadosFiltrados, setDadosFiltrados] = useState([])
  const [filtros, setFiltros] = useState({
    dataInicio: new Date(),
    dataFim: new Date(2025, 7, 7), // 7 de agosto de 2025
    graos: [],
    vendedores: [],
    compradores: [],
    ordenacao: 'data_agendamento',
    ordemCrescente: true
  })
  const [loading, setLoading] = useState(true)

  // Simular carregamento de dados (substituir por API real)
  useEffect(() => {
    const carregarDados = async () => {
      setLoading(true)
      try {
        // Simular dados do banco
        const dadosSimulados = Array.from({ length: 152 }, (_, i) => ({
          id: i + 1,
          data_agendamento: new Date(2025, 5, 20 + (i % 48)), // Distribuir ao longo de ~48 dias
          buyer: `Comprador ${String.fromCharCode(65 + (i % 26))} Ltda`,
          seller: `Vendedor ${String.fromCharCode(65 + (i % 20))} Farm`,
          grain: ['Soja', 'Milho', 'Trigo', 'Arroz'][i % 4],
          amount_allocated: 500 + (i * 50) % 2000,
          distance: 50 + (i * 10) % 500,
          viagens_necessarias: Math.ceil((500 + (i * 50) % 2000) / 900),
          caminhoes_necessarios: Math.ceil(Math.ceil((500 + (i * 50) % 2000) / 900) / 2),
          dias_operacao: Math.ceil(Math.ceil((500 + (i * 50) % 2000) / 900) / (Math.ceil(Math.ceil((500 + (i * 50) % 2000) / 900) / 2) * 2)),
          frete_por_saca: 2.5 + (i % 10) * 0.5,
          margem_lucro: 5 + (i % 20),
          ajuste_manual: i % 10 === 0,
          status: 'Agendado'
        }))
        
        setDados(dadosSimulados)
        setDadosFiltrados(dadosSimulados)
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
      } finally {
        setLoading(false)
      }
    }

    carregarDados()
  }, [])

  // Aplicar filtros
  useEffect(() => {
    let resultado = [...dados]

    // Filtro por data
    resultado = resultado.filter(item => {
      const dataItem = new Date(item.data_agendamento)
      return dataItem >= filtros.dataInicio && dataItem <= filtros.dataFim
    })

    // Filtro por grãos
    if (filtros.graos.length > 0) {
      resultado = resultado.filter(item => filtros.graos.includes(item.grain))
    }

    // Filtro por vendedores
    if (filtros.vendedores.length > 0) {
      resultado = resultado.filter(item => filtros.vendedores.includes(item.seller))
    }

    // Filtro por compradores
    if (filtros.compradores.length > 0) {
      resultado = resultado.filter(item => filtros.compradores.includes(item.buyer))
    }

    // Ordenação
    resultado.sort((a, b) => {
      const valorA = a[filtros.ordenacao]
      const valorB = b[filtros.ordenacao]
      
      if (filtros.ordemCrescente) {
        return valorA > valorB ? 1 : -1
      } else {
        return valorA < valorB ? 1 : -1
      }
    })

    setDadosFiltrados(resultado)
  }, [dados, filtros])

  // Calcular métricas
  const metricas = {
    totalCargas: dadosFiltrados.length,
    totalSacas: dadosFiltrados.reduce((sum, item) => sum + item.amount_allocated, 0),
    totalCaminhoes: dadosFiltrados.reduce((sum, item) => sum + item.caminhoes_necessarios, 0),
    receitaTotal: dadosFiltrados.reduce((sum, item) => sum + (item.amount_allocated * item.frete_por_saca * 1.2), 0),
    freteTotal: dadosFiltrados.reduce((sum, item) => sum + (item.amount_allocated * item.frete_por_saca), 0),
    ajustesManuais: dadosFiltrados.filter(item => item.ajuste_manual).length
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Truck className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
          <h2 className="text-xl font-semibold mb-2">Carregando Fox Control...</h2>
          <p className="text-muted-foreground">Conectando ao sistema de agendamento</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Truck className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">Fox Control</h1>
                <p className="text-sm text-muted-foreground">Sistema de gestão logística para transporte de grãos</p>
              </div>
            </div>
            <Badge variant="secondary" className="text-sm">
              {metricas.totalCargas} cargas ativas
            </Badge>
          </div>
        </div>
      </header>

      {/* Filtros Globais */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <FiltrosGlobais 
            dados={dados}
            filtros={filtros}
            onFiltrosChange={setFiltros}
          />
        </div>
      </div>

      {/* Métricas */}
      <div className="border-b bg-muted/30">
        <div className="container mx-auto px-4 py-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{metricas.totalCargas.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total de Cargas</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{metricas.totalSacas.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total de Sacas</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{metricas.totalCaminhoes.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Caminhões Necessários</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">R$ {metricas.receitaTotal.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Receita Total</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">R$ {metricas.freteTotal.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Frete Total</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{metricas.ajustesManuais}</div>
                <p className="text-xs text-muted-foreground">Ajustes Manuais</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="agendamento" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="agendamento" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Agendamento
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="rotas" className="flex items-center gap-2">
              <Map className="h-4 w-4" />
              Rotas
            </TabsTrigger>
            <TabsTrigger value="mapa" className="flex items-center gap-2">
              <Map className="h-4 w-4" />
              Mapa
            </TabsTrigger>
            <TabsTrigger value="simulador" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Simulador
            </TabsTrigger>
          </TabsList>

          <TabsContent value="agendamento" className="mt-6">
            <AgendamentoTab dados={dadosFiltrados} onDadosChange={setDados} />
          </TabsContent>

          <TabsContent value="analytics" className="mt-6">
            <AnalyticsTab dados={dadosFiltrados} />
          </TabsContent>

          <TabsContent value="rotas" className="mt-6">
            <RotasTab dados={dadosFiltrados} />
          </TabsContent>

          <TabsContent value="mapa" className="mt-6">
            <MapaTab dados={dadosFiltrados} />
          </TabsContent>

          <TabsContent value="simulador" className="mt-6">
            <SimuladorTab dados={dadosFiltrados} />
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="border-t bg-card mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p><strong>Fox Control</strong> - Sistema de gestão logística com persistência em banco para o agronegócio | Dados atualizados em tempo real</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App


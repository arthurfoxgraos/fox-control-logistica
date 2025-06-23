import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Settings, Calculator, TrendingUp, TrendingDown } from 'lucide-react'

export default function SimuladorTab({ dados }) {
  const [parametros, setParametros] = useState({
    capacidadeCaminhao: 900,
    velocidadeMedia: 60,
    horasTrabalho: 12,
    tempoCargaDescarga: 2.0
  })
  
  const [simulacaoAtiva, setSimulacaoAtiva] = useState(false)
  const [resultados, setResultados] = useState(null)

  const handleParametroChange = (campo, valor) => {
    setParametros(prev => ({
      ...prev,
      [campo]: Array.isArray(valor) ? valor[0] : valor
    }))
  }

  const executarSimulacao = () => {
    // Calcular simulação para cada carga
    const resultadosSimulacao = dados.map(item => {
      const viagens = Math.ceil(item.amount_allocated / parametros.capacidadeCaminhao)
      const tempoViagem = (item.distance * 2 / parametros.velocidadeMedia) + parametros.tempoCargaDescarga
      const viagensPorDia = Math.max(1, Math.floor(parametros.horasTrabalho / tempoViagem))
      const caminhoes = Math.ceil(viagens / viagensPorDia)
      const dias = Math.ceil(viagens / (caminhoes * viagensPorDia))
      
      return {
        ...item,
        viagens_sim: viagens,
        caminhoes_sim: caminhoes,
        dias_sim: dias,
        frete_sim: (item.amount_allocated * (item.distance * 0.15)) / item.amount_allocated
      }
    })

    // Calcular totais
    const totais = {
      viagensAtual: dados.reduce((sum, item) => sum + item.viagens_necessarias, 0),
      viagensSimulado: resultadosSimulacao.reduce((sum, item) => sum + item.viagens_sim, 0),
      caminhaoAtual: dados.reduce((sum, item) => sum + item.caminhoes_necessarios, 0),
      caminhaoSimulado: resultadosSimulacao.reduce((sum, item) => sum + item.caminhoes_sim, 0),
      diasAtual: dados.reduce((sum, item) => sum + item.dias_operacao, 0) / dados.length,
      diasSimulado: resultadosSimulacao.reduce((sum, item) => sum + item.dias_sim, 0) / resultadosSimulacao.length,
      freteAtual: dados.reduce((sum, item) => sum + item.frete_por_saca, 0) / dados.length,
      freteSimulado: resultadosSimulacao.reduce((sum, item) => sum + item.frete_sim, 0) / resultadosSimulacao.length
    }

    setResultados({
      dados: resultadosSimulacao,
      totais
    })
    setSimulacaoAtiva(true)
  }

  const calcularDelta = (atual, simulado) => {
    return ((simulado - atual) / atual * 100).toFixed(1)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Simulador de Cenários de Frete
          </CardTitle>
          <CardDescription>
            Simule diferentes cenários alterando os parâmetros operacionais
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Capacidade do Caminhão */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Capacidade do Caminhão (sacas)</Label>
              <div className="space-y-2">
                <Slider
                  value={[parametros.capacidadeCaminhao]}
                  onValueChange={(value) => handleParametroChange('capacidadeCaminhao', value)}
                  max={1200}
                  min={600}
                  step={50}
                  className="w-full"
                />
                <div className="text-center text-sm text-muted-foreground">
                  {parametros.capacidadeCaminhao} sacas
                </div>
              </div>
            </div>

            {/* Velocidade Média */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Velocidade Média (km/h)</Label>
              <div className="space-y-2">
                <Slider
                  value={[parametros.velocidadeMedia]}
                  onValueChange={(value) => handleParametroChange('velocidadeMedia', value)}
                  max={80}
                  min={40}
                  step={5}
                  className="w-full"
                />
                <div className="text-center text-sm text-muted-foreground">
                  {parametros.velocidadeMedia} km/h
                </div>
              </div>
            </div>

            {/* Horas de Trabalho */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Horas de Trabalho/Dia</Label>
              <div className="space-y-2">
                <Slider
                  value={[parametros.horasTrabalho]}
                  onValueChange={(value) => handleParametroChange('horasTrabalho', value)}
                  max={16}
                  min={8}
                  step={1}
                  className="w-full"
                />
                <div className="text-center text-sm text-muted-foreground">
                  {parametros.horasTrabalho} horas
                </div>
              </div>
            </div>

            {/* Tempo Carga/Descarga */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Tempo Carga/Descarga (horas)</Label>
              <div className="space-y-2">
                <Slider
                  value={[parametros.tempoCargaDescarga]}
                  onValueChange={(value) => handleParametroChange('tempoCargaDescarga', value)}
                  max={4}
                  min={1}
                  step={0.5}
                  className="w-full"
                />
                <div className="text-center text-sm text-muted-foreground">
                  {parametros.tempoCargaDescarga} horas
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 text-center">
            <Button onClick={executarSimulacao} className="flex items-center gap-2">
              <Calculator className="h-4 w-4" />
              🔄 Simular Novo Cenário
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Resultados da Simulação */}
      {simulacaoAtiva && resultados && (
        <Card>
          <CardHeader>
            <CardTitle>📊 Comparação: Atual vs Simulado</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Viagens Totais */}
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-primary">
                    {resultados.totais.viagensSimulado.toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">Viagens Totais</p>
                  <div className="flex items-center gap-1 mt-1">
                    {parseFloat(calcularDelta(resultados.totais.viagensAtual, resultados.totais.viagensSimulado)) > 0 ? (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    )}
                    <span className={`text-xs ${parseFloat(calcularDelta(resultados.totais.viagensAtual, resultados.totais.viagensSimulado)) > 0 ? 'text-red-500' : 'text-green-500'}`}>
                      {calcularDelta(resultados.totais.viagensAtual, resultados.totais.viagensSimulado)}%
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Caminhões Totais */}
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-primary">
                    {resultados.totais.caminhaoSimulado.toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">Caminhões Totais</p>
                  <div className="flex items-center gap-1 mt-1">
                    {parseFloat(calcularDelta(resultados.totais.caminhaoAtual, resultados.totais.caminhaoSimulado)) > 0 ? (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    )}
                    <span className={`text-xs ${parseFloat(calcularDelta(resultados.totais.caminhaoAtual, resultados.totais.caminhaoSimulado)) > 0 ? 'text-red-500' : 'text-green-500'}`}>
                      {calcularDelta(resultados.totais.caminhaoAtual, resultados.totais.caminhaoSimulado)}%
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Dias Médios */}
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-primary">
                    {resultados.totais.diasSimulado.toFixed(1)}
                  </div>
                  <p className="text-xs text-muted-foreground">Dias Médios</p>
                  <div className="flex items-center gap-1 mt-1">
                    {parseFloat(calcularDelta(resultados.totais.diasAtual, resultados.totais.diasSimulado)) > 0 ? (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    )}
                    <span className={`text-xs ${parseFloat(calcularDelta(resultados.totais.diasAtual, resultados.totais.diasSimulado)) > 0 ? 'text-red-500' : 'text-green-500'}`}>
                      {calcularDelta(resultados.totais.diasAtual, resultados.totais.diasSimulado)}%
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Frete Médio */}
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-primary">
                    R$ {resultados.totais.freteSimulado.toFixed(2)}
                  </div>
                  <p className="text-xs text-muted-foreground">Frete Médio/Saca</p>
                  <div className="flex items-center gap-1 mt-1">
                    {parseFloat(calcularDelta(resultados.totais.freteAtual, resultados.totais.freteSimulado)) > 0 ? (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    )}
                    <span className={`text-xs ${parseFloat(calcularDelta(resultados.totais.freteAtual, resultados.totais.freteSimulado)) > 0 ? 'text-red-500' : 'text-green-500'}`}>
                      {calcularDelta(resultados.totais.freteAtual, resultados.totais.freteSimulado)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Interpretação dos Resultados */}
            <div className="mt-6 p-4 bg-muted/30 rounded-lg">
              <h4 className="text-sm font-medium mb-2">💡 Interpretação dos Resultados:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
                <div>
                  <p><strong>Viagens:</strong> {resultados.totais.viagensSimulado > resultados.totais.viagensAtual ? 'Aumento' : 'Redução'} de {Math.abs(calcularDelta(resultados.totais.viagensAtual, resultados.totais.viagensSimulado))}%</p>
                  <p><strong>Caminhões:</strong> {resultados.totais.caminhaoSimulado > resultados.totais.caminhaoAtual ? 'Aumento' : 'Redução'} de {Math.abs(calcularDelta(resultados.totais.caminhaoAtual, resultados.totais.caminhaoSimulado))}%</p>
                </div>
                <div>
                  <p><strong>Tempo:</strong> {resultados.totais.diasSimulado > resultados.totais.diasAtual ? 'Aumento' : 'Redução'} de {Math.abs(calcularDelta(resultados.totais.diasAtual, resultados.totais.diasSimulado))}% nos dias</p>
                  <p><strong>Custo:</strong> {resultados.totais.freteSimulado > resultados.totais.freteAtual ? 'Aumento' : 'Redução'} de {Math.abs(calcularDelta(resultados.totais.freteAtual, resultados.totais.freteSimulado))}% no frete</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


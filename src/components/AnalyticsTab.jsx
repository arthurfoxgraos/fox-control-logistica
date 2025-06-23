import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'

export default function AnalyticsTab({ dados }) {
  // Preparar dados para gráficos
  const dadosPorGrao = dados.reduce((acc, item) => {
    const grao = item.grain
    if (!acc[grao]) {
      acc[grao] = { name: grao, sacas: 0, receita: 0, count: 0 }
    }
    acc[grao].sacas += item.amount_allocated
    acc[grao].receita += item.amount_allocated * item.frete_por_saca * 1.2
    acc[grao].count += 1
    return acc
  }, {})

  const chartDataGraos = Object.values(dadosPorGrao)

  const dadosPorMes = dados.reduce((acc, item) => {
    const mes = new Date(item.data_agendamento).toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' })
    if (!acc[mes]) {
      acc[mes] = { name: mes, viagens: 0, caminhoes: 0 }
    }
    acc[mes].viagens += item.viagens_necessarias
    acc[mes].caminhoes += item.caminhoes_necessarios
    return acc
  }, {})

  const chartDataMeses = Object.values(dadosPorMes)

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Analytics de Frete e Logística
          </CardTitle>
          <CardDescription>
            Análise detalhada dos dados de transporte e performance logística
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Sacas por Grão */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Distribuição de Sacas por Grão</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartDataGraos}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [value.toLocaleString(), 'Sacas']} />
                <Bar dataKey="sacas" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Pizza - Receita por Grão */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Receita por Tipo de Grão</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartDataGraos}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="receita"
                >
                  {chartDataGraos.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`R$ ${value.toLocaleString()}`, 'Receita']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Linha - Viagens por Mês */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Viagens Necessárias por Período</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartDataMeses}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="viagens" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Barras - Caminhões por Mês */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Caminhões Necessários por Período</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartDataMeses}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="caminhoes" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


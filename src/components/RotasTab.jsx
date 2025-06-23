import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Route } from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default function RotasTab({ dados }) {
  // Calcular score de otimização para cada rota
  const dadosComScore = dados.map(item => ({
    ...item,
    score_otimizacao: (
      (item.margem_lucro * 0.4) + 
      ((500 - item.distance) / 500 * 30) + 
      ((2000 - item.amount_allocated) / 2000 * 20) +
      (item.ajuste_manual ? 10 : 0)
    ).toFixed(1)
  })).sort((a, b) => parseFloat(b.score_otimizacao) - parseFloat(a.score_otimizacao))

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Route className="h-5 w-5" />
            Otimização de Rotas por Data
          </CardTitle>
          <CardDescription>
            Análise de rotas ordenadas por score de otimização (margem, distância, volume)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border" style={{ height: '500px', overflowY: 'auto' }}>
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Comprador</TableHead>
                  <TableHead className="text-right">Sacas</TableHead>
                  <TableHead className="text-right">Distância</TableHead>
                  <TableHead className="text-right">Frete/Saca</TableHead>
                  <TableHead className="text-right">Margem(%)</TableHead>
                  <TableHead className="text-right">Caminhões</TableHead>
                  <TableHead className="text-center">Manual</TableHead>
                  <TableHead className="text-right">Score Otim.</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dadosComScore.map((rota) => (
                  <TableRow key={rota.id} className="hover:bg-muted/50">
                    <TableCell>
                      {format(new Date(rota.data_agendamento), 'dd/MM/yyyy', { locale: ptBR })}
                    </TableCell>
                    <TableCell className="max-w-48">
                      <span className="truncate block" title={rota.buyer}>
                        {rota.buyer.length > 30 ? rota.buyer.substring(0, 30) + '...' : rota.buyer}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      {rota.amount_allocated.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      {rota.distance.toFixed(1)} km
                    </TableCell>
                    <TableCell className="text-right">
                      R$ {rota.frete_por_saca.toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge 
                        variant={rota.margem_lucro > 15 ? "default" : rota.margem_lucro > 10 ? "secondary" : "destructive"}
                      >
                        {rota.margem_lucro.toFixed(1)}%
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {rota.caminhoes_necessarios}
                    </TableCell>
                    <TableCell className="text-center">
                      {rota.ajuste_manual ? (
                        <Badge variant="secondary">✏️</Badge>
                      ) : (
                        <Badge variant="outline">🔢</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge 
                        variant={parseFloat(rota.score_otimizacao) > 40 ? "default" : parseFloat(rota.score_otimizacao) > 25 ? "secondary" : "outline"}
                      >
                        {rota.score_otimizacao}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Legenda */}
          <div className="mt-4 p-4 bg-muted/30 rounded-lg">
            <h4 className="text-sm font-medium mb-2">📊 Score de Otimização:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-muted-foreground">
              <div>• <strong>Margem de Lucro</strong>: 40% do score</div>
              <div>• <strong>Distância</strong>: 30% do score (menor = melhor)</div>
              <div>• <strong>Volume</strong>: 20% do score</div>
              <div>• <strong>Ajuste Manual</strong>: +10 pontos bonus</div>
            </div>
            <div className="mt-2 flex gap-4 text-xs">
              <span><Badge variant="default">40+</Badge> Excelente</span>
              <span><Badge variant="secondary">25-40</Badge> Bom</span>
              <span><Badge variant="outline">&lt;25</Badge> Regular</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


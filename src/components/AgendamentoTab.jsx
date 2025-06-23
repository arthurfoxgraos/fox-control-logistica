import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Calendar, Edit3, Save, X, Truck } from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default function AgendamentoTab({ dados, onDadosChange }) {
  const [editandoLinha, setEditandoLinha] = useState(null)
  const [valoresEdicao, setValoresEdicao] = useState({})

  const iniciarEdicao = (id, linha) => {
    setEditandoLinha(id)
    setValoresEdicao({
      data_agendamento: linha.data_agendamento.toISOString().split('T')[0],
      caminhoes_necessarios: linha.caminhoes_necessarios
    })
  }

  const cancelarEdicao = () => {
    setEditandoLinha(null)
    setValoresEdicao({})
  }

  const salvarEdicao = async (id) => {
    try {
      // Simular salvamento no backend
      console.log('Salvando alterações para ID:', id, valoresEdicao)
      
      // Atualizar dados localmente
      onDadosChange(prev => prev.map(item => 
        item.id === id 
          ? {
              ...item,
              data_agendamento: new Date(valoresEdicao.data_agendamento),
              caminhoes_necessarios: parseInt(valoresEdicao.caminhoes_necessarios),
              ajuste_manual: true
            }
          : item
      ))

      setEditandoLinha(null)
      setValoresEdicao({})
      
      // Simular feedback de sucesso
      alert(`✅ Dados atualizados para ID ${id}`)
    } catch (error) {
      console.error('Erro ao salvar:', error)
      alert('❌ Erro ao salvar alterações')
    }
  }

  const handleInputChange = (campo, valor) => {
    setValoresEdicao(prev => ({
      ...prev,
      [campo]: valor
    }))
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Lista de Cargas Agendadas - Edição Inline
          </CardTitle>
          <CardDescription>
            Clique nos ícones de edição para alterar datas e número de caminhões diretamente na tabela
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border" style={{ height: '600px', overflowY: 'auto' }}>
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableRow>
                  <TableHead className="w-16">ID</TableHead>
                  <TableHead className="w-32">Data Agendamento</TableHead>
                  <TableHead className="w-48">Comprador</TableHead>
                  <TableHead className="w-48">Vendedor</TableHead>
                  <TableHead className="w-20">Grão</TableHead>
                  <TableHead className="w-24 text-right">Sacas</TableHead>
                  <TableHead className="w-24 text-right">Dist.(km)</TableHead>
                  <TableHead className="w-20 text-right">Viagens</TableHead>
                  <TableHead className="w-24 text-right">Caminhões</TableHead>
                  <TableHead className="w-20 text-right">Dias</TableHead>
                  <TableHead className="w-28 text-right">Frete/Saca</TableHead>
                  <TableHead className="w-24 text-right">Margem(%)</TableHead>
                  <TableHead className="w-20 text-center">Manual</TableHead>
                  <TableHead className="w-24">Status</TableHead>
                  <TableHead className="w-20 text-center">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dados.map((linha) => (
                  <TableRow key={linha.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{linha.id}</TableCell>
                    
                    {/* Data Agendamento - Editável */}
                    <TableCell>
                      {editandoLinha === linha.id ? (
                        <Input
                          type="date"
                          value={valoresEdicao.data_agendamento}
                          onChange={(e) => handleInputChange('data_agendamento', e.target.value)}
                          className="w-full text-xs"
                        />
                      ) : (
                        <span className="text-sm">
                          {format(new Date(linha.data_agendamento), 'dd/MM/yyyy', { locale: ptBR })}
                        </span>
                      )}
                    </TableCell>
                    
                    <TableCell className="max-w-48">
                      <span className="text-sm truncate block" title={linha.buyer}>
                        {linha.buyer.length > 30 ? linha.buyer.substring(0, 30) + '...' : linha.buyer}
                      </span>
                    </TableCell>
                    
                    <TableCell className="max-w-48">
                      <span className="text-sm truncate block" title={linha.seller}>
                        {linha.seller.length > 30 ? linha.seller.substring(0, 30) + '...' : linha.seller}
                      </span>
                    </TableCell>
                    
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {linha.grain}
                      </Badge>
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      {linha.amount_allocated.toLocaleString()}
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      {linha.distance.toFixed(1)}
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      {linha.viagens_necessarias}
                    </TableCell>
                    
                    {/* Caminhões - Editável */}
                    <TableCell className="text-right">
                      {editandoLinha === linha.id ? (
                        <Input
                          type="number"
                          min="1"
                          max="50"
                          value={valoresEdicao.caminhoes_necessarios}
                          onChange={(e) => handleInputChange('caminhoes_necessarios', e.target.value)}
                          className="w-20 text-xs text-right"
                        />
                      ) : (
                        <span className="text-sm">{linha.caminhoes_necessarios}</span>
                      )}
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      {linha.dias_operacao}
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      R$ {linha.frete_por_saca.toFixed(2)}
                    </TableCell>
                    
                    <TableCell className="text-right text-sm">
                      {linha.margem_lucro.toFixed(1)}%
                    </TableCell>
                    
                    <TableCell className="text-center">
                      {linha.ajuste_manual ? (
                        <Badge variant="secondary" className="text-xs">✏️</Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs">🔢</Badge>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      <Badge variant="default" className="text-xs">
                        {linha.status}
                      </Badge>
                    </TableCell>
                    
                    {/* Ações */}
                    <TableCell className="text-center">
                      {editandoLinha === linha.id ? (
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => salvarEdicao(linha.id)}
                            className="h-6 w-6 p-0"
                          >
                            <Save className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={cancelarEdicao}
                            className="h-6 w-6 p-0"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => iniciarEdicao(linha.id, linha)}
                          className="h-6 w-6 p-0"
                        >
                          <Edit3 className="h-3 w-3" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {/* Instruções de uso */}
          <div className="mt-4 p-4 bg-muted/30 rounded-lg">
            <h4 className="text-sm font-medium mb-2">💡 Como usar a edição inline:</h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>📅 <strong>Data</strong>: Clique no ícone de edição para alterar a data de agendamento</li>
              <li>🚛 <strong>Caminhões</strong>: Clique no ícone de edição para ajustar o número de caminhões manualmente</li>
              <li>💾 <strong>Salvamento</strong>: Clique no ícone de salvar para confirmar as alterações</li>
              <li>✏️ <strong>Manual</strong>: Indica se o número de caminhões foi ajustado manualmente</li>
            </ul>
            <p className="text-xs text-muted-foreground mt-2">
              <strong>Legenda:</strong> ✏️ = Ajuste Manual | 🔢 = Cálculo Automático
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


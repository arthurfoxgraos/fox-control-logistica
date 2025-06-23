import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { ChevronDown, Filter, RotateCcw } from 'lucide-react'

export default function FiltrosGlobais({ dados, filtros, onFiltrosChange }) {
  const [isOpen, setIsOpen] = useState(false)

  // Extrair opções únicas dos dados
  const graosUnicos = [...new Set(dados.map(item => item.grain))].sort()
  const vendedoresUnicos = [...new Set(dados.map(item => item.seller))].sort()
  const compradoresUnicos = [...new Set(dados.map(item => item.buyer))].sort()

  const handleFiltroChange = (campo, valor) => {
    onFiltrosChange(prev => ({
      ...prev,
      [campo]: valor
    }))
  }

  const handleMultiSelectChange = (campo, valor, checked) => {
    onFiltrosChange(prev => {
      const lista = prev[campo] || []
      if (checked) {
        return {
          ...prev,
          [campo]: [...lista, valor]
        }
      } else {
        return {
          ...prev,
          [campo]: lista.filter(item => item !== valor)
        }
      }
    })
  }

  const handleSelecionarTodos = (campo, opcoes) => {
    onFiltrosChange(prev => ({
      ...prev,
      [campo]: opcoes
    }))
  }

  const handleLimparFiltros = () => {
    onFiltrosChange({
      dataInicio: new Date(),
      dataFim: new Date(2025, 7, 7),
      graos: graosUnicos,
      vendedores: vendedoresUnicos,
      compradores: compradoresUnicos,
      ordenacao: 'data_agendamento',
      ordemCrescente: true
    })
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className="flex items-center justify-between">
        <CollapsibleTrigger asChild>
          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros e Ordenação
            <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        
        <Button variant="outline" size="sm" onClick={handleLimparFiltros} className="flex items-center gap-2">
          <RotateCcw className="h-4 w-4" />
          Limpar Todos os Filtros
        </Button>
      </div>

      <CollapsibleContent className="mt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Filtros de Data */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Período</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label htmlFor="dataInicio" className="text-xs">Data Início</Label>
                <Input
                  id="dataInicio"
                  type="date"
                  value={filtros.dataInicio?.toISOString().split('T')[0] || ''}
                  onChange={(e) => handleFiltroChange('dataInicio', new Date(e.target.value))}
                  className="text-xs"
                />
              </div>
              <div>
                <Label htmlFor="dataFim" className="text-xs">Data Fim</Label>
                <Input
                  id="dataFim"
                  type="date"
                  value={filtros.dataFim?.toISOString().split('T')[0] || ''}
                  onChange={(e) => handleFiltroChange('dataFim', new Date(e.target.value))}
                  className="text-xs"
                />
              </div>
            </CardContent>
          </Card>

          {/* Filtro de Grãos */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                Grãos
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleSelecionarTodos('graos', graosUnicos)}
                  className="text-xs h-6 px-2"
                >
                  ✅ Todos
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-32 overflow-y-auto">
              {graosUnicos.map(grao => (
                <div key={grao} className="flex items-center space-x-2">
                  <Checkbox
                    id={`grao-${grao}`}
                    checked={filtros.graos?.includes(grao) || false}
                    onCheckedChange={(checked) => handleMultiSelectChange('graos', grao, checked)}
                  />
                  <Label htmlFor={`grao-${grao}`} className="text-xs">{grao}</Label>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Filtro de Vendedores */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                Vendedores
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleSelecionarTodos('vendedores', vendedoresUnicos)}
                  className="text-xs h-6 px-2"
                >
                  ✅ Todos
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-32 overflow-y-auto">
              {vendedoresUnicos.slice(0, 5).map(vendedor => (
                <div key={vendedor} className="flex items-center space-x-2">
                  <Checkbox
                    id={`vendedor-${vendedor}`}
                    checked={filtros.vendedores?.includes(vendedor) || false}
                    onCheckedChange={(checked) => handleMultiSelectChange('vendedores', vendedor, checked)}
                  />
                  <Label htmlFor={`vendedor-${vendedor}`} className="text-xs truncate" title={vendedor}>
                    {vendedor.length > 15 ? vendedor.substring(0, 15) + '...' : vendedor}
                  </Label>
                </div>
              ))}
              {vendedoresUnicos.length > 5 && (
                <p className="text-xs text-muted-foreground">+{vendedoresUnicos.length - 5} mais...</p>
              )}
            </CardContent>
          </Card>

          {/* Filtro de Compradores */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                Compradores
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleSelecionarTodos('compradores', compradoresUnicos)}
                  className="text-xs h-6 px-2"
                >
                  ✅ Todos
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-32 overflow-y-auto">
              {compradoresUnicos.slice(0, 5).map(comprador => (
                <div key={comprador} className="flex items-center space-x-2">
                  <Checkbox
                    id={`comprador-${comprador}`}
                    checked={filtros.compradores?.includes(comprador) || false}
                    onCheckedChange={(checked) => handleMultiSelectChange('compradores', comprador, checked)}
                  />
                  <Label htmlFor={`comprador-${comprador}`} className="text-xs truncate" title={comprador}>
                    {comprador.length > 15 ? comprador.substring(0, 15) + '...' : comprador}
                  </Label>
                </div>
              ))}
              {compradoresUnicos.length > 5 && (
                <p className="text-xs text-muted-foreground">+{compradoresUnicos.length - 5} mais...</p>
              )}
            </CardContent>
          </Card>

          {/* Ordenação */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Ordenação</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label htmlFor="ordenacao" className="text-xs">Ordenar por</Label>
                <Select value={filtros.ordenacao} onValueChange={(value) => handleFiltroChange('ordenacao', value)}>
                  <SelectTrigger className="text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="data_agendamento">Data Agendamento</SelectItem>
                    <SelectItem value="distance">Distância</SelectItem>
                    <SelectItem value="amount_allocated">Sacas</SelectItem>
                    <SelectItem value="margem_lucro">Margem Lucro</SelectItem>
                    <SelectItem value="frete_por_saca">Frete por Saca</SelectItem>
                    <SelectItem value="caminhoes_necessarios">Caminhões</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="ordemCrescente"
                  checked={filtros.ordemCrescente}
                  onCheckedChange={(checked) => handleFiltroChange('ordemCrescente', checked)}
                />
                <Label htmlFor="ordemCrescente" className="text-xs">Ordem Crescente</Label>
              </div>
            </CardContent>
          </Card>
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}


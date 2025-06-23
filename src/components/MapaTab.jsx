import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Map, Maximize, Navigation } from 'lucide-react'

export default function MapaTab({ dados }) {
  const [modoFullScreen, setModoFullScreen] = useState(false)
  const [filtroDistancia, setFiltroDistancia] = useState([0, 500])

  // Filtrar dados por distância
  const dadosFiltrados = dados.filter(item => 
    item.distance >= filtroDistancia[0] && item.distance <= filtroDistancia[1]
  )

  // Simular coordenadas para demonstração
  const dadosComCoordenadas = dadosFiltrados.map(item => ({
    ...item,
    lat_origem: -15.7801 + (Math.random() - 0.5) * 10,
    lng_origem: -47.9292 + (Math.random() - 0.5) * 10,
    lat_destino: -15.7801 + (Math.random() - 0.5) * 10,
    lng_destino: -47.9292 + (Math.random() - 0.5) * 10
  }))

  // Calcular estatísticas
  const stats = {
    totalRotas: dadosFiltrados.length,
    distanciaMedia: dadosFiltrados.reduce((sum, item) => sum + item.distance, 0) / dadosFiltrados.length || 0,
    sacasTotal: dadosFiltrados.reduce((sum, item) => sum + item.amount_allocated, 0),
    caminhoesMedio: dadosFiltrados.reduce((sum, item) => sum + item.caminhoes_necessarios, 0) / dadosFiltrados.length || 0
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Map className="h-5 w-5" />
                Visualização de Rotas no Mapa
              </CardTitle>
              <CardDescription>
                Visualize todas as rotas de transporte em um mapa interativo
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="fullscreen-mode"
                checked={modoFullScreen}
                onCheckedChange={setModoFullScreen}
              />
              <Label htmlFor="fullscreen-mode" className="flex items-center gap-2">
                <Maximize className="h-4 w-4" />
                Modo Full Screen
              </Label>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filtros do Mapa */}
          {!modoFullScreen && (
            <div className="mb-6 p-4 bg-muted/30 rounded-lg">
              <h4 className="text-sm font-medium mb-3">🔍 Filtro Adicional do Mapa</h4>
              <div className="space-y-3">
                <Label className="text-sm">Faixa de distância (km): {filtroDistancia[0]} - {filtroDistancia[1]}</Label>
                <Slider
                  value={filtroDistancia}
                  onValueChange={setFiltroDistancia}
                  max={500}
                  min={0}
                  step={10}
                  className="w-full"
                />
              </div>
            </div>
          )}

          {/* Área do Mapa */}
          <div 
            className="w-full bg-muted/20 border-2 border-dashed border-muted-foreground/25 rounded-lg flex items-center justify-center"
            style={{ height: modoFullScreen ? '600px' : '400px' }}
          >
            <div className="text-center space-y-4">
              <Navigation className="h-16 w-16 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-lg font-medium text-muted-foreground">Mapa Interativo</h3>
                <p className="text-sm text-muted-foreground">
                  Aqui seria renderizado o mapa com as {dadosFiltrados.length} rotas filtradas
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  (Integração com Leaflet/MapBox seria implementada aqui)
                </p>
              </div>
            </div>
          </div>

          {/* Estatísticas do Mapa */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{stats.totalRotas}</div>
                <p className="text-xs text-muted-foreground">Rotas Visíveis</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{stats.distanciaMedia.toFixed(1)} km</div>
                <p className="text-xs text-muted-foreground">Distância Média</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{stats.sacasTotal.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total de Sacas</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">{stats.caminhoesMedio.toFixed(1)}</div>
                <p className="text-xs text-muted-foreground">Caminhões Médio</p>
              </CardContent>
            </Card>
          </div>

          {/* Top 5 Informações */}
          {dadosFiltrados.length > 0 && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium mb-3">🎯 Top 5 Maiores Volumes:</h4>
                <div className="space-y-2">
                  {dadosFiltrados
                    .sort((a, b) => b.amount_allocated - a.amount_allocated)
                    .slice(0, 5)
                    .map((item, index) => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span className="truncate">
                          {item.seller.substring(0, 20)}...
                        </span>
                        <Badge variant="outline">
                          {item.amount_allocated.toLocaleString()} sacas ({item.distance.toFixed(1)} km)
                        </Badge>
                      </div>
                    ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium mb-3">🚛 Top 5 Maiores Distâncias:</h4>
                <div className="space-y-2">
                  {dadosFiltrados
                    .sort((a, b) => b.distance - a.distance)
                    .slice(0, 5)
                    .map((item, index) => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span className="truncate">
                          {item.seller.substring(0, 15)}... → {item.buyer.substring(0, 15)}...
                        </span>
                        <Badge variant="outline">
                          {item.distance.toFixed(1)} km
                        </Badge>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


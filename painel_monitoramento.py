import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import threading
import psycopg2
import folium
from streamlit_folium import st_folium
import json

# Importar módulos de processamento
from sync_combinations import sync_combinations
from provisionings_min_distance import provisioning_min_distance

# Configuração da página
st.set_page_config(
    page_title="Fox Control - Painel de Monitoramento",
    page_icon="📊",
    layout="wide"
)

# CSS customizado para cores preto e prata
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6c757d;
        margin-bottom: 1rem;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-completed {
        color: #007bff;
        font-weight: bold;
    }
    .log-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        max-height: 400px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🚛 Fox Control - Painel de Monitoramento</h1>
    <p>Sistema de gestão logística para transporte de grãos</p>
</div>
""", unsafe_allow_html=True)

# Configurações do banco de dados
DB_CONFIG = {
    'host': '24.199.75.66',
    'port': 5432,
    'user': 'myuser',
    'password': 'mypassword',
    'database': 'mydb'
}

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return None

def carregar_dados_provisionamento():
    """Carrega dados da tabela de provisionamento"""
    try:
        conn = conectar_banco()
        if conn:
            query = """
            SELECT 
                buyer,
                seller,
                grain,
                amount_allocated,
                revenue,
                cost,
                freight,
                profit_total,
                distance,
                from_coords,
                to_coords
            FROM provisioningsv2_best_scenario_distance
            ORDER BY distance ASC
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def executar_sync_combinations():
    """Executa sincronização em thread separada"""
    def run():
        sync_combinations.run_sync()
    
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

def executar_provisioning():
    """Executa provisionamento em thread separada"""
    def run():
        provisioning_min_distance.run_provisioning()
    
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

# Sidebar com controles
st.sidebar.header("🎛️ Controles do Sistema")

# Seção de Sincronização de Combinações
st.sidebar.subheader("🔄 Sincronização de Combinações")

if st.sidebar.button("▶️ Executar Sincronização", key="sync_btn"):
    executar_sync_combinations()
    st.sidebar.success("Sincronização iniciada!")

# Status da sincronização
sync_status = sync_combinations.status
if sync_status == "Executando":
    st.sidebar.markdown(f'<p class="status-running">Status: {sync_status}</p>', unsafe_allow_html=True)
    st.sidebar.progress(sync_combinations.progress / 100)
elif sync_status == "Erro":
    st.sidebar.markdown(f'<p class="status-error">Status: {sync_status}</p>', unsafe_allow_html=True)
elif sync_status == "Concluído":
    st.sidebar.markdown(f'<p class="status-completed">Status: {sync_status}</p>', unsafe_allow_html=True)
else:
    st.sidebar.write(f"Status: {sync_status}")

# Seção de Provisionamento
st.sidebar.subheader("📦 Provisionamento por Distância")

if st.sidebar.button("▶️ Executar Provisionamento", key="prov_btn"):
    executar_provisioning()
    st.sidebar.success("Provisionamento iniciado!")

# Status do provisionamento
prov_status = provisioning_min_distance.status
if prov_status == "Executando":
    st.sidebar.markdown(f'<p class="status-running">Status: {prov_status}</p>', unsafe_allow_html=True)
    st.sidebar.progress(provisioning_min_distance.progress / 100)
elif prov_status == "Erro":
    st.sidebar.markdown(f'<p class="status-error">Status: {prov_status}</p>', unsafe_allow_html=True)
elif prov_status == "Concluído":
    st.sidebar.markdown(f'<p class="status-completed">Status: {prov_status}</p>', unsafe_allow_html=True)
else:
    st.sidebar.write(f"Status: {prov_status}")

# Auto-refresh
if st.sidebar.checkbox("🔄 Auto-refresh (5s)", value=False):
    time.sleep(5)
    st.rerun()

# Tabs principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "🔄 Sincronização", 
    "📦 Provisionamento", 
    "🗺️ Mapa de Rotas",
    "📋 Logs do Sistema"
])

with tab1:
    st.header("📊 Dashboard Geral")
    
    # Carregar dados para métricas
    df_prov = carregar_dados_provisionamento()
    
    if not df_prov.empty:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sacas = df_prov['amount_allocated'].sum()
            st.metric("Total de Sacas", f"{total_sacas:,.0f}")
        
        with col2:
            total_receita = df_prov['revenue'].sum()
            st.metric("Receita Total", f"R$ {total_receita:,.2f}")
        
        with col3:
            total_lucro = df_prov['profit_total'].sum()
            st.metric("Lucro Total", f"R$ {total_lucro:,.2f}")
        
        with col4:
            dist_media = df_prov['distance'].mean()
            st.metric("Distância Média", f"{dist_media:.1f} km")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por grão
            grain_dist = df_prov.groupby('grain')['amount_allocated'].sum().reset_index()
            fig_grain = px.pie(
                grain_dist, 
                values='amount_allocated', 
                names='grain',
                title="Distribuição de Sacas por Grão",
                color_discrete_sequence=['#2c3e50', '#34495e', '#6c757d', '#95a5a6']
            )
            st.plotly_chart(fig_grain, use_container_width=True)
        
        with col2:
            # Top 10 compradores por volume
            buyer_vol = df_prov.groupby('buyer')['amount_allocated'].sum().nlargest(10).reset_index()
            fig_buyers = px.bar(
                buyer_vol,
                x='amount_allocated',
                y='buyer',
                orientation='h',
                title="Top 10 Compradores por Volume",
                color_discrete_sequence=['#2c3e50']
            )
            fig_buyers.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_buyers, use_container_width=True)
        
        # Análise de distância vs lucro
        st.subheader("📈 Análise de Distância vs Lucro")
        fig_scatter = px.scatter(
            df_prov,
            x='distance',
            y='profit_total',
            size='amount_allocated',
            color='grain',
            title="Relação entre Distância e Lucro",
            labels={'distance': 'Distância (km)', 'profit_total': 'Lucro Total (R$)'},
            color_discrete_sequence=['#2c3e50', '#34495e', '#6c757d', '#95a5a6']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    else:
        st.info("📋 Nenhum dado de provisionamento disponível. Execute o processo de provisionamento primeiro.")

with tab2:
    st.header("🔄 Sincronização de Combinações")
    
    # Métricas da sincronização
    if sync_combinations.stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Operações", sync_combinations.stats.get('total_operations', 0))
        
        with col2:
            st.metric("Vendas", sync_combinations.stats.get('total_sales', 0))
        
        with col3:
            st.metric("Compras", sync_combinations.stats.get('total_purchases', 0))
        
        with col4:
            st.metric("Combinações", sync_combinations.stats.get('total_combinations', 0))
        
        # Distâncias por comprador
        if sync_combinations.stats.get('buyer_distances'):
            st.subheader("📏 Distância Média por Comprador")
            buyer_data = []
            for buyer, distances in sync_combinations.stats['buyer_distances'].items():
                if distances:
                    avg_dist = sum(distances) / len(distances)
                    buyer_data.append({
                        'Comprador': buyer,
                        'Distância Média (km)': avg_dist,
                        'Número de Rotas': len(distances)
                    })
            
            if buyer_data:
                df_buyers = pd.DataFrame(buyer_data)
                df_buyers = df_buyers.sort_values('Distância Média (km)')
                
                fig_buyer_dist = px.bar(
                    df_buyers,
                    x='Distância Média (km)',
                    y='Comprador',
                    orientation='h',
                    title="Distância Média por Comprador",
                    color='Número de Rotas',
                    color_continuous_scale='Viridis'
                )
                fig_buyer_dist.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_buyer_dist, use_container_width=True)
    
    # Logs da sincronização
    st.subheader("📝 Logs da Sincronização")
    if sync_combinations.logs:
        logs_text = "\n".join(sync_combinations.logs[-20:])  # Últimos 20 logs
        st.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum log disponível. Execute a sincronização para ver os logs.")

with tab3:
    st.header("📦 Provisionamento por Distância Mínima")
    
    # Métricas do provisionamento
    if provisioning_min_distance.stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Combinações Processadas", 
                     f"{provisioning_min_distance.stats.get('processed_combinations', 0)}/{provisioning_min_distance.stats.get('total_combinations', 0)}")
        
        with col2:
            total_allocated = provisioning_min_distance.stats.get('total_allocated', 0)
            st.metric("Sacas Alocadas", f"{total_allocated:,.0f}")
        
        with col3:
            avg_distance = provisioning_min_distance.stats.get('average_distance', 0)
            st.metric("Distância Média", f"{avg_distance:.1f} km")
        
        # Métricas financeiras
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_revenue = provisioning_min_distance.stats.get('total_revenue', 0)
            st.metric("Receita Total", f"R$ {total_revenue:,.2f}")
        
        with col2:
            total_cost = provisioning_min_distance.stats.get('total_cost', 0)
            st.metric("Custo Total", f"R$ {total_cost:,.2f}")
        
        with col3:
            total_profit = provisioning_min_distance.stats.get('total_profit', 0)
            st.metric("Lucro Total", f"R$ {total_profit:,.2f}")
        
        # Totais por grão
        if provisioning_min_distance.stats.get('grain_totals'):
            st.subheader("🌾 Distribuição por Grão")
            grain_data = []
            for grain, qty in provisioning_min_distance.stats['grain_totals'].items():
                grain_data.append({'Grão': grain, 'Quantidade': qty})
            
            df_grains = pd.DataFrame(grain_data)
            fig_grains = px.bar(
                df_grains,
                x='Grão',
                y='Quantidade',
                title="Quantidade Alocada por Grão",
                color_discrete_sequence=['#2c3e50']
            )
            st.plotly_chart(fig_grains, use_container_width=True)
    
    # Logs do provisionamento
    st.subheader("📝 Logs do Provisionamento")
    if provisioning_min_distance.logs:
        logs_text = "\n".join(provisioning_min_distance.logs[-20:])  # Últimos 20 logs
        st.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum log disponível. Execute o provisionamento para ver os logs.")

with tab4:
    st.header("🗺️ Mapa de Rotas Otimizadas")
    
    df_prov = carregar_dados_provisionamento()
    
    if not df_prov.empty:
        # Filtros para o mapa
        col1, col2 = st.columns(2)
        
        with col1:
            grains_selected = st.multiselect(
                "Filtrar por Grão",
                options=df_prov['grain'].unique(),
                default=df_prov['grain'].unique()
            )
        
        with col2:
            max_distance = st.slider(
                "Distância Máxima (km)",
                min_value=0,
                max_value=int(df_prov['distance'].max()),
                value=int(df_prov['distance'].max()),
                step=50
            )
        
        # Filtrar dados
        df_filtered = df_prov[
            (df_prov['grain'].isin(grains_selected)) &
            (df_prov['distance'] <= max_distance)
        ]
        
        if not df_filtered.empty:
            # Criar mapa
            center_lat = -15.0  # Centro do Brasil
            center_lon = -47.0
            
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=5,
                tiles='OpenStreetMap'
            )
            
            # Adicionar rotas ao mapa
            colors = {'milho': 'blue', 'sorgo': 'green', 'soja': 'orange', 'arroz': 'red'}
            
            for idx, row in df_filtered.head(100).iterrows():  # Limitar a 100 rotas para performance
                if row['from_coords'] and row['to_coords'] and len(row['from_coords']) == 2 and len(row['to_coords']) == 2:
                    from_coords = [row['from_coords'][1], row['from_coords'][0]]  # lat, lon
                    to_coords = [row['to_coords'][1], row['to_coords'][0]]  # lat, lon
                    
                    color = colors.get(row['grain'], 'gray')
                    
                    # Linha da rota
                    folium.PolyLine(
                        locations=[from_coords, to_coords],
                        color=color,
                        weight=2,
                        opacity=0.7,
                        popup=f"{row['seller']} → {row['buyer']}<br>"
                              f"Grão: {row['grain']}<br>"
                              f"Distância: {row['distance']:.1f} km<br>"
                              f"Sacas: {row['amount_allocated']:,.0f}<br>"
                              f"Lucro: R$ {row['profit_total']:,.2f}"
                    ).add_to(m)
                    
                    # Marcador de origem
                    folium.CircleMarker(
                        location=from_coords,
                        radius=3,
                        popup=f"Origem: {row['seller']}",
                        color=color,
                        fill=True
                    ).add_to(m)
                    
                    # Marcador de destino
                    folium.CircleMarker(
                        location=to_coords,
                        radius=3,
                        popup=f"Destino: {row['buyer']}",
                        color=color,
                        fill=True
                    ).add_to(m)
            
            # Adicionar legenda
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><b>Legenda</b></p>
            <p><i class="fa fa-circle" style="color:blue"></i> Milho</p>
            <p><i class="fa fa-circle" style="color:green"></i> Sorgo</p>
            <p><i class="fa fa-circle" style="color:orange"></i> Soja</p>
            <p><i class="fa fa-circle" style="color:red"></i> Arroz</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Exibir mapa
            st_folium(m, width=1200, height=600, use_container_width=True)
            
            # Estatísticas do mapa
            st.subheader("📊 Estatísticas das Rotas Filtradas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Rotas Exibidas", len(df_filtered))
            
            with col2:
                st.metric("Distância Total", f"{df_filtered['distance'].sum():,.1f} km")
            
            with col3:
                st.metric("Sacas Totais", f"{df_filtered['amount_allocated'].sum():,.0f}")
            
            with col4:
                st.metric("Lucro Total", f"R$ {df_filtered['profit_total'].sum():,.2f}")
        
        else:
            st.warning("Nenhuma rota encontrada com os filtros selecionados.")
    
    else:
        st.info("📋 Nenhum dado de rota disponível. Execute o processo de provisionamento primeiro.")

with tab5:
    st.header("📋 Logs Completos do Sistema")
    
    # Logs da sincronização
    st.subheader("🔄 Logs da Sincronização")
    if sync_combinations.logs:
        logs_sync = "\n".join(sync_combinations.logs)
        st.text_area("Logs Sincronização", logs_sync, height=300, key="logs_sync")
    else:
        st.info("Nenhum log de sincronização disponível.")
    
    # Logs do provisionamento
    st.subheader("📦 Logs do Provisionamento")
    if provisioning_min_distance.logs:
        logs_prov = "\n".join(provisioning_min_distance.logs)
        st.text_area("Logs Provisionamento", logs_prov, height=300, key="logs_prov")
    else:
        st.info("Nenhum log de provisionamento disponível.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    <p>🚛 Fox Control - Sistema de Gestão Logística | Desenvolvido com ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)


# Board de Agendamento de Cargas - Fox Control
# Sistema de gestão logística para transporte de grãos - Versão com Banco de Dados

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math
import psycopg2
from decimal import Decimal

# Configuração da página
st.set_page_config(
    page_title="Fox Control - Agendamento de Cargas",
    page_icon="🚛",
    layout="wide"
)

# Constantes do sistema
CAPACIDADE_CAMINHAO = 900  # sacas por caminhão
VELOCIDADE_MEDIA = 60  # km/h
HORAS_TRABALHO_DIA = 10  # horas por dia
TEMPO_CARGA_DESCARGA = 2.0  # horas por viagem

def calcular_viagens_e_caminhoes(amount_allocated, distance_km, capacidade_colheita_dia=None):
    """
    Calcula número de viagens e caminhões necessários
    
    Args:
        amount_allocated: Quantidade de sacas a transportar
        distance_km: Distância em km
        capacidade_colheita_dia: Sacas colhidas por dia (opcional)
    
    Returns:
        dict com cálculos detalhados
    """
    # Número de viagens necessárias
    viagens_necessarias = math.ceil(amount_allocated / CAPACIDADE_CAMINHAO)
    
    # Tempo por viagem (ida + volta + carga/descarga)
    tempo_viagem_horas = (distance_km * 2 / VELOCIDADE_MEDIA) + TEMPO_CARGA_DESCARGA
    
    # Viagens possíveis por dia por caminhão
    viagens_por_dia_caminhao = math.floor(HORAS_TRABALHO_DIA / tempo_viagem_horas)
    viagens_por_dia_caminhao = max(1, viagens_por_dia_caminhao)  # Mínimo 1 viagem por dia
    
    # Caminhões necessários baseado na logística
    caminhoes_logistica = math.ceil(viagens_necessarias / viagens_por_dia_caminhao)
    
    # Se temos capacidade de colheita, ajustar número de caminhões
    if capacidade_colheita_dia:
        dias_colheita = math.ceil(amount_allocated / capacidade_colheita_dia)
        viagens_necessarias_por_dia = math.ceil(viagens_necessarias / dias_colheita)
        caminhoes_colheita = math.ceil(viagens_necessarias_por_dia / viagens_por_dia_caminhao)
        caminhoes_necessarios = max(caminhoes_logistica, caminhoes_colheita)
    else:
        caminhoes_necessarios = caminhoes_logistica
        dias_colheita = math.ceil(viagens_necessarias / (caminhoes_necessarios * viagens_por_dia_caminhao))
    
    return {
        'viagens_necessarias': viagens_necessarias,
        'caminhoes_necessarios': caminhoes_necessarios,
        'viagens_por_dia_caminhao': viagens_por_dia_caminhao,
        'tempo_viagem_horas': tempo_viagem_horas,
        'dias_operacao': dias_colheita,
        'sacas_por_viagem': CAPACIDADE_CAMINHAO,
        'utilizacao_ultima_viagem': amount_allocated % CAPACIDADE_CAMINHAO or CAPACIDADE_CAMINHAO
    }

@st.cache_data
def conectar_banco_dados():
    """
    Conecta ao banco de dados PostgreSQL e retorna os dados da tabela
    """
    try:
        db_pg = psycopg2.connect(
            host='24.199.75.66', 
            port=5432,
            user='myuser', 
            password='mypassword', 
            database='mydb'
        )
        
        # Query para buscar todos os dados necessários
        query = """
        SELECT 
            id,
            destination_order,
            origin_order,
            grain,
            amount_allocated,
            revenue,
            cost,
            freight,
            tax_balance,
            profit_total,
            distance,
            buyer,
            seller
        FROM provisioningsv2_best_scenario_distance
        ORDER BY id;
        """
        
        df = pd.read_sql_query(query, db_pg)
        db_pg.close()
        
        # Converter Decimal para float para compatibilidade com Plotly
        decimal_columns = ['amount_allocated', 'revenue', 'cost', 'freight', 
                          'tax_balance', 'profit_total', 'distance']
        
        for col in decimal_columns:
            if col in df.columns:
                df[col] = df[col].astype(float)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return pd.DataFrame()

def processar_dados_logistica(df):
    """
    Processa os dados do banco adicionando cálculos de logística
    """
    if df.empty:
        return df
    
    # Aplicar cálculos de logística para cada linha
    resultados = []
    for _, row in df.iterrows():
        calc = calcular_viagens_e_caminhoes(row['amount_allocated'], row['distance'])
        resultados.append(calc)
    
    # Adicionar colunas calculadas ao DataFrame
    calc_df = pd.DataFrame(resultados)
    df_final = pd.concat([df, calc_df], axis=1)
    
    # Adicionar cálculos adicionais
    df_final['margem_lucro'] = (df_final['profit_total'] / df_final['revenue'] * 100).round(2)
    df_final['custo_por_saca'] = (df_final['cost'] / df_final['amount_allocated']).round(2)
    df_final['receita_por_saca'] = (df_final['revenue'] / df_final['amount_allocated']).round(2)
    
    return df_final

def criar_dados_exemplo():
    """Cria dados de exemplo baseados no código original"""
    dados = [
        {
            'destination_order': 'DEST001',
            'origin_order': 'ORIG001', 
            'buyer': 'Cooperativa Central',
            'seller': 'Fazenda São João',
            'grain': 'milho',
            'amount_allocated': 2700,  # 3 viagens
            'distance': 45,
            'revenue': 1350000,
            'cost': 1080000,
            'freight': 81000,
            'capacidade_colheita_dia': 1800
        },
        {
            'destination_order': 'DEST002',
            'origin_order': 'ORIG002',
            'buyer': 'Agroindústria Delta',
            'seller': 'Fazenda Esperança',
            'grain': 'sorgo',
            'amount_allocated': 1800,  # 2 viagens
            'distance': 120,
            'revenue': 900000,
            'cost': 720000,
            'freight': 108000,
            'capacidade_colheita_dia': 2400
        },
        {
            'destination_order': 'DEST003',
            'origin_order': 'ORIG003',
            'buyer': 'Exportadora Brasil',
            'seller': 'Fazenda Progresso',
            'grain': 'milho',
            'amount_allocated': 4500,  # 5 viagens
            'distance': 25,
            'revenue': 2250000,
            'cost': 1800000,
            'freight': 112500,
            'capacidade_colheita_dia': 3000
        },
        {
            'destination_order': 'DEST004',
            'origin_order': 'ORIG004',
            'buyer': 'Moinho Regional',
            'seller': 'Fazenda Vista Alegre',
            'grain': 'milho',
            'amount_allocated': 900,   # 1 viagem
            'distance': 80,
            'revenue': 450000,
            'cost': 360000,
            'freight': 36000,
            'capacidade_colheita_dia': 1200
        },
        {
            'destination_order': 'DEST005',
            'origin_order': 'ORIG005',
            'buyer': 'Ração Premium',
            'seller': 'Fazenda Boa Vista',
            'grain': 'sorgo',
            'amount_allocated': 3600,  # 4 viagens
            'distance': 200,
            'revenue': 1800000,
            'cost': 1440000,
            'freight': 288000,
            'capacidade_colheita_dia': 2000
        }
    ]
    
    # Adicionar cálculos de logística
    for item in dados:
        calc = calcular_viagens_e_caminhoes(
            item['amount_allocated'], 
            item['distance'],
            item['capacidade_colheita_dia']
        )
        item.update(calc)
        item['profit_total'] = item['revenue'] - item['cost'] - item['freight']
        item['margem_lucro'] = (item['profit_total'] / item['revenue']) * 100
    
    return pd.DataFrame(dados)

# Interface principal
st.title("🚛 Fox Control - Board de Agendamento de Cargas")
st.markdown("### Sistema Inteligente de Gestão Logística para Transporte de Grãos")

# Sidebar com controles
st.sidebar.header("⚙️ Configurações")

# Parâmetros ajustáveis
capacidade_caminhao = st.sidebar.number_input(
    "Capacidade do Caminhão (sacas)", 
    value=CAPACIDADE_CAMINHAO, 
    min_value=500, 
    max_value=1500
)

velocidade_media = st.sidebar.number_input(
    "Velocidade Média (km/h)", 
    value=VELOCIDADE_MEDIA, 
    min_value=40, 
    max_value=80
)

horas_trabalho = st.sidebar.number_input(
    "Horas de Trabalho/Dia", 
    value=HORAS_TRABALHO_DIA, 
    min_value=8, 
    max_value=12
)

# Atualizar constantes globais
CAPACIDADE_CAMINHAO = capacidade_caminhao
VELOCIDADE_MEDIA = velocidade_media
HORAS_TRABALHO_DIA = horas_trabalho
# TEMPO_CARGA_DESCARGA permanece como definido inicialmente (2 horas)

# Carregar dados do banco
with st.spinner("🔄 Carregando dados do banco..."):
    df_raw = conectar_banco_dados()

if df_raw.empty:
    st.error("❌ Não foi possível carregar os dados do banco de dados.")
    st.stop()

# Processar dados com cálculos de logística
df = processar_dados_logistica(df_raw)

# Métricas principais
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total de Sacas", 
        f"{df['amount_allocated'].sum():,.0f}",
        help="Quantidade total de sacas a transportar"
    )

with col2:
    st.metric(
        "Total de Viagens", 
        f"{df['viagens_necessarias'].sum():,.0f}",
        help="Número total de viagens necessárias"
    )

with col3:
    st.metric(
        "Caminhões Necessários", 
        f"{df['caminhoes_necessarios'].sum():,.0f}",
        help="Número total de caminhões necessários"
    )

with col4:
    st.metric(
        "Receita Total", 
        f"R$ {df['revenue'].sum():,.0f}",
        help="Receita total das operações"
    )

with col5:
    st.metric(
        "Lucro Total", 
        f"R$ {df['profit_total'].sum():,.0f}",
        help="Lucro total após custos e frete"
    )

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📋 Agendamento", "📊 Analytics", "🗺️ Rotas", "⚡ Otimização"])

with tab1:
    st.header("📋 Agendamento de Cargas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_grao = st.selectbox(
            "Filtrar por Grão",
            ["Todos"] + list(df['grain'].unique())
        )
    
    with col2:
        filtro_distancia = st.selectbox(
            "Filtrar por Distância",
            ["Todas", "Curta (< 50km)", "Média (50-100km)", "Longa (> 100km)"]
        )
    
    with col3:
        ordenar_por = st.selectbox(
            "Ordenar por",
            ["Distância", "Quantidade", "Viagens", "Lucro"]
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_grao != "Todos":
        df_filtrado = df_filtrado[df_filtrado['grain'] == filtro_grao]
    
    if filtro_distancia == "Curta (< 50km)":
        df_filtrado = df_filtrado[df_filtrado['distance'] < 50]
    elif filtro_distancia == "Média (50-100km)":
        df_filtrado = df_filtrado[(df_filtrado['distance'] >= 50) & (df_filtrado['distance'] <= 100)]
    elif filtro_distancia == "Longa (> 100km)":
        df_filtrado = df_filtrado[df_filtrado['distance'] > 100]
    
    # Ordenação
    if ordenar_por == "Distância":
        df_filtrado = df_filtrado.sort_values('distance')
    elif ordenar_por == "Quantidade":
        df_filtrado = df_filtrado.sort_values('amount_allocated', ascending=False)
    elif ordenar_por == "Viagens":
        df_filtrado = df_filtrado.sort_values('viagens_necessarias', ascending=False)
    elif ordenar_por == "Lucro":
        df_filtrado = df_filtrado.sort_values('profit_total', ascending=False)
    
    # Tabela principal com detalhes de logística
    st.subheader("Detalhes das Cargas")
    
    for idx, row in df_filtrado.iterrows():
        with st.expander(f"🚛 {row['seller']} → {row['buyer']} | {row['amount_allocated']:,.0f} sacas | {row['viagens_necessarias']} viagens"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📍 Informações da Rota**")
                st.write(f"• Origem: {row['origin_order']}")
                st.write(f"• Destino: {row['destination_order']}")
                st.write(f"• Distância: {row['distance']} km")
                st.write(f"• Grão: {row['grain'].title()}")
                
            with col2:
                st.markdown("**🚛 Logística**")
                st.write(f"• Sacas: {row['amount_allocated']:,.0f}")
                st.write(f"• Viagens: {row['viagens_necessarias']}")
                st.write(f"• Caminhões: {row['caminhoes_necessarios']}")
                st.write(f"• Dias operação: {row['dias_operacao']}")
                st.write(f"• Tempo/viagem: {row['tempo_viagem_horas']:.1f}h")
                
            with col3:
                st.markdown("**💰 Financeiro**")
                st.write(f"• Receita: R$ {row['revenue']:,.0f}")
                st.write(f"• Custo: R$ {row['cost']:,.0f}")
                st.write(f"• Frete: R$ {row['freight']:,.0f}")
                st.write(f"• Lucro: R$ {row['profit_total']:,.0f}")
                st.write(f"• Margem: {row['margem_lucro']:.1f}%")
            
            # Barra de progresso para utilização do último caminhão
            if row['utilizacao_ultima_viagem'] < CAPACIDADE_CAMINHAO:
                st.progress(row['utilizacao_ultima_viagem'] / CAPACIDADE_CAMINHAO)
                st.caption(f"Última viagem: {row['utilizacao_ultima_viagem']} sacas ({row['utilizacao_ultima_viagem']/CAPACIDADE_CAMINHAO*100:.1f}% da capacidade)")

with tab2:
    st.header("📊 Analytics de Transporte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de viagens por destino
        fig_viagens = px.bar(
            df, 
            x='buyer', 
            y='viagens_necessarias',
            color='grain',
            title="Viagens Necessárias por Comprador",
            labels={'viagens_necessarias': 'Número de Viagens', 'buyer': 'Comprador'}
        )
        fig_viagens.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_viagens, use_container_width=True)
        
        # Gráfico de eficiência por distância
        fig_eficiencia = px.scatter(
            df,
            x='distance',
            y='viagens_por_dia_caminhao',
            size='amount_allocated',
            color='grain',
            title="Eficiência de Viagens por Distância",
            labels={
                'distance': 'Distância (km)',
                'viagens_por_dia_caminhao': 'Viagens/Dia por Caminhão',
                'amount_allocated': 'Sacas'
            }
        )
        st.plotly_chart(fig_eficiencia, use_container_width=True)
    
    with col2:
        # Gráfico de distribuição de caminhões
        fig_caminhoes = px.pie(
            df,
            values='caminhoes_necessarios',
            names='buyer',
            title="Distribuição de Caminhões por Comprador"
        )
        st.plotly_chart(fig_caminhoes, use_container_width=True)
        
        # Gráfico de margem de lucro
        fig_margem = px.bar(
            df,
            x='buyer',
            y='margem_lucro',
            color='distance',
            title="Margem de Lucro por Comprador",
            labels={'margem_lucro': 'Margem de Lucro (%)', 'buyer': 'Comprador'}
        )
        fig_margem.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_margem, use_container_width=True)

with tab3:
    st.header("🗺️ Otimização de Rotas")
    
    # Análise de rotas por distância
    st.subheader("Classificação de Rotas")
    
    df['categoria_distancia'] = df['distance'].apply(
        lambda x: 'Curta (< 50km)' if x < 50 
        else 'Média (50-100km)' if x <= 100 
        else 'Longa (> 100km)'
    )
    
    resumo_rotas = df.groupby('categoria_distancia').agg({
        'amount_allocated': 'sum',
        'viagens_necessarias': 'sum',
        'caminhoes_necessarios': 'sum',
        'profit_total': 'sum',
        'distance': 'mean'
    }).round(2)
    
    st.dataframe(resumo_rotas, use_container_width=True)
    
    # Recomendações de otimização
    st.subheader("💡 Recomendações de Otimização")
    
    # Rotas curtas - múltiplas viagens
    rotas_curtas = df[df['distance'] < 50]
    if not rotas_curtas.empty:
        st.success(f"**Rotas Curtas ({len(rotas_curtas)} rotas):** Ideal para múltiplas viagens. Média de {rotas_curtas['viagens_por_dia_caminhao'].mean():.1f} viagens/dia por caminhão.")
    
    # Rotas longas - otimizar carga
    rotas_longas = df[df['distance'] > 100]
    if not rotas_longas.empty:
        st.warning(f"**Rotas Longas ({len(rotas_longas)} rotas):** Maximizar carga por viagem. Média de {rotas_longas['viagens_por_dia_caminhao'].mean():.1f} viagens/dia por caminhão.")
    
    # Análise de subutilização
    subutilizacao = df[df['utilizacao_ultima_viagem'] < CAPACIDADE_CAMINHAO * 0.8]
    if not subutilizacao.empty:
        st.info(f"**Oportunidade de Consolidação:** {len(subutilizacao)} cargas com subutilização na última viagem.")

with tab4:
    st.header("⚡ Simulador de Cenários")
    
    st.subheader("Ajustar Parâmetros de Operação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        novo_capacidade = st.slider(
            "Capacidade do Caminhão (sacas)",
            min_value=500,
            max_value=1500,
            value=CAPACIDADE_CAMINHAO,
            step=50
        )
        
        nova_velocidade = st.slider(
            "Velocidade Média (km/h)",
            min_value=40,
            max_value=80,
            value=VELOCIDADE_MEDIA,
            step=5
        )
    
    with col2:
        novas_horas = st.slider(
            "Horas de Trabalho/Dia",
            min_value=8,
            max_value=14,
            value=HORAS_TRABALHO_DIA,
            step=1
        )
        
        novo_tempo_carga = st.slider(
            "Tempo Carga/Descarga (horas)",
            min_value=1.0,
            max_value=4.0,
            value=TEMPO_CARGA_DESCARGA,
            step=0.5
        )
    
    if st.button("🔄 Simular Novo Cenário"):
        # Recalcular com novos parâmetros
        df_simulacao = df.copy()
        
        for idx, row in df_simulacao.iterrows():
            # Recalcular com novos parâmetros
            viagens_sim = math.ceil(row['amount_allocated'] / novo_capacidade)
            tempo_viagem_sim = (row['distance'] * 2 / nova_velocidade) + novo_tempo_carga
            viagens_dia_sim = math.floor(novas_horas / tempo_viagem_sim)
            viagens_dia_sim = max(1, viagens_dia_sim)
            caminhoes_sim = math.ceil(viagens_sim / viagens_dia_sim)
            
            df_simulacao.loc[idx, 'viagens_necessarias_sim'] = viagens_sim
            df_simulacao.loc[idx, 'caminhoes_necessarios_sim'] = caminhoes_sim
            df_simulacao.loc[idx, 'viagens_por_dia_sim'] = viagens_dia_sim
        
        # Comparação
        st.subheader("📊 Comparação de Cenários")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Viagens Totais",
                f"{df_simulacao['viagens_necessarias_sim'].sum():.0f}",
                f"{df_simulacao['viagens_necessarias_sim'].sum() - df['viagens_necessarias'].sum():.0f}"
            )
        
        with col2:
            st.metric(
                "Caminhões Totais",
                f"{df_simulacao['caminhoes_necessarios_sim'].sum():.0f}",
                f"{df_simulacao['caminhoes_necessarios_sim'].sum() - df['caminhoes_necessarios'].sum():.0f}"
            )
        
        with col3:
            economia_viagens = (df['viagens_necessarias'].sum() - df_simulacao['viagens_necessarias_sim'].sum()) / df['viagens_necessarias'].sum() * 100
            st.metric(
                "Economia (%)",
                f"{economia_viagens:.1f}%"
            )

# Footer
st.markdown("---")
st.markdown("**Fox Control** - Sistema Inteligente de Gestão Logística | Desenvolvido para otimizar o transporte de grãos")


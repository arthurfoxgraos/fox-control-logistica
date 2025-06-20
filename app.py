# Board de Agendamento de Cargas - Fox Control com Banco de Dados
# Sistema de gestão logística para transporte de grãos - Versão com Persistência em BD

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import math
import psycopg2
from decimal import Decimal
import json
import os

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

def carregar_ajustes_caminhoes():
    """Carrega ajustes manuais de caminhões do banco de dados"""
    conn = conectar_banco()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT carga_id, caminhoes_manual, caminhoes_calculado, usuario, data_ajuste, observacoes
            FROM fox_control_ajustes_caminhoes 
            WHERE ativo = TRUE
            ORDER BY data_ajuste DESC
        """)
        
        ajustes = {}
        for row in cursor.fetchall():
            carga_id, caminhoes_manual, caminhoes_calculado, usuario, data_ajuste, observacoes = row
            ajustes[str(carga_id)] = {
                'caminhoes_manual': caminhoes_manual,
                'caminhoes_calculado': caminhoes_calculado,
                'usuario': usuario,
                'data_ajuste': data_ajuste.isoformat() if data_ajuste else None,
                'observacoes': observacoes
            }
        
        cursor.close()
        conn.close()
        return ajustes
        
    except Exception as e:
        st.error(f"Erro ao carregar ajustes: {e}")
        conn.close()
        return {}

def salvar_ajuste_caminhoes(carga_id, caminhoes_manual, caminhoes_calculado, usuario="sistema", observacoes=""):
    """Salva ajuste manual de caminhões no banco de dados"""
    conn = conectar_banco()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Converter tipos numpy para Python nativos para compatibilidade com PostgreSQL
        carga_id_int = int(carga_id) if hasattr(carga_id, 'item') else int(carga_id)
        caminhoes_manual_int = int(caminhoes_manual) if hasattr(caminhoes_manual, 'item') else int(caminhoes_manual)
        caminhoes_calculado_int = int(caminhoes_calculado) if hasattr(caminhoes_calculado, 'item') else int(caminhoes_calculado)
        usuario_str = str(usuario)
        observacoes_str = str(observacoes) if observacoes else ""
        
        # Inserir novo ajuste (o trigger desativará os anteriores automaticamente)
        cursor.execute("""
            INSERT INTO fox_control_ajustes_caminhoes 
            (carga_id, caminhoes_manual, caminhoes_calculado, usuario, observacoes)
            VALUES (%s, %s, %s, %s, %s)
        """, (carga_id_int, caminhoes_manual_int, caminhoes_calculado_int, usuario_str, observacoes_str))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar ajuste: {e}")
        conn.rollback()
        conn.close()
        return False

def remover_ajuste_caminhoes(carga_id):
    """Remove ajuste manual de caminhões (desativa)"""
    conn = conectar_banco()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Converter tipo numpy para Python nativo
        carga_id_int = int(carga_id) if hasattr(carga_id, 'item') else int(carga_id)
        
        # Desativar ajuste
        cursor.execute("""
            UPDATE fox_control_ajustes_caminhoes 
            SET ativo = FALSE, data_atualizacao = CURRENT_TIMESTAMP
            WHERE carga_id = %s AND ativo = TRUE
        """, (carga_id_int,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao remover ajuste: {e}")
        conn.rollback()
        conn.close()
        return False

def limpar_todos_ajustes():
    """Remove todos os ajustes manuais"""
    conn = conectar_banco()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Desativar todos os ajustes
        cursor.execute("""
            UPDATE fox_control_ajustes_caminhoes 
            SET ativo = FALSE, data_atualizacao = CURRENT_TIMESTAMP
            WHERE ativo = TRUE
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao limpar ajustes: {e}")
        conn.rollback()
        conn.close()
        return False

def obter_estatisticas_ajustes():
    """Obtém estatísticas dos ajustes do banco"""
    conn = conectar_banco()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ajustes,
                COUNT(CASE WHEN ativo THEN 1 END) as ajustes_ativos,
                COUNT(DISTINCT carga_id) as cargas_com_ajuste,
                COUNT(DISTINCT usuario) as usuarios_distintos
            FROM fox_control_ajustes_caminhoes
        """)
        
        row = cursor.fetchone()
        stats = {
            'total_ajustes': row[0] if row else 0,
            'ajustes_ativos': row[1] if row else 0,
            'cargas_com_ajuste': row[2] if row else 0,
            'usuarios_distintos': row[3] if row else 0
        }
        
        cursor.close()
        conn.close()
        return stats
        
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {e}")
        conn.close()
        return {}

def calcular_viagens_e_caminhoes(amount_allocated, distance_km, capacidade_colheita_dia=None):
    """
    Calcula número de viagens e caminhões necessários
    
    Args:
        amount_allocated: Quantidade de sacas a transportar
        distance_km: Distância em km
        capacidade_colheita_dia: Capacidade de colheita por dia (opcional)
    
    Returns:
        dict com cálculos de logística
    """
    # Número de viagens necessárias
    viagens_necessarias = math.ceil(amount_allocated / CAPACIDADE_CAMINHAO)
    
    # Tempo total por viagem (ida + volta + carga/descarga)
    tempo_viagem_horas = (distance_km * 2 / VELOCIDADE_MEDIA) + TEMPO_CARGA_DESCARGA
    
    # Quantas viagens um caminhão consegue fazer por dia
    viagens_por_dia_caminhao = math.floor(HORAS_TRABALHO_DIA / tempo_viagem_horas)
    viagens_por_dia_caminhao = max(1, viagens_por_dia_caminhao)  # Mínimo 1 viagem por dia
    
    # Número de caminhões necessários
    caminhoes_necessarios = math.ceil(viagens_necessarias / viagens_por_dia_caminhao)
    
    # Dias necessários para completar o transporte
    dias_operacao = math.ceil(viagens_necessarias / (caminhoes_necessarios * viagens_por_dia_caminhao))
    
    # Se há capacidade de colheita limitada, ajustar número de caminhões
    if capacidade_colheita_dia:
        caminhoes_por_capacidade = math.ceil(capacidade_colheita_dia / CAPACIDADE_CAMINHAO)
        caminhoes_necessarios = min(caminhoes_necessarios, caminhoes_por_capacidade)
    
    return {
        'viagens_necessarias': viagens_necessarias,
        'tempo_viagem_horas': round(tempo_viagem_horas, 2),
        'viagens_por_dia_caminhao': viagens_por_dia_caminhao,
        'caminhoes_necessarios': caminhoes_necessarios,
        'dias_operacao': dias_operacao,
        'sacas_por_viagem': CAPACIDADE_CAMINHAO
    }

@st.cache_data
def conectar_banco_dados():
    """
    Conecta ao banco de dados PostgreSQL e retorna os dados da tabela
    """
    try:
        db_pg = psycopg2.connect(**DB_CONFIG)
        
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
    
    # Carregar ajustes manuais do banco
    ajustes = carregar_ajustes_caminhoes()
    
    # Aplicar cálculos de logística para cada linha
    resultados = []
    for _, row in df.iterrows():
        calc = calcular_viagens_e_caminhoes(row['amount_allocated'], row['distance'])
        
        # Verificar se há ajuste manual para este ID
        id_str = str(row['id'])
        if id_str in ajustes:
            calc['caminhoes_necessarios'] = ajustes[id_str]['caminhoes_manual']
            calc['ajuste_manual'] = True
            calc['caminhoes_calculado'] = ajustes[id_str]['caminhoes_calculado']
            calc['usuario_ajuste'] = ajustes[id_str].get('usuario', 'N/A')
            calc['data_ajuste'] = ajustes[id_str].get('data_ajuste', 'N/A')
            calc['observacoes'] = ajustes[id_str].get('observacoes', '')
            # Recalcular dias com o número manual de caminhões
            calc['dias_operacao'] = math.ceil(calc['viagens_necessarias'] / (ajustes[id_str]['caminhoes_manual'] * calc['viagens_por_dia_caminhao']))
        else:
            calc['ajuste_manual'] = False
            calc['caminhoes_calculado'] = calc['caminhoes_necessarios']
            calc['usuario_ajuste'] = ''
            calc['data_ajuste'] = ''
            calc['observacoes'] = ''
        
        resultados.append(calc)
    
    # Adicionar colunas calculadas ao DataFrame
    calc_df = pd.DataFrame(resultados)
    df_final = pd.concat([df, calc_df], axis=1)
    
    # Adicionar cálculos adicionais
    df_final['margem_lucro'] = (df_final['profit_total'] / df_final['revenue'] * 100).round(2)
    df_final['custo_por_saca'] = (df_final['cost'] / df_final['amount_allocated']).round(2)
    df_final['receita_por_saca'] = (df_final['revenue'] / df_final['amount_allocated']).round(2)
    df_final['frete_por_saca'] = (df_final['freight'] / df_final['amount_allocated']).round(2)
    
    # Adicionar campos de agendamento (simulados - em produção viriam do banco)
    df_final['data_agendamento'] = pd.date_range(
        start=datetime.now().date(),
        periods=len(df_final),
        freq='D'
    )
    
    # Adicionar prioridade baseada na margem de lucro
    df_final['prioridade'] = pd.cut(
        df_final['margem_lucro'], 
        bins=[-float('inf'), 10, 20, float('inf')], 
        labels=['Baixa', 'Média', 'Alta']
    )
    
    # Adicionar status de agendamento
    df_final['status'] = 'Agendado'
    
    return df_final

def aplicar_filtros_ordenacao(df):
    """
    Aplica filtros e ordenação aos dados
    """
    st.header("🔍 Filtros e Ordenação")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro por data
        data_inicio = st.date_input(
            "Data Início",
            value=datetime.now().date(),
            help="Data inicial para filtrar agendamentos"
        )
        
        data_fim = st.date_input(
            "Data Fim",
            value=datetime.now().date() + timedelta(days=180),  # Expandido para 6 meses
            help="Data final para filtrar agendamentos"
        )
    
    with col2:
        # Filtro por grão
        grains_filter = st.multiselect(
            "Filtrar por Grão",
            options=df['grain'].unique(),
            default=df['grain'].unique()
        )
        
        # Filtro por prioridade
        prioridade_filter = st.multiselect(
            "Filtrar por Prioridade",
            options=df['prioridade'].unique(),
            default=df['prioridade'].unique()
        )
    
    with col3:
        # Filtro por comprador
        buyers_filter = st.multiselect(
            "Filtrar por Comprador",
            options=df['buyer'].unique(),
            default=df['buyer'].unique()  # Incluir todos os compradores por padrão
        )
    
    with col4:
        # Ordenação
        ordem_opcoes = {
            'Data Agendamento': 'data_agendamento',
            'Prioridade': 'prioridade',
            'Distância': 'distance',
            'Sacas': 'amount_allocated',
            'Margem Lucro': 'margem_lucro',
            'Frete por Saca': 'frete_por_saca',
            'Caminhões': 'caminhoes_necessarios'
        }
        
        ordenar_por = st.selectbox(
            "Ordenar por",
            options=list(ordem_opcoes.keys()),
            index=0
        )
        
        ordem_crescente = st.checkbox("Ordem Crescente", value=True)
    
    # Aplicar filtros
    df_filtered = df[
        (df['data_agendamento'] >= pd.to_datetime(data_inicio)) &
        (df['data_agendamento'] <= pd.to_datetime(data_fim)) &
        (df['grain'].isin(grains_filter)) &
        (df['prioridade'].isin(prioridade_filter)) &
        (df['buyer'].isin(buyers_filter))
    ]
    
    # Aplicar ordenação
    coluna_ordenacao = ordem_opcoes[ordenar_por]
    df_filtered = df_filtered.sort_values(
        by=coluna_ordenacao, 
        ascending=ordem_crescente
    ).reset_index(drop=True)
    
    return df_filtered

def interface_edicao_caminhoes(df_filtered):
    """
    Interface para edição do número de caminhões
    """
    st.header("🚛 Edição de Caminhões por Carga")
    
    # Obter estatísticas do banco
    stats = obter_estatisticas_ajustes()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Editar Número de Caminhões")
        
        # Seletor de carga
        if not df_filtered.empty:
            opcoes_edicao = []
            for _, row in df_filtered.iterrows():
                status_ajuste = "✏️ MANUAL" if row['ajuste_manual'] else "🔢 AUTO"
                opcao = f"ID {row['id']} - {row['buyer'][:25]}... - {row['amount_allocated']:,.0f} sacas - {status_ajuste}"
                opcoes_edicao.append(opcao)
            
            carga_selecionada_idx = st.selectbox(
                "Selecionar carga para editar",
                options=range(len(opcoes_edicao)),
                format_func=lambda x: opcoes_edicao[x],
                help="Escolha uma carga para ajustar o número de caminhões"
            )
            
            if carga_selecionada_idx is not None:
                row_selecionada = df_filtered.iloc[carga_selecionada_idx]
                id_selecionado = row_selecionada['id']
                
                # Mostrar informações da carga
                info_text = f"""
                **Carga Selecionada:**
                - **ID**: {id_selecionado}
                - **Comprador**: {row_selecionada['buyer']}
                - **Sacas**: {row_selecionada['amount_allocated']:,.0f}
                - **Distância**: {row_selecionada['distance']:.1f} km
                - **Viagens Necessárias**: {row_selecionada['viagens_necessarias']}
                - **Caminhões Calculado**: {row_selecionada['caminhoes_calculado']}
                """
                
                if row_selecionada['ajuste_manual']:
                    info_text += f"""
                - **Usuário do Ajuste**: {row_selecionada['usuario_ajuste']}
                - **Data do Ajuste**: {row_selecionada['data_ajuste'][:19] if row_selecionada['data_ajuste'] else 'N/A'}
                """
                
                st.info(info_text)
                
                # Input para novo número de caminhões
                valor_atual = row_selecionada['caminhoes_necessarios']
                novo_numero_caminhoes = st.number_input(
                    "Número de Caminhões",
                    min_value=1,
                    max_value=50,
                    value=int(valor_atual),
                    step=1,
                    help="Defina o número de caminhões para esta carga"
                )
                
                # Campo para observações
                observacoes = st.text_area(
                    "Observações (opcional)",
                    value=row_selecionada.get('observacoes', ''),
                    help="Adicione observações sobre o ajuste"
                )
                
                # Campo para usuário
                usuario = st.text_input(
                    "Usuário",
                    value="admin",
                    help="Nome do usuário que está fazendo o ajuste"
                )
                
                # Mostrar impacto da mudança
                if novo_numero_caminhoes != valor_atual:
                    viagens_por_dia = row_selecionada['viagens_por_dia_caminhao']
                    novos_dias = math.ceil(row_selecionada['viagens_necessarias'] / (novo_numero_caminhoes * viagens_por_dia))
                    
                    st.warning(f"""
                    **Impacto da Alteração:**
                    - **Dias de Operação**: {row_selecionada['dias_operacao']} → {novos_dias}
                    - **Diferença**: {novos_dias - row_selecionada['dias_operacao']:+d} dias
                    """)
                
                # Botões de ação
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("💾 Salvar Ajuste", type="primary"):
                        # Salvar ajuste no banco
                        if salvar_ajuste_caminhoes(
                            id_selecionado, 
                            novo_numero_caminhoes, 
                            int(row_selecionada['caminhoes_calculado']),
                            usuario,
                            observacoes
                        ):
                            st.success(f"✅ Ajuste salvo no banco! Caminhões para ID {id_selecionado}: {novo_numero_caminhoes}")
                            # Limpar cache para recarregar dados
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar ajuste no banco")
                
                with col_btn2:
                    if st.button("🔄 Restaurar Automático"):
                        # Remover ajuste manual do banco
                        if remover_ajuste_caminhoes(id_selecionado):
                            st.success(f"✅ Restaurado cálculo automático para ID {id_selecionado}")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Erro ao restaurar cálculo automático")
                
                with col_btn3:
                    if st.button("🗑️ Limpar Todos"):
                        # Limpar todos os ajustes do banco
                        if st.session_state.get('confirmar_limpeza', False):
                            if limpar_todos_ajustes():
                                st.success("✅ Todos os ajustes foram removidos do banco")
                                st.session_state['confirmar_limpeza'] = False
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            st.session_state['confirmar_limpeza'] = True
                            st.warning("⚠️ Clique novamente para confirmar")
    
    with col2:
        st.subheader("📊 Estatísticas do Banco")
        
        # Estatísticas dos ajustes
        total_cargas = len(df_filtered)
        cargas_ajustadas = len([row for _, row in df_filtered.iterrows() if row['ajuste_manual']])
        
        st.metric("Total de Cargas", total_cargas)
        st.metric("Cargas Ajustadas", cargas_ajustadas)
        st.metric("% Ajustadas", f"{(cargas_ajustadas/total_cargas*100):.1f}%" if total_cargas > 0 else "0%")
        
        # Estatísticas do banco
        st.subheader("🗄️ Dados do Banco")
        st.metric("Total Histórico", stats.get('total_ajustes', 0))
        st.metric("Ajustes Ativos", stats.get('ajustes_ativos', 0))
        st.metric("Usuários Distintos", stats.get('usuarios_distintos', 0))
        
        # Lista de ajustes ativos
        ajustes = carregar_ajustes_caminhoes()
        if ajustes:
            st.subheader("🔧 Ajustes Ativos")
            for id_str, ajuste in list(ajustes.items())[:5]:  # Mostrar apenas os 5 primeiros
                # Encontrar a linha correspondente
                linha = df_filtered[df_filtered['id'] == int(id_str)]
                if not linha.empty:
                    row = linha.iloc[0]
                    st.text(f"ID {id_str}: {ajuste['caminhoes_manual']} caminhões")
                    st.caption(f"{row['buyer'][:20]}... - {row['amount_allocated']:,.0f} sacas")
                    st.caption(f"Por: {ajuste.get('usuario', 'N/A')}")

# Interface principal
st.title("🚛 Fox Control - Agendamento de Cargas")
st.markdown("**Sistema de gestão logística para transporte de grãos com persistência em banco**")

# Sidebar com configurações
st.sidebar.header("⚙️ Configurações do Sistema")

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

# Carregar dados do banco
with st.spinner("🔄 Carregando dados do banco..."):
    df_raw = conectar_banco_dados()

if df_raw.empty:
    st.error("❌ Não foi possível carregar os dados do banco de dados.")
    st.stop()

# Processar dados com cálculos de logística
df = processar_dados_logistica(df_raw)

# Aplicar filtros e ordenação
df_filtered = aplicar_filtros_ordenacao(df)

# Métricas principais
st.header("📊 Resumo Executivo")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Total de Sacas", 
        f"{df_filtered['amount_allocated'].sum():,.0f}",
        help="Quantidade total de sacas a transportar"
    )

with col2:
    st.metric(
        "Total de Viagens", 
        f"{df_filtered['viagens_necessarias'].sum():,.0f}",
        help="Número total de viagens necessárias"
    )

with col3:
    st.metric(
        "Caminhões Necessários", 
        f"{df_filtered['caminhoes_necessarios'].sum():,.0f}",
        help="Número total de caminhões necessários"
    )

with col4:
    st.metric(
        "Receita Total", 
        f"R$ {df_filtered['revenue'].sum():,.0f}",
        help="Receita total de todas as operações"
    )

with col5:
    st.metric(
        "Frete Total", 
        f"R$ {df_filtered['freight'].sum():,.0f}",
        help="Custo total de frete"
    )

with col6:
    ajustes_ativos = len([row for _, row in df_filtered.iterrows() if row['ajuste_manual']])
    st.metric(
        "Ajustes Manuais", 
        f"{ajustes_ativos}",
        help="Número de cargas com ajuste manual de caminhões"
    )

# Tabs para diferentes visualizações
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Agendamento", "🚛 Editar Caminhões", "📈 Analytics", "🗺️ Rotas", "⚙️ Simulador"])

with tab1:
    st.header("📋 Cronograma de Cargas")
    
    # Funcionalidade de agendamento
    st.subheader("📅 Reagendar Cargas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Seletor de carga para reagendar
        if not df_filtered.empty:
            opcoes_reagendamento = [
                f"ID {row['id']} - {row['buyer'][:30]}... - {row['amount_allocated']:,.0f} sacas"
                for _, row in df_filtered.iterrows()
            ]
            
            carga_selecionada = st.selectbox(
                "Selecionar carga para reagendar",
                options=opcoes_reagendamento,
                help="Escolha uma carga para alterar a data de agendamento"
            )
    
    with col2:
        nova_data = st.date_input(
            "Nova data de agendamento",
            value=datetime.now().date() + timedelta(days=1),
            help="Selecione a nova data para o carregamento"
        )
        
        if st.button("📅 Reagendar"):
            st.success(f"✅ Carga reagendada para {nova_data.strftime('%d/%m/%Y')}")
    
    # Tabela principal de agendamento
    st.subheader("📊 Lista de Cargas Agendadas")
    
    # Preparar dados para exibição
    display_df = df_filtered[[
        'id', 'data_agendamento', 'prioridade', 'buyer', 'seller', 'grain', 
        'amount_allocated', 'distance', 'viagens_necessarias', 'caminhoes_necessarios', 
        'dias_operacao', 'frete_por_saca', 'margem_lucro', 'ajuste_manual', 'status'
    ]].copy()
    
    # Renomear colunas para melhor visualização
    display_df.columns = [
        'ID', 'Data', 'Prioridade', 'Comprador', 'Vendedor', 'Grão', 'Sacas', 
        'Dist.(km)', 'Viagens', 'Caminhões', 'Dias', 'Frete/Saca', 'Margem(%)', 'Manual', 'Status'
    ]
    
    # Formatar valores
    display_df['Data'] = pd.to_datetime(display_df['Data']).dt.strftime('%d/%m/%Y')
    display_df['Sacas'] = display_df['Sacas'].apply(lambda x: f"{x:,.0f}")
    display_df['Dist.(km)'] = display_df['Dist.(km)'].apply(lambda x: f"{x:.1f}")
    display_df['Frete/Saca'] = display_df['Frete/Saca'].apply(lambda x: f"R$ {x:.2f}")
    display_df['Margem(%)'] = display_df['Margem(%)'].apply(lambda x: f"{x:.1f}%")
    display_df['Comprador'] = display_df['Comprador'].apply(lambda x: x[:25] + "..." if len(x) > 25 else x)
    display_df['Vendedor'] = display_df['Vendedor'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
    display_df['Manual'] = display_df['Manual'].apply(lambda x: "✏️" if x else "🔢")
    
    # Colorir por prioridade e ajuste manual
    def colorir_linha(row):
        if row['Manual'] == "✏️":
            return ['background-color: #e6f3ff'] * len(row)  # Azul claro para ajustes manuais
        elif row['Prioridade'] == 'Alta':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Prioridade'] == 'Média':
            return ['background-color: #ffffcc'] * len(row)
        else:
            return ['background-color: #ccffcc'] * len(row)
    
    styled_df = display_df.style.apply(colorir_linha, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # Legenda
    st.caption("🔢 = Cálculo Automático | ✏️ = Ajuste Manual | 🟦 = Linha com Ajuste Manual")

with tab2:
    # Interface de edição de caminhões
    interface_edicao_caminhoes(df_filtered)

with tab3:
    st.header("📈 Analytics de Frete e Logística")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de frete por saca por comprador
        fig_frete = px.box(
            df_filtered,
            x='buyer',
            y='frete_por_saca',
            color='grain',
            title="Distribuição do Frete por Saca por Comprador",
            labels={'frete_por_saca': 'Frete por Saca (R$)', 'buyer': 'Comprador'}
        )
        fig_frete.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_frete, use_container_width=True)
        
        # Gráfico de viagens por data
        viagens_por_data = df_filtered.groupby('data_agendamento')['viagens_necessarias'].sum().reset_index()
        fig_cronograma = px.bar(
            viagens_por_data,
            x='data_agendamento',
            y='viagens_necessarias',
            title="Viagens Agendadas por Data",
            labels={'viagens_necessarias': 'Número de Viagens', 'data_agendamento': 'Data'}
        )
        st.plotly_chart(fig_cronograma, use_container_width=True)
    
    with col2:
        # Gráfico de ajustes manuais vs automáticos
        ajustes_stats = df_filtered['ajuste_manual'].value_counts()
        
        # Verificar se há dados suficientes para o gráfico de pizza
        if len(ajustes_stats) > 0 and not ajustes_stats.empty:
            # Criar labels baseados nos dados reais
            ajustes_labels = []
            ajustes_values = []
            
            for valor, count in ajustes_stats.items():
                if valor == False:
                    ajustes_labels.append('Cálculo Automático')
                else:
                    ajustes_labels.append('Ajuste Manual')
                ajustes_values.append(count)
            
            # Só criar o gráfico se houver dados válidos
            if len(ajustes_values) > 0:
                fig_ajustes = px.pie(
                    values=ajustes_values,
                    names=ajustes_labels,
                    title="Distribuição: Automático vs Manual",
                    color_discrete_map={'Cálculo Automático': '#6bcf7f', 'Ajuste Manual': '#ff6b6b'}
                )
                st.plotly_chart(fig_ajustes, use_container_width=True)
            else:
                st.info("📊 Não há dados suficientes para exibir o gráfico de distribuição.")
        else:
            st.info("📊 Não há dados de ajustes para exibir.")
        
        # Gráfico de eficiência de frete
        if not df_filtered.empty and len(df_filtered) > 0:
            fig_eficiencia_frete = px.scatter(
                df_filtered,
                x='distance',
                y='frete_por_saca',
                size='amount_allocated',
                color='ajuste_manual',
                title="Eficiência do Frete por Distância",
                labels={
                    'distance': 'Distância (km)',
                    'frete_por_saca': 'Frete por Saca (R$)',
                    'amount_allocated': 'Sacas',
                    'ajuste_manual': 'Tipo'
                },
                color_discrete_map={True: '#ff6b6b', False: '#6bcf7f'}
            )
            st.plotly_chart(fig_eficiencia_frete, use_container_width=True)
        else:
            st.info("📊 Não há dados suficientes para exibir o gráfico de eficiência.")

with tab4:
    st.header("🗺️ Otimização de Rotas por Data")
    
    # Análise de rotas por data
    st.subheader("📍 Cargas por Data e Região")
    
    # Gráfico de timeline de cargas com indicação de ajustes manuais
    if not df_filtered.empty and len(df_filtered) > 0:
        fig_timeline = px.scatter(
            df_filtered,
            x='data_agendamento',
            y='buyer',
            size='amount_allocated',
            color='ajuste_manual',
            title="Timeline de Cargas por Comprador",
            labels={
                'data_agendamento': 'Data de Agendamento',
                'buyer': 'Comprador',
                'amount_allocated': 'Sacas',
                'ajuste_manual': 'Tipo de Cálculo'
            },
            color_discrete_map={True: '#ff6b6b', False: '#6bcf7f'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("📊 Não há dados suficientes para exibir o timeline de cargas.")
    
    # Tabela de otimização
    st.subheader("🎯 Sugestões de Otimização")
    
    # Calcular score de otimização apenas se há dados
    if not df_filtered.empty and len(df_filtered) > 0:
        df_otimizacao = df_filtered.copy()
        
        # Verificar se há valores válidos para evitar divisão por zero
        max_margem = df_otimizacao['margem_lucro'].max()
        max_distance = df_otimizacao['distance'].max()
        max_amount = df_otimizacao['amount_allocated'].max()
        
        if max_margem > 0 and max_distance > 0 and max_amount > 0:
            df_otimizacao['score_otimizacao'] = (
                (df_otimizacao['margem_lucro'] / max_margem) * 0.4 +
                (1 - df_otimizacao['distance'] / max_distance) * 0.3 +
                (df_otimizacao['amount_allocated'] / max_amount) * 0.3
            ) * 100
        else:
            df_otimizacao['score_otimizacao'] = 50.0  # Score padrão
        
        otimizacao_display = df_otimizacao[['data_agendamento', 'buyer', 'amount_allocated', 
                                           'distance', 'frete_por_saca', 'margem_lucro', 
                                           'caminhoes_necessarios', 'ajuste_manual', 'score_otimizacao']].copy()
        
        otimizacao_display.columns = ['Data', 'Comprador', 'Sacas', 'Distância', 
                                      'Frete/Saca', 'Margem(%)', 'Caminhões', 'Manual', 'Score Otim.']
        
        # Ordenar por score de otimização
        otimizacao_display = otimizacao_display.sort_values('Score Otim.', ascending=False)
        
        # Formatar valores
        otimizacao_display['Data'] = pd.to_datetime(otimizacao_display['Data']).dt.strftime('%d/%m/%Y')
        otimizacao_display['Sacas'] = otimizacao_display['Sacas'].apply(lambda x: f"{x:,.0f}")
        otimizacao_display['Distância'] = otimizacao_display['Distância'].apply(lambda x: f"{x:.1f} km")
        otimizacao_display['Frete/Saca'] = otimizacao_display['Frete/Saca'].apply(lambda x: f"R$ {x:.2f}")
        otimizacao_display['Margem(%)'] = otimizacao_display['Margem(%)'].apply(lambda x: f"{x:.1f}%")
        otimizacao_display['Score Otim.'] = otimizacao_display['Score Otim.'].apply(lambda x: f"{x:.1f}")
        otimizacao_display['Comprador'] = otimizacao_display['Comprador'].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
        otimizacao_display['Manual'] = otimizacao_display['Manual'].apply(lambda x: "✏️" if x else "🔢")
        
        st.dataframe(otimizacao_display, use_container_width=True)
    else:
        st.info("📊 Não há dados suficientes para calcular otimizações.")

with tab5:
    st.header("⚙️ Simulador de Cenários de Frete")
    
    st.markdown("**Simule diferentes cenários alterando os parâmetros:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nova_capacidade = st.slider(
            "Nova Capacidade do Caminhão (sacas)",
            min_value=500,
            max_value=1500,
            value=CAPACIDADE_CAMINHAO,
            step=50
        )
        
        nova_velocidade = st.slider(
            "Nova Velocidade Média (km/h)",
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
        def calcular_simulacao(amount, distance):
            viagens = math.ceil(amount / nova_capacidade)
            tempo_viagem = (distance * 2 / nova_velocidade) + novo_tempo_carga
            viagens_dia = max(1, math.floor(novas_horas / tempo_viagem))
            caminhoes = math.ceil(viagens / viagens_dia)
            dias = math.ceil(viagens / (caminhoes * viagens_dia))
            
            return {
                'viagens_sim': viagens,
                'caminhoes_sim': caminhoes,
                'dias_sim': dias,
                'frete_por_saca_sim': (amount * (distance * 0.15)) / amount  # Simulação de novo cálculo de frete
            }
        
        # Aplicar simulação
        sim_results = []
        for _, row in df_filtered.iterrows():
            sim = calcular_simulacao(row['amount_allocated'], row['distance'])
            sim_results.append(sim)
        
        sim_df = pd.DataFrame(sim_results)
        df_sim = pd.concat([
            df_filtered[['buyer', 'amount_allocated', 'distance', 'viagens_necessarias', 
                        'caminhoes_necessarios', 'dias_operacao', 'frete_por_saca']], 
            sim_df
        ], axis=1)
        
        # Comparação
        st.subheader("📊 Comparação: Atual vs Simulado")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Viagens Totais",
                f"{df_sim['viagens_sim'].sum():,.0f}",
                delta=f"{df_sim['viagens_sim'].sum() - df_sim['viagens_necessarias'].sum():,.0f}"
            )
        
        with col2:
            st.metric(
                "Caminhões Totais",
                f"{df_sim['caminhoes_sim'].sum():,.0f}",
                delta=f"{df_sim['caminhoes_sim'].sum() - df_sim['caminhoes_necessarios'].sum():,.0f}"
            )
        
        with col3:
            st.metric(
                "Dias Médios",
                f"{df_sim['dias_sim'].mean():.1f}",
                delta=f"{df_sim['dias_sim'].mean() - df_sim['dias_operacao'].mean():.1f}"
            )
        
        with col4:
            st.metric(
                "Frete Médio/Saca",
                f"R$ {df_sim['frete_por_saca_sim'].mean():.2f}",
                delta=f"R$ {df_sim['frete_por_saca_sim'].mean() - df_sim['frete_por_saca'].mean():.2f}"
            )

# Rodapé
st.markdown("---")
st.markdown("**Fox Control** - Sistema de gestão logística com persistência em banco para o agronegócio | Dados atualizados em tempo real")


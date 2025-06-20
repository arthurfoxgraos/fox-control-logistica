# Configurações do Banco de Dados
# Edite este arquivo com suas credenciais do PostgreSQL

DB_CONFIG = {
    'host': '24.199.75.66',  # Substitua pelo seu host
    'port': 5432,
    'user': 'myuser',        # Substitua pelo seu usuário
    'password': 'mypassword', # Substitua pela sua senha
    'database': 'mydb'       # Substitua pelo seu banco
}

# Configurações da Aplicação
APP_CONFIG = {
    'title': 'Fox Control - Agendamento de Cargas',
    'icon': '🚛',
    'layout': 'wide'
}

# Constantes do Sistema
SYSTEM_CONFIG = {
    'capacidade_caminhao': 900,      # sacas por caminhão
    'velocidade_media': 60,          # km/h
    'horas_trabalho_dia': 10,        # horas por dia
    'tempo_carga_descarga': 2.0      # horas por viagem
}


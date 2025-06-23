#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de provisionamento baseado em distância mínima
"""

from pymongo import MongoClient
from bson import ObjectId
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import streamlit as st
import traceback

# Mapeia IDs de grão para nomes legíveis
GRAIN_NAMES = {
    ObjectId('5e349bed3b0fd74ea91f1488'): 'milho',
    ObjectId('5e349c053b0fd74ea91f148a'): 'sorgo'
}

# Configurações do banco de dados
DB_CONFIG = {
    'host': '24.199.75.66',
    'port': 5432,
    'user': 'myuser',
    'password': 'mypassword',
    'database': 'mydb'
}

def prepare(val):
    """Converte ObjectId para string"""
    if isinstance(val, ObjectId):
        return str(val)
    return val

class ProvisioningMinDistance:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.pg_conn = None
        self.status = "Não iniciado"
        self.progress = 0
        self.logs = []
        self.stats = {
            'total_combinations': 0,
            'total_allocated': 0,
            'total_revenue': 0,
            'total_cost': 0,
            'total_profit': 0,
            'total_freight': 0,
            'total_tax_balance': 0,
            'average_distance': 0,
            'grain_totals': {},
            'processed_combinations': 0
        }
    
    def log(self, message, level="INFO"):
        """Adiciona log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def connect_mongodb(self):
        """Conecta ao MongoDB"""
        try:
            self.mongo_client = MongoClient(
                "mongodb+srv://doadmin:5vk9a08N2tX3e64U@"
                "foxdigital-e8bf0024.mongo.ondigitalocean.com/admin?"
                "authSource=admin&replicaSet=foxdigital"
            )
            self.db = self.mongo_client['fox']
            self.log("Conectado ao MongoDB com sucesso")
            return True
        except Exception as e:
            self.log(f"Erro ao conectar MongoDB: {str(e)}", "ERROR")
            return False
    
    def connect_postgresql(self):
        """Conecta ao PostgreSQL"""
        try:
            self.pg_conn = psycopg2.connect(**DB_CONFIG)
            self.log("Conectado ao PostgreSQL com sucesso")
            return True
        except Exception as e:
            self.log(f"Erro ao conectar PostgreSQL: {str(e)}", "ERROR")
            return False
    
    def load_combinations(self):
        """Carrega combinações ordenadas por distância"""
        try:
            comb_col = self.db['provisioningsv2Combinations']
            comb_list = list(comb_col.find({}).sort('distance', 1))
            self.stats['total_combinations'] = len(comb_list)
            self.log(f"{len(comb_list)} combinações carregadas e ordenadas por distância")
            return comb_list
        except Exception as e:
            self.log(f"Erro ao carregar combinações: {str(e)}", "ERROR")
            return []
    
    def prepare_postgresql_table(self):
        """Prepara tabela no PostgreSQL"""
        try:
            cursor = self.pg_conn.cursor()
            
            # Cria tabela se não existir
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS provisioningsv2_best_scenario_distance (
              id SERIAL PRIMARY KEY,
              destination_order TEXT,
              origin_order TEXT,
              buyer TEXT,
              seller TEXT,
              grain TEXT,
              amount_allocated NUMERIC,
              revenue NUMERIC,
              cost NUMERIC,
              freight NUMERIC,
              tax_balance NUMERIC,
              profit_total NUMERIC,
              distance NUMERIC,
              from_coords FLOAT[],
              to_coords FLOAT[]
            );
            ''')
            
            # Adiciona colunas se não existirem
            cursor.execute("ALTER TABLE provisioningsv2_best_scenario_distance ADD COLUMN IF NOT EXISTS buyer TEXT;")
            cursor.execute("ALTER TABLE provisioningsv2_best_scenario_distance ADD COLUMN IF NOT EXISTS seller TEXT;")
            cursor.execute("ALTER TABLE provisioningsv2_best_scenario_distance ADD COLUMN IF NOT EXISTS from_coords FLOAT[];")
            cursor.execute("ALTER TABLE provisioningsv2_best_scenario_distance ADD COLUMN IF NOT EXISTS to_coords FLOAT[];")
            
            # Limpa dados existentes
            cursor.execute('TRUNCATE provisioningsv2_best_scenario_distance;')
            self.pg_conn.commit()
            
            self.log("Tabela PostgreSQL preparada e truncada")
            return True
        except Exception as e:
            self.log(f"Erro ao preparar tabela PostgreSQL: {str(e)}", "ERROR")
            return False
    
    def process_allocations(self, comb_list):
        """Processa alocações baseadas em distância mínima"""
        try:
            rows = []
            destination_remaining = {}
            origin_remaining = {}
            allocated_per_dest = {}
            result = {}
            
            total_revenue = total_cost = total_profit = 0
            total_freight = total_tax_balance = total_allocated = 0
            total_distance_sum = 0
            distance_count = 0
            
            self.log("=== Iniciando alocação por distância mínima ===")
            
            for idx, comb in enumerate(comb_list, start=1):
                self.progress = (idx / len(comb_list)) * 80 + 10  # 10-90%
                self.stats['processed_combinations'] = idx
                
                dist = comb.get('distance', 0)
                dest = comb['destinationOrder']
                orig = comb['originOrder']
                buyer = comb.get('buyer')
                seller = comb.get('seller')
                from_coords = comb.get('from_coords', [None, None])
                to_coords = comb.get('to_coords', [None, None])
                
                if idx % 100 == 0:  # Log a cada 100 processados
                    self.log(f"Processando {idx}/{len(comb_list)} - Dist={dist:.1f}km")
                
                # Usa amountProvisionedOriginal como base para destino
                original_amount = comb.get('amountProvisionedOriginal', comb['amountDestination'])
                destination_remaining.setdefault(dest, original_amount)
                allocated_per_dest.setdefault(dest, 0)
                origin_remaining.setdefault(orig, comb['amountOrigin'])
                
                if destination_remaining[dest] <= 0 or origin_remaining[orig] <= 0:
                    continue
                
                qty = min(destination_remaining[dest], origin_remaining[orig])
                cap = original_amount
                if allocated_per_dest[dest] + qty > cap:
                    qty = cap - allocated_per_dest[dest]
                    if qty <= 0:
                        continue
                
                # Cálculos financeiros
                rev = comb['destinationPrice'] * qty
                cost_val = comb['originPrice'] * qty
                freight = comb['freightCost'] * qty
                tax_bal = (comb['originCredit'] - comb['destinationTax']) * qty
                profit_val = comb['profit'] * qty
                
                # Atualiza saldos
                destination_remaining[dest] -= qty
                origin_remaining[orig] -= qty
                allocated_per_dest[dest] += qty
                total_allocated += qty
                total_revenue += rev
                total_cost += cost_val
                total_profit += profit_val
                total_freight += freight
                total_tax_balance += tax_bal
                
                total_distance_sum += dist
                distance_count += 1
                
                # Mapeia grão
                grain_id = comb.get('grain')
                grao_name = GRAIN_NAMES.get(grain_id) or prepare(grain_id)
                
                result.setdefault(dest, {'grao': grao_name, 'orders': []})['orders'].append({
                    'originOrder': orig, 
                    'amount': qty
                })
                
                rows.append((
                    prepare(dest),
                    prepare(orig),
                    buyer,
                    seller,
                    grao_name,
                    qty,
                    rev,
                    cost_val,
                    freight,
                    tax_bal,
                    profit_val,
                    dist,
                    from_coords,
                    to_coords
                ))
            
            # Atualiza estatísticas
            self.stats.update({
                'total_allocated': total_allocated,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'total_freight': total_freight,
                'total_tax_balance': total_tax_balance,
                'average_distance': total_distance_sum / distance_count if distance_count else 0
            })
            
            # Calcula totais por grão
            grain_totals = {}
            for data in result.values():
                grain = data['grao']
                total = sum(o['amount'] for o in data['orders'])
                grain_totals[grain] = grain_totals.get(grain, 0) + total
            self.stats['grain_totals'] = grain_totals
            
            self.log(f"Alocação finalizada: {len(rows)} registros gerados")
            self.log(f"Total alocado: {total_allocated} sacas")
            self.log(f"Distância média: {self.stats['average_distance']:.2f} km")
            
            return rows
        except Exception as e:
            self.log(f"Erro no processamento de alocações: {str(e)}", "ERROR")
            return []
    
    def save_to_postgresql(self, rows):
        """Salva resultados no PostgreSQL"""
        try:
            cursor = self.pg_conn.cursor()
            
            self.log(f"Inserindo {len(rows)} registros no PostgreSQL...")
            execute_values(cursor, '''
            INSERT INTO provisioningsv2_best_scenario_distance (
              destination_order,
              origin_order,
              buyer,
              seller,
              grain,
              amount_allocated,
              revenue,
              cost,
              freight,
              tax_balance,
              profit_total,
              distance,
              from_coords,
              to_coords
            ) VALUES %s;
            ''', rows)
            
            self.pg_conn.commit()
            self.log("Dados inseridos no PostgreSQL com sucesso")
            return True
        except Exception as e:
            self.log(f"Erro ao salvar no PostgreSQL: {str(e)}", "ERROR")
            return False
    
    def run_provisioning(self):
        """Executa provisionamento completo"""
        try:
            self.status = "Executando"
            self.progress = 0
            self.logs = []
            self.stats = {
                'total_combinations': 0,
                'total_allocated': 0,
                'total_revenue': 0,
                'total_cost': 0,
                'total_profit': 0,
                'total_freight': 0,
                'total_tax_balance': 0,
                'average_distance': 0,
                'grain_totals': {},
                'processed_combinations': 0
            }
            
            self.log("=== Iniciando provisionamento por distância mínima ===")
            
            # Conectar aos bancos
            if not self.connect_mongodb():
                self.status = "Erro"
                return False
            
            if not self.connect_postgresql():
                self.status = "Erro"
                return False
            
            # Preparar tabela PostgreSQL
            self.progress = 5
            if not self.prepare_postgresql_table():
                self.status = "Erro"
                return False
            
            # Carregar combinações
            self.progress = 10
            comb_list = self.load_combinations()
            if not comb_list:
                self.status = "Erro"
                return False
            
            # Processar alocações
            rows = self.process_allocations(comb_list)
            if not rows:
                self.status = "Erro"
                return False
            
            # Salvar no PostgreSQL
            self.progress = 90
            if not self.save_to_postgresql(rows):
                self.status = "Erro"
                return False
            
            self.progress = 100
            self.status = "Concluído"
            self.log("=== Provisionamento concluído com sucesso ===")
            
            # Log resumo final
            self.log("=== Resumo Final ===")
            self.log(f"Total sacas alocadas: {self.stats['total_allocated']}")
            self.log(f"Receita total: R$ {self.stats['total_revenue']:,.2f}")
            self.log(f"Custo total: R$ {self.stats['total_cost']:,.2f}")
            self.log(f"Lucro total: R$ {self.stats['total_profit']:,.2f}")
            self.log(f"Distância média: {self.stats['average_distance']:.2f} km")
            self.log("Total de sacas por grão:")
            for grain, qty in self.stats['grain_totals'].items():
                self.log(f"  {grain}: {qty:,} sacas")
            
            return True
            
        except Exception as e:
            self.status = "Erro"
            self.log(f"Erro geral no provisionamento: {str(e)}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            return False
        finally:
            # Fechar conexões
            if self.mongo_client:
                self.mongo_client.close()
            if self.pg_conn:
                self.pg_conn.close()

# Instância global
provisioning_min_distance = ProvisioningMinDistance()


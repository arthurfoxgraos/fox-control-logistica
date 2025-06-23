#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de sincronização de combinações entre MongoDB e PostgreSQL
"""

from pymongo import MongoClient, InsertOne
from bson import ObjectId
import psycopg2
from psycopg2.extras import execute_values
import requests
from datetime import datetime
import streamlit as st
import time
import traceback

# --- Token Mapbox ---
MAPBOX_TOKEN = "pk.your_mapbox_token_here"

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

class SyncCombinations:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.pg_conn = None
        self.status = "Não iniciado"
        self.progress = 0
        self.logs = []
        self.stats = {
            'total_operations': 0,
            'total_sales': 0,
            'total_purchases': 0,
            'total_combinations': 0,
            'distances_calculated': 0,
            'buyer_distances': {}
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
    
    def clear_old_combinations(self):
        """Remove combinações antigas"""
        try:
            comb_col = self.db['provisioningsv2Combinations']
            deleted = comb_col.delete_many({}).deleted_count
            self.log(f"Removidas {deleted} combinações antigas")
            return True
        except Exception as e:
            self.log(f"Erro ao limpar combinações: {str(e)}", "ERROR")
            return False
    
    def load_operations(self):
        """Carrega operações de venda e compra"""
        try:
            provs = list(self.db.provisioningsv2Operations.find().sort('_id', -1))
            self.stats['total_operations'] = len(provs)
            self.log(f"Encontradas {len(provs)} operações")
            
            sales, purchases = [], []
            
            for prov in provs:
                d = prov.get('destinationOrder', {})
                raw_to = d.get('to', {})
                to_id = raw_to.get('_id') if isinstance(raw_to, dict) else raw_to
                to_coords = raw_to.get('location', {}).get('coordinates')
                amount_provisioned = d.get('amountProvisioned', d.get('amount'))
                
                sales.append({
                    '_id': d.get('_id'),
                    'grain': d.get('grain'),
                    'bagPrice': d.get('bagPrice'),
                    'amount': d.get('amount'),
                    'hasPIS': d.get('hasPIS', False),
                    'buyerName': (d.get('buyer') or {}).get('name'),
                    'to_id': to_id,
                    'to_coords': to_coords,
                    'amountProvisionedOriginal': amount_provisioned
                })
                
                for o in prov.get('originOrders', []):
                    ord_ = o.get('order', {})
                    raw_from = ord_.get('from', {})
                    from_id = raw_from.get('_id') if isinstance(raw_from, dict) else raw_from
                    from_coords = raw_from.get('location', {}).get('coordinates')
                    
                    purchases.append({
                        '_id': ord_.get('_id'),
                        'grain': ord_.get('grain'),
                        'bagPrice': ord_.get('bagPrice'),
                        'amount': ord_.get('amount'),
                        'hasPIS': ord_.get('hasPIS'),
                        'sellerName': (ord_.get('seller') or {}).get('name'),
                        'from_id': from_id,
                        'from_coords': from_coords
                    })
            
            self.stats['total_sales'] = len(sales)
            self.stats['total_purchases'] = len(purchases)
            self.log(f"Separados {len(sales)} vendas e {len(purchases)} compras")
            
            return sales, purchases
        except Exception as e:
            self.log(f"Erro ao carregar operações: {str(e)}", "ERROR")
            return [], []
    
    def load_distances(self):
        """Carrega distâncias existentes"""
        try:
            distcursor = self.db.distances.find({}, {'from':1,'to':1,'inKm':1})
            distances_map = {(d['from'], d['to']): d.get('inKm',0) for d in distcursor}
            self.log(f"{len(distances_map)} distâncias carregadas na memória")
            return distances_map
        except Exception as e:
            self.log(f"Erro ao carregar distâncias: {str(e)}", "ERROR")
            return {}
    
    def get_mapbox_distance(self, frm, to):
        """Consulta distância via Mapbox se necessário"""
        try:
            fa = self.db.addresses.find_one({'_id':frm}, {'farmLocation.coordinates':1})
            ta = self.db.addresses.find_one({'_id':to}, {'farmLocation.coordinates':1})
            
            if not fa or not ta:
                return 0
            
            lon1, lat1 = fa['farmLocation']['coordinates']
            lon2, lat2 = ta['farmLocation']['coordinates']
            
            url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}?access_token={MAPBOX_TOKEN}&overview=false"
            r = requests.get(url)
            
            if r.status_code != 200:
                return 0
            
            try:
                km = r.json()['routes'][0]['distance'] / 1000
            except:
                km = 0
            
            # Salva no MongoDB
            self.db.distances.update_one(
                {'from':frm,'to':to},
                {'$set':{'inKm':km,'isActive':True,'updatedAt':datetime.utcnow()},
                 '$setOnInsert':{'createdAt':datetime.utcnow(),'__v':0}},
                upsert=True
            )
            
            self.stats['distances_calculated'] += 1
            return km
        except Exception as e:
            self.log(f"Erro ao consultar Mapbox: {str(e)}", "ERROR")
            return 0
    
    def generate_combinations(self, sales, purchases, distances_map):
        """Gera e persiste combinações"""
        try:
            comb_col = self.db['provisioningsv2Combinations']
            buyer_distances = {}
            ops = []
            count = 0
            
            total_pairs = len(sales) * len(purchases)
            processed = 0
            
            for sale in sales:
                for pur in purchases:
                    processed += 1
                    self.progress = (processed / total_pairs) * 100
                    
                    if sale['grain'] != pur['grain']:
                        continue
                    
                    frm, to = pur['from_id'], sale['to_id']
                    dist = distances_map.get((frm, to), 0)
                    
                    if dist == 0:
                        dist = self.get_mapbox_distance(frm, to)
                        distances_map[(frm, to)] = dist
                    
                    freight = max(dist * 0.024, 1.50)
                    oricredit = pur['bagPrice'] * 0.0925 if pur['hasPIS'] else 0
                    dentax = sale['bagPrice'] * 0.0925 if sale['hasPIS'] else 0
                    efforig = pur['bagPrice'] + freight + (dentax - oricredit)
                    profit = sale['bagPrice'] - efforig
                    maxprov = sale['amountProvisionedOriginal']
                    allocated = min(maxprov, pur['amount'])
                    
                    buyer = sale['buyerName'] or 'Desconhecido'
                    buyer_distances.setdefault(buyer, []).append(dist)
                    
                    doc = {
                        'destinationOrder': ObjectId(sale['_id']),
                        'originOrder': ObjectId(pur['_id']),
                        'seller': pur['sellerName'],
                        'buyer': sale['buyerName'],
                        'destinationPrice': sale['bagPrice'],
                        'originPrice': pur['bagPrice'],
                        'amountDestination': sale['amount'],
                        'amountOrigin': pur['amount'],
                        'freightCost': freight,
                        'originCredit': oricredit,
                        'destinationTax': dentax,
                        'effectiveOriginCost': efforig,
                        'profit': profit,
                        'grain': ObjectId(sale['grain']),
                        'distance': dist,
                        'from_coords': pur.get('from_coords'),
                        'to_coords': sale.get('to_coords'),
                        'amountProvisionedOriginal': maxprov,
                        'amountAllocatedOriginal': allocated,
                        'paymentDaysAfterDelivery': None,
                        'financialCost': 0
                    }
                    ops.append(InsertOne(doc))
                    count += 1
            
            self.stats['total_combinations'] = count
            self.stats['buyer_distances'] = buyer_distances
            self.log(f"Geradas {count} combinações")
            
            if ops:
                self.log(f"Inserindo {len(ops)} combinações (bulk_write)")
                res = comb_col.bulk_write(ops)
                self.log(f"Bulk write concluído: {res.inserted_count} inseridos")
                
                # Log distâncias médias por comprador
                self.log("=== Distância média por comprador ===")
                for buyer, dists in buyer_distances.items():
                    avg = sum(dists)/len(dists) if dists else 0
                    self.log(f"  {buyer}: {avg:.2f} km em {len(dists)} rotas")
            else:
                self.log("Nenhuma combinação para inserir", "WARNING")
            
            return True
        except Exception as e:
            self.log(f"Erro ao gerar combinações: {str(e)}", "ERROR")
            return False
    
    def run_sync(self):
        """Executa sincronização completa"""
        try:
            self.status = "Executando"
            self.progress = 0
            self.logs = []
            self.stats = {
                'total_operations': 0,
                'total_sales': 0,
                'total_purchases': 0,
                'total_combinations': 0,
                'distances_calculated': 0,
                'buyer_distances': {}
            }
            
            self.log("=== Iniciando sincronização de combinações ===")
            
            # Conectar aos bancos
            if not self.connect_mongodb():
                self.status = "Erro"
                return False
            
            if not self.connect_postgresql():
                self.status = "Erro"
                return False
            
            # Limpar combinações antigas
            self.progress = 10
            if not self.clear_old_combinations():
                self.status = "Erro"
                return False
            
            # Carregar operações
            self.progress = 20
            sales, purchases = self.load_operations()
            if not sales or not purchases:
                self.status = "Erro"
                return False
            
            # Carregar distâncias
            self.progress = 30
            distances_map = self.load_distances()
            
            # Gerar combinações
            self.progress = 40
            if not self.generate_combinations(sales, purchases, distances_map):
                self.status = "Erro"
                return False
            
            self.progress = 100
            self.status = "Concluído"
            self.log("=== Sincronização concluída com sucesso ===")
            return True
            
        except Exception as e:
            self.status = "Erro"
            self.log(f"Erro geral na sincronização: {str(e)}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            return False
        finally:
            # Fechar conexões
            if self.mongo_client:
                self.mongo_client.close()
            if self.pg_conn:
                self.pg_conn.close()

# Instância global
sync_combinations = SyncCombinations()


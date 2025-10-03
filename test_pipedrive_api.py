#!/usr/bin/env python3
"""
Script simples para buscar negócios no Pipedrive e salvar o JSON bruto da resposta
"""
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv('backend/.env')

# Configurações da API
PIPEDRIVE_API_KEY = os.getenv('PIPEDRIVE_API_KEY')
PIPEDRIVE_DOMAIN = os.getenv('PIPEDRIVE_DOMAIN')
BASE_URL = f"https://{PIPEDRIVE_DOMAIN}.pipedrive.com/api/v1"

def buscar_detalhes_organizacao(org_id):
    """Busca detalhes COMPLETOS de uma organização (onde pode estar o CNPJ!)"""
    print(f"\n{'='*80}")
    print(f"BUSCANDO DETALHES DA ORGANIZAÇÃO ID: {org_id}")
    print(f"{'='*80}")
    
    params = {
        'api_token': PIPEDRIVE_API_KEY
    }
    
    try:
        url = f"{BASE_URL}/organizations/{org_id}"
        print(f"URL: {url}")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Salva o JSON da organização
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pipedrive_organization_{org_id}_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Detalhes da organização salvos em: {filename}")
        
        # Mostra TODOS os campos da organização
        if data.get('data'):
            org_data = data['data']
            print(f"\n📋 TODOS OS CAMPOS DA ORGANIZAÇÃO (AQUI DEVE ESTAR O CNPJ!):")
            print(f"Total de campos: {len(org_data.keys())}\n")
            
            for key in sorted(org_data.keys()):
                valor = org_data[key]
                if isinstance(valor, (str, int, float, bool)):
                    print(f"  - {key}: {valor}")
                elif valor is None:
                    print(f"  - {key}: null")
                elif isinstance(valor, dict):
                    print(f"  - {key}: {{dict com {len(valor)} campos}}")
                elif isinstance(valor, list):
                    print(f"  - {key}: [lista com {len(valor)} itens]")
                else:
                    print(f"  - {key}: {type(valor)}")
        
        return data
        
    except Exception as e:
        print(f"\n❌ Erro ao buscar organização: {e}")
        return None

def buscar_detalhes_negocio(deal_id):
    """Busca detalhes COMPLETOS de um negócio específico"""
    print(f"\n{'='*80}")
    print(f"BUSCANDO DETALHES COMPLETOS DO NEGÓCIO ID: {deal_id}")
    print(f"{'='*80}")
    
    params = {
        'api_token': PIPEDRIVE_API_KEY,
        'get_all_custom_fields': True  # CRÍTICO: Pega todos os campos personalizados!
    }
    
    try:
        url = f"{BASE_URL}/deals/{deal_id}"
        print(f"URL: {url}")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Salva o JSON dos detalhes
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pipedrive_deal_details_{deal_id}_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Detalhes completos salvos em: {filename}")
        
        # Mostra TODOS os campos
        if data.get('data'):
            deal_data = data['data']
            print(f"\n📋 TODOS OS CAMPOS DO NEGÓCIO (INCLUINDO PERSONALIZADOS):")
            print(f"Total de campos: {len(deal_data.keys())}\n")
            
            for key in sorted(deal_data.keys()):
                valor = deal_data[key]
                if isinstance(valor, (str, int, float, bool)):
                    print(f"  - {key}: {valor}")
                elif valor is None:
                    print(f"  - {key}: null")
                elif isinstance(valor, dict):
                    print(f"  - {key}: {{dict com {len(valor)} campos}}")
                elif isinstance(valor, list):
                    print(f"  - {key}: [lista com {len(valor)} itens]")
                else:
                    print(f"  - {key}: {type(valor)}")
            
            # AGORA BUSCA A ORGANIZAÇÃO!
            org_id = deal_data.get('org_id')
            if org_id:
                if isinstance(org_id, dict):
                    org_id = org_id.get('value')
                
                print(f"\n🏢 Encontrado org_id: {org_id}")
                buscar_detalhes_organizacao(org_id)
            else:
                print(f"\n⚠️  Negócio sem organização vinculada")
        
        return data
        
    except Exception as e:
        print(f"\n❌ Erro ao buscar detalhes: {e}")
        return None

def buscar_negocios(nome):
    """Busca negócios por nome e salva o JSON"""
    print(f"Buscando por: {nome if nome else 'TODOS'}")
    print(f"API URL: {BASE_URL}")
    
    # Parâmetros da busca
    params = {
        'api_token': PIPEDRIVE_API_KEY,
        'start': 0,
        'limit': 5,  # Limita a 5 para não sobrecarregar
        'get_all_custom_fields': True,
        'get_summary': True
    }
    
    if nome:
        params['term'] = nome
    
    try:
        # Faz a requisição
        print(f"\nFazendo requisição para: {BASE_URL}/deals")
        response = requests.get(f"{BASE_URL}/deals", params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Salva o JSON completo da lista
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pipedrive_list_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Lista de negócios salva em: {filename}")
        print(f"Total de negócios retornados: {len(data.get('data', []))}")
        
        # Busca detalhes do primeiro negócio
        if data.get('data') and len(data['data']) > 0:
            primeiro = data['data'][0]
            deal_id = primeiro.get('id')
            
            print(f"\n🔍 Buscando detalhes completos do negócio ID: {deal_id}")
            buscar_detalhes_negocio(deal_id)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return None

if __name__ == '__main__':
    print("="*80)
    print("TESTE API PIPEDRIVE - BUSCAR NEGÓCIOS")
    print("="*80)
    
    # Solicita o nome
    nome = input("\nDigite o nome para buscar (ou ENTER para buscar todos): ").strip()
    
    # Busca
    resultado = buscar_negocios(nome if nome else "")
    
    if resultado:
        print("\n✅ Processo concluído!")
        print("Verifique o arquivo JSON gerado para ver todos os campos.")
    else:
        print("\n❌ Falha ao buscar dados.")

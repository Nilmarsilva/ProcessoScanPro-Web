from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import pandas as pd

from app.services.pipedrive import PipedriveAPI

router = APIRouter(prefix="/api/pipedrive", tags=["pipedrive"])

def extrair_cpf_cnpj(negocio: Dict, api: PipedriveAPI) -> tuple:
    """Extrai CPF e CNPJ dos campos personalizados do negócio"""
    import json
    cpf = ''
    cnpj = ''
    
    # Log para debug - mostra o JSON completo do negócio
    print(f"\n{'='*80}")
    print(f"[DEBUG] JSON COMPLETO DO NEGÓCIO ID: {negocio.get('id')}")
    print(json.dumps(negocio, indent=2, ensure_ascii=False))
    print(f"{'='*80}\n")
    
    print(f"[DEBUG] Chaves disponíveis no negócio: {list(negocio.keys())}")
    
    # Tenta extrair CPF
    if api.cpf_field_id in negocio:
        cpf = negocio.get(api.cpf_field_id, '')
        print(f"[DEBUG] CPF encontrado direto: {cpf}")
    
    # Tenta em custom_fields
    if not cpf:
        custom_fields = negocio.get('custom_fields', {})
        cpf = custom_fields.get(api.cpf_field_id, '')
        if cpf:
            print(f"[DEBUG] CPF encontrado em custom_fields: {cpf}")
    
    # Tenta CNPJ se houver ID configurado
    if api.cnpj_field_id:
        print(f"[DEBUG] Buscando CNPJ com ID: {api.cnpj_field_id}")
        if api.cnpj_field_id in negocio:
            cnpj = negocio.get(api.cnpj_field_id, '')
            print(f"[DEBUG] CNPJ encontrado direto: {cnpj}")
        if not cnpj:
            custom_fields = negocio.get('custom_fields', {})
            print(f"[DEBUG] Custom fields disponíveis: {list(custom_fields.keys()) if custom_fields else 'Nenhum'}")
            cnpj = custom_fields.get(api.cnpj_field_id, '')
            if cnpj:
                print(f"[DEBUG] CNPJ encontrado em custom_fields: {cnpj}")
            else:
                print(f"[DEBUG] CNPJ NÃO encontrado em custom_fields")
    
    print(f"[DEBUG] Resultado final - CPF: {cpf}, CNPJ: {cnpj}")
    return cpf, cnpj

@router.get("/funis")
async def listar_funis():
    """
    Lista todos os funis (pipelines) disponíveis no Pipedrive
    """
    try:
        api = PipedriveAPI()
        funis = api.listar_funis()
        return {
            "success": True,
            "funis": funis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filtros")
async def listar_filtros():
    """
    Lista todos os filtros disponíveis no Pipedrive
    Filtra apenas os que contêm '.API' no nome
    """
    try:
        api = PipedriveAPI()
        todos_filtros = api.listar_filtros()
        
        # Filtra apenas os que contêm '.API' no nome
        filtros_api = [f for f in todos_filtros if '.API' in f.get('name', '')]
        
        return {
            "success": True,
            "filtros": filtros_api
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/carregar-negocios")
async def carregar_negocios(
    funil_id: Optional[int] = None,
    filtro_id: Optional[int] = None
):
    """
    Carrega negócios do Pipedrive com base nos filtros
    """
    try:
        api = PipedriveAPI()
        todos_negocios = []
        
        if filtro_id:
            # Carrega com filtro específico
            start = 0
            limit = 500
            tem_mais = True
            
            while tem_mais:
                resultado = api.buscar_negocios_por_filtro_paginado(
                    filter_id=filtro_id,
                    pipeline_id=funil_id,
                    start=start,
                    limit=limit
                )
                
                negocios = resultado.get('negocios', [])
                todos_negocios.extend(negocios)
                
                tem_mais = resultado.get('tem_proxima', False)
                start += limit
                
                # Limita para evitar requisições infinitas
                if len(todos_negocios) >= 10000:
                    break
        else:
            # Carrega todos os negócios
            start = 0
            limit = 500
            tem_mais = True
            
            while tem_mais:
                resultado = api.listar_negocios_paginado(
                    start=start,
                    limit=limit,
                    pipeline_id=funil_id
                )
                
                negocios = resultado.get('negocios', [])
                todos_negocios.extend(negocios)
                
                tem_mais = resultado.get('tem_proxima', False)
                start += limit
                
                if len(todos_negocios) >= 10000:
                    break
        
        # Processa os negócios para formato simplificado
        # Cache de organizações e pessoas para evitar múltiplas requisições
        org_cache = {}
        person_cache = {}
        
        negocios_processados = []
        for negocio in todos_negocios:
            # Extrai nome da pessoa (pode vir como string ou objeto)
            person_id_data = negocio.get('person_id')
            if isinstance(person_id_data, dict):
                pessoa = person_id_data.get('name', '')
                person_id = person_id_data.get('value') or person_id_data.get('id')
            else:
                pessoa = negocio.get('person_name', '')
                person_id = person_id_data
            
            # Extrai nome da organização (pode vir como string ou objeto)
            org_id = negocio.get('org_id')
            if isinstance(org_id, dict):
                org = org_id.get('name', '')
            else:
                org = negocio.get('org_name', '')
            
            # Extrai nome do responsável (pode vir como objeto)
            owner_id = negocio.get('owner_id')
            if isinstance(owner_id, dict):
                owner = owner_id.get('name', '')
            else:
                owner = negocio.get('owner_name', '')
            
            # Busca CPF da pessoa (com cache)
            cpf = ''
            if person_id:
                try:
                    # Verifica se já está no cache
                    if person_id in person_cache:
                        cpf = person_cache[person_id]
                    else:
                        # Busca detalhes da pessoa
                        person_response = api.session.get(
                            f"{api.base_url}/persons/{person_id}",
                            params={'api_token': api.api_token}
                        )
                        person_response.raise_for_status()
                        person_data = person_response.json()
                        
                        if person_data and person_data.get('success') and person_data.get('data'):
                            person_details = person_data['data']
                            # Extrai CPF do campo personalizado
                            cpf = person_details.get(api.cpf_field_id, '')
                            # Armazena no cache
                            person_cache[person_id] = cpf
                except Exception as e:
                    print(f"[DEBUG] Erro ao buscar pessoa {person_id}: {e}")
            
            # Busca CNPJ na organização (com cache)
            cnpj = ''
            org_id_data = negocio.get('org_id')
            if org_id_data:
                try:
                    # Extrai o ID da organização
                    if isinstance(org_id_data, dict):
                        org_id = org_id_data.get('value') or org_id_data.get('id')
                    else:
                        org_id = org_id_data
                    
                    if org_id:
                        # Verifica se já está no cache
                        if org_id in org_cache:
                            cnpj = org_cache[org_id]
                        else:
                            # Busca detalhes da organização
                            org_response = api.session.get(
                                f"{api.base_url}/organizations/{org_id}",
                                params={'api_token': api.api_token}
                            )
                            org_response.raise_for_status()
                            org_data = org_response.json()
                            
                            if org_data and org_data.get('success') and org_data.get('data'):
                                org_details = org_data['data']
                                # Extrai CNPJ do campo personalizado
                                cnpj = org_details.get(api.cnpj_field_id, '')
                                # Armazena no cache
                                org_cache[org_id] = cnpj
                except Exception as e:
                    print(f"[DEBUG] Erro ao buscar organização: {e}")
            
            negocios_processados.append({
                'id': negocio.get('id'),
                'title': negocio.get('title', ''),
                'person_name': pessoa,
                'cpf': cpf,
                'org_name': org,
                'cnpj': cnpj,
                'status': negocio.get('status', ''),
                'value': negocio.get('value', 0),
                'currency': negocio.get('currency', 'BRL'),
                'add_time': negocio.get('add_time', ''),
                'stage_id': negocio.get('stage_id', ''),
                'pipeline_id': negocio.get('pipeline_id', ''),
                'owner_name': owner
            })
        
        return {
            "success": True,
            "total": len(negocios_processados),
            "negocios": negocios_processados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/buscar-nome")
async def buscar_por_nome(
    termo: str
):
    """
    Busca negócios por nome/título usando a API de busca do Pipedrive
    """
    try:
        api = PipedriveAPI()
        
        # Usa o método buscar_por_nome que faz a busca correta
        negocios = api.buscar_por_nome(termo, case_sensitive=False)
        
        # Log para debug - mostra JSON do primeiro negócio
        import json
        if negocios:
            print(f"\n{'='*80}")
            print(f"[DEBUG BUSCAR NOME] JSON DO PRIMEIRO NEGÓCIO:")
            print(json.dumps(negocios[0], indent=2, ensure_ascii=False))
            print(f"{'='*80}\n")
        
        # Processa os negócios para formato simplificado
        negocios_processados = []
        for negocio in negocios:
            # O método buscar_por_nome já retorna CPF e CNPJ processados
            # Não precisa buscar novamente
            negocios_processados.append({
                'id': negocio.get('id'),
                'title': negocio.get('titulo', ''),  # Campo correto: 'titulo'
                'person_name': negocio.get('pessoa', ''),  # Campo correto: 'pessoa'
                'cpf': negocio.get('cpf', ''),
                'org_name': negocio.get('organization', ''),  # Campo correto: 'organization'
                'cnpj': negocio.get('cnpj', ''),  # Já vem do método buscar_por_nome
                'status': negocio.get('status', ''),
                'value': negocio.get('valor', 0),  # Campo correto: 'valor'
                'currency': negocio.get('currency', 'BRL'),
                'add_time': negocio.get('add_time', ''),
                'stage_id': negocio.get('stage_id', ''),
                'pipeline_id': negocio.get('pipeline_id', ''),
                'owner_name': negocio.get('owner_name', '')
            })
        
        return {
            "success": True,
            "total": len(negocios_processados),
            "negocios": negocios_processados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

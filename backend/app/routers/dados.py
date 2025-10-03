from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
import pandas as pd

# Importa as classes das APIs locais
from app.services.pipedrive import PipedriveAPI
from app.services.assertiva import AssertiveAPI
from app.services.invertexto import InvertextoAPI

router = APIRouter(prefix="/api/dados", tags=["dados"])

@router.post("/check-pipedrive")
async def check_pipedrive(
    data: List[Dict[str, Any]],
    coluna_nome: str,
    coluna_cpf: str,
    coluna_org: str = None
):
    """
    Verifica se os CPFs existem no Pipedrive usando validação tripla
    """
    try:
        api = PipedriveAPI()
        df = pd.DataFrame(data)
        
        # Adiciona coluna de resultado
        df['Existe_No_Pipedrive'] = False
        cpf_field_id = "e3c63a9658469cbb216157a807cadcf263637383"
        
        cpfs_encontrados = 0
        resultados = []
        
        for index, row in df.iterrows():
            nome = str(row[coluna_nome]).strip()
            cpf = str(row[coluna_cpf]).strip()
            
            if not nome or not cpf or pd.isna(nome) or pd.isna(cpf):
                continue
                
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            if len(cpf_limpo) < 11:
                continue
            
            # Busca no Pipedrive
            try:
                org_nome = str(row[coluna_org]).strip() if coluna_org else None
                pessoas = api.buscar_pessoa_por_nome(nome)
                
                for pessoa in pessoas:
                    cpf_pipedrive = pessoa.get(cpf_field_id, '')
                    cpf_pipe_limpo = ''.join(filter(str.isdigit, str(cpf_pipedrive)))
                    
                    if cpf_pipe_limpo == cpf_limpo:
                        df.at[index, 'Existe_No_Pipedrive'] = True
                        cpfs_encontrados += 1
                        resultados.append({
                            'nome': nome,
                            'cpf': cpf,
                            'encontrado': True
                        })
                        break
            except Exception as e:
                print(f"Erro ao verificar {nome}: {e}")
                
        return {
            "success": True,
            "cpfs_encontrados": cpfs_encontrados,
            "total": len(df),
            "data": df.to_dict('records'),
            "resultados": resultados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assertiva-cnpj")
async def assertiva_cnpj(
    data: List[Dict[str, Any]],
    coluna_cnpj: str
):
    """
    Consulta CNPJs na API Assertiva
    """
    try:
        api = AssertiveAPI()
        df = pd.DataFrame(data)
        
        # Adiciona colunas de resultado
        campos = ['Razão Social', 'Endereço', 'Situação']
        for campo in campos:
            if campo not in df.columns:
                df[campo] = ''
        
        encontrados = 0
        erros = 0
        
        for index, row in df.iterrows():
            cnpj_raw = str(row[coluna_cnpj]).strip()
            cnpj_clean = ''.join(filter(str.isdigit, cnpj_raw))
            
            if len(cnpj_clean) != 14:
                continue
                
            try:
                resp = api.consultar_cnpj(cnpj_clean)
                encontrados += 1
                
                dados = resp.get('resposta', {})
                dados_cad = dados.get('dadosCadastrais', {})
                
                df.at[index, 'Razão Social'] = dados_cad.get('razaoSocial', '')
                df.at[index, 'Situação'] = dados_cad.get('situacaoCadastral', '')
                
                enderecos = dados.get('enderecos', [])
                if enderecos and isinstance(enderecos, list):
                    end = enderecos[0]
                    endereco = f"{end.get('logradouro', '')} {end.get('numero', '')} {end.get('bairro', '')} {end.get('cidade', '')} - {end.get('uf', '')}".strip()
                    df.at[index, 'Endereço'] = endereco
                    
            except Exception as e:
                erros += 1
                print(f"Erro ao consultar {cnpj_raw}: {e}")
        
        return {
            "success": True,
            "encontrados": encontrados,
            "erros": erros,
            "total": len(df),
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invertexto-cnpj")
async def invertexto_cnpj(
    data: List[Dict[str, Any]],
    coluna_cnpj: str
):
    """
    Consulta CNPJs na API Invertexto
    """
    try:
        api = InvertextoAPI()
        df = pd.DataFrame(data)
        
        # Adiciona colunas de resultado
        if 'Nome Fantasia' not in df.columns:
            df['Nome Fantasia'] = ''
        if 'Situação' not in df.columns:
            df['Situação'] = ''
            
        encontrados = 0
        erros = 0
        
        for index, row in df.iterrows():
            cnpj_raw = str(row[coluna_cnpj]).strip()
            cnpj_clean = ''.join(filter(str.isdigit, cnpj_raw))
            
            if len(cnpj_clean) != 14:
                continue
                
            try:
                dados = api.consultar_cnpj(cnpj_clean)
                encontrados += 1
                
                df.at[index, 'Nome Fantasia'] = dados.get('fantasia', '')
                df.at[index, 'Situação'] = dados.get('situacao', '')
                    
            except Exception as e:
                erros += 1
                print(f"Erro ao consultar {cnpj_raw}: {e}")
        
        return {
            "success": True,
            "encontrados": encontrados,
            "erros": erros,
            "total": len(df),
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

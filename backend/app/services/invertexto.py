#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para integração com a API da Invertexto para consulta de CNPJ.
Serve como uma alternativa à API da Assertiva.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('invertexto')

class InvertextoAPI:
    """Classe para gerenciar a integração com a API da Invertexto.
    Fornece métodos para consultar informações de CNPJ."""
    
    def __init__(self, token=None):
        """Inicializa a conexão com a API da Invertexto usando o token fornecido ou do ambiente"""
        # Token da API
        self.token = token or "20100|FzvEqoOOa3I8CffxwAAoSh0jr5cT0DEX"
        self.base_url = "https://api.invertexto.com/v1"
        
        try:
            self.session = requests.Session()
            self.session.headers.update({
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            })
            logger.info("Conexão com Invertexto configurada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao configurar conexão com Invertexto: {str(e)}")
            raise
    
    def consultar_cnpj(self, cnpj: str) -> Dict:
        """
        Consulta um CNPJ na API da Invertexto.
        
        Args:
            cnpj: CNPJ a ser consultado (pode conter formatação)
            
        Returns:
            Dicionário com os dados da consulta
        """
        try:
            # Remove caracteres não numéricos do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            if not cnpj_limpo or len(cnpj_limpo) != 14:
                error_msg = f"CNPJ inválido para consulta: '{cnpj}'"
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"[INVERTEXTO] Buscando CNPJ: '{cnpj}' (limpo: '{cnpj_limpo}')")
            
            # Endpoint para consulta de CNPJ
            cnpj_endpoint = f"{self.base_url}/cnpj/{cnpj_limpo}"
            
            # Parâmetros da consulta (token pode ser enviado como parâmetro ou no header)
            params = {
                'token': self.token
            }
            
            # Faz a requisição de consulta
            response = self.session.get(
                cnpj_endpoint,
                params=params
            )
            
            # Verifica se a consulta foi bem-sucedida
            response.raise_for_status()
            
            # Processa a resposta
            resposta_json = response.json()
            
            # Salva a resposta em um arquivo para análise posterior (opcional)
            with open('ultima_resposta_invertexto_cnpj.json', 'w', encoding='utf-8') as f:
                json.dump(resposta_json, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[INVERTEXTO] CNPJ {cnpj_limpo} consultado com sucesso")
            return resposta_json
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"[INVERTEXTO] Erro HTTP ao consultar CNPJ {cnpj}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[INVERTEXTO] Erro ao consultar CNPJ {cnpj}: {str(e)}")
            raise
    
    def consultar_cnpj_detalhado(self, cnpj: str) -> Dict:
        """
        Consulta um CNPJ na API da Invertexto com logs detalhados para debug.
        
        Args:
            cnpj: CNPJ a ser consultado (pode conter formatação)
            
        Returns:
            Dicionário com os dados da consulta
        """
        try:
            print("\n" + "=" * 50)
            print("CONSULTA DE CNPJ NA API INVERTEXTO")
            print("=" * 50 + "\n")
            
            # Remove caracteres não numéricos do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            if not cnpj_limpo or len(cnpj_limpo) != 14:
                error_msg = f"CNPJ inválido para consulta: '{cnpj}'"
                print(f"❌ {error_msg}")
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            print(f"CNPJ a ser consultado: {cnpj_limpo}")
            
            # Endpoint para consulta de CNPJ
            cnpj_endpoint = f"{self.base_url}/cnpj/{cnpj_limpo}"
            
            # Parâmetros da consulta
            params = {
                'token': self.token
            }
            
            print(f"URL de consulta: {cnpj_endpoint}")
            print(f"Token: {self.token[:10]}...")
            
            # Headers para a requisição
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            # Log para debug
            logger.info(f"Consultando CNPJ em: {cnpj_endpoint}")
            logger.info(f"Parâmetros: {params}")
            
            # Faz a requisição de consulta
            print("\nEnviando requisição...")
            cnpj_response = requests.get(
                cnpj_endpoint,
                headers=headers,
                params=params
            )
            
            # Exibe informações sobre a resposta da consulta
            print(f"\nResposta da consulta de CNPJ:")
            print(f"Status code: {cnpj_response.status_code}")
            logger.info(f"Status code da resposta: {cnpj_response.status_code}")
            
            # Verifica se a consulta foi bem-sucedida
            cnpj_response.raise_for_status()
            
            # Tenta formatar a resposta como JSON para melhor visualização
            try:
                resposta_json = cnpj_response.json()
                print("\nResposta completa (formatada):")
                print(json.dumps(resposta_json, indent=2, ensure_ascii=False))
                
                # Salva a resposta em um arquivo para análise posterior
                with open('ultima_resposta_invertexto_cnpj.json', 'w', encoding='utf-8') as f:
                    json.dump(resposta_json, f, indent=2, ensure_ascii=False)
                print("\nResposta salva no arquivo: ultima_resposta_invertexto_cnpj.json")
                
                logger.info(f"CNPJ {cnpj_limpo} consultado com sucesso")
                return resposta_json
                
            except json.JSONDecodeError:
                print("\nResposta completa (não é um JSON válido):")
                print(cnpj_response.text)
                logger.error(f"Resposta não é um JSON válido: {cnpj_response.text}")
                raise Exception("Resposta da API não é um JSON válido")
            
        except Exception as e:
            error_msg = f"Erro ao consultar CNPJ {cnpj}: {str(e)}"
            print(f"\n❌ {error_msg}")
            logger.error(error_msg)
            raise
    
    def processar_registros_cnpj(self, registros: List[Dict]) -> List[Dict]:
        """Processa uma lista de registros usando a API da Invertexto para consulta de CNPJ.
        
        Args:
            registros: Lista de dicionários contendo os dados dos registros a serem processados
            
        Returns:
            Lista de registros processados com os resultados da API
        """
        try:
            if not registros:
                logger.warning("Nenhum registro para processar")
                return []
            
            resultados = []
            for registro in registros:
                try:
                    # Extrai o CNPJ do registro
                    cnpj = registro.get('CNPJ', '').strip()
                    if not cnpj:
                        logger.warning(f"CNPJ não encontrado no registro: {registro}")
                        continue
                    
                    # Consulta o CNPJ na API
                    data = self.consultar_cnpj(cnpj)
                    
                    # Processa o resultado
                    resultado = {
                        **registro,
                        'status_invertexto': 'sucesso',
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'resultado_invertexto': data
                    }
                    resultados.append(resultado)
                    logger.info(f"Registro processado com sucesso: {cnpj}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar registro {registro}: {str(e)}")
                    resultado = {
                        **registro,
                        'status_invertexto': 'erro',
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'erro': str(e)
                    }
                    resultados.append(resultado)
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro ao processar registros de CNPJ: {str(e)}")
            raise


# Função para teste rápido da API
if __name__ == "__main__":
    # CNPJ para teste
    cnpj_teste = "23035415000104"  # CNPJ do exemplo da documentação
    
    try:
        # Cria uma instância da API
        api = InvertextoAPI()
        
        # Consulta o CNPJ
        print(f"Consultando CNPJ: {cnpj_teste}")
        resultado = api.consultar_cnpj_detalhado(cnpj_teste)
        
        # Exibe informações básicas
        print("\nInformações básicas:")
        print(f"Razão Social: {resultado.get('razao_social', 'N/A')}")
        print(f"Nome Fantasia: {resultado.get('nome_fantasia', 'N/A')}")
        print(f"Situação: {resultado.get('situacao', {}).get('nome', 'N/A')}")
        
    except Exception as e:
        print(f"Erro ao testar API: {str(e)}")

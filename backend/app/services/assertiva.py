import os
from datetime import datetime
import logging
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import time
from urllib.parse import urljoin
from pathlib import Path

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('assertiva')

# Diretório seguro para salvar última resposta da Assertiva
RESPONSES_DIR = os.path.join(os.getenv("LOCALAPPDATA") or os.path.join(Path.home(), "Documents"), "ProcessoScanPro", "assertiva_respostas")
os.makedirs(RESPONSES_DIR, exist_ok=True)

class AssertiveAPI:
    """Classe para gerenciar a integração com a API da Assertiva.
    Fornece métodos para processar registros e consultar informações."""
    
    def __init__(self):
        """Inicializa a conexão com a API da Assertiva usando as credenciais do arquivo .env"""
        load_dotenv()
        
        # Credenciais OAuth2
        self.client_id = 'mVUhrzLyXuBqqMivWtwBrIX7HPmEzCiB++esd5xo+Bo0IQOQvlj35oWU+HbEOwfEQpjyg7tZKxXzuGCQCtPLfw=='
        self.client_secret = 'XAJyqIthZDDUc5nrwQhJ/44qFpz1/gkd4z0jkHByTjYby9oPb6mraUmKrISNWwf4L9dbGfpeE45DvUxN4QtaeQ=='
        self.base_url = 'https://api.assertivasolucoes.com.br'
        self.auth_url = 'https://api.assertivasolucoes.com.br/oauth2/v3/token'
        
        # Informações do token
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
        if not self.client_id or not self.client_secret or not self.base_url:
            raise ValueError("Credenciais da Assertiva não encontradas no arquivo .env")
        
        try:
            self.session = requests.Session()
            self.session.headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            
            # Obtém o token inicial
            self._get_access_token()
            logger.info("Conexão com Assertiva estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar com Assertiva: {str(e)}")
            raise
    
    def _get_access_token(self):
        """Obtém um token de acesso usando o fluxo OAuth2 Client Credentials com Basic Auth"""
        try:
            # Usando requests diretamente sem a sessão para a autenticação
            from urllib.parse import urlencode
            import base64
            
            # Preparando as credenciais para Basic Auth
            # Importante: Não incluir caracteres especiais ou quebras de linha nas credenciais
            client_id_clean = self.client_id.strip()
            client_secret_clean = self.client_secret.strip()
            credentials = f"{client_id_clean}:{client_secret_clean}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            
            # Dados do corpo da requisição - apenas o grant_type conforme documentação
            data = {
                'grant_type': 'client_credentials'
            }
            
            # Headers para a requisição OAuth2 com Basic Auth
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            # Log para debug
            logger.info(f"Tentando autenticar em: {self.auth_url}")
            logger.info(f"Enviando requisição com credenciais no corpo")
            
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=urlencode(data),
                verify=True
            )
            
            # Log para debug da resposta
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
            
            if response.status_code == 403:
                logger.error(f"Erro de autenticação 403 Forbidden. Resposta: {response.text}")
                raise Exception(f"Erro de autenticação: 403 Forbidden. Verifique as credenciais e a URL de autenticação.")
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)  # Padrão de 1 hora se não especificado
            
            # Calcula quando o token expira (com uma margem de segurança de 60 segundos)
            self.token_expires_at = time.time() + expires_in - 60
            
            # Atualiza o header de autorização na sessão
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            logger.info("Token de acesso OAuth2 obtido com sucesso")
        except Exception as e:
            logger.error(f"Erro ao obter token de acesso: {str(e)}")
            raise
    
    def _refresh_token_if_needed(self):
        """Verifica se o token está expirado e o atualiza se necessário"""
        if time.time() >= self.token_expires_at:
            logger.info("Token de acesso expirado, renovando...")
            if self.refresh_token:
                try:
                    from urllib.parse import urlencode
                    import base64
                    
                    # Preparando as credenciais para Basic Auth
                    # Importante: Não incluir caracteres especiais ou quebras de linha nas credenciais
                    client_id_clean = self.client_id.strip()
                    client_secret_clean = self.client_secret.strip()
                    credentials = f"{client_id_clean}:{client_secret_clean}"
                    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                    
                    # Dados para renovação do token
                    data = {
                        'grant_type': 'refresh_token',
                        'refresh_token': self.refresh_token
                    }
                    
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                        'Authorization': f'Basic {encoded_credentials}'
                    }
                    
                    response = requests.post(
                        self.auth_url,
                        data=urlencode(data),
                        headers=headers,
                        verify=True  # Garante verificação SSL
                    )
                    
                    # Log para debug da resposta
                    logger.info(f"Status code refresh: {response.status_code}")
                    
                    # Se receber erro 403, tenta logar mais informações para diagnóstico
                    if response.status_code == 403:
                        logger.error(f"Erro de renovação 403 Forbidden. Resposta: {response.text}")
                        raise Exception(f"Erro de renovação: 403 Forbidden. Obtendo novo token...")
                    
                    response.raise_for_status()
                    token_data = response.json()
                    
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token', self.refresh_token)
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = time.time() + expires_in - 60
                    
                    # Atualiza o header de autorização na sessão
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    logger.info("Token de acesso renovado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao renovar token: {str(e)}")
                    # Se falhar ao renovar, tenta obter um novo token
                    self._get_access_token()
            else:
                # Se não tiver refresh token, obtém um novo token
                self._get_access_token()
    
    def consultar_cpf(self, cpf: str) -> Dict:
        """
        Consulta um CPF na API da Assertiva v3 usando a abordagem do teste_assertiva_simples.py
        que está funcionando corretamente.
        
        Args:
            cpf: CPF a ser consultado (apenas números)
            
        Returns:
            Dicionário com os dados da consulta
        """
        try:
            print("\n" + "=" * 50)
            print("CONSULTA DE CPF NA API ASSERTIVA")
            print("=" * 50 + "\n")
            
            # Credenciais da API (usando as mesmas do __init__)
            client_id = self.client_id
            client_secret = self.client_secret
            auth_url = self.auth_url
            base_url = self.base_url
            
            # Passo 1: Autenticação para obter o token
            print("Passo 1: Obtendo token de autenticação...")
            logger.info("Iniciando autenticação para consulta de CPF")
            
            # Preparando as credenciais para Basic Auth
            import base64
            from urllib.parse import urlencode
            import json
            
            # Dados para autenticação - apenas o grant_type conforme documentação
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            # Preparando as credenciais para Basic Auth
            # Importante: Não incluir caracteres especiais ou quebras de linha nas credenciais
            client_id_clean = client_id.strip()
            client_secret_clean = client_secret.strip()
            credentials = f"{client_id_clean}:{client_secret_clean}"
            
            # Codificando as credenciais em Base64
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            
            # Headers para a requisição com Basic Auth
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            print(f"URL de autenticação: {auth_url}")
            print(f"Credenciais codificadas: {encoded_credentials[:10]}...")
            logger.info(f"Tentando autenticar em: {auth_url}")
            
            # Faz a requisição de autenticação
            auth_response = requests.post(
                auth_url,
                headers=headers,
                data=urlencode(auth_data),
                verify=True
            )
            
            # Exibe informações sobre a resposta de autenticação
            print(f"\nResposta da autenticação:")
            print(f"Status code: {auth_response.status_code}")
            logger.info(f"Status code: {auth_response.status_code}")
            logger.info(f"Resposta: {auth_response.text}")
            
            # Verifica se a autenticação foi bem-sucedida
            if auth_response.status_code != 200:
                error_msg = f"Falha na autenticação! Código: {auth_response.status_code}"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Extrai o token de acesso
            token_data = auth_response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                error_msg = "Token de acesso não encontrado na resposta!"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            print(f"✅ Token obtido com sucesso: {access_token[:15]}...")
            logger.info("Token de acesso OAuth2 obtido com sucesso")
            
            # Passo 2: Consulta de CPF
            print("\nPasso 2: Consultando CPF...")
            
            # Remove caracteres não numéricos do CPF
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            if not cpf_limpo or len(cpf_limpo) != 11:
                raise ValueError("CPF inválido")
                
            print(f"CPF a ser consultado: {cpf_limpo}")
            
            # Endpoint para consulta de CPF
            cpf_endpoint = f"{base_url}/localize/v3/cpf"
            
            # Parâmetros da consulta
            params = {
                'cpf': cpf_limpo,
                'idFinalidade': '1'
            }
            
            # Headers com o token de autenticação
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Log para debug
            logger.info(f"Consultando CPF em: {cpf_endpoint}")
            logger.info(f"Parâmetros: {params}")
            logger.info(f"Headers: {headers}")
            
            # Faz a requisição de consulta
            cpf_response = requests.get(
                cpf_endpoint,
                headers=headers,
                params=params
            )
            
            # Exibe informações sobre a resposta da consulta
            print(f"\nResposta da consulta de CPF:")
            print(f"Status code: {cpf_response.status_code}")
            logger.info(f"Status code da resposta: {cpf_response.status_code}")
            
            # Verifica se a consulta foi bem-sucedida
            cpf_response.raise_for_status()
            
            # Tenta formatar a resposta como JSON para melhor visualização
            try:
                resposta_json = cpf_response.json()
                print("\nResposta completa (formatada):")
                print(json.dumps(resposta_json, indent=2, ensure_ascii=False))
                
                # Salva a resposta em um arquivo para análise posterior
                output_json = os.path.join(RESPONSES_DIR, 'ultima_resposta_assertiva.json')
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(resposta_json, f, indent=2, ensure_ascii=False)
                print(f"\nResposta salva no arquivo: {output_json}")
                
                # Atualiza o token na sessão para uso futuro
                self.access_token = access_token
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600) - 60
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
                
                logger.info(f"CPF {cpf_limpo} consultado com sucesso")
                return resposta_json
                
            except json.JSONDecodeError:
                print("\nResposta completa (não é um JSON válido):")
                print(cpf_response.text)
                logger.error(f"Resposta não é um JSON válido: {cpf_response.text}")
                raise Exception("Resposta da API não é um JSON válido")
            
        except Exception as e:
            error_msg = f"Erro ao consultar CPF {cpf}: {str(e)}"
            print(f"\n❌ {error_msg}")
            logger.error(error_msg)
            raise
    
    def consultar_cnpj(self, cnpj: str) -> Dict:
        """
        Consulta um CNPJ na API da Assertiva v3.
        
        Args:
            cnpj: CNPJ a ser consultado (pode conter formatação)
            
        Returns:
            Dicionário com os dados da consulta
        """
        # Versão otimizada que usa o mecanismo de refresh de token existente
        try:
            # Garante que o token está válido
            self._refresh_token_if_needed()
            
            # Remove caracteres não numéricos do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            if not cnpj_limpo or len(cnpj_limpo) != 14:
                error_msg = f"CNPJ inválido para consulta: '{cnpj}'"
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"[ASSERTIVA] Buscando CNPJ: '{cnpj}' (limpo: '{cnpj_limpo}')")
            
            # Endpoint para consulta de CNPJ
            cnpj_endpoint = f"{self.base_url}/localize/v3/cnpj"
            
            # Parâmetros da consulta
            params = {
                'cnpj': cnpj_limpo,
                'idFinalidade': '1'  # Mesmo valor usado para CPF
            }
            
            # Faz a requisição de consulta usando a sessão já configurada com o token
            response = self.session.get(
                cnpj_endpoint,
                params=params
            )
            
            # Verifica se a consulta foi bem-sucedida
            response.raise_for_status()
            
            # Processa a resposta
            resposta_json = response.json()
            
            # Salva a resposta em um arquivo para análise posterior (opcional)
            import json
            with open('ultima_resposta_assertiva_cnpj.json', 'w', encoding='utf-8') as f:
                json.dump(resposta_json, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[ASSERTIVA] CNPJ {cnpj_limpo} consultado com sucesso")
            return resposta_json
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"[ASSERTIVA] Erro HTTP ao consultar CNPJ {cnpj}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[ASSERTIVA] Erro ao consultar CNPJ {cnpj}: {str(e)}")
            raise
            
    # Versão detalhada do método consultar_cnpj para debug e testes
    def consultar_cnpj_detalhado(self, cnpj: str) -> Dict:
        """
        Consulta um CNPJ na API da Assertiva v3 com logs detalhados para debug.
        
        Args:
            cnpj: CNPJ a ser consultado (pode conter formatação)
            
        Returns:
            Dicionário com os dados da consulta
        """
        try:
            print("\n" + "=" * 50)
            print("CONSULTA DE CNPJ NA API ASSERTIVA")
            print("=" * 50 + "\n")
            
            # Credenciais da API (usando as mesmas do __init__)
            client_id = self.client_id
            client_secret = self.client_secret
            auth_url = self.auth_url
            base_url = self.base_url
            
            # Passo 1: Autenticação para obter o token
            print("Passo 1: Obtendo token de autenticação...")
            logger.info("Iniciando autenticação para consulta de CNPJ")
            
            # Preparando as credenciais para Basic Auth
            import base64
            from urllib.parse import urlencode
            import json
            
            # Dados para autenticação - apenas o grant_type conforme documentação
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            # Preparando as credenciais para Basic Auth
            # Importante: Não incluir caracteres especiais ou quebras de linha nas credenciais
            client_id_clean = client_id.strip()
            client_secret_clean = client_secret.strip()
            credentials = f"{client_id_clean}:{client_secret_clean}"
            
            # Codificando as credenciais em Base64
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            
            # Headers para a requisição com Basic Auth
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            print(f"URL de autenticação: {auth_url}")
            print(f"Credenciais codificadas: {encoded_credentials[:10]}...")
            logger.info(f"Tentando autenticar em: {auth_url}")
            
            # Faz a requisição de autenticação
            auth_response = requests.post(
                auth_url,
                headers=headers,
                data=urlencode(auth_data),
                verify=True
            )
            
            # Exibe informações sobre a resposta de autenticação
            print(f"\nResposta da autenticação:")
            print(f"Status code: {auth_response.status_code}")
            logger.info(f"Status code: {auth_response.status_code}")
            logger.info(f"Resposta: {auth_response.text}")
            
            # Verifica se a autenticação foi bem-sucedida
            if auth_response.status_code != 200:
                error_msg = f"Falha na autenticação! Código: {auth_response.status_code}"
                print(f"\u274c {error_msg}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Extrai o token de acesso
            token_data = auth_response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                error_msg = "Token de acesso não encontrado na resposta!"
                print(f"\u274c {error_msg}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            print(f"\u2705 Token obtido com sucesso: {access_token[:15]}...")
            logger.info("Token de acesso OAuth2 obtido com sucesso")
            
            # Passo 2: Consulta de CNPJ
            print("\nPasso 2: Consultando CNPJ...")
            
            # Remove caracteres não numéricos do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            if not cnpj_limpo or len(cnpj_limpo) != 14:
                error_msg = f"CNPJ inválido para consulta: '{cnpj}'"
                print(f"\u274c {error_msg}")
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            print(f"CNPJ a ser consultado: {cnpj_limpo}")
            
            # Endpoint para consulta de CNPJ
            cnpj_endpoint = f"{base_url}/localize/v3/cnpj"
            
            # Parâmetros da consulta
            params = {
                'cnpj': cnpj_limpo,
                'idFinalidade': '1'  # Mesmo valor usado para CPF
            }
            
            # Headers com o token de autenticação
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Log para debug
            logger.info(f"Consultando CNPJ em: {cnpj_endpoint}")
            logger.info(f"Parâmetros: {params}")
            logger.info(f"Headers: {headers}")
            
            # Faz a requisição de consulta
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
                with open('ultima_resposta_assertiva_cnpj.json', 'w', encoding='utf-8') as f:
                    json.dump(resposta_json, f, indent=2, ensure_ascii=False)
                print("\nResposta salva no arquivo: ultima_resposta_assertiva_cnpj.json")
                
                # Atualiza o token na sessão para uso futuro
                self.access_token = access_token
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600) - 60
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
                
                logger.info(f"CNPJ {cnpj_limpo} consultado com sucesso")
                return resposta_json
                
            except json.JSONDecodeError:
                print("\nResposta completa (não é um JSON válido):")
                print(cnpj_response.text)
                logger.error(f"Resposta não é um JSON válido: {cnpj_response.text}")
                raise Exception("Resposta da API não é um JSON válido")
            
        except Exception as e:
            error_msg = f"Erro ao consultar CNPJ {cnpj}: {str(e)}"
            print(f"\n\u274c {error_msg}")
            logger.error(error_msg)
            raise
    
    def processar_registros_cnpj(self, registros: List[Dict]) -> List[Dict]:
        """Processa uma lista de registros usando a API da Assertiva para consulta de CNPJ.
        
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
                        'status_assertiva': data.get('status'),
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'resultado_assertiva': data
                    }
                    resultados.append(resultado)
                    logger.info(f"Registro processado com sucesso: {cnpj}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar registro {registro}: {str(e)}")
                    resultado = {
                        **registro,
                        'status_assertiva': 'erro',
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'erro': str(e)
                    }
                    resultados.append(resultado)
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro ao processar registros de CNPJ: {str(e)}")
            raise
    
    def processar_registros(self, registros: List[Dict]) -> List[Dict]:
        """Processa uma lista de registros usando a API da Assertiva.
        
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
                    # Extrai o CPF do registro
                    cpf = registro.get('CPF', '').strip()
                    if not cpf:
                        logger.warning(f"CPF não encontrado no registro: {registro}")
                        continue
                    
                    # Consulta o CPF na API
                    data = self.consultar_cpf(cpf)
                    
                    # Processa o resultado
                    resultado = {
                        **registro,
                        'status_assertiva': data.get('status'),
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'resultado_assertiva': data
                    }
                    resultados.append(resultado)
                    logger.info(f"Registro processado com sucesso: {cpf}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar registro {registro}: {str(e)}")
                    resultado = {
                        **registro,
                        'status_assertiva': 'erro',
                        'data_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'erro': str(e)
                    }
                    resultados.append(resultado)
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro ao processar registros: {str(e)}")
            raise
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union
import requests
from dotenv import load_dotenv
import json
import functools

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pipedrive_api')

class PipedriveAPI:
    """
    Classe para gerenciar a integração com a API do Pipedrive.
    Fornece métodos para interagir com deals (negócios) e outras entidades do Pipedrive.
    """
    
    def __init__(self):
        """
        Inicializa a conexão com a API do Pipedrive usando as credenciais do arquivo .env
        """
        # Tenta carregar .env do diretório atual e pai
        load_dotenv()
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
        
        self.api_token = os.getenv('PIPEDRIVE_API_KEY')
        self.domain = os.getenv('PIPEDRIVE_DOMAIN')
        
        # Log para debug
        logger.info(f"Inicializando PipedriveAPI...")
        logger.info(f"API Token: {'***' + self.api_token[-4:] if self.api_token else 'NÃO ENCONTRADO'}")
        logger.info(f"Domain: {self.domain if self.domain else 'NÃO ENCONTRADO'}")
        
        # IDs dos campos personalizados - CRÍTICO: Esses IDs são específicos da conta Pipedrive
        self.cpf_field_id = 'e3c63a9658469cbb216157a807cadcf263637383'  # ID do campo CPF personalizado
        self.cpf_field_keys = [
            'e3c63a9658469cbb216157a807cadcf263637383',  # ID principal
            'cpf',                                      # Nome do campo
            'CPF',                                      # Nome alternativo
            '9a8b7c6d5e4f3g2h1i'                       # ID alternativo (exemplo)
        ]
        
        # CNPJ também é um campo personalizado
        self.cnpj_field_id = '9d4c76c6dfc415d520cee2837699e3ace1045be9'  # ID do campo CNPJ personalizado
        
        if not self.api_token or not self.domain:
            raise ValueError("Credenciais do Pipedrive não encontradas no arquivo .env")
        
        try:
            self.base_url = f"https://{self.domain}.pipedrive.com/api/v1"
            self.session = requests.Session()
            self.session.headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            
            # Configuração de timeout para evitar erros de timeout
            self.timeout = 120  # 120 segundos de timeout (2 minutos)
            
            # Aplica o timeout a todos os métodos HTTP da sessão
            original_get = self.session.get
            original_post = self.session.post
            original_put = self.session.put
            original_delete = self.session.delete
            
            # Substitui os métodos originais por versões com timeout
            self.session.get = functools.partial(original_get, timeout=self.timeout)
            self.session.post = functools.partial(original_post, timeout=self.timeout)
            self.session.put = functools.partial(original_put, timeout=self.timeout)
            self.session.delete = functools.partial(original_delete, timeout=self.timeout)
            
            logger.info(f"Conexão com Pipedrive estabelecida com sucesso (timeout: {self.timeout}s)")
        except Exception as e:
            logger.error(f"Erro ao conectar com Pipedrive: {str(e)}")
            raise

    def listar_funis(self) -> List[Dict]:
        """
        Lista todos os funis (pipelines) disponíveis no Pipedrive.
        
        Returns:
            Lista de funis com seus IDs e nomes
        """
        try:
            response = self.session.get(
                f"{self.base_url}/pipelines",
                params={'api_token': self.api_token},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                pipelines = data.get('data', [])
                logger.info(f"Recuperados {len(pipelines)} funis do Pipedrive")
                return pipelines
            return []
            
        except Exception as e:
            logger.error(f"Erro ao listar funis: {str(e)}")
            raise

    def listar_filtros(self) -> List[Dict]:
        """
        Lista todos os filtros disponíveis no Pipedrive.
        
        Returns:
            Lista de filtros com seus IDs e condições
        """
        try:
            response = self.session.get(
                f"{self.base_url}/filters",
                params={'api_token': self.api_token},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                filters = data.get('data', [])
                logger.info(f"Recuperados {len(filters)} filtros do Pipedrive")
                return filters
            return []
            
        except Exception as e:
            logger.error(f"Erro ao listar filtros: {str(e)}")
            raise

    def buscar_negocios_por_filtro_paginado(self, filter_id: int, pipeline_id: Optional[int] = None, 
                                       start: int = 0, limit: int = 500) -> Dict:
        """
        Busca uma página de negócios usando um filtro específico do Pipedrive e opcionalmente filtra por funil.
        
        Args:
            filter_id: ID do filtro a ser usado
            pipeline_id: ID do funil para filtrar os negócios (opcional)
            start: Índice inicial para paginação
            limit: Número máximo de registros por página (máximo 500)
            
        Returns:
            Dicionário com os negócios e informações de paginação:
            {
                'negocios': [...],  # Lista de negócios na página atual
                'total': int,       # Total de negócios disponíveis
                'tem_proxima': bool  # Indica se há mais páginas disponíveis
            }
        """
        try:
            # Limita o número máximo de registros por página a 500 (limite da API)
            limit = min(limit, 500)
            
            params = {
                'api_token': self.api_token,
                'filter_id': filter_id,
                'start': start,
                'limit': limit,
                'get_all_custom_fields': True,
                'get_summary': True
            }
            
            if pipeline_id:
                params['pipeline_id'] = pipeline_id
            
            response = self.session.get(f"{self.base_url}/deals", params=params)
            response.raise_for_status()
            data = response.json()
            
            resultado = {
                'negocios': [],
                'total': 0,
                'tem_proxima': False
            }
            
            if data and data.get('success'):
                deals = data.get('data', [])
                pagination = data.get('additional_data', {}).get('pagination', {})
                
                # Obtém o total de itens
                total_items = pagination.get('total_count', 0)
                
                # Verifica se há mais páginas
                tem_proxima = pagination.get('more_items_in_collection', False)
                
                resultado = {
                    'negocios': deals,
                    'total': total_items,
                    'tem_proxima': tem_proxima
                }
                
                logger.info(f"Recuperados {len(deals)} negócios usando filtro {filter_id} (offset: {start}, total: {total_items})")
            else:
                logger.warning(f"Resposta da API não foi bem-sucedida para o filtro {filter_id}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar negócios com filtro {filter_id}: {str(e)}")
            raise
            
    def listar_negocios_paginado(self, start: int = 0, limit: int = 500, status: Optional[str] = None, 
                             term: Optional[str] = None, pipeline_id: Optional[int] = None) -> Dict:
        """
        Lista uma página de negócios (deals) do Pipedrive com opção de filtrar por status.
        
        Args:
            start: Índice inicial para paginação
            limit: Número máximo de registros por página (máximo 500)
            status: Status dos negócios para filtrar (open, won, lost, deleted)
            term: Termo para busca
            pipeline_id: ID do funil para filtrar os negócios (opcional)
            
        Returns:
            Dicionário com os negócios e informações de paginação:
            {
                'negocios': [...],  # Lista de negócios na página atual
                'total': int,       # Total de negócios disponíveis
                'tem_proxima': bool  # Indica se há mais páginas disponíveis
            }
        """
        try:
            # Limita o número máximo de registros por página a 500 (limite da API)
            limit = min(limit, 500)
            
            params = {
                'api_token': self.api_token,
                'start': start,
                'limit': limit,
                'get_all_custom_fields': True,
                'get_summary': True
            }
            
            if status:
                params['status'] = status
            if term:
                params['term'] = term
            if pipeline_id:
                params['pipeline_id'] = pipeline_id
            
            response = self.session.get(f"{self.base_url}/deals", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log para debug - mostra JSON RAW da resposta da API
            import json as json_lib
            if data and data.get('data') and len(data.get('data', [])) > 0:
                logger.info(f"\n{'='*100}")
                logger.info(f"[DEBUG] JSON RAW DA RESPOSTA DA API /deals (PRIMEIRO NEGÓCIO):")
                logger.info(json_lib.dumps(data['data'][0], indent=2, ensure_ascii=False))
                logger.info(f"{'='*100}\n")
            
            resultado = {
                'negocios': [],
                'total': 0,
                'tem_proxima': False
            }
            
            if data and data.get('success'):
                deals = data.get('data', [])
                pagination = data.get('additional_data', {}).get('pagination', {})
                
                # Obtém o total de itens
                total_items = pagination.get('total_count', 0)
                
                # Verifica se há mais páginas
                tem_proxima = pagination.get('more_items_in_collection', False)
                
                # Se pipeline_id foi especificado mas não foi usado na API (versões antigas),
                # filtra os resultados manualmente
                if pipeline_id and 'pipeline_id' not in params:
                    deals = [n for n in deals if n.get('pipeline_id') == pipeline_id]
                
                resultado = {
                    'negocios': deals,
                    'total': total_items,
                    'tem_proxima': tem_proxima
                }
                
                logger.info(f"Recuperados {len(deals)} negócios do Pipedrive (offset: {start}, total: {total_items})")
            else:
                logger.warning(f"Resposta da API não foi bem-sucedida ao listar negócios")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao listar negócios: {str(e)}")
            raise

    def buscar_negocios_por_filtro(self, filter_id: int, pipeline_id: Optional[int] = None) -> List[Dict]:
        """
        Busca negócios usando um filtro específico do Pipedrive e opcionalmente filtra por funil.
        Implementa paginação para buscar todos os registros disponíveis.
        
        Args:
            filter_id: ID do filtro a ser usado
            pipeline_id: ID do funil para filtrar os negócios (opcional)
            
        Returns:
            Lista completa de negócios que correspondem ao filtro
        """
        try:
            todos_negocios = []
            start = 0
            limit = 500  # Máximo permitido pela API por página

            while True:
                params = {
                'api_token': self.api_token,
                'filter_id': filter_id,
                'start': start,
                'limit': limit,
                'get_all_custom_fields': True,
                'get_summary': True
            }
            
                if pipeline_id:
                    params['pipeline_id'] = pipeline_id

                response = self.session.get(f"{self.base_url}/deals", params=params)
                response.raise_for_status()
                data = response.json()

                if data and data.get('success'):
                    deals = data.get('data', [])
                    pagination = data.get('additional_data', {}).get('pagination', {})

                    if deals:
                        todos_negocios.extend(deals)
                    logger.info(f"Recuperados {len(deals)} negócios usando filtro {filter_id} (offset: {start})")

                # Verifica se há mais páginas
                if not pagination.get('more_items_in_collection', False):
                    break

                # Usa `next_start` se disponível, senão incrementa por `limit`
                start = pagination.get('next_start', start + limit)

            logger.info(f"Total de negócios recuperados com filtro {filter_id}: {len(todos_negocios)}")
            return todos_negocios

        except Exception as e:
            logger.error(f"Erro ao buscar negócios com filtro {filter_id}: {str(e)}")
            raise


    def buscar_pessoas(self, termo: str, limite: int = 10) -> List[Dict]:
        """
        Busca pessoas no Pipedrive pelo nome ou outro termo de busca.
        
        Args:
            termo: Termo para busca (nome, email, etc)
            limite: Número máximo de resultados
            
        Returns:
            Lista de pessoas encontradas
        """
        try:
            # Constrói a URL e parâmetros
            url = f"{self.base_url}/persons/search"
            params = {
                'api_token': self.api_token,
                'term': termo,
                'fields': 'name,email',
                'exact_match': False,
                'limit': limite
            }
            
            # Log para depuração
            logger.info(f"[PIPEDRIVE] Buscando pessoas com o termo: '{termo}'")
            logger.debug(f"[PIPEDRIVE] URL: {url} | Params: {params}")
            
            # Faz a requisição
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log da resposta (truncada para não sobrecarregar o log)
            logger.debug(f"[PIPEDRIVE] Resposta: {json.dumps(data)[:500]}...")
            
            # Verifica se a requisição foi bem-sucedida
            if data and data.get('success'):
                # Extrai os itens encontrados
                items = data.get('data', {}).get('items', [])
                pessoas = [item.get('item', {}) for item in items]
                
                # Log das pessoas encontradas
                logger.info(f"[PIPEDRIVE] Encontradas {len(pessoas)} pessoas para o termo '{termo}'")
                
                # Log detalhado de cada pessoa encontrada
                for i, pessoa in enumerate(pessoas):
                    pessoa_id = pessoa.get('id')
                    pessoa_nome = pessoa.get('name', 'Sem nome')
                    logger.info(f"[PIPEDRIVE] Pessoa {i+1}: ID={pessoa_id}, Nome={pessoa_nome}")
                
                return pessoas
            else:
                logger.warning(f"[PIPEDRIVE] Erro na resposta ao buscar '{termo}': {data}")
                return []
                
        except Exception as e:
            logger.error(f"[PIPEDRIVE] Erro ao buscar pessoas com o termo '{termo}': {str(e)}")
            return []
            
    def buscar_pessoa_por_cpf(self, cpf: str, nome: str = None, org_id: int = None) -> List[Dict]:
        """
        Busca pessoas no Pipedrive pelo CPF (campo personalizado) e opcionalmente filtra por nome e organização.
        
        Esta função realiza uma busca precisa por CPF e permite validação tripla:
        1. CPF (critério principal)
        2. Nome (validação secundária)
        3. Organização (validação terciária)
        
        Args:
            cpf: CPF para busca (com ou sem formatação)
            nome: Nome da pessoa para validação adicional (opcional)
            org_id: ID da organização para validação adicional (opcional)
            
        Returns:
            Lista de pessoas encontradas que correspondem aos critérios
        """
        try:
            # Limpa o CPF para busca (remove formatação)
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            if not cpf_limpo or len(cpf_limpo) < 11:
                logger.warning(f"[PIPEDRIVE] CPF inválido para busca: '{cpf}'")
                return []
                
            # Formata o CPF no padrão XXX.XXX.XXX-XX para busca alternativa
            cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
                
            logger.info(f"[PIPEDRIVE] Buscando pessoa por CPF: '{cpf}' (limpo: '{cpf_limpo}', formatado: '{cpf_formatado}')")
            
            # Primeiro tentaremos com o CPF limpo
            
            # ID do campo personalizado de CPF no Pipedrive
            cpf_field_id = "e3c63a9658469cbb216157a807cadcf263637383"
            
            # Busca pelo CPF usando o endpoint de busca de pessoas
            url = f"{self.base_url}/persons/search"
            params = {
                'api_token': self.api_token,
                'term': cpf_limpo,  # Termo de busca (CPF)
                'exact_match': True  # Queremos correspondência exata
            }
            
            # Não adicionamos org_id como parâmetro na requisição pois causa erro 400
            # A validação por organização será feita após obter os resultados
            
            logger.debug(f"[PIPEDRIVE] Buscando por CPF - URL: {url} | Params: {params}")
            
            # Faz a requisição
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Verifica se a requisição foi bem-sucedida
            if not data or not data.get('success'):
                logger.warning(f"[PIPEDRIVE] Erro na resposta ao buscar por CPF '{cpf_limpo}': {data}")
                return []
                
            # Extrai os itens encontrados
            items = data.get('data', {}).get('items', [])
            pessoas = [item.get('item', {}) for item in items]
            
            logger.info(f"[PIPEDRIVE] Encontradas {len(pessoas)} pessoas com CPF '{cpf_limpo}'")
            
            # Se não encontrou ninguém pela busca direta com CPF limpo, tenta com CPF formatado
            if not pessoas:
                logger.info(f"[PIPEDRIVE] Nenhuma pessoa encontrada com CPF limpo. Tentando com CPF formatado: '{cpf_formatado}'")
                
                # Tenta buscar com o CPF formatado
                params['term'] = cpf_formatado
                logger.debug(f"[PIPEDRIVE] Buscando por CPF formatado - URL: {url} | Params: {params}")
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data and data.get('success'):
                    items = data.get('data', {}).get('items', [])
                    pessoas = [item.get('item', {}) for item in items]
                    logger.info(f"[PIPEDRIVE] Encontradas {len(pessoas)} pessoas com CPF formatado '{cpf_formatado}'")
                
            # Se ainda não encontrou ninguém, tenta o método alternativo
            if not pessoas:
                logger.info(f"[PIPEDRIVE] Nenhuma pessoa encontrada pelas buscas diretas. Tentando método alternativo...")
                return self._buscar_pessoa_por_cpf_alternativo(cpf_limpo, nome, org_id)
            
            # Lista para armazenar pessoas que passam na validação tripla
            pessoas_validadas = []
            
            # Para cada pessoa encontrada, obtemos os detalhes completos
            # e aplicamos a validação tripla (CPF, nome e organização)
            for pessoa in pessoas:
                pessoa_id = pessoa.get('id')
                if not pessoa_id:
                    continue
                    
                # Obtém detalhes completos da pessoa
                pessoa_detalhes = self.obter_pessoa(pessoa_id)
                if not pessoa_detalhes:
                    continue
                    
                # Validação 1: CPF - já garantida pela busca
                # Verificamos novamente para confirmar
                pessoa_cpf = None
                
                # Tenta obter o CPF do campo personalizado pelo ID específico
                if cpf_field_id in pessoa_detalhes:
                    pessoa_cpf = pessoa_detalhes.get(cpf_field_id)
                    
                # Tenta obter o CPF do campo 'cpf' genérico
                if not pessoa_cpf and 'cpf' in pessoa_detalhes:
                    pessoa_cpf = pessoa_detalhes.get('cpf')
                    
                # Se encontrou CPF, limpa e compara
                if pessoa_cpf:
                    # O CPF pode estar em múltiplos formatos separados por vírgula
                    # Ex: "071.323.149-12, 7132314912"
                    cpf_valores = str(pessoa_cpf).split(',')
                    
                    # Verificamos se algum dos formatos corresponde ao CPF buscado
                    cpf_encontrado = False
                    for cpf_valor in cpf_valores:
                        pessoa_cpf_limpo_atual = ''.join(filter(str.isdigit, cpf_valor.strip()))
                        if pessoa_cpf_limpo_atual and pessoa_cpf_limpo_atual == cpf_limpo:
                            cpf_encontrado = True
                            break
                    
                    # Se nenhum formato de CPF corresponde, pula esta pessoa
                    if not cpf_encontrado:
                        logger.info(f"[PIPEDRIVE] CPF não corresponde: '{cpf_limpo}' não encontrado em '{pessoa_cpf}'")
                        continue
                else:
                    # Se não encontrou CPF nos detalhes, pula esta pessoa
                    logger.info(f"[PIPEDRIVE] Pessoa ID={pessoa_id} não tem CPF cadastrado")
                    continue
                    
                # Validação 2: Nome (se fornecido)
                if nome and nome.strip():
                    pessoa_nome = pessoa_detalhes.get('name', '').strip().upper()
                    nome_busca = nome.strip().upper()
                    
                    # Verifica se o nome corresponde (pode ser parcial)
                    if nome_busca not in pessoa_nome and pessoa_nome not in nome_busca:
                        logger.info(f"[PIPEDRIVE] Nome não corresponde: '{nome_busca}' != '{pessoa_nome}'")
                        continue
                        
                # Validação 3: Organização (se fornecida)
                if org_id is not None:
                    pessoa_org_id = None
                    
                    # Tenta obter o org_id
                    if 'org_id' in pessoa_detalhes:
                        org_data = pessoa_detalhes.get('org_id')
                        if isinstance(org_data, dict):
                            pessoa_org_id = org_data.get('value')
                        else:
                            pessoa_org_id = org_data
                            
                    # Se o org_id não corresponde, pula esta pessoa
                    if pessoa_org_id != org_id:
                        logger.info(f"[PIPEDRIVE] Organização não corresponde: '{org_id}' != '{pessoa_org_id}'")
                        continue
                        
                # Se passou por todas as validações, adiciona à lista de pessoas validadas
                logger.info(f"[PIPEDRIVE] Pessoa ID={pessoa_id} passou na validação tripla!")
                pessoas_validadas.append(pessoa_detalhes)
                
            return pessoas_validadas
                
        except Exception as e:
            logger.error(f"[PIPEDRIVE] Erro ao buscar pessoa por CPF '{cpf}': {str(e)}")
            return []
            
    def _buscar_pessoa_por_cpf_alternativo(self, cpf_limpo: str, nome: str = None, org_id: int = None) -> List[Dict]:
        """
        Método alternativo para buscar pessoas por CPF quando a busca direta falha.
        Busca todas as pessoas e filtra pelo CPF nos detalhes.
        
        Args:
            cpf_limpo: CPF limpo (apenas números)
            nome: Nome para validação adicional
            org_id: ID da organização para validação adicional
            
        Returns:
            Lista de pessoas encontradas
        """
        try:
            logger.info(f"[PIPEDRIVE] Iniciando busca alternativa por CPF '{cpf_limpo}'")
            
            # ID do campo personalizado de CPF no Pipedrive
            cpf_field_id = "e3c63a9658469cbb216157a807cadcf263637383"
            
            # Se temos o nome, tentamos buscar pelo nome primeiro para reduzir o escopo
            pessoas_para_verificar = []
            if nome and nome.strip():
                logger.info(f"[PIPEDRIVE] Buscando pelo nome '{nome}' para reduzir escopo")
                pessoas = self.buscar_pessoas(termo=nome, limite=50)
                if pessoas:
                    pessoas_para_verificar.extend(pessoas)
                    
            # Lista para armazenar pessoas que passam na validação tripla
            pessoas_validadas = []
            
            # Para cada pessoa encontrada, obtemos os detalhes completos
            # e aplicamos a validação tripla (CPF, nome e organização)
            for pessoa in pessoas_para_verificar:
                pessoa_id = pessoa.get('id')
                if not pessoa_id:
                    continue
                    
                # Obtém detalhes completos da pessoa
                pessoa_detalhes = self.obter_pessoa(pessoa_id)
                if not pessoa_detalhes:
                    continue
                    
                # Validação 1: CPF
                pessoa_cpf = None
                
                # Tenta obter o CPF do campo personalizado pelo ID específico
                if cpf_field_id in pessoa_detalhes:
                    pessoa_cpf = pessoa_detalhes.get(cpf_field_id)
                    
                # Tenta obter o CPF do campo 'cpf' genérico
                if not pessoa_cpf and 'cpf' in pessoa_detalhes:
                    pessoa_cpf = pessoa_detalhes.get('cpf')
                    
                # Se encontrou CPF, limpa e compara
                if pessoa_cpf:
                    # O CPF pode estar em múltiplos formatos separados por vírgula
                    # Ex: "071.323.149-12, 7132314912"
                    cpf_valores = str(pessoa_cpf).split(',')
                    
                    # Verificamos se algum dos formatos corresponde ao CPF buscado
                    cpf_encontrado = False
                    for cpf_valor in cpf_valores:
                        pessoa_cpf_limpo_atual = ''.join(filter(str.isdigit, cpf_valor.strip()))
                        if pessoa_cpf_limpo_atual and pessoa_cpf_limpo_atual == cpf_limpo:
                            cpf_encontrado = True
                            break
                    
                    # Se nenhum formato de CPF corresponde, pula esta pessoa
                    if not cpf_encontrado:
                        logger.info(f"[PIPEDRIVE] CPF não corresponde: '{cpf_limpo}' não encontrado em '{pessoa_cpf}'")
                        continue
                else:
                    # Se não encontrou CPF nos detalhes, pula esta pessoa
                    continue
                    
                # Validação 2: Nome (já garantida pela busca, mas verificamos novamente)
                if nome and nome.strip():
                    pessoa_nome = pessoa_detalhes.get('name', '').strip().upper()
                    nome_busca = nome.strip().upper()
                    
                    # Verifica se o nome corresponde (pode ser parcial)
                    if nome_busca not in pessoa_nome and pessoa_nome not in nome_busca:
                        continue
                        
                # Validação 3: Organização (se fornecida)
                if org_id is not None:
                    pessoa_org_id = None
                    
                    # Tenta obter o org_id
                    if 'org_id' in pessoa_detalhes:
                        org_data = pessoa_detalhes.get('org_id')
                        if isinstance(org_data, dict):
                            pessoa_org_id = org_data.get('value')
                        else:
                            pessoa_org_id = org_data
                            
                    # Se o org_id não corresponde, pula esta pessoa
                    if pessoa_org_id != org_id:
                        continue
                        
                # Se passou por todas as validações, adiciona à lista de pessoas validadas
                logger.info(f"[PIPEDRIVE] Pessoa ID={pessoa_id} passou na validação tripla (método alternativo)!")
                pessoas_validadas.append(pessoa_detalhes)
                
            return pessoas_validadas
                
        except Exception as e:
            logger.error(f"[PIPEDRIVE] Erro no método alternativo de busca por CPF: {str(e)}")
            return []
    
    def buscar_organizacao_por_nome(self, nome: str) -> Optional[int]:
        """
        Busca uma organização no Pipedrive pelo nome e retorna seu ID.
        
        Args:
            nome: Nome da organização para busca
            
        Returns:
            ID da organização encontrada ou None se não encontrada
        """
        try:
            if not nome or nome.strip() == "":
                logger.warning(f"[PIPEDRIVE] Nome de organização vazio para busca")
                return None
                
            logger.info(f"[PIPEDRIVE] Buscando organização por nome: '{nome}'")
            
            # Endpoint para busca de organizações
            url = f"{self.base_url}/organizations/search"
            params = {
                'api_token': self.api_token,
                'term': nome,
                'exact_match': False,  # Permitimos correspondência parcial para nomes de organizações
                'limit': 5  # Limitamos a 5 resultados
            }
            
            logger.debug(f"[PIPEDRIVE] Buscando organização - URL: {url} | Params: {params}")
            
            # Faz a requisição
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Verifica se a requisição foi bem-sucedida
            if not data or not data.get('success'):
                logger.warning(f"[PIPEDRIVE] Erro na resposta ao buscar organização '{nome}': {data}")
                return None
                
            # Extrai os itens encontrados
            items = data.get('data', {}).get('items', [])
            if not items:
                logger.info(f"[PIPEDRIVE] Nenhuma organização encontrada para o nome: '{nome}'")
                return None
                
            # Pega a primeira organização encontrada
            org = items[0].get('item', {})
            org_id = org.get('id')
            org_nome = org.get('name', 'Sem nome')
            
            logger.info(f"[PIPEDRIVE] Organização encontrada: ID={org_id}, Nome='{org_nome}'")
            return org_id
            
        except Exception as e:
            logger.error(f"[PIPEDRIVE] Erro ao buscar organização por nome: {str(e)}")
            return None
            
    def obter_pessoa(self, person_id: Union[int, Dict]) -> Optional[Dict]:
        """
        Obtém os dados de uma pessoa no Pipedrive pelo ID, incluindo o CPF.
        
{{ ... }}
        Args:
            person_id: ID da pessoa a ser obtida. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            
        Returns:
            Dados da pessoa ou None em caso de erro
        """
        try:
            # Se person_id for um dicionário, extrai o ID do campo 'value'
            original_person_id = person_id
            if isinstance(person_id, dict):
                person_id = person_id.get('value')
                logger.debug(f"[PIPEDRIVE] Convertendo person_id de dict para valor: {original_person_id} -> {person_id}")
                
            if not person_id:
                logger.warning("[PIPEDRIVE] ID de pessoa inválido")
                return None
            
            logger.info(f"[PIPEDRIVE] Obtendo dados da pessoa com ID: {person_id}")
            
            # Busca os dados da pessoa com todos os campos personalizados
            url = f"{self.base_url}/persons/{person_id}"
            params = {
                'api_token': self.api_token,
                'get_summary': True
            }
            
            logger.debug(f"[PIPEDRIVE] URL: {url} | Params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                person_data = data.get('data', {})
                logger.debug(f"[PIPEDRIVE] Dados da pessoa: {json.dumps(person_data)[:500]}...")
                
                # Adiciona um campo CPF vazio por padrão
                person_data['cpf'] = ''
                
                # Log dos campos disponíveis na pessoa
                logger.info(f"[PIPEDRIVE] Campos disponíveis na pessoa {person_id}: {list(person_data.keys())}")
                
                # Busca os campos personalizados da pessoa
                fields_response = self.session.get(
                    f"{self.base_url}/personFields",
                    params={
                        'api_token': self.api_token
                    }
                )
                fields_response.raise_for_status()
                fields_data = fields_response.json()
                
                # Identifica o campo CPF
                cpf_field_key = None
                if fields_data and fields_data.get('success'):
                    fields = fields_data.get('data', [])
                    logger.debug(f"[PIPEDRIVE] Campos personalizados disponíveis: {[f.get('key') for f in fields]}")
                    
                    for field in fields:
                        field_key = field.get('key')
                        field_name = field.get('name', '')
                        if field_key == 'cpf' or field_name.lower() == 'cpf':
                            cpf_field_key = field_key
                            logger.info(f"[PIPEDRIVE] Campo CPF identificado: key={field_key}, name={field_name}")
                            break
                
                # Verificar diretamente o campo personalizado com ID conhecido
                cpf_field_id = "e3c63a9658469cbb216157a807cadcf263637383"
                if cpf_field_id in person_data:
                    cpf_valor = person_data.get(cpf_field_id)
                    logger.info(f"[PIPEDRIVE] CPF encontrado no campo personalizado ID={cpf_field_id}: {cpf_valor}")
                    person_data['cpf'] = cpf_valor
                
                # Se encontrou o campo CPF pela chave, busca o valor
                elif cpf_field_key and cpf_field_key in person_data:
                    cpf_valor = person_data.get(cpf_field_key, '')
                    logger.info(f"[PIPEDRIVE] CPF encontrado no campo key={cpf_field_key}: {cpf_valor}")
                    person_data['cpf'] = cpf_valor
                
                # Verifica nos campos personalizados
                if not person_data['cpf']:
                    logger.info("[PIPEDRIVE] CPF não encontrado nos campos principais, buscando em outros campos...")
                    for key, value in person_data.items():
                        # Verifica se o campo é o CPF pelo nome ou conteúdo
                        if (key == 'cpf' or key == self.cpf_field_id or 
                            (isinstance(key, str) and 'cpf' in key.lower())):
                            logger.info(f"[PIPEDRIVE] Possível campo CPF encontrado: {key}={value}")
                            if isinstance(value, dict) and 'value' in value:
                                person_data['cpf'] = value.get('value', '')
                                logger.info(f"[PIPEDRIVE] CPF extraído de dict: {person_data['cpf']}")
                            else:
                                person_data['cpf'] = value
                            break
                
                logger.info(f"Dados da pessoa {person_id} recuperados com sucesso")
                return person_data
            else:
                logger.warning(f"Resposta da API não foi bem-sucedida ao buscar pessoa {person_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados da pessoa {person_id}: {str(e)}")
            return None
            
    def buscar_dados_pessoa(self, person_id: Union[int, Dict]) -> Optional[Dict]:
        """
        Busca os dados de uma pessoa no Pipedrive pelo ID.
        
        Este método é um alias para obter_pessoa para manter compatibilidade.
        
        Args:
            person_id: ID da pessoa a ser obtida. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            
        Returns:
            Dados da pessoa ou None em caso de erro
        """
        return self.obter_pessoa(person_id)

    def buscar_campos_personalizados_pessoa(self) -> List[Dict]:
        """
        Busca todos os campos personalizados disponíveis para pessoas no Pipedrive.
        
        Returns:
            Lista de campos personalizados com seus IDs e nomes
        """
        try:
            response = self.session.get(
                f"{self.base_url}/personFields",
                params={'api_token': self.api_token}
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                fields = data.get('data', [])
                logger.info(f"Recuperados {len(fields)} campos personalizados")
                return fields
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar campos personalizados: {str(e)}")
            raise

    def buscar_negocios_com_dados_completos(self, pipeline_id: Optional[int] = None, 
                                           filter_id: Optional[int] = None,
                                           callback: Optional[callable] = None,
                                           pagina: int = 0,
                                           limite_por_pagina: int = 500) -> Dict:
        """
        Busca negócios com dados completos, incluindo informações de pessoa e organização.
        Suporta paginação e processamento assíncrono através de callback.
        
        Args:
            pipeline_id: ID do funil para filtrar
            filter_id: ID do filtro para aplicar
            callback: Função callback para processamento assíncrono. Se fornecida,
                     será chamada para cada negócio processado.
            pagina: Número da página a ser buscada (começa em 0)
            limite_por_pagina: Número máximo de registros por página (máximo 500)
            
        Returns:
            Dicionário contendo a lista de negócios e informações de paginação:
            {
                'negocios': [...],  # Lista de negócios na página atual
                'total': int,       # Total de negócios disponíveis
                'pagina_atual': int, # Página atual
                'total_paginas': int, # Total de páginas disponíveis
                'tem_proxima': bool  # Indica se há mais páginas disponíveis
            }
        """
        try:
            # Calcula o offset para a paginação
            start = pagina * limite_por_pagina
            
            # Limita o número máximo de registros por página a 500 (limite da API)
            limite_por_pagina = min(limite_por_pagina, 500)
            
            # Obtém os negócios para a página atual
            if filter_id:
                # Usa a função buscar_negocios_por_filtro_paginado para obter apenas uma página
                resultado_paginado = self.buscar_negocios_por_filtro_paginado(filter_id, pipeline_id, start, limite_por_pagina)
                negocios = resultado_paginado['negocios']
                total_negocios = resultado_paginado['total']
                tem_proxima = resultado_paginado['tem_proxima']
            else:
                # Usa a função listar_negocios_paginado para obter apenas uma página
                resultado_paginado = self.listar_negocios_paginado(start=start, limit=limite_por_pagina, pipeline_id=pipeline_id)
                negocios = resultado_paginado['negocios']
                total_negocios = resultado_paginado['total']
                tem_proxima = resultado_paginado['tem_proxima']

            # Para cada negócio, busca dados adicionais
            negocios_completos = []
            for negocio in negocios:
                # Extrai dados da organização diretamente do negócio
                org_data = negocio.get('org_id', {})
                organization_name = org_data.get('name') if isinstance(org_data, dict) else None
                
                # Extrai dados da pessoa diretamente do negócio
                person_data = negocio.get('person_id', {})
                person_name = person_data.get('name') if isinstance(person_data, dict) else None
                person_id = person_data.get('value') if isinstance(person_data, dict) else person_data.get('id') if isinstance(person_data, dict) else None
                
                # Busca dados completos da pessoa para obter o CPF
                cpf = None
                if person_id:
                    try:
                        # Busca os campos personalizados da pessoa em uma requisição separada
                        logger.info(f"Buscando dados da pessoa {person_id} para o negócio {negocio.get('id')}")
                        person_response = self.session.get(
                            f"{self.base_url}/persons/{person_id}",
                            params={
                                'api_token': self.api_token,
                                'get_all_custom_fields': True
                            }
                        )
                        person_response.raise_for_status()
                        person_data_complete = person_response.json()
                        
                        if person_data_complete and person_data_complete.get('success'):
                            person_details = person_data_complete.get('data', {})
                            
                            # Tenta buscar o CPF de diferentes maneiras
                            # 1. Primeiro tenta pelo ID do campo conhecido
                            cpf = person_details.get(self.cpf_field_id)
                            
                            # 2. Se não encontrou, tenta nos campos personalizados
                            if not cpf:
                                custom_fields = person_details.get('custom_fields', {})
                                cpf = custom_fields.get(self.cpf_field_id)
                            
                            # 3. Se ainda não encontrou, procura nos campos personalizados pelo nome
                            if not cpf:
                                custom_fields_data = person_details.get('custom_fields_data', [])
                                for field in custom_fields_data:
                                    if field.get('key') == 'cpf' or field.get('name', '').lower() == 'cpf':
                                        cpf = field.get('value')
                                        break
                            
                            if cpf:
                                logger.info(f"CPF encontrado para pessoa {person_id}: {cpf}")
                            else:
                                logger.warning(f"CPF não encontrado para pessoa {person_id} após tentar múltiplos métodos")
                                
                    except Exception as e:
                        logger.error(f"Erro ao buscar dados completos da pessoa {person_id}: {str(e)}")
                
                dados_completos = {
                    'id': negocio.get('id'),
                    'titulo': negocio.get('title'),
                    'valor': negocio.get('value'),
                    'status': negocio.get('status'),
                    'pipeline_id': negocio.get('pipeline_id'),
                    'organization': organization_name,
                    'pessoa': person_name,
                    'cpf': cpf
                }
                
                negocios_completos.append(dados_completos)
                logger.info(f"Dados completos do negócio {negocio.get('id')} processados com sucesso")
                
                # Chama o callback se fornecido
                if callback:
                    callback(dados_completos)

            # Calcula o total de páginas
            total_paginas = (total_negocios + limite_por_pagina - 1) // limite_por_pagina if total_negocios > 0 else 0
            
            # Prepara o resultado com informações de paginação
            resultado = {
                'negocios': negocios_completos,
                'total': total_negocios,
                'pagina_atual': pagina,
                'total_paginas': total_paginas,
                'tem_proxima': tem_proxima
            }
            
            logger.info(f"Recuperados {len(negocios_completos)} negócios com dados completos (página {pagina+1} de {total_paginas})")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar negócios com dados completos: {str(e)}")
            raise

    def listar_negocios(self, status: Optional[str] = None, term: Optional[str] = None) -> List[Dict]:
        try:
            todos_negocios = []
            start = 0
            limit = 500  # Máximo permitido pela API por página

            while True:
                params = {
                    'api_token': self.api_token,
                    'start': start,
                    'limit': limit
                }
                if status:
                    params['status'] = status
                if term:
                    params['term'] = term

                response = self.session.get(f"{self.base_url}/deals", params=params)
                response.raise_for_status()
                data = response.json()

                if data and data.get('success'):
                    deals = data.get('data', [])
                    pagination = data.get('additional_data', {}).get('pagination', {})

                # Log para verificar o que está vindo na paginação
                logger.info(f"Página atual: start={start}, limit={limit}")
                logger.info(f"Pagination: {pagination}")

                if deals:
                    todos_negocios.extend(deals)
                    logger.info(f"Recuperados {len(deals)} negócios do Pipedrive (offset: {start})")

                # Se não há mais itens, sair do loop
                if not pagination.get('more_items_in_collection', False):
                    break

                # Pegar `next_start` corretamente
                next_start = pagination.get('next_start')
                if next_start is None:
                    logger.warning("`next_start` não encontrado, usando start + limit")
                    next_start = start + limit  # Fallback para evitar travar a paginação

                start = next_start

            logger.info(f"Total de negócios recuperados: {len(todos_negocios)}")
            return todos_negocios

        except Exception as e:
            logger.error(f"Erro ao listar negócios: {str(e)}")
            raise


    def buscar_negocio(self, deal_id: int) -> Optional[Dict]:
        """
        Busca um negócio específico pelo ID.
        
        Args:
            deal_id: ID do negócio no Pipedrive
            
        Returns:
            Dados do negócio ou None se não encontrado
        """
        try:
            response = self.session.get(
                f"{self.base_url}/deals/{deal_id}",
                params={'api_token': self.api_token}
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                deal = data.get('data')
                if deal:
                    logger.info(f"Negócio {deal_id} recuperado com sucesso")
                    return deal
                logger.warning(f"Negócio {deal_id} não encontrado")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar negócio {deal_id}: {str(e)}")
            raise

    def criar_negocio(self, titulo: str, valor: float, 
                      pessoa_id: Optional[int] = None, 
                      organizacao_id: Optional[int] = None,
                      dados_adicionais: Optional[Dict] = None) -> Optional[Dict]:
        """
        Cria um novo negócio no Pipedrive.
        
        Args:
            titulo: Título do negócio
            valor: Valor do negócio
            pessoa_id: ID da pessoa relacionada (opcional)
            organizacao_id: ID da organização relacionada (opcional)
            dados_adicionais: Dados adicionais para o negócio (opcional)
            
        Returns:
            Dados do negócio criado ou None em caso de erro
        """
        try:
            deal_data = {
                'title': titulo,
                'value': valor,
                'currency': 'BRL'
            }
            
            if pessoa_id:
                deal_data['person_id'] = pessoa_id
            if organizacao_id:
                deal_data['org_id'] = organizacao_id
            if dados_adicionais:
                deal_data.update(dados_adicionais)
                
            response = self.session.post(
                f"{self.base_url}/deals",
                params={'api_token': self.api_token},
                json=deal_data
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                deal = data.get('data')
                logger.info(f"Negócio '{titulo}' criado com sucesso. ID: {deal.get('id')}")
                return deal
                
            logger.error(f"Erro ao criar negócio: {response.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar negócio: {str(e)}")
            raise

    def atualizar_negocio(self, deal_id: int, dados: Dict) -> Optional[Dict]:
        """
        Atualiza um negócio existente no Pipedrive.
        
        Args:
            deal_id: ID do negócio a ser atualizado
            dados: Dicionário com os dados a serem atualizados
            
        Returns:
            Dados do negócio atualizado ou None em caso de erro
        """
        try:
            response = self.session.put(
                f"{self.base_url}/deals/{deal_id}",
                params={'api_token': self.api_token},
                json=dados
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                deal = data.get('data')
                logger.info(f"Negócio {deal_id} atualizado com sucesso")
                return deal
                
            logger.error(f"Erro ao atualizar negócio: {response.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao atualizar negócio {deal_id}: {str(e)}")
            raise

    def deletar_negocio(self, deal_id: int) -> bool:
        """
        Deleta um negócio do Pipedrive.
        
        Args:
            deal_id: ID do negócio a ser deletado
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/deals/{deal_id}",
                params={'api_token': self.api_token}
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                logger.info(f"Negócio {deal_id} deletado com sucesso")
                return True
                
            logger.error(f"Erro ao deletar negócio: {response.get('error', 'Erro desconhecido')}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar negócio {deal_id}: {str(e)}")
            raise

    def buscar_por_nome(self, nome: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Busca leads (negócios) pelo título no Pipedrive.
        
        Args:
            nome: Título ou parte do título do lead para buscar
            case_sensitive: Se True, diferencia maiúsculas e minúsculas na busca
            
        Returns:
            Lista de leads encontrados que correspondem ao título
        """
        try:
            # Primeiro busca os negócios pelo nome usando a API de busca
            params = {
                'api_token': self.api_token,
                'term': nome,
                'exact_match': not case_sensitive,
                'fields': 'title',  # Busca apenas no campo título
                'get_all_custom_fields': True,
                'get_summary': True
            }
            
            response = self.session.get(f"{self.base_url}/deals/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                deals = data.get('data', {}).get('items', [])
                logger.info(f"Encontrados {len(deals)} leads com o título '{nome}'")
                
                # Lista para armazenar os IDs dos negócios encontrados
                deal_ids = [item.get('item', {}).get('id') for item in deals if item.get('item', {}).get('id')]
                
                # Busca os dados completos para cada negócio encontrado
                negocios_completos = []
                for deal_id in deal_ids:
                    try:
                        # Busca os dados completos do negócio
                        negocio_response = self.session.get(
                            f"{self.base_url}/deals/{deal_id}",
                            params={
                                'api_token': self.api_token,
                                'get_all_custom_fields': True
                            }
                        )
                        negocio_response.raise_for_status()
                        negocio_data = negocio_response.json()
                        
                        if negocio_data and negocio_data.get('success'):
                            negocio = negocio_data.get('data', {})
                            
                            # Extrai dados da organização
                            org_data = negocio.get('org_id', {})
                            organization_name = org_data.get('name') if isinstance(org_data, dict) else None
                            
                            # Extrai dados da pessoa
                            person_data = negocio.get('person_id', {})
                            person_name = person_data.get('name') if isinstance(person_data, dict) else None
                            person_id = person_data.get('value') if isinstance(person_data, dict) else person_data.get('id') if isinstance(person_data, dict) else None
                            
                            # Busca dados completos da pessoa para obter o CPF
                            cpf = None
                            if person_id:
                                try:
                                    # Busca os campos personalizados da pessoa
                                    logger.info(f"Buscando dados da pessoa {person_id} para o negócio {deal_id}")
                                    person_response = self.session.get(
                                        f"{self.base_url}/persons/{person_id}",
                                        params={
                                            'api_token': self.api_token,
                                            'get_all_custom_fields': True
                                        }
                                    )
                                    person_response.raise_for_status()
                                    person_data_complete = person_response.json()
                                    
                                    if person_data_complete and person_data_complete.get('success'):
                                        person_details = person_data_complete.get('data', {})
                                        
                                        # Tenta buscar o CPF de diferentes maneiras
                                        # 1. Primeiro tenta pelo ID do campo conhecido
                                        cpf = person_details.get(self.cpf_field_id)
                                        
                                        # 2. Se não encontrou, tenta nos campos personalizados
                                        if not cpf:
                                            custom_fields = person_details.get('custom_fields', {})
                                            cpf = custom_fields.get(self.cpf_field_id)
                                        
                                        # 3. Se ainda não encontrou, procura nos campos personalizados pelo nome
                                        if not cpf:
                                            custom_fields_data = person_details.get('custom_fields_data', [])
                                            for field in custom_fields_data:
                                                if field.get('key') == 'cpf' or field.get('name', '').lower() == 'cpf':
                                                    cpf = field.get('value')
                                                    break
                                        
                                        if cpf:
                                            logger.info(f"CPF encontrado para pessoa {person_id}: {cpf}")
                                        else:
                                            logger.warning(f"CPF não encontrado para pessoa {person_id} após tentar múltiplos métodos")
                                except Exception as e:
                                    logger.error(f"Erro ao buscar dados completos da pessoa {person_id}: {str(e)}")
                            
                            # Busca CNPJ da organização
                            cnpj = None
                            org_id = org_data.get('value') if isinstance(org_data, dict) else org_data.get('id') if isinstance(org_data, dict) else None
                            if org_id:
                                try:
                                    logger.info(f"Buscando dados da organização {org_id} para o negócio {deal_id}")
                                    org_response = self.session.get(
                                        f"{self.base_url}/organizations/{org_id}",
                                        params={'api_token': self.api_token}
                                    )
                                    org_response.raise_for_status()
                                    org_data_complete = org_response.json()
                                    
                                    if org_data_complete and org_data_complete.get('success'):
                                        org_details = org_data_complete.get('data', {})
                                        # Extrai CNPJ do campo personalizado
                                        cnpj = org_details.get(self.cnpj_field_id)
                                        
                                        if cnpj:
                                            logger.info(f"CNPJ encontrado para organização {org_id}: {cnpj}")
                                        else:
                                            logger.warning(f"CNPJ não encontrado para organização {org_id}")
                                except Exception as e:
                                    logger.error(f"Erro ao buscar dados da organização {org_id}: {str(e)}")
                            
                            dados_completos = {
                                'id': deal_id,
                                'titulo': negocio.get('title'),
                                'valor': negocio.get('value'),
                                'status': negocio.get('status'),
                                'pipeline_id': negocio.get('pipeline_id'),
                                'organization': organization_name,
                                'pessoa': person_name,
                                'cpf': cpf,
                                'cnpj': cnpj
                            }
                            
                            negocios_completos.append(dados_completos)
                            logger.info(f"Dados completos do negócio {deal_id} processados com sucesso")
                            
                    except Exception as e:
                        logger.error(f"Erro ao buscar dados completos do negócio {deal_id}: {str(e)}")
                        continue
                
                return negocios_completos
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar leads por título '{nome}': {str(e)}")
            raise

    def atualizar_pessoa(self, person_id: Union[int, Dict], dados: Dict) -> Optional[Dict]:
        """
        Atualiza uma pessoa existente no Pipedrive.
        
        Args:
            person_id: ID da pessoa a ser atualizada. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            dados: Dicionário com os dados a serem atualizados
            
        Returns:
            Dados da pessoa atualizada ou None em caso de erro
        """
        try:
            # Extrai o ID numérico se for um dicionário
            if isinstance(person_id, dict) and 'value' in person_id:
                numeric_id = int(person_id['value'])
                logger.info(f"Convertendo ID de objeto para numérico: {person_id} -> {numeric_id}")
                person_id = numeric_id
            
            # Garante que o ID seja um inteiro
            person_id = int(person_id)
            
            logger.info(f"Atualizando pessoa {person_id} no Pipedrive")
            response = self.session.put(
                f"{self.base_url}/persons/{person_id}",
                params={'api_token': self.api_token},
                json=dados
            )
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                person = data.get('data')
                logger.info(f"Pessoa {person_id} atualizada com sucesso")
                return person
                
            logger.error(f"Erro ao atualizar pessoa: {data.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao atualizar pessoa {person_id}: {str(e)}")
            raise
            
    def atualizar_telefones_pessoa(self, person_id: Union[int, Dict], telefones: List[str]) -> Optional[Dict]:
        """
        Atualiza os telefones de uma pessoa no Pipedrive.
        
        De acordo com a documentação da API, os telefones devem ser enviados como um array
        na propriedade 'phone' para o endpoint de atualização de pessoas.
        
        Esta função preserva os telefones existentes e adiciona apenas os novos.
        
        Args:
            person_id: ID da pessoa a ser atualizada. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            telefones: Lista de telefones a serem adicionados
            
        Returns:
            Dados da pessoa atualizada ou None em caso de erro
        """
        try:
            # Extrai o ID numérico se for um dicionário
            if isinstance(person_id, dict) and 'value' in person_id:
                numeric_id = int(person_id['value'])
                logger.info(f"Convertendo ID de objeto para numérico: {person_id} -> {numeric_id}")
                person_id = numeric_id
            
            # Garante que o ID seja um inteiro
            person_id = int(person_id)
            
            # Primeiro, obtém os dados atuais da pessoa para preservar os telefones existentes
            pessoa_atual = self.obter_pessoa(person_id)
            if not pessoa_atual:
                logger.error(f"Não foi possível obter os dados da pessoa {person_id} para atualizar telefones")
                return None
            
            # Obtém os telefones existentes
            telefones_existentes = []
            
            # Verifica se há telefones no formato de array de objetos
            if 'phone' in pessoa_atual and isinstance(pessoa_atual['phone'], list):
                for phone in pessoa_atual['phone']:
                    if isinstance(phone, dict) and 'value' in phone:
                        telefones_existentes.append(phone['value'])
            # Verifica se há telefones no formato de string
            elif 'phone' in pessoa_atual and pessoa_atual['phone'] and isinstance(pessoa_atual['phone'], str):
                telefones_existentes = [tel.strip() for tel in pessoa_atual['phone'].split(',') if tel.strip()]
            
            logger.info(f"Telefones existentes da pessoa {person_id}: {telefones_existentes}")
            
            # Formata os telefones como esperado pela API
            phones_data = []
            
            # Adiciona os telefones existentes primeiro
            for i, telefone in enumerate(telefones_existentes):
                if telefone and telefone.strip():
                    # Normaliza o formato do telefone
                    telefone_normalizado = telefone.strip()
                    phones_data.append({
                        "value": telefone_normalizado,
                        "primary": i == 0,  # O primeiro é primário
                        "label": "mobile"
                    })
            
            # Adiciona os novos telefones, verificando se já não existem
            for telefone in telefones:
                if telefone and telefone.strip():
                    # Normaliza o formato do telefone para comparação
                    telefone_normalizado = telefone.strip()
                    
                    # Verifica se o telefone já existe (mesmo que em formato diferente)
                    telefone_ja_existe = False
                    for tel_existente in telefones_existentes:
                        tel_existente_normalizado = tel_existente.strip()
                        if telefone_normalizado == tel_existente_normalizado:
                            telefone_ja_existe = True
                            break
                    
                    # Se o telefone não existe, adiciona
                    if not telefone_ja_existe:
                        logger.info(f"Adicionando novo telefone: {telefone_normalizado}")
                        phones_data.append({
                            "value": telefone_normalizado,
                            "primary": len(phones_data) == 0,  # Só será primário se for o único
                            "label": "mobile"
                        })
                    else:
                        logger.info(f"Telefone {telefone_normalizado} já existe e não será adicionado novamente")
            
            # Se não houver telefones para atualizar, retorna
            if not phones_data:
                logger.info(f"Não há novos telefones para adicionar à pessoa {person_id}")
                return pessoa_atual
            
            # Prepara os dados para a requisição
            dados = {
                "phone": phones_data
            }
            
            logger.info(f"Atualizando telefones da pessoa {person_id}")
            logger.info(f"Dados enviados para API: {dados}")
            
            # Define os headers para garantir que o conteúdo seja tratado como JSON
            headers = {'Content-Type': 'application/json'}
            
            # Faz a requisição para atualizar a pessoa
            response = self.session.put(
                f"{self.base_url}/persons/{person_id}",
                params={'api_token': self.api_token},
                json=dados,
                headers=headers
            )
            
            # Log da resposta para debug
            logger.info(f"Status code da resposta: {response.status_code}")
            logger.info(f"Resposta da API: {response.text[:500]}")
            
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                person = data.get('data')
                logger.info(f"Telefones da pessoa {person_id} atualizados com sucesso")
                
                # Log dos telefones atualizados para verificação
                if person:
                    if 'phone' in person:
                        logger.info(f"Campo 'phone' da pessoa {person_id}: {person['phone']}")
                    if 'phones' in person:
                        logger.info(f"Campo 'phones' da pessoa {person_id}: {person['phones']}")
                
                return person
            
            logger.error(f"Erro ao atualizar telefones: {data.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao atualizar telefones da pessoa {person_id}: {str(e)}")
            # Não propaga a exceção para evitar interrupção do processo
            return None
    
    def atualizar_emails_pessoa(self, person_id: Union[int, Dict], emails: List[str]) -> Optional[Dict]:
        """
        Atualiza os emails de uma pessoa no Pipedrive.
        
        De acordo com a documentação da API, os emails devem ser enviados como um array
        na propriedade 'email' para o endpoint de atualização de pessoas.
        
        Esta função preserva os emails existentes e adiciona apenas os novos.
        
        Args:
            person_id: ID da pessoa a ser atualizada. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            emails: Lista de emails a serem adicionados
            
        Returns:
            Dados da pessoa atualizada ou None em caso de erro
        """
        try:
            # Extrai o ID numérico se for um dicionário
            if isinstance(person_id, dict) and 'value' in person_id:
                numeric_id = int(person_id['value'])
                logger.info(f"Convertendo ID de objeto para numérico: {person_id} -> {numeric_id}")
                person_id = numeric_id
            
            # Garante que o ID seja um inteiro
            person_id = int(person_id)
            
            # Primeiro, obtém os dados atuais da pessoa para preservar os emails existentes
            pessoa_atual = self.obter_pessoa(person_id)
            if not pessoa_atual:
                logger.error(f"Não foi possível obter os dados da pessoa {person_id} para atualizar emails")
                return None
            
            # Obtém os emails existentes
            emails_existentes = []
            
            # Verifica se há emails no formato de array de objetos
            if 'email' in pessoa_atual and isinstance(pessoa_atual['email'], list):
                for email in pessoa_atual['email']:
                    if isinstance(email, dict) and 'value' in email:
                        emails_existentes.append(email['value'])
            # Verifica se há emails no formato de string
            elif 'email' in pessoa_atual and pessoa_atual['email'] and isinstance(pessoa_atual['email'], str):
                emails_existentes = [email.strip() for email in pessoa_atual['email'].split(',') if email.strip()]
            
            logger.info(f"Emails existentes da pessoa {person_id}: {emails_existentes}")
            
            # Formata os emails como esperado pela API
            emails_data = []
            
            # Adiciona os emails existentes primeiro
            for i, email in enumerate(emails_existentes):
                if email and email.strip():
                    # Normaliza o formato do email
                    email_normalizado = email.strip().lower()
                    emails_data.append({
                        "value": email_normalizado,
                        "primary": i == 0,  # O primeiro é primário
                        "label": "work"
                    })
            
            # Adiciona os novos emails, verificando se já não existem
            for email in emails:
                if email and email.strip():
                    # Normaliza o formato do email para comparação
                    email_normalizado = email.strip().lower()
                    
                    # Verifica se o email já existe
                    if email_normalizado not in [e.lower() for e in emails_existentes]:
                        logger.info(f"Adicionando novo email: {email_normalizado}")
                        emails_data.append({
                            "value": email_normalizado,
                            "primary": len(emails_data) == 0,  # Só será primário se for o único
                            "label": "work"
                        })
                    else:
                        logger.info(f"Email {email_normalizado} já existe e não será adicionado novamente")
            
            # Se não houver emails para atualizar, retorna
            if not emails_data:
                logger.info(f"Não há novos emails para adicionar à pessoa {person_id}")
                return pessoa_atual
            
            # Prepara os dados para a requisição
            dados = {
                "email": emails_data
            }
            
            logger.info(f"Atualizando emails da pessoa {person_id}")
            logger.info(f"Dados enviados para API: {dados}")
            
            # Define os headers para garantir que o conteúdo seja tratado como JSON
            headers = {'Content-Type': 'application/json'}
            
            # Faz a requisição para atualizar a pessoa
            response = self.session.put(
                f"{self.base_url}/persons/{person_id}",
                params={'api_token': self.api_token},
                json=dados,
                headers=headers
            )
            
            # Log da resposta para debug
            logger.info(f"Status code da resposta: {response.status_code}")
            logger.info(f"Resposta da API: {response.text[:500]}")
            
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                person = data.get('data')
                logger.info(f"Emails da pessoa {person_id} atualizados com sucesso")
                return person
                
            logger.error(f"Erro ao atualizar emails: {data.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao atualizar emails da pessoa {person_id}: {str(e)}")
            raise
    
    def adicionar_nota_negocio(self, deal_id: int, conteudo: str, pdf_base64: Optional[str] = None) -> Optional[Dict]:
        """
        Adiciona uma nota a um negócio no Pipedrive, opcionalmente com um arquivo PDF anexado.
        
        Args:
            deal_id: ID do negócio ao qual a nota será adicionada
            conteudo: Conteúdo da nota
            pdf_base64: Arquivo PDF em formato base64 (opcional)
            
        Returns:
            Dados da nota criada ou None em caso de erro
        """
        try:
            note_data = {
                'content': conteudo,
                'deal_id': deal_id
            }
            
            # Se tiver PDF, adiciona como anexo
            files = None
            if pdf_base64:
                import base64
                import io
                
                # Decodifica o PDF de base64 para bytes
                pdf_bytes = base64.b64decode(pdf_base64)
                
                # Prepara os arquivos para upload
                files = {
                    'file': ('relatorio.pdf', io.BytesIO(pdf_bytes), 'application/pdf')
                }
            
            # Faz a requisição para adicionar a nota
            if files:
                # Se tiver arquivos, usa multipart/form-data
                response = self.session.post(
                    f"{self.base_url}/notes",
                    params={'api_token': self.api_token},
                    data=note_data,
                    files=files
                )
            else:
                # Sem arquivos, usa application/json
                response = self.session.post(
                    f"{self.base_url}/notes",
                    params={'api_token': self.api_token},
                    json=note_data
                )
                
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success'):
                note = data.get('data')
                logger.info(f"Nota adicionada com sucesso ao negócio {deal_id}")
                return note
                
            logger.error(f"Erro ao adicionar nota: {response.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao adicionar nota ao negócio {deal_id}: {str(e)}")
            raise

    def adicionar_atividade(self, deal_id: int, assunto: str, tipo: str = 'task', 
                          concluida: bool = False, data_vencimento: Optional[str] = None,
                          nota: Optional[str] = None, owner_id: Optional[int] = None) -> Optional[Dict]:
        """
        Adiciona uma atividade (tarefa) a um negócio no Pipedrive.
        
        Args:
            deal_id: ID do negócio ao qual a atividade será adicionada
            assunto: Assunto/título da atividade
            tipo: Tipo da atividade (padrão: 'task')
            concluida: Se a atividade já está concluída
            data_vencimento: Data de vencimento no formato 'YYYY-MM-DD'
            nota: Descrição/anotação da atividade (opcional)
            owner_id: ID do usuário que será o proprietário da atividade (opcional).
                     Se não for fornecido, o proprietário será o usuário da API.
            
        Returns:
            Dados da atividade criada ou None em caso de erro
        """
        try:
            # Garante que o deal_id seja um inteiro
            try:
                deal_id = int(deal_id)
            except (ValueError, TypeError):
                logger.error(f"ID do negócio inválido: {deal_id} não é um número válido")
                return None
                
            # Prepara os dados da atividade
            activity_data = {
                'subject': assunto,
                'type': tipo,
                'deal_id': deal_id,
                'done': 1 if concluida else 0
            }
            
            # Adiciona o proprietário da atividade se fornecido
            if owner_id:
                activity_data['user_id'] = owner_id
            
            # Adiciona nota/descrição se fornecida
            if nota:
                activity_data['note'] = nota
            
            # Adiciona data de vencimento se fornecida
            if data_vencimento:
                activity_data['due_date'] = data_vencimento
            else:
                # Se não fornecida, usa a data atual
                from datetime import datetime
                activity_data['due_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Log dos dados da atividade para depuração
            logger.info(f"Dados da atividade a ser criada: {activity_data}")
            
            # Faz a requisição para adicionar a atividade
            response = self.session.post(
                f"{self.base_url}/activities",
                params={'api_token': self.api_token},
                json=activity_data
            )
            
            # Log da resposta para depuração
            logger.info(f"Status code da resposta: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            # Log da resposta JSON para depuração
            logger.info(f"Resposta da API: {data}")
            
            if data and data.get('success'):
                activity = data.get('data')
                logger.info(f"Atividade '{assunto}' adicionada com sucesso ao negócio {deal_id}")
                return activity
                
            logger.error(f"Erro ao adicionar atividade: {data.get('error', 'Erro desconhecido')}")
            if 'error_info' in data:
                logger.error(f"Detalhes do erro: {data.get('error_info')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao adicionar atividade ao negócio {deal_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Não propaga a exceção para evitar interrupção do processo
            return None

    def obter_pessoa(self, person_id: Union[int, Dict]) -> Optional[Dict]:
        """
        Obtém os dados de uma pessoa no Pipedrive pelo ID.
        
        Args:
            person_id: ID da pessoa a ser obtida. Pode ser um inteiro ou um dicionário 
                      contendo o ID no campo 'value'
            
        Returns:
            Dados da pessoa ou None em caso de erro
        """
        try:
            # Extrai o ID numérico se for um dicionário
            if isinstance(person_id, dict) and 'value' in person_id:
                numeric_id = int(person_id['value'])
                logger.info(f"Convertendo ID de objeto para numérico: {person_id} -> {numeric_id}")
                person_id = numeric_id
            
            # Garante que o ID seja um inteiro
            person_id = int(person_id)
            
            logger.info(f"Obtendo dados da pessoa {person_id} do Pipedrive")
            response = self.session.get(
                f"{self.base_url}/persons/{person_id}",
                params={'api_token': self.api_token}
            )
            response.raise_for_status()
            data = response.json()
            
            # Log da resposta completa para debug
            logger.info(f"Resposta completa da API para pessoa {person_id}: {data}")
            
            if data and data.get('success'):
                person = data.get('data')
                logger.info(f"Pessoa {person_id} obtida com sucesso")
                
                # Log específico dos campos de telefone
                if person:
                    if 'phone' in person:
                        logger.info(f"Campo 'phone' da pessoa {person_id}: {person['phone']}")
                    if 'phones' in person:
                        logger.info(f"Campo 'phones' da pessoa {person_id}: {person['phones']}")
                
                return person
                
            logger.error(f"Erro ao obter pessoa: {data.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter pessoa {person_id}: {str(e)}")
            # Não propaga a exceção para evitar interrupção do processo
            return None

    def obter_negocio(self, deal_id: int) -> Optional[Dict]:
        """
        Obtém os dados de um negócio no Pipedrive pelo ID.
        
        Args:
            deal_id: ID do negócio a ser obtido
            
        Returns:
            Dados do negócio ou None em caso de erro
        """
        try:
            # Faz a requisição para obter o negócio
            logger.info(f"Obtendo dados do negócio {deal_id} do Pipedrive")
            response = self.session.get(
                f"{self.base_url}/deals/{deal_id}",
                params={'api_token': self.api_token}
            )
            response.raise_for_status()
            data = response.json()
            
            # Log da resposta completa para debug
            logger.info(f"Resposta completa da API para negócio {deal_id}: {data}")
            
            if data and data.get('success'):
                deal = data.get('data')
                logger.info(f"Negócio {deal_id} obtido com sucesso")
                
                # Log específico do ID da pessoa associada
                if deal and 'person_id' in deal:
                    logger.info(f"ID da pessoa associada ao negócio {deal_id}: {deal['person_id']}")
                
                return deal
                
            logger.error(f"Erro ao obter negócio: {data.get('error', 'Erro desconhecido')}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter negócio {deal_id}: {str(e)}")
            # Não propaga a exceção para evitar interrupção do processo
            return None

    def adicionar_anexo_negocio(self, deal_id: int, arquivo_path: str, nome_arquivo: str, tipo_mime: str = 'application/pdf') -> Optional[Dict]:
        """
        Anexa um arquivo a um negócio (deal) no Pipedrive.
        
        Args:
            deal_id: ID do negócio
            arquivo_path: Caminho do arquivo a ser anexado
            nome_arquivo: Nome do arquivo a ser anexado
            tipo_mime: Tipo MIME do arquivo (padrão: application/pdf)
            
        Returns:
            Dados do anexo criado ou None em caso de erro
        """
        try:
            import os
            import requests
            import json
            
            # Verifica se o arquivo existe
            if not os.path.exists(arquivo_path):
                logger.error(f"Arquivo '{arquivo_path}' não encontrado")
                return None
            
            # Log do tamanho do arquivo para depuração
            tamanho_kb = os.path.getsize(arquivo_path) / 1024
            logger.info(f"Tamanho do arquivo a ser anexado: {tamanho_kb:.2f} KB")
            
            # URL da API
            url = f"{self.base_url}/files?api_token={self.api_token}"
            
            logger.info(f"URL da requisição: {url}")
            
            # Prepara os dados para o multipart/form-data
            # Em Python, o equivalente ao curl_file_create do PHP é abrir o arquivo em modo binário
            files = {
                'file': (nome_arquivo, open(arquivo_path, 'rb'), tipo_mime)
            }
            
            # Dados adicionais
            data = {
                'deal_id': str(deal_id)
            }
            
            # Log dos parâmetros da requisição
            logger.info(f"Enviando arquivo '{nome_arquivo}' para o negócio {deal_id}")
            logger.info(f"Dados: {data}")
            
            # Faz a requisição POST
            response = requests.post(
                url,
                files=files,
                data=data
            )
            
            # Log da resposta para depuração
            logger.info(f"Status code da resposta: {response.status_code}")
            
            # Fecha o arquivo
            files['file'][1].close()
            
            # Tenta obter o conteúdo JSON da resposta
            try:
                result = response.json()
                logger.info(f"Resposta da API: {result}")
                
                # Verifica se a resposta contém dados
                if not result.get('data'):
                    error_msg = result.get('error', 'Erro desconhecido')
                    logger.error(f"Erro retornado pela API: {error_msg}")
                    
                    # Verifica se há mais detalhes sobre o erro
                    if 'error_info' in result:
                        logger.error(f"Detalhes do erro: {result['error_info']}")
                    
                    return None
                
                # Verifica se o ID do arquivo foi retornado
                if result.get('data', {}).get('id'):
                    logger.info(f"Arquivo '{nome_arquivo}' anexado com sucesso ao negócio {deal_id}")
                    return result.get('data')
                else:
                    logger.error(f"ID do arquivo não encontrado na resposta")
                    return None
                
            except ValueError:
                # Se a resposta não for JSON válido
                logger.error(f"Resposta não é um JSON válido: {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Erro ao anexar arquivo ao negócio {deal_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None


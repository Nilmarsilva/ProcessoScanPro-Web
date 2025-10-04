import httpx
import os
import time
from typing import List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from ..models.judit import JuditBatch, JuditRequest, JuditResult
from ..db.base import SessionLocal

class JuditService:
    def __init__(self):
        self.api_key = os.getenv("JUDIT_API_KEY")
        self.base_url = "https://requests.prod.judit.io"
        self.webhook_url = os.getenv("JUDIT_WEBHOOK_URL")
        
    def processar_com_webhook(
        self,
        batch_id: str,
        dados: List[Dict[str, Any]],
        with_attachments: bool = True
    ):
        """
        Processa dados com busca em tempo real (on-demand = true)
        Usa webhook para receber respostas assíncronas
        """
        db = SessionLocal()
        
        try:
            with httpx.Client(timeout=30.0) as client:
                for idx, registro in enumerate(dados):
                    try:
                        # Extrai CPF/CNPJ do registro
                        cpf = registro.get("CPF", "").strip()
                        cnpj = registro.get("CNPJ", "").strip()
                        
                        documento = cnpj if cnpj else cpf
                        doc_type = "cnpj" if cnpj else "cpf"
                        
                        if not documento:
                            print(f"[JUDIT] Registro {idx+1}: Sem CPF/CNPJ")
                            continue
                        
                        request_id = str(uuid.uuid4())
                        
                        # Prepara payload para API Judit
                        payload = {
                            "search": {
                                "search_type": doc_type,
                                "search_key": documento
                            },
                            "callback_url": self.webhook_url,
                            "with_attachments": with_attachments
                        }
                        
                        headers = {
                            "api-key": self.api_key,
                            "Content-Type": "application/json"
                        }
                        
                        response = client.post(
                            f"{self.base_url}/requests",
                            json=payload,
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            judit_request_id = result.get("request_id")
                            
                            # Salva requisição no banco
                            req = JuditRequest(
                                batch_id=batch_id,
                                request_id=request_id,
                                judit_request_id=judit_request_id,
                                documento=documento,
                                doc_type=doc_type,
                                nome=registro.get("Título", registro.get("Pessoa", "")),
                                empresa=registro.get("Organização", ""),
                                status="aguardando"
                            )
                            db.add(req)
                            db.commit()
                            
                            print(f"[JUDIT] Requisição enviada: {documento} - ID: {judit_request_id}")
                        else:
                            print(f"[JUDIT] Erro ao enviar {documento}: {response.status_code}")
                            self._registrar_erro(db, batch_id, documento, f"HTTP {response.status_code}")
                        
                        # Delay de 1 segundo entre requisições para evitar rate limiting
                        time.sleep(1)
                    
                    except Exception as e:
                        print(f"[JUDIT] Erro no registro {idx+1}: {str(e)}")
                        self._registrar_erro(db, batch_id, registro.get("CPF", registro.get("CNPJ", "?")), str(e))
                
                # Atualiza status do batch
                batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
                if batch:
                    batch.status = "aguardando_webhooks"
                    db.commit()
                
                print(f"[JUDIT] Batch {batch_id}: Todas as requisições enviadas")
        
        except Exception as e:
            print(f"[JUDIT] Erro geral no batch {batch_id}: {str(e)}")
            batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
            if batch:
                batch.status = "erro"
                db.commit()
        finally:
            db.close()
    
    def processar_banco_dados(
        self,
        batch_id: str,
        dados: List[Dict[str, Any]],
        with_attachments: bool = True
    ):
        """
        Processa dados com busca no banco de dados (on-demand = false)
        Resposta síncrona - mais rápido
        """
        db = SessionLocal()
        
        try:
            with httpx.Client(timeout=30.0) as client:
                for idx, registro in enumerate(dados):
                    try:
                        cpf = registro.get("CPF", "").strip()
                        cnpj = registro.get("CNPJ", "").strip()
                        
                        documento = cnpj if cnpj else cpf
                        doc_type = "cnpj" if cnpj else "cpf"
                        
                        if not documento:
                            print(f"[JUDIT] Registro {idx+1}: Sem CPF/CNPJ")
                            continue
                        
                        # Prepara payload (SEM callback_url = banco de dados)
                        payload = {
                            "search": {
                                "search_type": doc_type,
                                "search_key": documento
                            },
                            "with_attachments": with_attachments
                        }
                        
                        headers = {
                            "api-key": self.api_key,
                            "Content-Type": "application/json"
                        }
                        
                        response = client.post(
                            f"{self.base_url}/requests",
                            json=payload,
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Processa resultado imediatamente
                            self._processar_resultado_banco(
                                db,
                                batch_id,
                                registro,
                                documento,
                                doc_type,
                                result
                            )
                            
                            print(f"[JUDIT] Processado: {documento}")
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            try:
                                error_detail = response.json()
                                error_msg = f"{error_msg} - {error_detail}"
                            except:
                                pass
                            print(f"[JUDIT] Erro ao consultar {documento}: {error_msg}")
                            self._registrar_erro(db, batch_id, documento, error_msg)
                        
                        # Delay de 1 segundo entre requisições para evitar rate limiting
                        time.sleep(1)
                    
                    except Exception as e:
                        print(f"[JUDIT] Erro no registro {idx+1}: {str(e)}")
                        self._registrar_erro(db, batch_id, registro.get("CPF", registro.get("CNPJ", "?")), str(e))
                
                # Atualiza status do batch como concluído
                batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
                if batch:
                    batch.status = "concluído"
                    db.commit()
                
                print(f"[JUDIT] Batch {batch_id}: Processamento concluído")
        
        except Exception as e:
            print(f"[JUDIT] Erro geral no batch {batch_id}: {str(e)}")
            batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
            if batch:
                batch.status = "erro"
                db.commit()
        finally:
            db.close()
    
    def processar_webhook(self, payload: Dict[str, Any]):
        """
        Processa callback recebido do webhook da Judit.io
        """
        db = SessionLocal()
        
        try:
            reference_id = payload.get("reference_id")
            webhook_payload = payload.get("payload", {})
            
            request_id = webhook_payload.get("request_id")
            response_type = webhook_payload.get("response_type")
            response_data = webhook_payload.get("response_data", {})
            
            print(f"[WEBHOOK] Processando: request_id={request_id}, type={response_type}")
            
            # Busca a requisição
            requisicao = db.query(JuditRequest).filter(
                JuditRequest.judit_request_id == request_id
            ).first()
            
            if not requisicao:
                print(f"[WEBHOOK] Requisição não encontrada: {request_id}")
                return
            
            batch_id = requisicao.batch_id
            
            # Processa de acordo com o tipo de resposta
            if response_type == "lawsuit":
                # Sucesso - processo encontrado
                self._processar_resultado_webhook(db, requisicao, response_data)
            elif response_type == "application_error":
                # Erro
                error_message = response_data.get("message", "Erro desconhecido")
                self._registrar_erro(db, batch_id, requisicao.documento, error_message)
            
            # Atualiza contadores
            self._atualizar_contadores(db, batch_id)
        
        except Exception as e:
            print(f"[WEBHOOK] Erro ao processar: {str(e)}")
        finally:
            db.close()
    
    def _processar_resultado_webhook(
        self,
        db: Session,
        requisicao: JuditRequest,
        response_data: Dict[str, Any]
    ):
        """Processa resultado recebido via webhook"""
        processos = []
        
        if isinstance(response_data, list):
            processos = response_data
        else:
            processos = [response_data]
        
        resultado = JuditResult(
            batch_id=requisicao.batch_id,
            request_id=requisicao.request_id,
            documento=requisicao.documento,
            doc_type=requisicao.doc_type,
            nome=requisicao.nome,
            empresa=requisicao.empresa,
            status="sucesso",
            qtd_processos=len(processos),
            processos=processos
        )
        db.add(resultado)
        
        # Atualiza requisição
        requisicao.status = "concluído"
        
        # Atualiza batch
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == requisicao.batch_id).first()
        if batch:
            batch.processados += 1
            batch.sucesso += 1
        
        db.commit()
        
        print(f"[WEBHOOK] Resultado salvo: {requisicao.documento} - {len(processos)} processos")
    
    def _processar_resultado_banco(
        self,
        db: Session,
        batch_id: str,
        registro: Dict[str, Any],
        documento: str,
        doc_type: str,
        result: Dict[str, Any]
    ):
        """Processa resultado da consulta no banco de dados"""
        processos = result.get("data", [])
        
        resultado = JuditResult(
            batch_id=batch_id,
            documento=documento,
            doc_type=doc_type,
            nome=registro.get("Título", registro.get("Pessoa", "")),
            empresa=registro.get("Organização", ""),
            status="sucesso",
            qtd_processos=len(processos),
            processos=processos
        )
        db.add(resultado)
        
        # Atualiza batch
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
        if batch:
            batch.processados += 1
            batch.sucesso += 1
        
        db.commit()
    
    def _registrar_erro(
        self,
        db: Session,
        batch_id: str,
        documento: str,
        erro: str
    ):
        """Registra erro no processamento"""
        resultado = JuditResult(
            batch_id=batch_id,
            documento=documento,
            status="erro",
            erro=erro
        )
        db.add(resultado)
        
        # Atualiza batch
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
        if batch:
            batch.processados += 1
            batch.erro += 1
        
        db.commit()
    
    def _atualizar_contadores(self, db: Session, batch_id: str):
        """Atualiza contadores e verifica se batch foi concluído"""
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
        
        if not batch:
            return
        
        # Se processou tudo, marca como concluído
        if batch.processados >= batch.total:
            batch.status = "concluído"
            db.commit()
            print(f"[JUDIT] Batch {batch_id} concluído: {batch.processados}/{batch.total}")

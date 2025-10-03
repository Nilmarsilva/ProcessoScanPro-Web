from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
from ..services.judit_service import JuditService
from ..db.base import get_db
from ..models.judit import JuditBatch, JuditRequest, JuditResult

router = APIRouter(prefix="/api/judit", tags=["judit"])
judit_service = JuditService()

# Modelos
class ProcessarRequest(BaseModel):
    dados: List[Dict[str, Any]]
    on_demand: bool = False
    with_attachments: bool = True

class StatusResponse(BaseModel):
    request_id: str
    status: str
    total: int
    processados: int
    sucesso: int
    erro: int
    resultados: List[Dict[str, Any]]

@router.post("/processar")
async def processar_dados(
    request: ProcessarRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Processa dados via API Judit.io
    - on_demand=true: Busca em tempo real (com webhook)
    - on_demand=false: Busca no banco de dados (mais rápido)
    """
    try:
        # Gera ID único para este lote de processamento
        batch_id = str(uuid.uuid4())
        
        # Salva informações do batch no banco
        batch = JuditBatch(
            batch_id=batch_id,
            total=len(request.dados),
            processados=0,
            sucesso=0,
            erro=0,
            on_demand=request.on_demand,
            status="processando"
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        
        # Processa em background
        if request.on_demand:
            # Tempo real com webhook
            background_tasks.add_task(
                judit_service.processar_com_webhook,
                batch_id,
                request.dados,
                request.with_attachments
            )
        else:
            # Banco de dados (mais rápido)
            background_tasks.add_task(
                judit_service.processar_banco_dados,
                batch_id,
                request.dados,
                request.with_attachments
            )
        
        return {
            "success": True,
            "batch_id": batch_id,
            "message": f"Processamento iniciado com {len(request.dados)} registros",
            "on_demand": request.on_demand
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{batch_id}")
async def obter_status(batch_id: str, db: Session = Depends(get_db)):
    """
    Obtém o status de um lote de processamento
    """
    try:
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        
        return {
            "success": True,
            "data": {
                "batch_id": batch.batch_id,
                "total": batch.total,
                "processados": batch.processados,
                "sucesso": batch.sucesso,
                "erro": batch.erro,
                "on_demand": batch.on_demand,
                "status": batch.status,
                "created_at": batch.created_at.isoformat() if batch.created_at else None
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def receber_webhook(request: Request):
    """
    Endpoint para receber callbacks da API Judit.io
    """
    try:
        # Recebe o payload do webhook
        payload = await request.json()
        
        # Extrai informações importantes
        reference_id = payload.get("reference_id")
        callback_id = payload.get("callback_id")
        event_type = payload.get("event_type")
        
        print(f"[WEBHOOK] Recebido: reference_id={reference_id}, event_type={event_type}")
        
        # Processa o webhook
        await judit_service.processar_webhook(payload)
        
        return {
            "success": True,
            "message": "Webhook processado com sucesso"
        }
    
    except Exception as e:
        print(f"[WEBHOOK] Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resultados/{batch_id}")
async def obter_resultados(batch_id: str, db: Session = Depends(get_db)):
    """
    Obtém os resultados processados de um lote
    """
    try:
        batch = db.query(JuditBatch).filter(JuditBatch.batch_id == batch_id).first()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        
        # Busca resultados
        resultados = db.query(JuditResult).filter(JuditResult.batch_id == batch_id).all()
        
        return {
            "success": True,
            "data": {
                "batch_id": batch_id,
                "status": batch.status,
                "total": batch.total,
                "processados": batch.processados,
                "sucesso": batch.sucesso,
                "erro": batch.erro,
                "resultados": [
                    {
                        "documento": r.documento,
                        "doc_type": r.doc_type,
                        "nome": r.nome,
                        "empresa": r.empresa,
                        "status": r.status,
                        "qtd_processos": r.qtd_processos,
                        "processos": r.processos,
                        "erro": r.erro,
                        "processado_at": r.processado_at.isoformat() if r.processado_at else None
                    }
                    for r in resultados
                ]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

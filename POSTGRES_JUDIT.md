# 🔄 Migração MongoDB → PostgreSQL para Judit.io

## ✅ O que já foi criado

### 1. Models PostgreSQL (`app/models/judit.py`)

Três tabelas criadas:
- **judit_batches**: Lotes de processamento
- **judit_requests**: Requisições individuais
- **judit_results**: Resultados

### 2. Service atualizado

`judit_service.py` já importa os models PostgreSQL.

## ⚙️ O que falta fazer

### 1. Atualizar Router (`app/routers/judit.py`)

**Trocar:**
```python
from ..database.mongo_client import get_database
```

**Por:**
```python
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..models.judit import JuditBatch, JuditRequest, JuditResult
```

**Em cada endpoint, adicionar:**
```python
@router.post("/processar")
async def processar_dados(
    request: ProcessarRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)  # ← Adicionar
):
```

### 2. Atualizar Service (`app/services/judit_service.py`)

Todos os métodos precisam receber `db: Session` como parâmetro.

**Exemplo de mudança:**

**Antes (MongoDB):**
```python
await db.judit_batches.insert_one(batch_doc)
```

**Depois (PostgreSQL):**
```python
batch = JuditBatch(
    batch_id=batch_id,
    total=len(dados),
    on_demand=on_demand
)
db.add(batch)
db.commit()
```

### 3. Registrar Models no Base

Em `app/db/base.py` ou `app/models/__init__.py`:

```python
from .judit import JuditBatch, JuditRequest, JuditResult
```

### 4. Criar Migration (Alembic)

```bash
cd backend
alembic revision --autogenerate -m "Add Judit tables"
alembic upgrade head
```

## 📋 Checklist Completo

- [x] Models criados (`judit.py`)
- [ ] Router atualizado (remover mongo_client)
- [ ] Service atualizado (usar SQLAlchemy)
- [ ] Models registrados no Base
- [ ] Migration criada e aplicada
- [ ] Remover arquivo `mongo_client.py`
- [ ] Remover `motor` do `requirements.txt`
- [ ] Remover variáveis MongoDB do `.env`

## 🎯 Resumo

**NÃO PRECISA de MongoDB!** Use apenas PostgreSQL que já está configurado.

**Benefícios:**
- ✅ Um banco só (PostgreSQL)
- ✅ Menos dependências
- ✅ Mais simples de gerenciar
- ✅ Já tem Alembic configurado

---

**Quer que eu complete a migração para PostgreSQL?**

-- Tabelas para integração Judit.io

-- Tabela de lotes de processamento
CREATE TABLE IF NOT EXISTS judit_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    total INTEGER DEFAULT 0,
    processados INTEGER DEFAULT 0,
    sucesso INTEGER DEFAULT 0,
    erro INTEGER DEFAULT 0,
    on_demand BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'processando',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_judit_batches_batch_id ON judit_batches(batch_id);
CREATE INDEX idx_judit_batches_status ON judit_batches(status);

-- Tabela de requisições individuais
CREATE TABLE IF NOT EXISTS judit_requests (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL,
    request_id VARCHAR(100) UNIQUE,
    judit_request_id VARCHAR(100),
    documento VARCHAR(20),
    doc_type VARCHAR(10),
    nome VARCHAR(255),
    empresa VARCHAR(255),
    status VARCHAR(50) DEFAULT 'aguardando',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_judit_requests_batch_id ON judit_requests(batch_id);
CREATE INDEX idx_judit_requests_request_id ON judit_requests(request_id);
CREATE INDEX idx_judit_requests_judit_request_id ON judit_requests(judit_request_id);

-- Tabela de resultados
CREATE TABLE IF NOT EXISTS judit_results (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL,
    request_id VARCHAR(100),
    documento VARCHAR(20),
    doc_type VARCHAR(10),
    nome VARCHAR(255),
    empresa VARCHAR(255),
    status VARCHAR(50),
    qtd_processos INTEGER DEFAULT 0,
    processos JSONB,
    erro TEXT,
    processado_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_judit_results_batch_id ON judit_results(batch_id);
CREATE INDEX idx_judit_results_request_id ON judit_results(request_id);
CREATE INDEX idx_judit_results_documento ON judit_results(documento);

-- Comentários
COMMENT ON TABLE judit_batches IS 'Lotes de processamento Judit.io';
COMMENT ON TABLE judit_requests IS 'Requisições individuais para Judit.io';
COMMENT ON TABLE judit_results IS 'Resultados do processamento';

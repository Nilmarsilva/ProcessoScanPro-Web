-- Adiciona coluna deal_id na tabela judit_results
ALTER TABLE judit_results ADD COLUMN IF NOT EXISTS deal_id VARCHAR(20);

-- Verifica se a coluna foi criada
\d judit_results

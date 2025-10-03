const API_URL = 'http://localhost:8000/api/dados';

export const dadosService = {
  async checkPipedrive(data, colunas) {
    const response = await fetch(`${API_URL}/check-pipedrive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data,
        coluna_nome: colunas.nome,
        coluna_cpf: colunas.cpf,
        coluna_org: colunas.org
      })
    });
    
    if (!response.ok) {
      throw new Error('Erro ao verificar Pipedrive');
    }
    
    return response.json();
  },

  async assertivaCNPJ(data, colunaCNPJ) {
    const response = await fetch(`${API_URL}/assertiva-cnpj`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data,
        coluna_cnpj: colunaCNPJ
      })
    });
    
    if (!response.ok) {
      throw new Error('Erro ao consultar Assertiva');
    }
    
    return response.json();
  },

  async invertextoCNPJ(data, colunaCNPJ) {
    const response = await fetch(`${API_URL}/invertexto-cnpj`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data,
        coluna_cnpj: colunaCNPJ
      })
    });
    
    if (!response.ok) {
      throw new Error('Erro ao consultar Invertexto');
    }
    
    return response.json();
  }
};

const API_URL = 'http://localhost:8000/api/pipedrive';

export const pipedriveService = {
  async listarFunis() {
    const response = await fetch(`${API_URL}/funis`);
    
    if (!response.ok) {
      throw new Error('Erro ao listar funis');
    }
    
    return response.json();
  },

  async listarFiltros() {
    const response = await fetch(`${API_URL}/filtros`);
    
    if (!response.ok) {
      throw new Error('Erro ao listar filtros');
    }
    
    return response.json();
  },

  async carregarNegocios(funilId = null, filtroId = null) {
    const params = new URLSearchParams();
    if (funilId) params.append('funil_id', funilId);
    if (filtroId) params.append('filtro_id', filtroId);

    const response = await fetch(`${API_URL}/carregar-negocios?${params.toString()}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error('Erro ao carregar negócios');
    }
    
    return response.json();
  },

  async buscarPorNome(termo) {
    const params = new URLSearchParams({ termo });

    const response = await fetch(`${API_URL}/buscar-nome?${params.toString()}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error('Erro ao buscar negócios');
    }
    
    return response.json();
  }
};

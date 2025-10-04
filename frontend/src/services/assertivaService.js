const API_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/assertiva`;

export const assertivaService = {
  // Consulta dados por CPF
  async consultarCPF(cpf) {
    try {
      const response = await fetch(`${API_URL}/consultar-cpf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cpf })
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao consultar CPF: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao consultar CPF:', error);
      throw error;
    }
  },

  // Consulta múltiplos CPFs
  async consultarCPFs(cpfs) {
    try {
      const response = await fetch(`${API_URL}/consultar-cpfs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cpfs })
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao consultar CPFs: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao consultar CPFs:', error);
      throw error;
    }
  }
};

/**
 * Utilitários de formatação de dados
 * Baseado no arquivo formatadores.py do sistema desktop
 */

/**
 * Formata um CPF no padrão xxx.xxx.xxx-xx
 */
export function formatCPF(cpf) {
  if (!cpf || cpf === 'null' || cpf === 'undefined') return '';
  
  // Remove caracteres não numéricos
  let digits = cpf.toString().replace(/\D/g, '');
  
  // Completa com zeros à esquerda se necessário
  if (digits.length < 11) {
    digits = digits.padStart(11, '0');
  } else if (digits.length > 11) {
    digits = digits.slice(-11);
  }
  
  if (digits.length !== 11) return cpf.toString();
  
  // Formata no padrão xxx.xxx.xxx-xx
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

/**
 * Formata um CNPJ no padrão xx.xxx.xxx/xxxx-xx
 */
export function formatCNPJ(cnpj) {
  if (!cnpj || cnpj === 'null' || cnpj === 'undefined') return '';
  
  // Remove caracteres não numéricos
  let digits = cnpj.toString().replace(/\D/g, '');
  
  // Completa com zeros à esquerda se necessário
  if (digits.length < 14) {
    digits = digits.padStart(14, '0');
  } else if (digits.length > 14) {
    digits = digits.slice(-14);
  }
  
  if (digits.length !== 14) return cnpj.toString();
  
  // Formata no padrão xx.xxx.xxx/xxxx-xx
  return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`;
}

/**
 * Formata um telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
 */
export function formatPhone(phone) {
  if (!phone || phone === 'null' || phone === 'undefined') return '';
  
  const phoneStr = phone.toString();
  
  // Verifica se há múltiplos telefones
  if (phoneStr.includes(',') || phoneStr.includes(';')) {
    const phones = phoneStr.split(/[,;]/).map(p => formatPhoneIndividual(p.trim()));
    return phones.join(', ');
  }
  
  return formatPhoneIndividual(phoneStr);
}

function formatPhoneIndividual(phone) {
  // Remove caracteres não numéricos
  const digits = phone.replace(/\D/g, '');
  
  if (digits.length < 3) return phone;
  
  // Formato: DDD-NÚMERO
  return `${digits.slice(0, 2)}-${digits.slice(2)}`;
}

/**
 * Normaliza um email para minúsculas
 */
export function formatEmail(email) {
  if (!email || email === 'null' || email === 'undefined') return '';
  
  const emailStr = email.toString();
  
  // Verifica se há múltiplos emails
  if (emailStr.includes(',') || emailStr.includes(';')) {
    const emails = emailStr.split(/[,;]/).map(e => e.trim().toLowerCase());
    return emails.join(', ');
  }
  
  return emailStr.trim().toLowerCase();
}

/**
 * Formata um CEP no padrão xxxxx-xxx
 */
export function formatCEP(cep) {
  if (!cep || cep === 'null' || cep === 'undefined') return '';
  
  // Remove caracteres não numéricos
  const digits = cep.toString().replace(/\D/g, '');
  
  if (digits.length !== 8) return cep.toString();
  
  // Formata no padrão xxxxx-xxx
  return `${digits.slice(0, 5)}-${digits.slice(5)}`;
}

/**
 * Formata uma data no padrão dd/mm/aaaa
 */
export function formatDate(date) {
  if (!date || date === 'null' || date === 'undefined') return '';
  
  try {
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return date.toString();
    
    const day = dateObj.getDate().toString().padStart(2, '0');
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const year = dateObj.getFullYear();
    
    return `${day}/${month}/${year}`;
  } catch (error) {
    return date.toString();
  }
}

/**
 * Formata gênero (M/F → Masculino/Feminino)
 */
export function formatGender(gender) {
  if (!gender || gender === 'null' || gender === 'undefined') return '';
  
  const val = gender.toString().trim().toUpperCase();
  
  if (['F', 'FEM', 'FEMININO'].includes(val)) return 'Feminino';
  if (['M', 'MASC', 'MASCULINO'].includes(val)) return 'Masculino';
  
  return gender.toString();
}

/**
 * Padroniza razão social
 */
export function formatOrganization(name) {
  if (!name || name === 'null' || name === 'undefined') return '';
  
  let text = name.toString().trim().toUpperCase();
  
  // Remove marcadores especiais
  if (['{Ñ CLASS}', 'Ñ CLASS', 'NULL', 'NOLL'].includes(text)) return '';
  
  // Remove pontos finais
  text = text.replace(/\.$/, '');
  
  // Remove pontos em geral
  text = text.replace(/\./g, '');
  
  // Remove frases de recuperação judicial
  text = text.replace(/\s*-?\s*EM RECUPERACAO JUDICIAL\b/g, '');
  
  // Converter LIMITADA → LTDA
  text = text.replace(/\bLIMITADA\b/g, 'LTDA');
  
  // Remover EPP
  text = text.replace(/\s+EPP\b/g, '');
  
  // Corrigir EIRELLI → EIRELI
  text = text.replace(/\bEIRELLI\b/g, 'EIRELI');
  
  // Padronizar SA para S. A
  text = text.replace(/\bS\s*\/\s*A\b/g, 'S. A');
  text = text.replace(/\bS\s*A\b/g, 'S. A');
  
  // Normalizar espaços múltiplos
  text = text.replace(/\s+/g, ' ').trim();
  
  return text;
}

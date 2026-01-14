import re

item = _input.first()
email_dados = item.json
anexos_binarios = item.get('binary') or {} 

corpo_email = email_dados.get('text', '')
anexos = email_dados.get('attachments', [])
padrao_url = r'https?://[^\s]+'
links = re.findall(padrao_url, corpo_email)
links_limpos = [l.strip('().,') for l in links]
remetente = email_dados['from']['value'][0]['address']

suspeitas = ['.xyz', '.top', '.pw', '.bit', '.tk', '.zip', '.click']
palavras_urgencia = ['urgente', 'suspensa', 'bloqueio', 'recadastro', 'vencimento', 'multa']
extensoes_perigosas = ['.exe', '.bat', '.scr', '.vbs', '.js', '.zip', '.rar', '.iso', '.click']


corpo_email_low = corpo_email.lower()
tem_urgencia = any(palavra in corpo_email_low for palavra in palavras_urgencia)

score = 0
if any(any(dominio_suspeito in l for dominio_suspeito in suspeitas) for l in links_limpos):
    score += 40
  
if tem_urgencia:  
    score += 20


anexos_analisados = []
score_anexo = 0
alerta_tamanho = False


for key, anexo in anexos_binarios.items():
    nome = anexo.get('fileName', '').lower()
    tamanho_raw = str(anexo.get('fileSize', '0'))
    tamanho_limpo = ''.join(filter(str.isdigit, tamanho_raw))
    tamanho_bytes = int(tamanho_limpo) if tamanho_limpo else 0
    tamanho_mb = tamanho_bytes / (1024 * 1024) 

    anexo_perigoso = any(nome.endswith(ext) for ext in extensoes_perigosas)
    
    if tamanho_mb > 500:
        alerta_tamanho = True
        score_anexo += 40

    if anexo_perigoso:
        score_anexo += 60

    anexos_analisados.append({
        "nome": nome,
        "tamanho_mb": round(tamanho_mb, 2),
        "suspeito": anexo_perigoso
    })


score_final = min(score + score_anexo, 100)

if score_final >= 70:
    nivel = "ALTO"
elif score_final >= 30:
    nivel = "MÉDIO"
else:
    nivel = "BAIXO"


return {
    "analise_phishing": {
        "score_total": score_final,
        "nivel_risco": nivel,
        "remetente": remetente,
        "links_detectados": links_limpos,
        "assunto": email_dados.get('subject', 'Sem Assunto'),
        "id_mensagem": email_dados.get('id'),
        "anexos": anexos_analisados,
        "alerta_arquivo_grande": alerta_tamanho,
        "possui_anexos": len(anexos_analisados) > 0
    }
}
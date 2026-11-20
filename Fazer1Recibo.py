from docx import Document
from docx.shared import Pt
import os
from datetime import datetime
from num2words import num2words
import extrair_dados
import re
# Variáveis de controle
fazerCliente1 = True
ultimo_recibo = ""
recibo = 0

# =====================================================
# FUNÇÃO PARA CONVERTER VALOR NUMÉRICO PARA EXTENSO
# =====================================================
def valor_por_extenso(valor_str):
    """
    Remove formatações (R$, separadores) da string de valor,
    converte para float e retorna o valor por extenso.
    """
    # Limpa a string removendo R$, espaços, pontos e ajusta a vírgula para ponto decimal
    valor_str = valor_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
    valor = float(valor_str)
    
    # Separa a parte inteira (reais) e os centavos
    reais = int(valor)
    centavos = int(round((valor - reais) * 100))
    
    # Converte cada parte para texto usando num2words
    extenso_reais = num2words(reais, lang='pt_BR')
    if centavos:
        extenso_centavos = num2words(centavos, lang='pt_BR')
        return f"{extenso_reais} reais e {extenso_centavos} centavos"
    else:
        return f"{extenso_reais} reais"
    
# =====================================================
# FUNÇÃO PARA SUBSTITUIR PLACEHOLDER EM PARÁGRAFOS DO DOCX
# =====================================================
def replace_placeholder_in_paragraph(paragraph, placeholder, replacement):
    """
    Busca o placeholder no parágrafo – mesmo se estiver fragmentado em vários runs –
    e o substitui pelo replacement, preservando o restante do texto.
    """
    while True:
        full_text = ""
        run_positions = []  # Lista de tuplas (run, posição_inicial, posição_final)
        
        # Concatena o texto de todos os runs e registra as posições
        for run in paragraph.runs:
            start = len(full_text)
            full_text += run.text
            end = len(full_text)
            run_positions.append((run, start, end))
        
        # Procura a ocorrência do placeholder
        pos = full_text.find(placeholder)
        if pos == -1:
            break  # Não há mais ocorrência do placeholder
        
        placeholder_end = pos + len(placeholder)
        
        # Itera pelos runs que contenham parte do placeholder
        for run, start, end in run_positions:
            # Se o run não contem parte do placeholder, ignora
            if end <= pos or start >= placeholder_end:
                continue
            
            # Calcula as posições relativas do placeholder dentro do run
            run_placeholder_start = max(0, pos - start)
            run_placeholder_end = min(len(run.text), placeholder_end - start)
            
            if start <= pos < end:
                # Se o run contém o início do placeholder, insere o replacement
                new_text = run.text[:run_placeholder_start] + str(replacement) + run.text[run_placeholder_end:]
                run.text = new_text
            else:
                # Se o run está completamente dentro do placeholder, remove esse trecho
                new_text = run.text[:max(0, pos - start)] + run.text[run_placeholder_end:]
                run.text = new_text

# =====================================================
# FUNÇÃO PARA GERAR O RECIBO (DOCX) E REGISTRAR A ROTA
# =====================================================
def fazerRecibo(clientes, fazerCliente1, recibo, ultimo_recibo, ultimo_nome):
    """
    Gera um recibo (documento DOCX) substituindo os placeholders pelo conteúdo de 'clientes'.
    Cria os diretórios necessários (data, período, recibos) e salva o documento.
    Atualiza e retorna o caminho do último recibo gerado.
    """
    # Incrementa o contador de recibos para usar como nome
    dir_atual = os.path.dirname(os.path.abspath(__file__))


    recibo += 1
    nome_cliente_limpo = clientes['nome'].replace(":", "").replace("/", "-").replace("\\", "").strip()
    nome_cliente_limpo1 = re.sub(r"\s*\(.*\)$", "", nome_cliente_limpo)
    # Seleciona o template com base na variável fazerCliente1
    if fazerCliente1:
        numero = 1

        caminho_recibo = os.path.join(dir_atual, "3 - templetes", "Recibo.docx")
        doc = Document(caminho_recibo)
        ultimo_nome = nome_cliente_limpo
        nome_arquivo = f"Recibo de {ultimo_nome}"
    else:
        numero = 2
        doc = Document(ultimo_recibo)
        nome_arquivo = f'Recibo de {ultimo_nome} e {nome_cliente_limpo}'
    
    # Dicionário com os placeholders e seus respectivos valoress
    substituicoes = {
        f"[cod{numero}]": clientes['codigo'],
        f"[cliente{numero}]": nome_cliente_limpo1,
        f"[valor{numero}]": clientes['financeiro'][0],
        f"[digitado{numero}]": valor_por_extenso(clientes['financeiro'][0]),
        f"[dados_do_serviço{numero}]": clientes['dadosDoServiço'],
        f"[formaPgto{numero}]": clientes['financeiro'][1],
        f"[data{numero}]": clientes['hora_data'][1]
    }
    
    # Para cada parágrafo do documento, substitui os placeholders
    for paragrafo in doc.paragraphs:
        for placeholder, replacement in substituicoes.items():
            replace_placeholder_in_paragraph(paragrafo, placeholder, replacement)
   
    # Criação do diretório baseado na data da OS (substituindo '/' por '-')
    dataSave = clientes['hora_data'][1].replace('/', '-')
    pasta_data = os.path.join("1 - ordens de serviço", f"{dataSave}")
    
    
    os.makedirs(pasta_data, exist_ok=True)
    
    # Define o diretório conforme o período (MANHÃ ou TARDE) com base na hora do serviço
    horario = datetime.strptime(clientes['hora_data'][0], "%H:%M").time()
    if horario.hour < 12:
        caminho_para_OS = os.path.join(pasta_data, "MANHÃ")
    else:
        caminho_para_OS = os.path.join(pasta_data, "TARDE")
    os.makedirs(caminho_para_OS, exist_ok=True)
    
    # Cria uma pasta 'recibos' dentro do diretório da OS e salva o arquivo
    pasta_recibos = os.path.join(caminho_para_OS, 'recibos')
    os.makedirs(pasta_recibos, exist_ok=True)
    
    if fazerCliente1:
        novo_caminho = os.path.join(pasta_recibos, f"{nome_arquivo}.docx")
        doc.save(novo_caminho)
        ultimo_recibo = novo_caminho
    else:
        # Aqui, depois de substituir os placeholders para o cliente2,
        # é preciso salvar o documento com as alterações para a parte de baixo.
        # e excluir o ultimo arquivo.
        arquivo_a_excluir = os.path.join(pasta_recibos, f"Recibo de {ultimo_nome}.docx")
        if os.path.exists(arquivo_a_excluir):
            os.remove(arquivo_a_excluir)

        novo_caminho = os.path.join(pasta_recibos, f"{nome_arquivo}.docx")
        doc.save(novo_caminho)
        ultimo_recibo = novo_caminho

    return ultimo_recibo, ultimo_nome

def extrair_dados_recibo(driver, código, data):
    cliente = {}
    extrair_dados.buscar_cliente(driver, código)
    
    cliente['codigo'] = código
    cliente['nome'] = extrair_dados.extrair_nome(driver)
    extrair_dados.atualizar_progresso(f'{cliente['nome']} buscando nome', 1, 6)
    extrair_dados.atualizar_progresso(f'{cliente['nome']} Buscando hora e data', 2, 6)
    cliente['hora_data'] = extrair_dados.extrair_data_hora_servico(driver, data)
    extrair_dados.atualizar_progresso(f'{cliente['nome']} buscando dados do serviço', 3, 6)
    cliente['dadosDoServiço'] = extrair_dados.extrair_dados_servico(driver)
    extrair_dados.atualizar_progresso(f'{cliente['nome']} buscando financeiro', 4, 6)
    cliente['financeiro'] = extrair_dados.extrair_financeiro(driver)
    return cliente

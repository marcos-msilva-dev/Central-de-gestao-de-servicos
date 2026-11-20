import os
import re
import sys
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from docx import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime
from selenium.webdriver.chrome.service import Service

OS_FEITAS = []
PROGRESS_WIDGET = None
INPUT_ENTRY = None
INPUT_BUTTON = None

def selecionar_data(geometry_str="400x300+100+100"):
    data_selecionada = None  # Variável que armazenará a data escolhida

    def confirmar():
        nonlocal data_selecionada
        data_selecionada = cal.selection_get()
        root.destroy()

    root = tk.Tk()
    root.title("Selecione a data")

    # Define a geometria da janela (largura x altura + posição X + posição Y)
    root.geometry(geometry_str)

    # Cria o widget de calendário com a data atual
    cal = Calendar(root, selectmode='day', year=datetime.now().year,
                   month=datetime.now().month, day=datetime.now().day)
    cal.pack(pady=20)

    btn_confirmar = tk.Button(root, text="Confirmar", command=confirmar)
    btn_confirmar.pack(pady=10)

    root.mainloop()

    # Se uma data foi selecionada, retorna no formato "dd/mm/aa"
    if data_selecionada:
        return data_selecionada.strftime("%d/%m/%Y")
    else:
        return None


def imprimir_mensagem(mensagem):
    """
    Imprime uma mensagem no terminal da interface.
    Se PROGRESS_WIDGET estiver definido, insere a mensagem nele;
    caso contrário, imprime no terminal convencional.
    """
    global PROGRESS_WIDGET
    if PROGRESS_WIDGET is not None:
        PROGRESS_WIDGET.insert("end", mensagem + "\n")
        PROGRESS_WIDGET.see("end")
    else:
        print(mensagem)


def atualizar_progresso(mensagem, passo_atual, total_passos, tamanho_barra=50):
    """
    Exibe uma mensagem e uma barra de progresso.
    Se PROGRESS_WIDGET estiver definido, atualiza a interface (incluindo as etapas já concluídas);
    caso contrário, imprime no terminal.
    """
    global OS_FEITAS, PROGRESS_WIDGET
    proporcao = passo_atual / total_passos
    preenchido = int(tamanho_barra * proporcao)
    barra = '█' * preenchido + ' ' * (tamanho_barra - preenchido)
    porcentagem = proporcao * 100

    if PROGRESS_WIDGET is not None:
        # Limpa o widget (simulando o "cls")
        PROGRESS_WIDGET.delete("1.0", "end")
        # Insere as etapas já concluídas (armazenadas em OS_FEITAS)
        if OS_FEITAS:
            for item in OS_FEITAS:
                PROGRESS_WIDGET.insert("end", f'{item[0]}\n[{item[1]}] {item[2]:.1f}% concluído\n\n')
        # Se a etapa atual estiver completa, armazena-a em OS_FEITAS
        if porcentagem == 100:
            OS_FEITAS.append([mensagem, barra, porcentagem])
        # Insere a mensagem atual
        PROGRESS_WIDGET.insert("end", f'{mensagem}\n[{barra}] {porcentagem:.1f}% concluído\n')
        PROGRESS_WIDGET.see("end")
    else:
        os.system("cls")
        if OS_FEITAS:
            for item in OS_FEITAS:
                print()
                sys.stdout.write(f'\r{item[0]}\n[{item[1]}] {item[2]:.1f}% concluído\n')
                sys.stdout.flush()
        if porcentagem == 100:
            OS_FEITAS.append([mensagem, barra, porcentagem])
        print()
        sys.stdout.write(f'\r{mensagem}\n[{barra}] {porcentagem:.1f}% concluído\n')
        sys.stdout.flush()


def configurar_driver():
    """
    Configura e retorna o driver do Chrome em modo headless, suprimindo logs desnecessários.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")  # Minimiza logs do Chrome

    # Cria um objeto Service com log_path redirecionado para o dispositivo nulo
    service = Service(log_path=os.devnull)
    # 
    # Passa o objeto service para o webdriver.Chrome
    return webdriver.Chrome(service=service, options=chrome_options)


def login_benu(driver, username="MARCOS", password="MARCOS10"):
    """
    Realiza o login no sistema Benu e navega até a página de busca de clientes.
    As mensagens são exibidas no terminal da interface.
    """
    driver.get('https://benuerp.com.br/')
    driver.maximize_window()

    def colocar_itens():
        try:
            user_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='usernameBenu']"))
            )
            user_field.click()
            user_field.clear()
            user_field.send_keys(username)
            senha_field = driver.find_element(By.XPATH, "//input[@id='SenhaBenu']")
            senha_field.click()
            senha_field.clear()
            senha_field.send_keys(password)
            botao_logar = driver.find_element(By.XPATH, "//input[@id='logarBenu']")
            botao_logar.click()
        except Exception as e:
            imprimir_mensagem("Erro ao preencher os campos: " + str(e))
    # Loop para tentar login
    while True:
        colocar_itens()
        elementos = driver.find_elements(By.XPATH, "//input[@id='logarBenu']")
        if elementos:
            imprimir_mensagem("Falha ao logar, tentando de novo...")
            sleep(1)
        else:
            imprimir_mensagem("Login bem-sucedido!")
            break


def buscar_cliente(driver, codigo):
    """
    Busca o cliente utilizando o código fornecido e, se houver múltiplos resultados,
    exibe a lista na área de progresso e solicita que o usuário informe o número do cliente
    usando o campo de input fixo da interface. Caso nenhum cliente seja encontrado,
    solicita ao usuário um novo código para tentar novamente.
    """
    global INPUT_ENTRY, INPUT_BUTTON  # Declaramos logo no início

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import tkinter as tk

    # Acessa a URL de busca
    driver.get('https://benuerp.com.br/new/buscarCliente.benu?nmUsuario=MARCOS&ref=579&cnpj=1')
    
    # Preenche o campo de busca
    nome_filtro = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='nomeFiltro']"))
    )
    nome_filtro.click()
    nome_filtro.clear()
    nome_filtro.send_keys(codigo)

    # Clica no botão de busca
    botao_buscar = driver.find_element(By.XPATH, "//button[@id='buscarCliente']")
    botao_buscar.click()

    # Tenta aguardar o carregamento do primeiro cliente
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@id='greeting:0:linkCliente']"))
        )
    except Exception as e:
        # Se o tempo de espera expirar, nenhum cliente foi encontrado
        from extrair_dados import imprimir_mensagem, atualizar_progresso
        imprimir_mensagem("Nenhum cliente encontrado para o código: " + codigo + 
                              "\nDigite um novo código no campo de input e clique em Enviar.")
        root = tk._default_root  # Instância principal do Tkinter
        new_code_var = tk.StringVar(root)

        def confirmar_codigo():
            new_code = INPUT_ENTRY.get().strip()
            if new_code == "":
                imprimir_mensagem("Entrada inválida. Digite um código válido.")
                return
            INPUT_ENTRY.delete(0, tk.END)
            new_code_var.set(new_code)

        default_input_command = INPUT_BUTTON.cget("command")
        INPUT_BUTTON.config(command=confirmar_codigo)
        root.wait_variable(new_code_var)
        new_code = new_code_var.get()
        INPUT_BUTTON.config(command=default_input_command)
        # Tenta novamente com o novo código informado pelo usuário
        return buscar_cliente(driver, new_code)

    # Obtém a lista de clientes encontrados
    clientes_list = driver.find_elements(By.XPATH, "//tbody[@id='greeting_data']/tr")
    if len(clientes_list) > 1:
        # Constrói uma string com a lista de clientes encontrados
        lista_texto = ""
        for idx, cliente in enumerate(clientes_list, start=1):
            nome_cliente = cliente.find_element(By.XPATH, "./td[2]").text.strip()
            lista_texto += f"{idx} - Cliente: {nome_cliente}\n"
        from extrair_dados import imprimir_mensagem, atualizar_progresso
        imprimir_mensagem("Clientes encontrados:\n" + lista_texto +
                              "\nDigite o número do cliente no campo de input e clique em Enviar.")
        
        root = tk._default_root
        selecao_var = tk.IntVar(root)

        def confirmar_selecao():
            try:
                escolha = int(INPUT_ENTRY.get().strip())
            except ValueError:
                imprimir_mensagem("Entrada inválida. Digite um número.")
                return
            if escolha < 1 or escolha > len(clientes_list):
                imprimir_mensagem("Número fora do intervalo. Tente novamente.")
                return
            INPUT_ENTRY.delete(0, tk.END)
            selecao_var.set(escolha)

        default_input_command = INPUT_BUTTON.cget("command")
        INPUT_BUTTON.config(command=confirmar_selecao)
        root.wait_variable(selecao_var)
        escolha = selecao_var.get()
        INPUT_BUTTON.config(command=default_input_command)
        link_cliente = driver.find_element(By.XPATH, f"//a[@id='greeting:{escolha-1}:linkCliente']")
        link_cliente.click()
    else:
        # Se houver apenas um resultado, clica diretamente
        primeiro_cliente = driver.find_element(By.XPATH, "//a[@id='greeting:0:linkCliente']")
        primeiro_cliente.click()


def extrair_nome(driver):
    """
    Extrai e retorna o nome do cliente.
    """
    nome = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='NomeCliente']"))
    ).get_attribute('value')
    return nome


def extrair_CPF(driver, cliente):
    try:
        CNPJ = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@id='CNPJ']"))).get_attribute('value')
        imprimir_mensagem(f'{cliente['nome']} CNPJ armazenado!')
    except:
        CNPJ = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@id='CPF']"))).get_attribute('value')
        imprimir_mensagem(f'{cliente['nome']} CPF armazenado!')
    return CNPJ


def extrair_telefones(driver):
    """
    Extrai e retorna uma lista de telefones do cliente.
    """
    linhas = driver.find_elements(By.XPATH, "//tbody[@id='telefone_data']/tr")
    telefones = []
    for linha in linhas:
        nome_tel = linha.find_element(By.XPATH, "./td[1]").text.strip()
        telefone = linha.find_element(By.XPATH, "./td[2]").text.strip()
        telefones.append((nome_tel, telefone))
    return telefones


def get_endereco_info(endereco_linha):
    """
    Extrai informações de uma linha de endereço e retorna um dicionário com os dados.
    """
    endereco = {}
    endereco["Nome"] = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Nome:')]/following-sibling::td"
    ).text.strip() or ""
    cidade_uf = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Cidade - UF:')]/following-sibling::td"
    ).text.strip()
    endereco["Cidade"] = cidade_uf.split(" - ")[0] if cidade_uf else "não tem"
    endereco["Endereço"] = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Endereço:')]/following-sibling::td"
    ).text.strip() or "não tem"
    numero = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Nº')]/following-sibling::td"
    ).text.strip()
    endereco["Nº"] = numero if numero != "0" else "não tem"
    endereco["Bairro"] = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Bairro:')]/following-sibling::td"
    ).text.strip() or "não tem"
    endereco["Complemento"] = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Complemento:')]/following-sibling::td"
    ).text.strip() or "não tem"
    endereco["Referência"] = endereco_linha.find_element(
        By.XPATH, ".//td[contains(text(), 'Referência')]/following-sibling::td"
    ).text.strip() or "não tem"
    return endereco


def extrair_enderecos(driver):
    """
    Navega até a aba de endereços e extrai todos os endereços em um dicionário.
    """
    driver.find_element(By.XPATH, "//a[@href='#tabEnderecos']").click()

    def coletar_enderecos():
        enderecos = {}
        linhas = driver.find_elements(
            By.XPATH, "//tbody[@id='endereco_data']/tr")
        for i, linha in enumerate(linhas, start=1):
            enderecos[f"Endereco{i}"] = get_endereco_info(linha)
        return enderecos

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[@id='endereco:0:link']"))
    )
    return coletar_enderecos()


def extrair_observacoes(driver):
    """
    Extrai e retorna as observações do cliente.
    """
    driver.find_element(By.XPATH, "//a[@href='#observacoes']").click()
    obs = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//textarea[@id='ObsOS']"))
    ).text.strip()
    return obs


def extrair_data_hora_servico(driver, data):
    """
    Define os filtros de data e extrai a hora e a data do serviço.
    Retorna uma tupla (hora, data_servico).
    """
    driver.find_element(By.XPATH, "//a[@href='#servicosContratos']").click()
    campo_inicio = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='inicioServ_input']"))
    )
    campo_inicio.clear()
    campo_inicio.send_keys(data)

    campo_fim = driver.find_element(By.XPATH, "//input[@id='fimServ_input']")
    campo_fim.clear()
    campo_fim.send_keys(data)

    driver.find_element(By.XPATH, "//a[@id='buscarServicos']").click()
    sleep(1)

    # Seleciona o primeiro serviço encontrado
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@id='servicos:0:servico']"))
    ).click()

    hora = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='horaInicioServico']"))
    ).get_attribute('value')
    data_serv = driver.find_element(
        By.ID, "dataServico_input").get_attribute('value')
    return hora, data_serv


def extrair_justificativa(driver):
    """
    Extrai e retorna a justificativa do cliente.
    """
    justificativa = driver.find_element(
        By.XPATH, "//textarea[@id='txJustificativaCliente']"
    ).get_attribute('value')
    return justificativa


def validar_endereco(driver, enderecos):
    """
    Compara o endereço de serviço exibido com os endereços coletados e retorna o endereço correto.
    """
    endereco_correto = driver.find_element(
        By.XPATH, "//span[@id='EnderecoServico_label']"
    ).text
    if len(enderecos) > 1:
        for endereco in enderecos.values():
            if endereco['Endereço'] in endereco_correto:
                return endereco
    # Se não houver correspondência ou houver só um endereço, retorna o primeiro
    return list(enderecos.values())[0]


def extrair_dados_servico(driver):
    """
    Extrai os dados dos serviços contratados e retorna uma string formatada.
    """
    driver.find_element(
        By.XPATH, "//a[@href='#especificacoesServico']").click()
    WebDriverWait(driver, 5).until(
        # espera até garegar um botão nada haver
        EC.presence_of_element_located(
            (By.XPATH, "//a[@id='tipoServ:addTipoServico']"))
    )

    # Extrai os tipos de serviço
    linhas_tipo = driver.find_elements(
        By.XPATH, "//tbody[@id='tipoServ_data']/tr")
    tipos = [
        re.sub(r'^\d+\s*', '',
               linha.find_element(By.XPATH, "./td[1]").text.strip())
        for linha in linhas_tipo
    ]

    # Extrai os itens (pragas) de cada serviço
    dados_servico = []
    for idx in range(len(tipos)):
        pragas_elements = driver.find_elements(
            By.XPATH, f"//tbody[@id='tipoServ:{idx}:objeto_data']/tr"
        )
        pragas = []
        for praga_el in pragas_elements:
            praga_text = praga_el.find_element(By.XPATH, "td[1]").text.strip()
            praga_text = praga_text.split("\n")[0].strip()
            praga_text = re.sub(r'^\d+\s*', '', praga_text)
            pragas.append(praga_text)
        dados_servico.append((tipos[idx], pragas))

    # Monta a descrição do serviço
    servico_contratado = ''
    for servico, pragas in dados_servico:
        pragas_formatadas = ", ".join(pragas)
        servico_contratado += f'{servico}: {pragas_formatadas}. '
    return servico_contratado


def extrair_tempos_garantia(driver):
    """
    Percorre os serviços na tabela e extrai os tempos de garantia encontrados.
    Se nenhuma garantia for encontrada, retorna None.
    Se todas as garantias forem iguais, retorna esse único valor.
    Se forem diferentes, exibe as opções para o usuário via interface e retorna a garantia escolhida.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import tkinter as tk

    garantias_coletadas = []

    # Seleciona todas as linhas de serviços
    servicos = driver.find_elements(By.XPATH, "//tbody[@id='tipoServ_data']/tr")

    for servico in servicos:
        # Tenta extrair o nome do serviço (não utilizado para a seleção final)
        try:
            texto_servico = servico.find_element(By.XPATH, ".//td").text.strip()
            nome_servico = texto_servico.splitlines()[0]
        except Exception:
            nome_servico = "Serviço não identificado"

        # Coleta as garantias de cada serviço
        garantia_elements = servico.find_elements(By.XPATH, ".//tbody[contains(@id, 'tipoG_data')]/tr/td")
        for elem in garantia_elements:
            garantia_texto = elem.text.strip()
            if garantia_texto:
                garantias_coletadas.append(garantia_texto)

    # Remove duplicatas mantendo a ordem
    garantias_unicas = list(dict.fromkeys(garantias_coletadas))

    # Se nenhuma garantia for encontrada, retorna None
    if not garantias_unicas:
        return None

    # Se houver apenas uma garantia, retorna-a
    if len(garantias_unicas) == 1:
        return garantias_unicas[0]

    # Se houver mais de uma garantia, exibe as opções na interface
    # Constrói uma mensagem com a lista de garantias
    mensagem_lista = "Foram encontradas várias garantias:\n"
    for idx, garantia in enumerate(garantias_unicas, start=1):
        mensagem_lista += f"{idx} - {garantia}\n"
    mensagem_lista += "\nDigite o número da garantia que deseja usar no campo de input e clique em Enviar."

    # Exibe a mensagem na área de progresso (a função atualizar_progresso usa o widget da interface, se definido)
    imprimir_mensagem(mensagem_lista, 0, 1)

    # Utiliza os widgets de input fixo definidos na interface
    global INPUT_ENTRY, INPUT_BUTTON
    # Obtém a instância principal do Tkinter
    root = tk._default_root
    # Cria uma variável para aguardar a seleção
    selecao_var = tk.IntVar(root)

    def confirmar_garantia():
        try:
            escolha = int(INPUT_ENTRY.get().strip())
        except ValueError:
            imprimir_mensagem("Entrada inválida. Digite um número.", 0, 1)
            return
        if escolha < 1 or escolha > len(garantias_unicas):
            imprimir_mensagem("Opção inválida. Tente novamente.", 0, 1)
            return
        # Limpa o campo de input e define a variável de seleção
        INPUT_ENTRY.delete(0, tk.END)
        selecao_var.set(escolha)

    # Guarda o comando original do botão para restaurá-lo posteriormente
    default_input_command = INPUT_BUTTON.cget("command")
    # Redefine o comando do botão para confirmar a seleção da garantia
    INPUT_BUTTON.config(command=confirmar_garantia)

    # Bloqueia a execução até que o usuário informe uma escolha válida
    root.wait_variable(selecao_var)
    escolha = selecao_var.get()

    # Restaura o comando original do botão
    INPUT_BUTTON.config(command=default_input_command)

    return garantias_unicas[escolha - 1]


def calcular_data_termino(data_inicial, garantia):
    """
    Recebe uma data inicial (string no formato "dd/mm/yyyy") e uma garantia (string)
    e retorna a data de término calculada no formato "dd/mm/yyyy".
    """
    # Converte a data inicial para datetime
    try:
        data_inicial = datetime.strptime(data_inicial, "%d/%m/%Y")
    except ValueError:
        return "erro ao calcular o termino"

    # Dicionário para mapear períodos de garantia
    garantias_validas = {
        "1 ano": relativedelta(years=1),
        "2 anos": relativedelta(years=2),
        "1 mês": relativedelta(months=1),
        "2 meses": relativedelta(months=2),
        "3 meses": relativedelta(months=3),
        "4 meses": relativedelta(months=4),
        "5 meses": relativedelta(months=5),
        "6 meses": relativedelta(months=6),
    }

    # Verifica se a garantia fornecida é válida
    if garantia not in garantias_validas:
        return "erro ao calcular o termino"

    # Calcula a data de término
    data_termino = data_inicial + garantias_validas[garantia]

    return data_termino.strftime("%d/%m/%Y")


def extrair_financeiro(driver):
    """
    Extrai os dados financeiros do serviço e retorna uma tupla (preco, forma_pgto, recibo).
    """
    try:
        driver.find_element(By.XPATH, "//a[@href='#telaFinanceira']").click()
        preco = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "Preco"))
        ).get_attribute("value")

        preco_valor = float(preco.replace(
            '.', '').replace(',', '.')) if preco else 0

        if preco_valor > 0:
            recibo = True
            forma_pgto = driver.find_element(
                By.XPATH, "//span[@id='contaCorrenteTelaInfoPagamento_label']"
            ).text.strip()
            novo_texto = re.sub(r'^\d+\s*', '', forma_pgto)
            forma_pgto = novo_texto
        else:
            recibo = False
            forma_pgto = "não tem valor"
        return preco, forma_pgto, recibo
    except Exception:
        print('Não vai fazer o recibo!')
        return None, None, False


def gerar_ordem_servico_e_rota(clientes, data):
    """
    Gera o documento de ordem de serviço utilizando um template do Word,
    substitui os placeholders e salva o arquivo na pasta correspondente.
    Também registra a rota em um arquivo de texto.
    """
    # Diretório do arquivo atual (por exemplo, o arquivo principal do seu app)
    dir_atual = os.getcwd()

    # Monta o caminho relativo para o arquivo dentro da pasta "templetes"
    caminho_parteFrente = os.path.join(dir_atual, "3 - templetes", "apenas frente.docx")
    doc = Document(caminho_parteFrente)

    # Preparar os valores de substituição
    substituicoes = {
        "[Empresa]": clientes['nome']
    }

    # Seleciona o telefone a ser utilizado
    if len(clientes["telefones"]) > 1:
        import tkinter as tk
        # Constrói uma string com a lista de telefones disponíveis
        lista_texto = f'Escolha dentre os {len(clientes["telefones"])} telefones disponíveis:\n'
        for idx, (nome_tel, tel) in enumerate(clientes['telefones'], start=1):
            lista_texto += f'{idx} - {nome_tel} - {tel}\n'
        # Exibe a lista na área de progresso
        imprimir_mensagem(lista_texto + "\nDigite a opção desejada no campo de input e clique em Enviar.")
        
        # Usa o campo de input fixo da interface para obter a escolha do usuário
        # Assume que INPUT_ENTRY e INPUT_BUTTON são variáveis globais definidas no módulo de interface
        global INPUT_ENTRY, INPUT_BUTTON
        root = tk._default_root  # Obtém a instância principal do Tkinter
        
        # Cria uma variável Tkinter para aguardar a seleção
        selecao_tel = tk.IntVar(root)
        
        # Define uma função que será chamada ao clicar no botão "Enviar"
        def confirmar_telefone():
            try:
                opcao = int(INPUT_ENTRY.get().strip())
            except ValueError:
                imprimir_mensagem("Entrada inválida. Digite um número.")
                return
            if opcao < 1 or opcao > len(clientes["telefones"]):
                imprimir_mensagem("Número fora do intervalo. Tente novamente.")
                return
            # Limpa o campo de input e define a variável de seleção
            INPUT_ENTRY.delete(0, tk.END)
            selecao_tel.set(opcao)
        
        # Guarda o comando original do botão para restaurá-lo posteriormente
        default_tel_command = INPUT_BUTTON.cget("command")
        # Redefine o comando do botão para confirmar a seleção
        INPUT_BUTTON.config(command=confirmar_telefone)
        
        # Aguarda de forma bloqueante até que o usuário informe uma escolha válida
        root.wait_variable(selecao_tel)
        opcao = selecao_tel.get()
        # Restaura o comando original do botão
        INPUT_BUTTON.config(command=default_tel_command)
        
        # Seleciona o telefone de acordo com a escolha do usuário
        nome_tel, tel = clientes["telefones"][opcao - 1]
        substituicoes["[Gerente]"] = f'{nome_tel} - {tel}'
    else:
        nome_tel, tel = clientes["telefones"][0]
        substituicoes["[Gerente]"] = f'{nome_tel} - {tel}'

    if clientes['justificativa do cliente'] == "":
        observações = clientes['obs']
    elif clientes['obs'] == "":
        observações = clientes['justificativa do cliente']
    else:
        observações = f"{clientes['justificativa do cliente']}\n\n{clientes['obs']}"

    endereco = clientes['endereço']
    endereco_str = f"{endereco['Cidade']} - {endereco.get('Nome', '') + ', ' if endereco.get('Nome') else ''}{endereco['Endereço']}, {endereco['Nº']} - {endereco['Bairro']}"
    substituicoes["[Endereço da Empresa]"] = endereco_str

    referencia = f"{endereco['Referência']}. complemento: {endereco['Complemento']}"
    substituicoes["[Assunto]"] = referencia

    substituicoes["[Data de Publicação]"] = clientes['hora_data'][1]
    substituicoes["[Status]"] = clientes['hora_data'][0]
    substituicoes["[Comentários]"] = clientes['dadosDoServiço']
    substituicoes["[obs]"] = observações

    # Realiza a substituição nos parágrafos e tabelas do documento
    for paragrafo in doc.paragraphs:
        for chave, valor in substituicoes.items():
            if chave in paragrafo.text:
                paragrafo.text = paragrafo.text.replace(chave, valor)
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for chave, valor in substituicoes.items():
                    if chave in celula.text:
                        celula.text = celula.text.replace(chave, valor)

    # Cria os diretórios para salvar o documento
    data_save = data.replace('/', '-')
    pasta_destino = os.path.join(dir_atual, "1 - ordens de serviço", data_save)
    os.makedirs(pasta_destino, exist_ok=True)

    nome_cliente_limpo = clientes['nome'].replace(":", "").replace("/", "-").replace("\\", "").strip()
    hora_serv = datetime.strptime(clientes['hora_data'][0], "%H:%M").time()
    periodo = "MANHÃ" if hora_serv.hour < 12 else "TARDE"
    caminho_para_OS = os.path.join(pasta_destino, periodo)
    os.makedirs(caminho_para_OS, exist_ok=True)

    novo_caminho = os.path.join(caminho_para_OS, f"{nome_cliente_limpo}.docx")
    doc.save(novo_caminho)

    # Registra a rota no arquivo
    caminho_rota = os.path.join(dir_atual, "3 - templetes", "rota.txt")
    with open(caminho_rota, 'a') as arquivo:
        arquivo.write(f"{clientes['nome']},{endereco['Bairro']},{clientes['hora_data'][0]}.\n")


def fazer_1_ordem(driver, data, codigo, total_dePasso):
    """
    Orquestra o processo completo:
      1. Busca e seleção do cliente;
      2. Extração dos dados (nome, telefones, endereços, observações, data/hora, justificativa, serviços, financeiro);
      3. Geração do documento de ordem de serviço.

    Retorna uma tupla com os dados do cliente, o status do recibo e uma mensagem em caso de ausência de recibo.
    """
    cliente = {}

    # Buscar e selecionar o cliente
    buscar_cliente(driver, codigo)
    cliente['codigo'] = codigo
    cliente['nome'] = extrair_nome(driver)
    atualizar_progresso(
        f'{cliente['nome']} Nome do cliente armazenado', 1, total_dePasso)

    cliente['telefones'] = extrair_telefones(driver)
    atualizar_progresso(
        f'{cliente['nome']} Telefones armazenados', 2, total_dePasso)

    enderecos = extrair_enderecos(driver)
    cliente['endereço'] = enderecos
    atualizar_progresso(
        f'{cliente['nome']} Endereços armazenados', 3, total_dePasso)

    cliente['obs'] = extrair_observacoes(driver)
    atualizar_progresso(
        f'{cliente['nome']} Observações armazenadas', 4, total_dePasso)

    cliente['hora_data'] = extrair_data_hora_servico(driver, data)
    atualizar_progresso(
        f'{cliente['nome']} Data e hora armazenadas', 5, total_dePasso)

    cliente['justificativa do cliente'] = extrair_justificativa(driver)
    atualizar_progresso(
        f'{cliente['nome']} Justificativa armazenada', 6, total_dePasso)

    # Valida e seleciona o endereço correto
    cliente['endereço'] = validar_endereco(driver, cliente['endereço'])
    atualizar_progresso(
        f'{cliente['nome']} Endereço validado', 7, total_dePasso)

    cliente['dadosDoServiço'] = extrair_dados_servico(driver)
    atualizar_progresso(
        f'{cliente['nome']} Dados do serviço armazenados', 8, total_dePasso)

    preco, forma_pgto, recibo = extrair_financeiro(driver)
    cliente["financeiro"] = [preco, forma_pgto, recibo]
    atualizar_progresso(
        f'{cliente['nome']} Dados financeiros armazenados', 9, total_dePasso)

    # Gera o documento de ordem de serviço
    gerar_ordem_servico_e_rota(cliente, data)
    atualizar_progresso(
        f'{cliente['nome']} Ordem de serviço finalizada', 10, total_dePasso)

    return cliente


def extrair_certificado(driver, Cod, data):
    cliente = {}
    atualizar_progresso('Buscando cliente', 1, 10)
    buscar_cliente(driver, Cod)
    cliente['cod'] = Cod
    cliente['nome'] = extrair_nome(driver)
    atualizar_progresso(f'{cliente['nome']} buscando CPF/CNPJ... ', 2, 10)
    cliente['cpf'] = extrair_CPF(driver, cliente)
    atualizar_progresso(f'{cliente['nome']} buscando endereço... ', 3, 10)
    endereços = extrair_enderecos(driver)  # pode vir varios endereços
    data_hora = extrair_data_hora_servico(driver, data)  # virá uma lista
    endereço = validar_endereco(driver, endereços)  # né!
    cliente['endereço'] = endereço
    atualizar_progresso(f'{cliente['nome']} Buscando data... ', 4, 10)
    cliente['data'] = data_hora[1]
    atualizar_progresso(
        f'{cliente['nome']} Buscando dados do serviço... ', 5, 10)
    cliente['dados_serv'] = extrair_dados_servico(driver)
    atualizar_progresso(
        f'{cliente['nome']} Buscando tempo de garantia... ', 6, 10)
    cliente['garantia'] = str(extrair_tempos_garantia(driver))
    atualizar_progresso(f'{cliente['nome']} Calculando termino... ', 7, 10)
    cliente['termino'] = calcular_data_termino(
        cliente['data'], cliente['garantia'])
    return cliente


def certificado_controlePragas(cliente, caminho_para_salvar):
    """
    Abre o modelo de certificado (arquivo "CERTIFICADO [controle de pragas].docx"),
    substitui os marcadores [palavra] pelos valores do dicionário cliente e salva
    o resultado no caminho fornecido com o nome "certificado de {nome} [controle de pragas].docx".
    """
    # Carrega o modelo do certificado
    dir_atual = os.getcwd()

    certificado_templete = os.path.join(
        dir_atual, "3 - templetes", "CERTIFICADO [controle de pragas].docx")
    doc = Document(certificado_templete)

    atualizar_progresso(f'{cliente['nome']} ajustando dados... ', 8, 10)

    # Determina se o valor de cliente["cpf"] é CPF ou CNPJ
    cpf_cnpj = re.sub(r'\D', '', cliente['cpf'])
    if len(cpf_cnpj) == 10:
        tipo_documento = "CPF"
    elif len(cpf_cnpj) == 14:
        tipo_documento = "CNPJ"
    else:
        tipo_documento = "CNPJ"

    endereco = cliente['endereço']
    endereco_str = f"{endereco['Endereço']}, {endereco['Nº']}"
    nome_sem_codigo = re.sub(r"\s*\(.*\)$", "", cliente['nome'])

    # Cria o dicionário de substituições com as palavras-chave e os respectivos valores
    substituicoes = {
        "[código]": str(cliente['cod']),
        "[cliente]": nome_sem_codigo,
        "[tipo]": tipo_documento,
        "[aqui]": str(cliente['cpf']),
        "[endereço]": endereco_str,
        "[bairro]": endereco['Bairro'],
        "[cidade]": endereco['Cidade'],
        "[data]": str(cliente['data']),
        "[termino]": str(cliente['termino']),
        "[garantia]": str(cliente['garantia']),
        "[insetos]": cliente['dados_serv']
    }
    atualizar_progresso(f'{cliente['nome']} Criando certificado... ', 9, 10)
    # Função auxiliar para substituir texto em um parágrafo preservando (ao menos parcialmente) a formatação

    def substituir_texto(paragraph, subs):
        # Junta o texto de todos os runs do parágrafo
        full_text = "".join(run.text for run in paragraph.runs)

        # Realiza as substituições no texto completo
        for chave, valor in subs.items():
            full_text = full_text.replace(chave, valor)

        # Atualiza o primeiro run com o texto modificado e limpa os demais para evitar duplicação
        if paragraph.runs:
            paragraph.runs[0].text = full_text
            for run in paragraph.runs[1:]:
                run.text = ""

    # Substituição nos parágrafos do documento
    for paragrafo in doc.paragraphs:
        substituir_texto(paragrafo, substituicoes)

    # Substituição nas células das tabelas
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for paragrafo in celula.paragraphs:
                    substituir_texto(paragrafo, substituicoes)
    # Define o nome do arquivo a partir do nome do cliente
    atualizar_progresso(f'{cliente['nome']} Certificado concluido!!', 10, 10)
    nome_cliente = cliente['nome'].replace(
        ":", "").replace("/", "-").replace("\\", "").strip()
    nome_arquivo = f"{nome_cliente} [controle de pragas].docx"
    caminho_completo = os.path.join(caminho_para_salvar, nome_arquivo)

    # Salva o documento no caminho especificado
    doc.save(caminho_completo)


'''if __name__ == "__main__":
    # Exemplo de uso
    driver = configurar_driver()
    login_benu(driver)
    
    # Solicita os dados do usuário
    data_input = input("Digite a data (formato DD/MM/AAAA): ")
    codigo_cliente = input("Digite o código do cliente: ")
    
    resultado = processar_os(driver, data_input, codigo_cliente)
    print("Processo concluído.")
    driver.quit()'''

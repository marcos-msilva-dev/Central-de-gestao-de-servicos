import extrair_dados
import pprint
import Fazer1Recibo
from selenium import webdriver
from selenium.webdriver.common.by import By
import openpyxl
import os
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime


def main():
    # Configura o driver e realiza o login no Benu
    
    driver = extrair_dados.configurar_driver()
    extrair_dados.login_benu(driver)
    print("Login efetuado")

    # Inicializa as variáveis de controle
    cliente = []
    dados = []
    # Indica se será gerado o recibo da parte 1 (True) ou parte 2 (False)
    n1Recibo = True
    nome_recibo = 0
    ultimo_recibo_nome = ["", ""]
    os.system("cls")
    
    while True:
        print("=== MENU ===")
        print("1 - Fazer 1 ordem de serviço")
        print("2 - Esteira de ordem de serviço")
        print("3 - Fazer 1 recibo")
        print('4 - Fazer 1 certificado')
        print("0 - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            # Processa uma ordem de serviço única
            cliente.clear()
            código = input('\nDigite o código do cliente: ')
            cliente = extrair_dados.fazer_1_ordem(driver, data, código, 12)
            # Verifica se o financeiro indica que o recibo deve ser gerado
            if cliente["financeiro"][2] == True:
                ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                    cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                )
                # Atualiza a barra de progresso (chama função de atualização com mensagem)
                extrair_dados.atualizar_progresso(
                    f"{cliente['nome']} recibo finalizada", 11, 12
                )
                # Alterna entre a parte de cima e a parte de baixo do recibo
                if n1Recibo:
                    n1Recibo = False  # Próximo recibo será a parte 2
                else:
                    nome_recibo += 1
                    n1Recibo = True   # Após a parte 2, reinicia para parte 1
                extrair_dados.atualizar_progresso(
                    f'{cliente['nome']} OS + recibo feito!', 12, 12)
            else:
                extrair_dados.atualizar_progresso(
                    f'{cliente['nome']} OS Feita!', 12, 12)
            dados.append(cliente)

        elif escolha == "2":
            # Variáveis de controle iniciais
            n1Recibo = True
            nome_recibo = 0
            ultimo_recibo_nome = ["", ""]
            cliente_sem_recibo = []
            dados = []

            # Carrega a planilha e seleciona a primeira página
            planilha = openpyxl.load_workbook("Lista.xlsx")
            pagina1 = planilha["Plan1"]

            # Processa cada linha da planilha (cada código de cliente)
            for linha in pagina1.iter_rows(min_row=1, values_only=True):
                codigo = linha[0]
                if codigo is None:
                    print("\n\nAcabou os códigos")
                    break

                # Chama a função para gerar a ordem de serviço para o cliente
                cliente = extrair_dados.fazer_1_ordem(driver, data, codigo, 11)

                # Verifica se o campo financeiro indica que o recibo deve ser gerado
                if cliente["financeiro"][2]:
                    ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                        cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                    )
                    # Atualiza o progresso com mensagem informando que OS + recibo foram feitos
                    extrair_dados.atualizar_progresso(
                        f"{cliente['nome']} OS + recibo feitos!", 11, 11)

                    # Alterna entre a parte 1 e a parte 2 do recibo
                    if n1Recibo:
                        n1Recibo = False  # O próximo recibo será a parte 2
                    else:
                        nome_recibo += 1
                        n1Recibo = True   # Reinicia para a parte 1 após concluir a parte 2
                else:
                    # Se não for para gerar recibo, armazena o nome do cliente na lista de clientes sem recibo
                    cliente_sem_recibo.append(cliente["nome"])
                    extrair_dados.atualizar_progresso(
                        f"{cliente['nome']} OS feita!", 11, 11)

                # Adiciona os dados do cliente à lista geral
                dados.append(cliente)

            # Exibe os nomes dos clientes que não tiveram recibo gerado
            print("Cliente sem recibos:")
            for cliente1 in cliente_sem_recibo:
                print(cliente1)

        elif escolha == "3":
            # Processa o recibo com base nos dados extraídos para recibos
            cliente.clear()
            código = input('\nDigite o código do cliente: ')
            cliente = Fazer1Recibo.extrair_dados_recibo(driver, código, data)
            if cliente["financeiro"][2] == True:
                extrair_dados.atualizar_progresso(
                    f'{cliente['nome']} fazendo o recibo', 5, 6)
                ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                    cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                )
                # Alterna entre as partes do recibo
                if n1Recibo:
                    n1Recibo = False  # Próximo recibo será a parte 2
                else:
                    nome_recibo += 1
                    n1Recibo = True   # Reinicia para a parte 1
                extrair_dados.atualizar_progresso(
                    f'{cliente['nome']} Recibo feito!', 6, 6)
            else:
                extrair_dados.atualizar_progresso(
                    f'{cliente['nome']} Sem valor no financeiro!', 4, 6)

        elif escolha == "4":
            # extrair dados necesssários(nome, cpf, endereço, bairro, cidade dados do serviço (apenas as pragas), data de inicio e cód)
            data = extrair_dados.selecionar_data()
            código = input('Digite o código do cliente: ')
            cliente = extrair_dados.extrair_certificado(driver, código, data)
            # colar dados no tamplete
            dir_atual = os.path.dirname(os.path.abspath(__file__))
            caminho_para_salvar = os.path.join(dir_atual, "certificado")
            extrair_dados.certificado_controlePragas(
                cliente, caminho_para_salvar)
            # coloca a praga alvo no 'Sinantrópicos previstos'
            # eu vou ter que marcar manualmente a praga alvo, programar isso é muito trabalhoso e ariscado
            # embora seja totalmente possivel fazer isso de forma automatica
            # mas daria muito trampo.

        elif escolha == "0":
            print("\nSaindo do programa...")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    main()


# fazer OS de caixa d'água
# fazer certificado de todos que tem valor
# opção de fazer certificado para qualquer cliente

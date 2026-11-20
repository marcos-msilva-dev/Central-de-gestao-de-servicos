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

def iniciar_interface():
    # --- Código da interface (Tkinter) ---
    import tkinter as tk
    from tkinter import ttk
    from tkcalendar import Calendar
    import threading
    global extrair_dados

    # Função para atualizar o widget de progresso (terminal da interface)
    def atualizar_progresso_gui(mensagem, porcentagem=None):
        progress_text.insert(tk.END, mensagem + "\n")
        progress_text.see(tk.END)

    # CALLBACK DE LOGIN: Será acionado pelo botão de Login
    def callback_login():
        global driver
        atualizar_progresso_gui("Iniciando login...")
        driver = extrair_dados.configurar_driver()
        extrair_dados.login_benu(driver)
        atualizar_progresso_gui("Login realizado com sucesso!")

    # CALLBACKS existentes (Fazer 1 OS, Esteira, Recibo, Certificado)
    def callback_fazer_os():
        from tkinter import messagebox  # Para alertas
        data_selecionada = cal.get_date()
        codigo = input_entry.get()
        if not data_selecionada:
            messagebox.showerror("Erro", "Por favor, informe uma data.")
            return
        if not codigo:
            messagebox.showerror("Erro", "Por favor, informe o código do cliente.")
            return
        extrair_dados.atualizar_progresso(f"[Fazer 1 OS] Data: {data_selecionada} | Código: {codigo}", 0, 12)
        def processar():
            global driver, n1Recibo, nome_recibo, ultimo_recibo_nome, dados
            cliente = extrair_dados.fazer_1_ordem(driver, data_selecionada, codigo, 12)
            if cliente["financeiro"][2] == True:
                ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                    cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                )
                extrair_dados.atualizar_progresso(f"{cliente['nome']} recibo finalizada", 11, 12)
                if n1Recibo:
                    n1Recibo = False
                else:
                    nome_recibo += 1
                    n1Recibo = True
                extrair_dados.atualizar_progresso(f"{cliente['nome']} OS + recibo feito!", 12, 12)
            else:
                extrair_dados.atualizar_progresso(f"{cliente['nome']} OS Feita!", 12, 12)
            dados.append(cliente)
        threading.Thread(target=processar).start()

    def callback_esteira():
        from tkinter import messagebox
        data_selecionada = cal.get_date()
        if not data_selecionada:
            messagebox.showerror("Erro", "Por favor, informe uma data.")
            return
        extrair_dados.atualizar_progresso(f"[Esteira de OS] Iniciando processo para data: {data_selecionada}", 0, 11)
        def processar():
            global driver, n1Recibo, nome_recibo, ultimo_recibo_nome, dados
            n1Recibo = True
            nome_recibo = 0
            ultimo_recibo_nome = ["", ""]
            cliente_sem_recibo = []
            dados = []
            import openpyxl
            planilha = openpyxl.load_workbook("Lista.xlsx")
            pagina1 = planilha["Plan1"]
            for linha in pagina1.iter_rows(min_row=1, values_only=True):
                codigo = linha[0]
                if codigo is None:
                    extrair_dados.imprimir_mensagem("Acabaram os códigos.")
                    break
                cliente = extrair_dados.fazer_1_ordem(driver, data_selecionada, codigo, 11)
                if cliente["financeiro"][2]:
                    ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                        cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                    )
                    extrair_dados.atualizar_progresso(f"{cliente['nome']} OS + recibo feitos!", 11, 11)
                    if n1Recibo:
                        n1Recibo = False
                    else:
                        nome_recibo += 1
                        n1Recibo = True
                else:
                    cliente_sem_recibo.append(cliente["nome"])
                    extrair_dados.atualizar_progresso(f"{cliente['nome']} OS feita!", 11, 11)
                dados.append(cliente)
            if cliente_sem_recibo:
                msg = "Clientes sem recibos:\n" + "\n".join(cliente_sem_recibo)
                extrair_dados.imprimir_mensagem(msg)
            else:
                extrair_dados.imprimir_mensagem("Todos os clientes tiveram recibo gerado.")
            extrair_dados.imprimir_mensagem("Processo de Esteira finalizado!")
        threading.Thread(target=processar).start()

    def callback_recibo():
        from tkinter import messagebox
        data_selecionada = cal.get_date()
        codigo = input_entry.get()
        if not data_selecionada:
            messagebox.showerror("Erro", "Por favor, informe uma data.")
            return
        if not codigo:
            messagebox.showerror("Erro", "Por favor, informe o código do cliente.")
            return
        extrair_dados.atualizar_progresso(f"[Fazer 1 Recibo] Data: {data_selecionada} | Código: {codigo}", 0, 6)
        def processar():
            global driver, n1Recibo, nome_recibo, ultimo_recibo_nome, dados
            cliente = Fazer1Recibo.extrair_dados_recibo(driver, codigo, data_selecionada)
            if cliente["financeiro"][2] == True:
                extrair_dados.atualizar_progresso(f"{cliente['nome']} fazendo o recibo", 5, 6)
                ultimo_recibo_nome = Fazer1Recibo.fazerRecibo(
                    cliente, n1Recibo, nome_recibo, ultimo_recibo_nome[0], ultimo_recibo_nome[1]
                )
                if n1Recibo:
                    n1Recibo = False
                else:
                    nome_recibo += 1
                    n1Recibo = True
                extrair_dados.atualizar_progresso(f"{cliente['nome']} Recibo feito!", 6, 6)
            else:
                extrair_dados.atualizar_progresso(f"{cliente['nome']} Sem valor no financeiro!", 4, 6)
            dados.append(cliente)
        threading.Thread(target=processar).start()

    def callback_certificado():
        from tkinter import messagebox
        data_selecionada = cal.get_date()
        codigo = input_entry.get()
        if not data_selecionada:
            messagebox.showerror("Erro", "Por favor, informe uma data.")
            return
        if not codigo:
            messagebox.showerror("Erro", "Por favor, informe o código do cliente.")
            return
        atualizar_progresso_gui(f"[Fazer 1 Certificado] Data: {data_selecionada} | Código: {codigo}")
        def processar():
            global driver
            cliente = extrair_dados.extrair_certificado(driver, codigo, data_selecionada)
            dir_atual = os.getcwd()
            caminho_para_salvar = os.path.join(dir_atual, "2 - certificado")
            extrair_dados.certificado_controlePragas(cliente, caminho_para_salvar)
            atualizar_progresso_gui("Certificado gerado com sucesso!")
        threading.Thread(target=processar).start()

    # Criação da janela principal e definição do layout
    root = tk.Tk()
    root.title("Central de Gestão de Serviços")

    # Configura a grade do root: três linhas (top, input e autor)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=0)
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)

    # Frame principal (top) com dois subframes: esquerdo e direito
    frame_top = tk.Frame(root)
    frame_top.grid(row=0, column=0, columnspan=2, sticky="nsew")

    # Frame esquerdo para calendário, botões e login
    frame_left = tk.Frame(frame_top, width=200)
    frame_left.grid(row=0, column=0, sticky="ns")

    # Adiciona um botão de Login no topo
    """btn_login = tk.Button(frame_left, text="Login", width=20, command=callback_login)
    btn_login.pack(pady=5, padx=5, fill="x")"""

    # Calendário
    from tkcalendar import Calendar
    cal = Calendar(frame_left, selectmode='day', date_pattern="dd/mm/yyyy")
    cal.pack(pady=10, padx=5)

    # Botões para as ações
    btn_fazer_os = tk.Button(frame_left, text="Fazer 1 OS", width=20, command=callback_fazer_os)
    btn_fazer_os.pack(pady=5, padx=5, fill="x")

    btn_esteira = tk.Button(frame_left, text="Esteira de OS", width=20, command=callback_esteira)
    btn_esteira.pack(pady=5, padx=5, fill="x")

    btn_recibo = tk.Button(frame_left, text="Fazer 1 Recibo", width=20, command=callback_recibo)
    btn_recibo.pack(pady=5, padx=5, fill="x")

    btn_certificado = tk.Button(frame_left, text="Fazer 1 Certificado", width=20, command=callback_certificado)
    btn_certificado.pack(pady=5, padx=5, fill="x")

    # Frame direito para exibição do progresso
    frame_right = tk.Frame(frame_top)
    frame_right.grid(row=0, column=1, sticky="nsew")
    frame_top.grid_columnconfigure(1, weight=1)
    progress_text = tk.Text(frame_right)
    progress_text.pack(expand=True, fill="both", padx=5, pady=5)
    extrair_dados.PROGRESS_WIDGET = progress_text

    # Frame inferior para área de input
    frame_bottom = tk.Frame(root)
    frame_bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    input_label = tk.Label(frame_bottom, text="Insira o código ou outro dado:")
    input_label.pack(side="left", padx=5)
    input_entry = tk.Entry(frame_bottom)
    input_entry.pack(side="left", fill="x", expand=True, padx=5)
    input_button = tk.Button(frame_bottom, text="Enviar")
    input_button.pack(side="left", padx=5)
    extrair_dados.INPUT_ENTRY = input_entry
    extrair_dados.INPUT_BUTTON = input_button

    # Frame do autor
    frame_author = tk.Frame(root)
    frame_author.grid(row=2, column=0, columnspan=2, sticky="se", padx=10, pady=5)
    author_label = tk.Label(frame_author, text="Desenvolvido por: Marcos Martins", font=("Arial", 8), fg="gray")
    author_label.pack(side="right")
    
    root.after(1, callback_login)

    root.mainloop()

def main():
    global driver, n1Recibo, nome_recibo, ultimo_recibo_nome, dados
    # Inicializa as variáveis de controle
    n1Recibo = True
    nome_recibo = 0
    ultimo_recibo_nome = ["", ""]
    dados = []
    os.system("cls")
    # Inicia a interface gráfica (o login será feito a partir do botão "Login")
    iniciar_interface()

if __name__ == "__main__":
    main()

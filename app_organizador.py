import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

ARQUIVO_HISTORICO = "historico.json"

tipos = {
    "imagens": [".png", ".jpg", ".jpeg", ".webp", ".gif"],
    "pdfs": [".pdf"],
    "videos": [".mp4", ".mkv", ".avi", ".mov"],
    "documentos": [".docx", ".txt", ".doc"],
    "planilhas": [".xlsx", ".xls", ".csv"],
    "musicas": [".mp3", ".wav", ".flac", ".aac"],
    "compactados": [".rar", ".zip", ".7z", ".tar", ".gz"],
    "programas": [".exe", ".msi", ".bat", ".cmd"]
}

pasta_selecionada = ""
historico_movimentos = []


def adicionar_log(texto):
    caixa_log.insert(tk.END, texto + "\n")
    caixa_log.see(tk.END)


def salvar_historico():
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
        json.dump(historico_movimentos, arquivo, ensure_ascii=False, indent=4)


def carregar_historico():
    global historico_movimentos

    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
                historico_movimentos = json.load(arquivo)
        except Exception:
            historico_movimentos = []
    else:
        historico_movimentos = []


def limpar_historico():
    global historico_movimentos
    historico_movimentos = []

    if os.path.exists(ARQUIVO_HISTORICO):
        os.remove(ARQUIVO_HISTORICO)


def gerar_destino_sem_sobrescrever(destino, arquivo):
    destino_final = os.path.join(destino, arquivo)
    contador = 1

    while os.path.exists(destino_final):
        nome, extensao = os.path.splitext(arquivo)
        novo_nome = f"{nome}_{contador}{extensao}"
        destino_final = os.path.join(destino, novo_nome)
        contador += 1

    return destino_final


def organizar_arquivos():
    global pasta_selecionada, historico_movimentos

    if not pasta_selecionada:
        messagebox.showwarning("Aviso", "Escolha uma pasta primeiro.")
        return

    historico_movimentos = []

    resumo = {
        "imagens": 0,
        "pdfs": 0,
        "videos": 0,
        "documentos": 0,
        "planilhas": 0,
        "musicas": 0,
        "compactados": 0,
        "programas": 0,
        "outros": 0
    }

    caixa_log.delete("1.0", tk.END)
    adicionar_log("Iniciando organização...")

    for arquivo in os.listdir(pasta_selecionada):
        caminho_arquivo = os.path.join(pasta_selecionada, arquivo)

        if os.path.isfile(caminho_arquivo):
            movido = False

            for pasta_destino, extensoes in tipos.items():
                if any(arquivo.lower().endswith(ext) for ext in extensoes):
                    destino = os.path.join(pasta_selecionada, pasta_destino)
                    os.makedirs(destino, exist_ok=True)

                    destino_final = gerar_destino_sem_sobrescrever(destino, arquivo)

                    adicionar_log(f"Movendo {arquivo} para {pasta_destino}")
                    shutil.move(caminho_arquivo, destino_final)

                    historico_movimentos.append({
                        "origem": caminho_arquivo,
                        "destino": destino_final
                    })

                    resumo[pasta_destino] += 1
                    movido = True
                    break

            if not movido:
                destino = os.path.join(pasta_selecionada, "outros")
                os.makedirs(destino, exist_ok=True)

                destino_final = gerar_destino_sem_sobrescrever(destino, arquivo)

                adicionar_log(f"Movendo {arquivo} para outros")
                shutil.move(caminho_arquivo, destino_final)

                historico_movimentos.append({
                    "origem": caminho_arquivo,
                    "destino": destino_final
                })

                resumo["outros"] += 1

    salvar_historico()

    adicionar_log("")
    adicionar_log("Resumo final:")

    for categoria, quantidade in resumo.items():
        if quantidade > 0:
            adicionar_log(f"{categoria}: {quantidade} arquivo(s)")

    adicionar_log("")
    adicionar_log("Organização concluída.")
    messagebox.showinfo("Sucesso", "Arquivos organizados com sucesso!")


def desfazer_organizacao():
    global historico_movimentos

    carregar_historico()

    if not historico_movimentos:
        messagebox.showwarning("Aviso", "Não há nenhuma organização para desfazer.")
        return

    adicionar_log("")
    adicionar_log("Desfazendo última organização...")

    for item in reversed(historico_movimentos):
        origem = item["origem"]
        destino = item["destino"]

        if os.path.exists(destino):
            pasta_origem = os.path.dirname(origem)
            os.makedirs(pasta_origem, exist_ok=True)

            origem_final = gerar_destino_sem_sobrescrever(
                pasta_origem,
                os.path.basename(origem)
            )

            adicionar_log(
                f"Voltando {os.path.basename(destino)} para {pasta_origem}"
            )
            shutil.move(destino, origem_final)

    limpar_historico()

    adicionar_log("Desfazer concluído.")
    messagebox.showinfo("Sucesso", "Última organização foi desfeita.")


def escolher_pasta():
    global pasta_selecionada

    pasta = filedialog.askdirectory()

    if pasta:
        pasta_selecionada = pasta
        label_pasta.config(text=f"Pasta: {pasta_selecionada}")
        adicionar_log(f"Pasta escolhida: {pasta_selecionada}")


def abrir_pasta():
    global pasta_selecionada

    if not pasta_selecionada:
        messagebox.showwarning("Aviso", "Escolha uma pasta primeiro.")
        return

    if os.path.exists(pasta_selecionada):
        os.startfile(pasta_selecionada)
    else:
        messagebox.showerror("Erro", "A pasta selecionada não existe mais.")


janela = tk.Tk()
janela.title("Organizador de Arquivos")
janela.geometry("780x520")
janela.configure(bg="#f4f6f8")

titulo = tk.Label(
    janela,
    text="Organizador de Arquivos",
    font=("Segoe UI", 18, "bold"),
    bg="#f4f6f8",
    fg="#1f2937"
)
titulo.pack(pady=15)

botao_escolher = tk.Button(
    janela,
    text="Escolher pasta",
    command=escolher_pasta,
    bg="#2563eb",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=18,
    height=2,
    bd=0,
    cursor="hand2"
)
botao_escolher.pack(pady=8)

label_pasta = tk.Label(
    janela,
    text="Nenhuma pasta selecionada",
    font=("Segoe UI", 10),
    bg="#f4f6f8",
    fg="#374151"
)
label_pasta.pack(pady=8)

frame_botoes = tk.Frame(janela, bg="#f4f6f8")
frame_botoes.pack(pady=10)

botao_organizar = tk.Button(
    frame_botoes,
    text="Organizar arquivos",
    command=organizar_arquivos,
    bg="#16a34a",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=18,
    height=2,
    bd=0,
    cursor="hand2"
)
botao_organizar.pack(side="left", padx=8)

botao_desfazer = tk.Button(
    frame_botoes,
    text="Desfazer última",
    command=desfazer_organizacao,
    bg="#dc2626",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=18,
    height=2,
    bd=0,
    cursor="hand2"
)
botao_desfazer.pack(side="left", padx=8)

botao_abrir_pasta = tk.Button(
    frame_botoes,
    text="Abrir pasta",
    command=abrir_pasta,
    bg="#7c3aed",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=18,
    height=2,
    bd=0,
    cursor="hand2"
)
botao_abrir_pasta.pack(side="left", padx=8)

frame_log = tk.Frame(janela, bg="#f4f6f8")
frame_log.pack(pady=12)

scrollbar = tk.Scrollbar(frame_log)
scrollbar.pack(side="right", fill="y")

caixa_log = tk.Text(
    frame_log,
    height=18,
    width=88,
    font=("Consolas", 10),
    bg="white",
    fg="#111827",
    bd=1,
    relief="solid",
    yscrollcommand=scrollbar.set
)
caixa_log.pack(side="left")

scrollbar.config(command=caixa_log.yview)

carregar_historico()

if historico_movimentos:
    adicionar_log("Histórico carregado. Você ainda pode desfazer a última organização.")

janela.mainloop()
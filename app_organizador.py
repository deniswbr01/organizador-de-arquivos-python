import os
import json
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu

VERSAO_APP = "2.3.0"
ARQUIVO_HISTORICO = "historico.json"
ARQUIVO_CONFIG = "config.json"

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

nomes_bonitos = {
    "imagens": "Imagens",
    "pdfs": "PDFs",
    "videos": "Vídeos",
    "documentos": "Documentos",
    "planilhas": "Planilhas",
    "musicas": "Músicas",
    "compactados": "Compactados",
    "programas": "Programas",
    "outros": "Outros"
}

pasta_selecionada = ""
historico_movimentos = []

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def adicionar_log(texto):
    caixa_log.configure(state="normal")
    caixa_log.insert("end", texto + "\n")
    caixa_log.see("end")
    caixa_log.configure(state="disabled")


def limpar_log():
    caixa_log.configure(state="normal")
    caixa_log.delete("1.0", "end")
    caixa_log.configure(state="disabled")
    adicionar_log("Log limpo.")


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


def salvar_config():
    config = {
        "ultima_pasta": pasta_selecionada
    }
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
            json.dump(config, arquivo, ensure_ascii=False, indent=4)
    except Exception as erro:
        adicionar_log(f"Erro ao salvar configurações: {erro}")


def carregar_config():
    global pasta_selecionada

    if not os.path.exists(ARQUIVO_CONFIG):
        return

    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
            config = json.load(arquivo)

        ultima_pasta = config.get("ultima_pasta", "")
        if ultima_pasta and os.path.exists(ultima_pasta):
            pasta_selecionada = ultima_pasta
            atualizar_label_pasta()
            adicionar_log(f"Última pasta carregada: {pasta_selecionada}")
            atualizar_status("Última pasta carregada")
    except Exception as erro:
        adicionar_log(f"Erro ao carregar configurações: {erro}")


def gerar_destino_sem_sobrescrever(destino, arquivo):
    destino_final = os.path.join(destino, arquivo)
    contador = 1

    while os.path.exists(destino_final):
        nome, extensao = os.path.splitext(arquivo)
        novo_nome = f"{nome}_{contador}{extensao}"
        destino_final = os.path.join(destino, novo_nome)
        contador += 1

    return destino_final


def animar_barra(valor, total):
    if total <= 0:
        barra_progresso.set(0)
        label_percentual.configure(text="0%")
        janela.update_idletasks()
        return

    alvo = valor / total
    atual = barra_progresso.get()

    if alvo < atual:
        barra_progresso.set(alvo)
    else:
        passo = 0.01
        while atual < alvo:
            atual = min(atual + passo, alvo)
            barra_progresso.set(atual)
            label_percentual.configure(text=f"{int(atual * 100)}%")
            janela.update_idletasks()

    label_percentual.configure(text=f"{int(alvo * 100)}%")


def atualizar_status(texto):
    label_status.configure(text=f"Status: {texto}")
    janela.update_idletasks()


def bloquear_botoes(bloquear=True):
    estado = "disabled" if bloquear else "normal"

    botao_escolher.configure(state=estado)
    botao_organizar.configure(state=estado)
    botao_simular.configure(state=estado)
    botao_desfazer.configure(state=estado)
    botao_abrir_pasta.configure(state=estado)

    for checkbox in checkboxes_categorias.values():
        checkbox.configure(state=estado)


def obter_categorias_selecionadas():
    categorias = []

    for categoria, variavel in variaveis_categorias.items():
        if variavel.get():
            categorias.append(categoria)

    return categorias


def obter_arquivos_da_pasta():
    if not pasta_selecionada:
        return []

    arquivos = []
    pastas_categorias = set(tipos.keys()) | {"outros"}

    for item in os.listdir(pasta_selecionada):
        caminho_item = os.path.join(pasta_selecionada, item)

        # pega apenas arquivos soltos da pasta principal
        if os.path.isfile(caminho_item):
            arquivos.append(item)

        # ignora pastas já criadas pelo organizador
        elif os.path.isdir(caminho_item) and item.lower() in pastas_categorias:
            continue

    return arquivos


def analisar_arquivos(categorias_selecionadas):
    resumo = {categoria: 0 for categoria in tipos.keys()}
    resumo["outros"] = 0

    detalhes = []
    arquivos = obter_arquivos_da_pasta()

    for arquivo in arquivos:
        classificado = False

        for categoria, extensoes in tipos.items():
            if categoria in categorias_selecionadas and any(
                arquivo.lower().endswith(ext) for ext in extensoes
            ):
                resumo[categoria] += 1
                detalhes.append((arquivo, categoria))
                classificado = True
                break

        if not classificado:
            resumo["outros"] += 1
            detalhes.append((arquivo, "outros"))

    return arquivos, resumo, detalhes


def montar_texto_resumo(resumo):
    linhas = []
    total = 0

    for categoria, quantidade in resumo.items():
        if quantidade > 0:
            linhas.append(f"{nomes_bonitos[categoria]}: {quantidade}")
            total += quantidade

    linhas.append(f"Total: {total} arquivo(s)")
    return "\n".join(linhas), total


def atualizar_label_pasta():
    if pasta_selecionada:
        texto = pasta_selecionada
        if len(texto) > 80:
            texto = "..." + texto[-77:]
        label_pasta_valor.configure(text=texto)
    else:
        label_pasta_valor.configure(text="Nenhuma pasta selecionada")


def escolher_pasta():
    global pasta_selecionada

    pasta = filedialog.askdirectory()

    if pasta:
        pasta_selecionada = pasta
        atualizar_label_pasta()
        salvar_config()
        adicionar_log(f"Pasta escolhida: {pasta_selecionada}")
        atualizar_status("Pasta selecionada")


def abrir_pasta():
    if not pasta_selecionada:
        messagebox.showwarning("Aviso", "Escolha uma pasta primeiro.")
        return

    if os.path.exists(pasta_selecionada):
        os.startfile(pasta_selecionada)
        adicionar_log("Pasta aberta no Explorador.")
        atualizar_status("Pasta aberta")
    else:
        messagebox.showerror("Erro", "A pasta selecionada não existe mais.")


def simular_organizacao():
    if not pasta_selecionada:
        messagebox.showwarning("Aviso", "Escolha uma pasta primeiro.")
        return

    categorias_selecionadas = obter_categorias_selecionadas()

    if not categorias_selecionadas:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma categoria.")
        return

    limpar_log()
    adicionar_log("Simulando organização...")
    atualizar_status("Analisando arquivos para simulação")
    animar_barra(0, 0)

    arquivos, resumo, detalhes = analisar_arquivos(categorias_selecionadas)

    if not arquivos:
        messagebox.showinfo(
            "Aviso",
            "Não há arquivos soltos na pasta principal para analisar."
        )
        adicionar_log("Não há arquivos soltos na pasta principal para analisar.")
        atualizar_status("Nada para analisar")
        return

    texto_resumo, total = montar_texto_resumo(resumo)

    adicionar_log("Resultado da simulação:")
    adicionar_log("")

    for categoria, quantidade in resumo.items():
        if quantidade > 0:
            adicionar_log(f"{nomes_bonitos[categoria]}: {quantidade} arquivo(s)")

    adicionar_log("")
    adicionar_log("Prévia dos arquivos:")
    adicionar_log("")

    total_detalhes = len(detalhes)
    for indice, (arquivo, categoria) in enumerate(detalhes, start=1):
        adicionar_log(f"{arquivo}  ->  {nomes_bonitos[categoria]}")
        animar_barra(indice, total_detalhes)
        atualizar_status(f"Simulando {indice} de {total_detalhes}")

    atualizar_status("Simulação concluída")
    messagebox.showinfo(
        "Simulação concluída",
        f"Arquivos encontrados antes de organizar:\n\n{texto_resumo}"
    )


def organizar_arquivos():
    global historico_movimentos

    if not pasta_selecionada:
        messagebox.showwarning("Aviso", "Escolha uma pasta primeiro.")
        return

    categorias_selecionadas = obter_categorias_selecionadas()

    if not categorias_selecionadas:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma categoria.")
        return

    arquivos, resumo_previo, _ = analisar_arquivos(categorias_selecionadas)

    if not arquivos:
        messagebox.showinfo(
            "Aviso",
            "Não há arquivos soltos na pasta principal para organizar."
        )
        adicionar_log("Não há arquivos soltos na pasta principal para organizar.")
        animar_barra(0, 0)
        atualizar_status("Nada para organizar")
        return

    texto_resumo, total_encontrado = montar_texto_resumo(resumo_previo)

    confirmar = messagebox.askyesno(
        "Confirmar organização",
        f"Foram encontrados estes arquivos:\n\n{texto_resumo}\n\nDeseja continuar?"
    )

    if not confirmar:
        adicionar_log("Organização cancelada pelo usuário.")
        atualizar_status("Organização cancelada")
        return

    historico_movimentos = []
    resumo_final = {categoria: 0 for categoria in tipos.keys()}
    resumo_final["outros"] = 0

    limpar_log()
    adicionar_log("Iniciando organização...")
    atualizar_status("Preparando organização")
    bloquear_botoes(True)
    animar_barra(0, 1)

    total_arquivos = len(arquivos)
    arquivos_processados = 0
    total_movido = 0

    try:
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(pasta_selecionada, arquivo)
            movido = False

            try:
                atualizar_status(f"Processando: {arquivo}")

                for pasta_destino, extensoes in tipos.items():
                    if (
                        pasta_destino in categorias_selecionadas
                        and any(arquivo.lower().endswith(ext) for ext in extensoes)
                    ):
                        destino = os.path.join(pasta_selecionada, pasta_destino)
                        os.makedirs(destino, exist_ok=True)

                        destino_final = gerar_destino_sem_sobrescrever(destino, arquivo)

                        adicionar_log(
                            f"Movendo {arquivo} para {nomes_bonitos[pasta_destino]}"
                        )
                        shutil.move(caminho_arquivo, destino_final)

                        historico_movimentos.append({
                            "origem": caminho_arquivo,
                            "destino": destino_final
                        })

                        resumo_final[pasta_destino] += 1
                        total_movido += 1
                        movido = True
                        break

                if not movido:
                    destino = os.path.join(pasta_selecionada, "outros")
                    os.makedirs(destino, exist_ok=True)

                    destino_final = gerar_destino_sem_sobrescrever(destino, arquivo)

                    adicionar_log(f"Movendo {arquivo} para Outros")
                    shutil.move(caminho_arquivo, destino_final)

                    historico_movimentos.append({
                        "origem": caminho_arquivo,
                        "destino": destino_final
                    })

                    resumo_final["outros"] += 1
                    total_movido += 1

            except Exception as erro:
                adicionar_log(f"Erro ao mover {arquivo}: {erro}")

            arquivos_processados += 1
            animar_barra(arquivos_processados, total_arquivos)
            atualizar_status(f"Organizando {arquivos_processados} de {total_arquivos}")

        salvar_historico()

        adicionar_log("")
        adicionar_log("Resumo final:")

        for categoria, quantidade in resumo_final.items():
            if quantidade > 0:
                adicionar_log(f"{nomes_bonitos[categoria]}: {quantidade} arquivo(s)")

        adicionar_log(f"Total movido: {total_movido} arquivo(s)")
        adicionar_log("")
        adicionar_log("Organização concluída.")

        atualizar_status("Concluído com sucesso")
        messagebox.showinfo("Sucesso", "Arquivos organizados com sucesso!")

    finally:
        bloquear_botoes(False)


def desfazer_organizacao():
    global historico_movimentos

    carregar_historico()

    if not historico_movimentos:
        messagebox.showwarning("Aviso", "Não há nenhuma organização para desfazer.")
        return

    confirmar = messagebox.askyesno(
        "Confirmar desfazer",
        "Deseja desfazer a última organização?"
    )
    if not confirmar:
        adicionar_log("Desfazer cancelado pelo usuário.")
        return

    atualizar_status("Desfazendo organização...")
    bloquear_botoes(True)
    adicionar_log("")
    adicionar_log("Desfazendo última organização...")

    total_itens = len(historico_movimentos)
    itens_processados = 0
    animar_barra(0, 1)

    try:
        for item in reversed(historico_movimentos):
            origem = item["origem"]
            destino = item["destino"]

            try:
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

            except Exception as erro:
                adicionar_log(f"Erro ao desfazer {os.path.basename(destino)}: {erro}")

            itens_processados += 1
            animar_barra(itens_processados, total_itens)
            atualizar_status(f"Desfazendo {itens_processados} de {total_itens}")

        limpar_historico()
        adicionar_log("Desfazer concluído.")
        atualizar_status("Última organização desfeita")
        messagebox.showinfo("Sucesso", "Última organização foi desfeita.")

    finally:
        bloquear_botoes(False)


def mostrar_sobre():
    messagebox.showinfo(
        "Sobre o app",
        f"Organizador de Arquivos\n"
        f"Versão: {VERSAO_APP}\n\n"
        f"Organiza arquivos automaticamente por tipo.\n"
        f"Permite simular, desfazer e escolher categorias.\n\n"
        f"Desenvolvido por Denis."
    )


def definir_modo_claro():
    ctk.set_appearance_mode("light")
    adicionar_log("Tema alterado para modo claro.")
    atualizar_status("Modo claro ativado")


def definir_modo_escuro():
    ctk.set_appearance_mode("dark")
    adicionar_log("Tema alterado para modo escuro.")
    atualizar_status("Modo escuro ativado")


def criar_menu():
    barra_menu = Menu(janela)

    menu_config = Menu(barra_menu, tearoff=0)
    menu_config.add_command(label="Modo claro", command=definir_modo_claro)
    menu_config.add_command(label="Modo escuro", command=definir_modo_escuro)
    menu_config.add_separator()
    menu_config.add_command(label="Limpar log", command=limpar_log)

    menu_ajuda = Menu(barra_menu, tearoff=0)
    menu_ajuda.add_command(label="Sobre o app", command=mostrar_sobre)

    barra_menu.add_cascade(label="Configurações", menu=menu_config)
    barra_menu.add_cascade(label="Ajuda", menu=menu_ajuda)

    janela.config(menu=barra_menu)


janela = ctk.CTk()
janela.title(f"Organizador de Arquivos v{VERSAO_APP}")
janela.geometry("1080x860")
janela.resizable(False, False)

janela.update_idletasks()
largura = 1080
altura = 860
x = (janela.winfo_screenwidth() // 2) - (largura // 2)
y = (janela.winfo_screenheight() // 2) - (altura // 2)
janela.geometry(f"{largura}x{altura}+{x}+{y}")

frame_externo = ctk.CTkFrame(
    janela,
    fg_color="transparent"
)
frame_externo.pack(fill="both", expand=True, padx=22, pady=22)

frame_principal = ctk.CTkFrame(
    frame_externo,
    corner_radius=22,
    fg_color=("#f6f8fb", "#1f1f1f"),
    border_width=1,
    border_color=("#d9e1ea", "#323232")
)
frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

criar_menu()

titulo = ctk.CTkLabel(
    frame_principal,
    text="Organizador de Arquivos",
    font=ctk.CTkFont(size=24, weight="bold")
)
titulo.pack(pady=(20, 4))

subtitulo = ctk.CTkLabel(
    frame_principal,
    text="Organize seus arquivos por categoria de forma simples",
    font=ctk.CTkFont(size=12)
)
subtitulo.pack()

label_versao = ctk.CTkLabel(
    frame_principal,
    text=f"v{VERSAO_APP}",
    font=ctk.CTkFont(size=11)
)
label_versao.pack(pady=(2, 14))

frame_pasta = ctk.CTkFrame(
    frame_principal,
    corner_radius=14,
    fg_color=("#eaf0f7", "#2a2a2a"),
    height=56
)
frame_pasta.pack(fill="x", padx=26, pady=(0, 12))
frame_pasta.pack_propagate(False)

linha_pasta = ctk.CTkFrame(frame_pasta, fg_color="transparent")
linha_pasta.pack(fill="both", expand=True, padx=14, pady=10)

label_pasta_valor = ctk.CTkLabel(
    linha_pasta,
    text="Nenhuma pasta selecionada",
    font=ctk.CTkFont(size=12),
    anchor="w"
)
label_pasta_valor.pack(side="left", fill="x", expand=True)

frame_botao_escolher = ctk.CTkFrame(frame_principal, fg_color="transparent")
frame_botao_escolher.pack(fill="x", pady=(0, 12))

botao_escolher = ctk.CTkButton(
    frame_botao_escolher,
    text="Escolher pasta",
    command=escolher_pasta,
    width=180,
    height=38,
    corner_radius=12
)
botao_escolher.pack(anchor="center")

label_categorias = ctk.CTkLabel(
    frame_principal,
    text="Categorias para organizar",
    font=ctk.CTkFont(size=14, weight="bold")
)
label_categorias.pack(anchor="center", pady=(2, 6))

frame_categorias = ctk.CTkFrame(
    frame_principal,
    corner_radius=14,
    fg_color=("#eaf0f7", "#2a2a2a")
)
frame_categorias.pack(fill="x", padx=26, pady=(0, 12))

variaveis_categorias = {}
checkboxes_categorias = {}

container_categorias = ctk.CTkFrame(frame_categorias, fg_color="transparent")
container_categorias.pack(pady=14)

lista_categorias = list(tipos.keys())

for i, categoria in enumerate(lista_categorias):
    var = ctk.BooleanVar(value=True)
    variaveis_categorias[categoria] = var

    item_frame = ctk.CTkFrame(
        container_categorias,
        fg_color="transparent",
        width=170,
        height=34
    )
    item_frame.grid(row=i // 4, column=i % 4, padx=10, pady=8)
    item_frame.grid_propagate(False)

    checkbox = ctk.CTkCheckBox(
        item_frame,
        text=nomes_bonitos[categoria],
        variable=var
    )
    checkbox.pack(anchor="w", padx=10)

    checkboxes_categorias[categoria] = checkbox

frame_botoes_principais = ctk.CTkFrame(frame_principal, fg_color="transparent")
frame_botoes_principais.pack(pady=(2, 14))

botao_organizar = ctk.CTkButton(
    frame_botoes_principais,
    text="Organizar arquivos",
    command=organizar_arquivos,
    width=175,
    height=40,
    corner_radius=12,
    fg_color="#16a34a",
    hover_color="#15803d"
)
botao_organizar.pack(side="left", padx=6)

botao_simular = ctk.CTkButton(
    frame_botoes_principais,
    text="Simular organização",
    command=simular_organizacao,
    width=175,
    height=40,
    corner_radius=12,
    fg_color="#2563eb",
    hover_color="#1d4ed8"
)
botao_simular.pack(side="left", padx=6)

botao_desfazer = ctk.CTkButton(
    frame_botoes_principais,
    text="Desfazer última",
    command=desfazer_organizacao,
    width=175,
    height=40,
    corner_radius=12,
    fg_color="#dc2626",
    hover_color="#b91c1c"
)
botao_desfazer.pack(side="left", padx=6)

botao_abrir_pasta = ctk.CTkButton(
    frame_botoes_principais,
    text="Abrir pasta",
    command=abrir_pasta,
    width=175,
    height=40,
    corner_radius=12,
    fg_color="#7c3aed",
    hover_color="#6d28d9"
)
botao_abrir_pasta.pack(side="left", padx=6)

label_log = ctk.CTkLabel(
    frame_principal,
    text="Log de atividades",
    font=ctk.CTkFont(size=14, weight="bold")
)
label_log.pack(anchor="w", padx=28, pady=(4, 6))

frame_log = ctk.CTkFrame(
    frame_principal,
    corner_radius=16,
    fg_color=("#ffffff", "#262626"),
    border_width=1,
    border_color=("#dfe5ec", "#343434")
)
frame_log.pack(fill="both", expand=True, padx=26, pady=(0, 14))

caixa_log = ctk.CTkTextbox(
    frame_log,
    wrap="word",
    font=ctk.CTkFont(family="Consolas", size=12),
    corner_radius=12
)
caixa_log.pack(fill="both", expand=True, padx=10, pady=10)
caixa_log.configure(state="disabled")

frame_progresso = ctk.CTkFrame(
    frame_principal,
    corner_radius=14,
    fg_color=("#eaf0f7", "#2a2a2a")
)
frame_progresso.pack(fill="x", padx=26, pady=(0, 12))

linha_status = ctk.CTkFrame(frame_progresso, fg_color="transparent")
linha_status.pack(fill="x", padx=14, pady=(10, 4))

label_status = ctk.CTkLabel(
    linha_status,
    text="Status: Aguardando ação",
    font=ctk.CTkFont(size=11)
)
label_status.pack(side="left")

linha_progresso = ctk.CTkFrame(frame_progresso, fg_color="transparent")
linha_progresso.pack(fill="x", padx=14, pady=(0, 12))

barra_progresso = ctk.CTkProgressBar(
    linha_progresso,
    height=16,
    corner_radius=10
)
barra_progresso.pack(side="left", fill="x", expand=True)
barra_progresso.set(0)

label_percentual = ctk.CTkLabel(
    linha_progresso,
    text="0%",
    width=45,
    font=ctk.CTkFont(size=11, weight="bold")
)
label_percentual.pack(side="left", padx=(10, 0))

label_rodape = ctk.CTkLabel(
    frame_principal,
    text=f"Organizador de Arquivos • v{VERSAO_APP} • Desenvolvido por Denis",
    font=ctk.CTkFont(size=10)
)
label_rodape.pack(pady=(0, 14))

carregar_historico()
carregar_config()
atualizar_label_pasta()

if historico_movimentos:
    adicionar_log("Histórico carregado. Você ainda pode desfazer a última organização.")

janela.mainloop()
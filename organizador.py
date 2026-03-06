import os
import shutil

pasta = r"D:\Downloads 1"

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

for arquivo in os.listdir(pasta):

    caminho_arquivo = os.path.join(pasta, arquivo)

    if os.path.isfile(caminho_arquivo):

        movido = False

        for pasta_destino, extensoes in tipos.items():

            if any(arquivo.lower().endswith(ext) for ext in extensoes):

                destino = os.path.join(pasta, pasta_destino)

                os.makedirs(destino, exist_ok=True)

                destino_final = os.path.join(destino, arquivo)

                contador = 1

                while os.path.exists(destino_final):

                    nome, extensao = os.path.splitext(arquivo)

                    novo_nome = f"{nome}_{contador}{extensao}"

                    destino_final = os.path.join(destino, novo_nome)

                    contador += 1

                print(f"Movendo {arquivo} para {pasta_destino}")

                shutil.move(caminho_arquivo, destino_final)

                movido = True
                break

        if not movido:

            destino = os.path.join(pasta, "outros")

            os.makedirs(destino, exist_ok=True)

            destino_final = os.path.join(destino, arquivo)

            contador = 1

            while os.path.exists(destino_final):

                nome, extensao = os.path.splitext(arquivo)

                novo_nome = f"{nome}_{contador}{extensao}"

                destino_final = os.path.join(destino, novo_nome)

                contador += 1

            print(f"Movendo {arquivo} para outros")

            shutil.move(caminho_arquivo, destino_final)

print("Arquivos organizados!")
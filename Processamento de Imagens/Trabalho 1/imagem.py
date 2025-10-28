import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from filtros import *
from utils import mostrar_img

def start_image_mode():
    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Arquivos de imagem", "*.jpg *.jpeg *.png *.bmp")]
    )
    if not caminho:
        return

    img = cv2.imread(caminho)
    if img is None:
        messagebox.showerror("Erro", "Não foi possível carregar a imagem.")
        return

    win = tk.Toplevel()
    win.title("Processamento de Imagem")
    win.geometry("500x750")
    win.configure(bg="#ffffff")

    tk.Label(
        win,
        text="Escolha uma operação:",
        font=("Arial", 14, "bold"),
        bg="#ffffff",
        fg="#5e2b97"
    ).pack(pady=15)

    def add_button(text, func):
        btn = tk.Button(
            win,
            text=text,
            width=30,
            height=2,
            bg="#8e44ad",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief="flat",
            command=lambda: func(img)
        )
        btn.pack(pady=6)

    add_button("Converter para níveis de cinza", lambda i: mostrar_img(converter_cinza(i), "Cinza"))
    add_button("Converter para negativo", lambda i: mostrar_img(converter_negativo(i), "Negativo"))
    add_button("Binarizar (Otsu)", lambda i: mostrar_img(binarizar_otsu(i), "Binarizacao"))
    add_button("Filtro média", lambda i: mostrar_img(filtro_media(i), "Filtro Media"))
    add_button("Filtro mediana", lambda i: mostrar_img(filtro_mediana(i), "Filtro Mediana"))
    add_button("Detector de bordas (Canny)", lambda i: mostrar_img(detector_canny(i), "Bordas Canny"))

    add_button("Erosão", erosao_morfologica)
    add_button("Dilatação", dilatacao_morfologica)
    add_button("Abertura", abertura_morfologica)
    add_button("Fechamento", fechamento_morfologico)

    add_button("Exibir Histograma", lambda i: exibir_histograma(i))
    add_button("Calcular área, perímetro, diâmetro", lambda i: calcular_medidas(i))
    add_button("Contar Objetos", lambda i: contagem_objetos(i))

    tk.Button(
        win,
        text="Fechar",
        bg="#ffffff",
        fg="#8e44ad",
        font=("Arial", 10, "bold"),
        relief="solid",
        borderwidth=1,
        command=lambda: (cv2.destroyAllWindows(), win.destroy())
    ).pack(pady=20)

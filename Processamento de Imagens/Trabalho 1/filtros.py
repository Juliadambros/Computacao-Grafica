from tkinter import messagebox
import tkinter as tk
import cv2
import numpy as np
from matplotlib import pyplot as plt
from utils import mostrar_img

def converter_cinza(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def converter_negativo(img):
    return 255 - img

def binarizar_otsu(img):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    gray = cv2.equalizeHist(gray)
    _, binaria = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binaria


def filtro_media(img):
    kernel = np.ones((3,3), np.float32) / 9
    return cv2.filter2D(img, -1, kernel)

def filtro_mediana(img):
    return cv2.medianBlur(img, 3)

def detector_canny(img):
    gray = converter_cinza(img)
    return cv2.Canny(gray, 100, 200)

def erosao_morfologica(img):
    kernel = np.ones((20,20), np.uint8)
    gray = converter_cinza(img)
    resultado = cv2.erode(gray, kernel, iterations=1)
    mostrar_img(resultado, "Erosão")

def dilatacao_morfologica(img):
    kernel = np.ones((20,20), np.uint8)
    gray = converter_cinza(img)
    resultado = cv2.dilate(gray, kernel, iterations=1)
    mostrar_img(resultado, "Dilatação")

def abertura_morfologica(img):
    kernel = np.ones((20,20), np.uint8)
    gray = converter_cinza(img)
    resultado = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    mostrar_img(resultado, "Abertura")

def fechamento_morfologico(img):
    kernel = np.ones((20,20), np.uint8)
    gray = converter_cinza(img)
    resultado = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    mostrar_img(resultado, "Fechamento")


def exibir_histograma(img):
    gray = converter_cinza(img)
    plt.hist(gray.ravel(), 256, [0,256])
    plt.title("Histograma da Imagem")
    plt.show()


def calcular_medidas(img):
    binaria = binarizar_otsu(img)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contornos:
        messagebox.showinfo("Resultados", "Nenhum objeto encontrado.")
        return

    img_resultado = img.copy()
    resultados = []

    for i, c in enumerate(contornos):
        area = cv2.contourArea(c)
        if area < 10:
            continue
        perimetro = cv2.arcLength(c, True)
        x, y, w, h = cv2.boundingRect(c)

        cv2.rectangle(img_resultado, (x, y), (x + w, y + h), (128, 0, 128), 2)

        #idetificação
        numero_x = x + w // 2 - 10
        numero_y = y + h // 2 + 10
        cv2.putText(img_resultado, str(i+1), (numero_x, numero_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv2.LINE_AA)

        resultados.append(f"Objeto {i+1}:\n - Área: {area:.2f} pixels\n - Perímetro: {perimetro:.2f} pixels\n - Largura: {w:.2f} pixels\n - Altura: {h:.2f} pixels\n")

    mostrar_img(img_resultado, "Objetos Identificados")
    
    janela_resultados = tk.Toplevel()
    janela_resultados.title(f"Medidas Geométricas ({len(resultados)} objetos)")
    janela_resultados.geometry("500x400")
    janela_resultados.configure(bg="white")

    frame = tk.Frame(janela_resultados, bg="white")
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                          bg="white", fg="black", font=("Arial", 10),
                          insertbackground="black", borderwidth=0, highlightthickness=0)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=text_widget.yview)
    text_widget.insert(tk.END, "\n".join(resultados))
    text_widget.config(state=tk.DISABLED)

def contagem_objetos(img):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    _, binaria = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    if np.sum(binaria == 255) > np.sum(binaria == 0):
        binaria = cv2.bitwise_not(binaria)

    # Cria imagem de marcação (0 = não visitado, 1 = marcado)
    marcado = np.zeros_like(binaria, dtype=np.uint8)

    altura, largura = binaria.shape
    contador = 0

    vizinhos = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    for y in range(altura):
        for x in range(largura):
            if binaria[y, x] == 255 and marcado[y, x] == 0:
                # Encontrou novo objeto
                contador += 1
                pilha = [(x, y)]

                while pilha:
                    cx, cy = pilha.pop()
                    if cx < 0 or cy < 0 or cx >= largura or cy >= altura:
                        continue
                    if binaria[cy, cx] == 255 and marcado[cy, cx] == 0:
                        marcado[cy, cx] = 1
                        for dx, dy in vizinhos:
                            pilha.append((cx + dx, cy + dy))

    resultado = cv2.cvtColor(binaria, cv2.COLOR_GRAY2BGR)
    resultado[marcado == 1] = [0, 255, 0]

    mostrar_img(resultado, f"Objetos encontrados: {contador}")
    print(f"Quantidade de objetos encontrados: {contador}")



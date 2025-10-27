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

def aplicar_morfologia(img):
    kernel = np.ones((20,20), np.uint8)
    gray = converter_cinza(img)
    erosao = cv2.erode(gray, kernel, iterations=1)
    dilatacao = cv2.dilate(gray, kernel, iterations=1)
    abertura = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    fechamento = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    mostrar_img(erosao, "Erosao")
    mostrar_img(dilatacao, "Dilatacao")
    mostrar_img(abertura, "Abertura")
    mostrar_img(fechamento, "Fechamento")

def exibir_histograma(img):
    gray = converter_cinza(img)
    plt.hist(gray.ravel(), 256, [0,256])
    plt.title("Histograma da Imagem")
    plt.show()

def calcular_medidas(img):
    binaria = binarizar_otsu(img)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contornos:
        area = cv2.contourArea(c)
        perimetro = cv2.arcLength(c, True)
        (x, y), raio = cv2.minEnclosingCircle(c)
        print(f"Área: {area:.2f}, Perímetro: {perimetro:.2f}, Diâmetro: {2*raio:.2f}")

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

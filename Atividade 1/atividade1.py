import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("Atividade 1\PDI_Exercicios_1_Imagens\lena.png")
cv2.imshow('Lena',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

img1 = cv2.imread("Atividade 1\img_aluno.jpeg")
cv2.imshow('Aluno',img1)
cv2.waitKey(0)
cv2.destroyAllWindows()

questao1 = cv2.imread('Atividade 1\PDI_Exercicios_1_Imagens\lena.png', cv2.IMREAD_GRAYSCALE)
cv2.imshow('Niveis de Cinza',questao1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\Lenacinza.jpg',questao1)
questao1_1 = cv2.imread('Atividade 1\img_aluno.jpeg', cv2.IMREAD_GRAYSCALE)
cv2.imshow('Niveis de Cinza',questao1_1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\Alunocinza.jpg',questao1_1)

neg = 255 - img
neg1 = 255 - img1
cv2.imshow('Negativo Lena', neg)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\LenaNegativo.jpeg',neg)
cv2.imshow('Negativo Aluno', neg1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\AlunoNegativo.jpeg',neg1)

questao3 = cv2.normalize(img, None, 0, 100, cv2.NORM_MINMAX)
cv2.imshow('Normalizado Lena', questao3)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\LenaNormalizado.jpeg',questao3)
questao3_1 = cv2.normalize(img1, None, 0, 100, cv2.NORM_MINMAX)
cv2.imshow('Normalizado Aluno', questao3_1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Atividade 1\AlunoNormalizado.jpeg',questao3_1)


lena_pot = np.clip(2 * ((img / 255.0) ** 2) * 255, 0, 255).astype(np.uint8)
cv2.imshow("Lena Potencia", lena_pot)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("Atividade 1/LenaPotencia.jpeg", lena_pot)
aluno_pot = np.clip(2 * ((img1 / 255.0) ** 2) * 255, 0, 255).astype(np.uint8)
cv2.imshow("Aluno Potencia", aluno_pot)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("Atividade 1/AlunoPotencia.jpeg", aluno_pot)

for i in range(8):
    plano = ((questao1 >> i) & 1) * 255
    plano = plano.astype(np.uint8)
    cv2.imshow(f"Lena - Bit {i}", plano)
    cv2.imwrite(f"Atividade 1/Lena_Bit{i}.jpeg", plano)
    cv2.waitKey(0)
cv2.destroyAllWindows()
for i in range(8):
    plano = ((questao1_1 >> i) & 1) * 255
    plano = plano.astype(np.uint8)
    cv2.imshow(f"Aluno - Bit {i}", plano)
    cv2.imwrite(f"Atividade 1/Aluno_Bit{i}.jpeg", plano)
    cv2.waitKey(0)
cv2.destroyAllWindows()

def histograma(img):
    hist = np.zeros(256, dtype=int)
    for valor in img.ravel():   # percorre todos os pixels
        hist[valor] += 1
    return hist
def histograma_normalizado(img):
    hist = histograma(img)
    return hist / hist.sum()
def histograma_acumulado(img):
    hist = histograma(img)
    return np.cumsum(hist)
def histograma_acumulado_normalizado(img):
    hist_norm = histograma_normalizado(img)
    return np.cumsum(hist_norm)
def salvar_histograma(dados, titulo, nome_arquivo, cor='k'):
    plt.figure()
    plt.title(titulo)
    plt.plot(dados, color=cor)
    plt.savefig(nome_arquivo)
    plt.close()

img_uneq = cv2.imread("Atividade 1/PDI_Exercicios_1_Imagens/unequalized.jpg", cv2.IMREAD_GRAYSCALE)
hist_uneq = histograma(img_uneq)
salvar_histograma(hist_uneq, "Histograma - Unequalized Cinza", "Atividade 1/Hist_UnequalizedCinza.png")
img_aluno = cv2.imread("Atividade 1/img_aluno.jpeg")
cores = ('b','g','r')
plt.figure()
for i, cor in enumerate(cores):
    hist = histograma(img_aluno[:,:,i])
    plt.plot(hist, color=cor)
plt.title("Histograma RGB - Aluno")
plt.savefig("Atividade 1/Hist_RGB_Aluno.png")
plt.close()
img_aluno_gray = cv2.cvtColor(img_aluno, cv2.COLOR_BGR2GRAY)
salvar_histograma(histograma(img_aluno_gray), "Histograma (A) - Cinza Aluno", "Atividade 1/Hist_CinzaAluno_A.png")
salvar_histograma(histograma_normalizado(img_aluno_gray), "Histograma Normalizado (B) - Cinza Aluno", "Atividade 1/Hist_CinzaAluno_B.png")
salvar_histograma(histograma_acumulado(img_aluno_gray), "Histograma Acumulado (C) - Cinza Aluno", "Atividade 1/Hist_CinzaAluno_C.png")
salvar_histograma(histograma_acumulado_normalizado(img_aluno_gray), "Histograma Acumulado Normalizado (D) - Cinza Aluno", "Atividade 1/Hist_CinzaAluno_D.png")


lena_gray = cv2.imread("Atividade 1/PDI_Exercicios_1_Imagens/lena.png", cv2.IMREAD_GRAYSCALE)
lena_eq = cv2.equalizeHist(lena_gray)
cv2.imshow("Lena Equalizada", lena_eq)
cv2.imwrite("Atividade 1/LenaEqualizada.jpeg", lena_eq)
cv2.waitKey(0)
cv2.destroyAllWindows()
uneq_eq = cv2.equalizeHist(img_uneq)
cv2.imshow("Unequalized Equalizada", uneq_eq)
cv2.imwrite("Atividade 1/UnequalizedEqualizada.jpeg", uneq_eq)
cv2.waitKey(0)
cv2.destroyAllWindows()
aluno_eq = cv2.equalizeHist(img_aluno_gray)
cv2.imshow("Aluno Equalizado", aluno_eq)
cv2.imwrite("Atividade 1/AlunoEqualizado.jpeg", aluno_eq)
cv2.waitKey(0)
cv2.destroyAllWindows()

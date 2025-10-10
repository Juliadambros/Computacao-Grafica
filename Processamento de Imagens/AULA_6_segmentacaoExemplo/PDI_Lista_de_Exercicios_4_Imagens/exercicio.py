import cv2
import numpy as np
import matplotlib.pyplot as plt

#1
img1 = cv2.imread("imgs/circuito.tif", cv2.IMREAD_GRAYSCALE)
med1 = cv2.medianBlur(img1, 3)
med2 = cv2.medianBlur(med1, 3)
med3 = cv2.medianBlur(med2, 3)

cv2.imshow("Circuito Original", img1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("circuito_original.jpg", img1)

cv2.imshow("Mediana 1", med1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("circuito_mediana1.jpg", med1)

cv2.imshow("Mediana 2", med2)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("circuito_mediana2.jpg", med2)

cv2.imshow("Mediana 3", med3)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("circuito_mediana3.jpg", med3)


#2
img2 = cv2.imread("imgs/pontos.png", cv2.IMREAD_GRAYSCALE)
kernel = np.array([[0,-1,0],[-1,8,-1],[0,-1,0]], dtype=np.float32)
resp = cv2.filter2D(img2, -1, kernel)
_, pontos = cv2.threshold(resp, 200, 255, cv2.THRESH_BINARY)

cv2.imshow("Pontos Originais", img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("pontos_original.jpg", img2)

cv2.imshow("Pontos Detectados", pontos)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("pontos_detectados.jpg", pontos)


#3
img3 = cv2.imread("imgs/linhas.png", cv2.IMREAD_GRAYSCALE)

kh = np.array([[-1,-1,-1],[2,2,2],[-1,-1,-1]], np.float32)   # horizontal
kv = kh.T                                                    # vertical
kd1 = np.array([[2,-1,-1],[-1,2,-1],[-1,-1,2]], np.float32)  # diagonal \
kd2 = np.array([[-1,-1,2],[-1,2,-1],[2,-1,-1]], np.float32)  # diagonal /

resp_h = cv2.filter2D(img3, -1, kh)
resp_v = cv2.filter2D(img3, -1, kv)
resp_d1 = cv2.filter2D(img3, -1, kd1)
resp_d2 = cv2.filter2D(img3, -1, kd2)

_, bh = cv2.threshold(resp_h, 80, 255, cv2.THRESH_BINARY)
_, bv = cv2.threshold(resp_v, 80, 255, cv2.THRESH_BINARY)
_, bd1 = cv2.threshold(resp_d1, 80, 255, cv2.THRESH_BINARY)
_, bd2 = cv2.threshold(resp_d2, 80, 255, cv2.THRESH_BINARY)

final = cv2.bitwise_or(cv2.bitwise_or(bh, bv), cv2.bitwise_or(bd1, bd2))

cv2.imshow("Linhas Original", img3)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("linhas_original.jpg", img3)

cv2.imshow("Linhas Detectadas", final)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("linhas_detectadas.jpg", final)


#4
img4 = cv2.imread("imgs/igreja.png", cv2.IMREAD_GRAYSCALE)
canny = cv2.Canny(img4, 100, 200)

cv2.imshow("Igreja Original", img4)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("igreja_original.jpg", img4)

cv2.imshow("Igreja Canny", canny)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("igreja_canny.jpg", canny)


#5
def region_growing(img, seed, tol=15):
    h, w = img.shape
    seed_val = int(img[seed[1], seed[0]])
    mask = np.zeros_like(img, np.uint8)
    stack = [seed]
    while stack:
        x, y = stack.pop()
        if mask[y, x] == 0 and abs(int(img[y, x]) - seed_val) <= tol:
            mask[y, x] = 255
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        stack.append((nx, ny))
    return mask

img5_color = cv2.imread("imgs/root.jpg")
img5_gray = cv2.cvtColor(img5_color, cv2.COLOR_BGR2GRAY)


seed = (50, 50)  
mask = region_growing(img5_gray, seed, tol=18)
highlight = img5_color.copy()
highlight[mask==255] = [0,0,255]

cv2.imshow("Root Original", img5_color)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("root_original.jpg", img5_color)

cv2.imshow("Root Segmentada", highlight)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("root_segmentada.jpg", highlight)


#6
arquivos = ["harewood.jpg", "nuts.jpg", "snow.jpg", "img_aluno.jpeg"]
for arq in arquivos:
    img6 = cv2.imread("imgs/"+arq, cv2.IMREAD_GRAYSCALE) \
           if arq != "img_aluno.jpeg" else cv2.imread(arq, cv2.IMREAD_GRAYSCALE)
    if img6 is None: 
        continue
    _, otsu = cv2.threshold(img6, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    cv2.imshow(f"{arq} Original", img6)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite(arq.replace(".jpg","")+"_original.jpg", img6)

    cv2.imshow(f"{arq} Otsu", otsu)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite(arq.replace(".jpg","")+"_otsu.jpg", otsu)
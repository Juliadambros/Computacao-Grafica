import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

def exercicio2():
    img = cv.imread('quadrados.png', cv.IMREAD_GRAYSCALE)
   
    _, binary = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

    kernel = cv.getStructuringElement(cv.MORPH_RECT, (45, 45))
    eroded = cv.erode(binary, kernel)
    dilated = cv.dilate(eroded, kernel)

    cv.imwrite('resultados/ex2_original.png', img)
    cv.imwrite('resultados/ex2_erosao.png', eroded)
    cv.imwrite('resultados/ex2_dilatacao.png', dilated)

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1), plt.imshow(img, cmap='gray'), plt.title('Original')
    plt.subplot(1, 3, 2), plt.imshow(eroded, cmap='gray'), plt.title('Após Erosão')
    plt.subplot(1, 3, 3), plt.imshow(dilated, cmap='gray'), plt.title('Após Dilatação')
    plt.show()

def abertura_manual(img, kernel):
    eroded = cv.erode(img, kernel)
    opened = cv.dilate(eroded, kernel)
    return opened

def fechamento_manual(img, kernel):
    dilated = cv.dilate(img, kernel)
    closed = cv.erode(dilated, kernel)
    return closed

def exercicio3():
    img = cv.imread('ruidos.png', cv.IMREAD_GRAYSCALE)

    _, binary = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    opened = abertura_manual(binary, kernel)
    closed = fechamento_manual(binary, kernel)

    cv.imwrite('resultados/ex3_original.png', img)
    cv.imwrite('resultados/ex3_abertura.png', opened)
    cv.imwrite('resultados/ex3_fechamento.png', closed)

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1), plt.imshow(binary, cmap='gray'), plt.title('Original Binária')
    plt.subplot(1, 3, 2), plt.imshow(opened, cmap='gray'), plt.title('Abertura (sem ruídos fundo)')
    plt.subplot(1, 3, 3), plt.imshow(closed, cmap='gray'), plt.title('Fechamento (sem ruídos objeto)')
    plt.show()

def extrair_fronteiras(img):
    kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))

    eroded = cv.erode(img, kernel)
    bordas_internas = cv.subtract(img, eroded)
    
    dilated = cv.dilate(img, kernel)
    bordas_externas = cv.subtract(dilated, img)
    
    return bordas_internas, bordas_externas

def exercicio4():
    img = cv.imread('cachorro.png', cv.IMREAD_GRAYSCALE)
    
    _, binary = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

    bordas_internas, bordas_externas = extrair_fronteiras(binary)

    cv.imwrite('resultados/ex4_original.png', img)
    cv.imwrite('resultados/ex4_bordas_internas.png', bordas_internas)
    cv.imwrite('resultados/ex4_bordas_externas.png', bordas_externas)
    
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1), plt.imshow(binary, cmap='gray'), plt.title('Original')
    plt.subplot(1, 3, 2), plt.imshow(bordas_internas, cmap='gray'), plt.title('Bordas Internas')
    plt.subplot(1, 3, 3), plt.imshow(bordas_externas, cmap='gray'), plt.title('Bordas Externas')
    plt.show()

def preenchimento_regiao(img, ponto_semente):
    h, w = img.shape
    mask = np.zeros((h+2, w+2), np.uint8)
   
    flags = 4 | (255 << 8) | cv.FLOODFILL_FIXED_RANGE
    _, img_preenchida, _, _ = cv.floodFill(img.copy(), mask, ponto_semente, 255, loDiff=10, upDiff=10, flags=flags)
    
    return img_preenchida

def exercicio5():
    img = cv.imread('gato.png', cv.IMREAD_GRAYSCALE)

    if np.mean(img) > 127:  
        img = cv.bitwise_not(img)
    
    h, w = img.shape
    ponto_semente = (w//2, h//2)
   
    img_preenchida = preenchimento_regiao(img, ponto_semente)

    cv.imwrite('resultados/ex5_original.png', img)
    cv.imwrite('resultados/ex5_preenchida.png', img_preenchida)
   
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1), plt.imshow(img, cmap='gray'), plt.title('Original')
    plt.subplot(1, 2, 2), plt.imshow(img_preenchida, cmap='gray'), plt.title('Região Preenchida')
    plt.show()

def extrair_componente_conectado(img, ponto_inicial):
    h, w = img.shape
    mask = np.zeros((h+2, w+2), np.uint8)
 
    _, componente, _, _ = cv.floodFill(img.copy(), mask, ponto_inicial, 255)
    
    img_colorida = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    img_colorida[componente == 255] = [0, 255, 255]  
    
    return componente, img_colorida

def exercicio6():
    img = cv.imread("quadrados.png", cv.IMREAD_GRAYSCALE)
    _, bin_img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    
    if np.mean(bin_img) > 127:
        bin_img = cv.bitwise_not(bin_img)
        print("Imagem invertida: objetos brancos sobre fundo preto")
    
 
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(bin_img)
    
    print(f"Encontrados {num_labels - 1} componentes conectados (excluindo fundo)")
    
    if num_labels > 1:
        idx = 1 + np.argmax(stats[1:, cv.CC_STAT_AREA])
        
        
        mask = np.zeros_like(bin_img)
        mask[labels == idx] = 255
        color_img = cv.cvtColor(bin_img, cv.COLOR_GRAY2BGR)
        color_img[labels == idx] = [0, 255, 255]  
        area = stats[idx, cv.CC_STAT_AREA]
        width = stats[idx, cv.CC_STAT_WIDTH]
        height = stats[idx, cv.CC_STAT_HEIGHT]
        print(f"Maior componente: área={area}, largura={width}, altura={height}")
    
        cv.imwrite('resultados/ex6_original.png', bin_img)
        cv.imwrite('resultados/ex6_mascara.png', mask)
        cv.imwrite('resultados/ex6_amarelo.png', color_img)
        
        plt.figure(figsize=(15, 5))
        plt.subplot(1, 3, 1), plt.imshow(bin_img, cmap='gray'), plt.title('Original Binária')
        plt.subplot(1, 3, 2), plt.imshow(mask, cmap='gray'), plt.title(f'Máscara (Área: {area})')
        plt.subplot(1, 3, 3), plt.imshow(cv.cvtColor(color_img, cv.COLOR_BGR2RGB)), plt.title('Maior Quadrado em Amarelo')
        plt.show()
        
        cv.imshow("Ex6 - Maior Componente (80px)", color_img)
        cv.waitKey(2000) 
        cv.destroyAllWindows()
        
    else:
        print("Nenhum componente encontrado além do fundo")

def gradiente_morfologico(img):
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    
    dilated = cv.dilate(img, kernel)
    eroded = cv.erode(img, kernel)
    
    gradient = cv.subtract(dilated, eroded)
    return gradient

def exercicio7():
    img = cv.imread('img_aluno.jpeg', cv.IMREAD_GRAYSCALE)

    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
    dilated = cv.dilate(img, kernel)
    eroded = cv.erode(img, kernel)
    gradient = gradiente_morfologico(img)
    
    cv.imwrite('resultados/ex7_original.png', img)
    cv.imwrite('resultados/ex7_dilatacao.png', dilated)
    cv.imwrite('resultados/ex7_erosao.png', eroded)
    cv.imwrite('resultados/ex7_gradiente.png', gradient)
    
    plt.figure(figsize=(15, 10))
    plt.subplot(2, 2, 1), plt.imshow(img, cmap='gray'), plt.title('Original')
    plt.subplot(2, 2, 2), plt.imshow(dilated, cmap='gray'), plt.title('Dilatação')
    plt.subplot(2, 2, 3), plt.imshow(eroded, cmap='gray'), plt.title('Erosão')
    plt.subplot(2, 2, 4), plt.imshow(gradient, cmap='gray'), plt.title('Gradiente Morfológico')
    plt.show()

def main():
    import os
    if not os.path.exists('resultados'):
        os.makedirs('resultados')
    
    exercicio2()
    exercicio3()
    exercicio4()
    exercicio5()
    exercicio6()
    exercicio7()

if __name__ == "__main__":
    main()
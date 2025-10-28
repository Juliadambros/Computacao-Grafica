import cv2
import numpy as np
from tkinter import filedialog
import pygame

stop_video = False  

def start_video_mode():
    global stop_video
    stop_video = False

    video_path = filedialog.askopenfilename(title="Selecione o vídeo")
    audio_path = filedialog.askopenfilename(title="Selecione o áudio")
    ref_paths = filedialog.askopenfilenames(title="Selecione imagens de referência da garrafa")

    if not video_path or not audio_path or not ref_paths:
        print("Seleção cancelada")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)

    orb = cv2.ORB_create(nfeatures=1500)
    ref_kp_des = []
    for path in ref_paths:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            kp, des = orb.detectAndCompute(img, None) #pontos e vetores
            ref_kp_des.append((img, kp, des))

    bf = cv2.BFMatcher(cv2.NORM_HAMMING) #comparação
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo")
        return

    while True:
        if stop_video:
            break

        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_frame, des_frame = orb.detectAndCompute(frame_gray, None)

        garrafa_detectada = False
        if des_frame is not None and len(kp_frame) > 0:
            for ref_img, kp_ref, des_ref in ref_kp_des:
                if des_ref is None:
                    continue

                matches = bf.knnMatch(des_ref, des_frame, k=2)
                good_matches = [m for m,n in matches if m.distance < 0.75*n.distance]

                if len(good_matches) > 15:
                    garrafa_detectada = True
                    src_pts = np.float32([kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
                    dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0) #trasformação geometrica
                    if M is not None:
                        h, w = ref_img.shape
                        pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
                        dst = cv2.perspectiveTransform(pts, M)
                        frame = cv2.polylines(frame, [np.int32(dst)], True, (0,255,0), 2)
                    break

        if garrafa_detectada and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        elif not garrafa_detectada and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        cv2.imshow("Deteccao de Garrafa", frame)
        if cv2.waitKey(30) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()

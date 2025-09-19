import cv2

# Tenta abrir a câmera
cap = cv2.VideoCapture(0)

print("Câmera aberta com sucesso! Pressione 'q' para sair.")

# Loop infinito para capturar o vídeo
while True:
    ret, frame = cap.read()  # Lê o frame da câmera
    
    # Verifica se o frame foi capturado corretamente
    if not ret:
        print("Erro: Não foi possível capturar o frame!")
        break
    
    cv2.imshow('Câmera', frame)  # Mostra o frame na janela
    
    # Espera a tecla 'q' ser pressionada para sair do loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()
print("Programa finalizado.")
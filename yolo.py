import cv2
from ultralytics import YOLO

# Carrega o modelo YOLO pré-treinado
model = YOLO("yolo11n.pt")

# Tenta abrir a câmera
cap = cv2.VideoCapture(0)

# Verifica se a câmera foi aberta com sucesso
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera!")
    print("Verifique se:")
    print("1. A câmera está conectada")
    print("2. Outros aplicativos não estão usando a câmera")
    print("3. As permissões de câmera estão habilitadas nas Preferências do Sistema")
    exit()

print("Câmera aberta com sucesso! Pressione 'q' para sair.")
print("Processando detecção de objetos em tempo real...")

# Loop infinito para capturar o vídeo
while True:
    ret, frame = cap.read()  # Lê o frame da câmera
    
    # Verifica se o frame foi capturado corretamente
    if not ret:
        print("Erro: Não foi possível capturar o frame!")
        break
    
    # Aplica a detecção YOLO no frame
    results = model.predict(frame, conf=0.5, verbose=False)
    
    # Processa os resultados da detecção
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Obtém as coordenadas da caixa delimitadora
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Obtém a confiança e classe
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                
                # Desenha a caixa delimitadora
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Adiciona o texto com classe e confiança
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Imprime informações no console
                print(f"Detectado: {class_name} - Confiança: {conf:.2f}")
    
    # Mostra o frame processado na janela
    cv2.imshow('Câmera com YOLO', frame)
    
    # Espera a tecla 'q' ser pressionada para sair do loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()
print("Programa finalizado.") 
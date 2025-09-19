import cv2
from ultralytics import YOLO
import ifcopenshell
import numpy as np
import os

# 1. Carrega o modelo YOLO
try:
    model = YOLO("yolov8n.pt")  # Usando o arquivo YOLO disponível
    print("Modelo YOLO carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar modelo YOLO: {e}")
    exit(1)

# 2. Carrega o arquivo BIM (IFC) ou cria dados simulados
bim_data = None
ifc_file = "metro_sp.ifc"
json_file = "metrosp.json"

# Tenta carregar arquivo IFC primeiro
if os.path.exists(ifc_file):
    try:
        bim_model = ifcopenshell.open(ifc_file)
        walls = bim_model.by_type("IfcWall")
        beams = bim_model.by_type("IfcBeam")
        print(f"Arquivo IFC carregado: {len(walls)} paredes, {len(beams)} vigas")
        bim_data = {"walls": walls, "beams": beams, "type": "ifc"}
    except Exception as e:
        print(f"Erro ao carregar arquivo IFC: {e}")
        bim_data = None

# Se não conseguiu carregar IFC, tenta JSON
elif os.path.exists(json_file):
    try:
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            json_bim = json.load(f)
        
        # Converte dados JSON para formato compatível
        walls = []
        beams = []
        
        for wall in json_bim['elements']['walls']:
            # Cria objeto simulado de parede
            wall_obj = type('Wall', (), {
                'Geometry': [(wall['geometry']['start'][0], wall['geometry']['start'][1]),
                           (wall['geometry']['end'][0], wall['geometry']['end'][1])],
                'Name': wall['name'],
                'properties': wall['properties']
            })()
            walls.append(wall_obj)
        
        for beam in json_bim['elements']['beams']:
            # Cria objeto simulado de viga
            beam_obj = type('Beam', (), {
                'Geometry': [(beam['geometry']['start'][0], beam['geometry']['start'][1]),
                           (beam['geometry']['end'][0], beam['geometry']['end'][1])],
                'Name': beam['name'],
                'properties': beam['properties']
            })()
            beams.append(beam_obj)
        
        print(f"Arquivo JSON carregado: {len(walls)} paredes, {len(beams)} vigas")
        bim_data = {"walls": walls, "beams": beams, "type": "json", "raw_data": json_bim}
        
    except Exception as e:
        print(f"Erro ao carregar arquivo JSON: {e}")
        bim_data = None

# Se nenhum arquivo encontrado, usa dados simulados
else:
    print(f"Arquivos IFC '{ifc_file}' e JSON '{json_file}' não encontrados. Usando dados simulados.")
    print("Dica: Execute 'python simple_bim_generator.py' para criar dados BIM")
    
    # Dados simulados para teste
    bim_data = {
        "walls": [
            {"Geometry": [(100, 100), (300, 100), (300, 200), (100, 200)]},
            {"Geometry": [(400, 150), (600, 150), (600, 250), (400, 250)]}
        ],
        "beams": [
            {"Geometry": [(200, 150), (500, 150)]},
            {"Geometry": [(150, 300), (450, 300)]}
        ],
        "type": "simulated"
    }

# 3. Função para calcular distância entre objetos detectados e BIM
def calculate_deviation(detected_pos, bim_pos, tolerance=50):
    """
    Calcula desvio entre posição detectada e posição no BIM
    tolerance: tolerância em pixels
    """
    deviation = np.linalg.norm(np.array(detected_pos) - np.array(bim_pos))
    if deviation > tolerance:
        return f"ALERTA: Desvio de {deviation:.1f}px!"
    return None

# 4. Função para calcular porcentagem de conformidade
def calculate_compliance_percentage(detections, bim_data):
    """Calcula porcentagem de conformidade entre BIM e detecções"""
    if not detections or not bim_data:
        return 0.0
    
    total_deviation = 0
    total_elements = 0
    matched_elements = 0
    
    for det in detections:
        class_name = det['class'].lower()
        detected_pos = det['position']
        confidence = det['confidence']
        
        # Procura elemento correspondente no BIM
        element_found = False
        
        # Verifica paredes
        if "walls" in bim_data:
            for wall in bim_data["walls"]:
                if 'wall' in class_name or 'parede' in class_name or 'person' in class_name:
                    if bim_data['type'] == 'json' and 'raw_data' in bim_data:
                        # Para dados JSON
                        for json_wall in bim_data['raw_data']['elements']['walls']:
                            if 'expected_position' in json_wall:
                                expected_pos = json_wall['expected_position']
                                deviation = np.linalg.norm(np.array(expected_pos) - np.array(detected_pos))
                                total_deviation += deviation
                                total_elements += 1
                                matched_elements += 1
                                element_found = True
                                break
                    else:
                        # Para dados simulados
                        geom = wall["Geometry"]
                        expected_pos = ((geom[0][0] + geom[2][0]) / 2, (geom[0][1] + geom[2][1]) / 2)
                        deviation = np.linalg.norm(np.array(expected_pos) - np.array(detected_pos))
                        total_deviation += deviation
                        total_elements += 1
                        matched_elements += 1
                        element_found = True
                        break
        
        # Verifica vigas
        if not element_found and "beams" in bim_data:
            for beam in bim_data["beams"]:
                if 'beam' in class_name or 'viga' in class_name or 'chair' in class_name:
                    if bim_data['type'] == 'json' and 'raw_data' in bim_data:
                        # Para dados JSON
                        for json_beam in bim_data['raw_data']['elements']['beams']:
                            if 'expected_position' in json_beam:
                                expected_pos = json_beam['expected_position']
                                deviation = np.linalg.norm(np.array(expected_pos) - np.array(detected_pos))
                                total_deviation += deviation
                                total_elements += 1
                                matched_elements += 1
                                element_found = True
                                break
                    else:
                        # Para dados simulados
                        geom = beam["Geometry"]
                        expected_pos = ((geom[0][0] + geom[1][0]) / 2, (geom[0][1] + geom[1][1]) / 2)
                        deviation = np.linalg.norm(np.array(expected_pos) - np.array(detected_pos))
                        total_deviation += deviation
                        total_elements += 1
                        matched_elements += 1
                        element_found = True
                        break
        
        # Se não encontrou correspondência, conta como elemento extra
        if not element_found:
            total_elements += 1
    
    if total_elements == 0:
        return 0.0
    
    # Calcula porcentagem de conformidade
    avg_deviation = total_deviation / total_elements if total_deviation > 0 else 0
    max_acceptable_deviation = 150  # pixels
    
    # Fatores de conformidade
    position_compliance = max(0, 100 - (avg_deviation / max_acceptable_deviation) * 100)
    detection_compliance = (matched_elements / total_elements) * 100
    
    # Conformidade final (média ponderada)
    final_compliance = (position_compliance * 0.7) + (detection_compliance * 0.3)
    
    return max(0, min(100, final_compliance))

# 5. Função para obter posição do BIM (simulada ou real)
def get_bim_position(element_type, index=0):
    """Obtém posição de um elemento do BIM"""
    if bim_data is None:
        return None
    
    if element_type == "beam" and "beams" in bim_data:
        if index < len(bim_data["beams"]):
            beam = bim_data["beams"][index]
            if bim_data["type"] == "ifc":
                # Para arquivo IFC real
                return (beam.Geometry[0][0], beam.Geometry[0][1])
            else:
                # Para dados simulados
                geom = beam["Geometry"]
                return ((geom[0][0] + geom[1][0]) / 2, (geom[0][1] + geom[1][1]) / 2)
    
    elif element_type == "wall" and "walls" in bim_data:
        if index < len(bim_data["walls"]):
            wall = bim_data["walls"][index]
            if bim_data["type"] == "ifc":
                # Para arquivo IFC real
                return (wall.Geometry[0][0], wall.Geometry[0][1])
            else:
                # Para dados simulados
                geom = wall["Geometry"]
                return ((geom[0][0] + geom[2][0]) / 2, (geom[0][1] + geom[2][1]) / 2)
    
    return None

# 5. Captura de vídeo
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera!")
    exit(1)

print("Pressione 'q' para sair, 's' para salvar screenshot")

# Contadores para estatísticas
detection_count = 0
alert_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao ler frame da câmera")
        break

    # Detecta objetos com YOLO
    try:
        results = model.predict(frame, conf=0.5, verbose=False)
    except Exception as e:
        print(f"Erro na detecção YOLO: {e}")
        continue

    # Lista para armazenar informações de detecção
    detection_info = []
    current_detections = 0

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            class_name = model.names[cls]
            confidence = float(box.conf[0])
            current_detections += 1

            # Desenha a caixa no frame
            color = (0, 255, 0)  # Verde
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # --- COMPARAÇÃO COM O BIM ---
            detected_pos = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            # Verifica diferentes tipos de objetos
            analysis_result = "Sem correspondência BIM"
            alert_message = None
            
            for obj_type in ["beam", "wall", "person", "chair"]:
                if class_name.lower() in obj_type or obj_type in class_name.lower():
                    bim_pos = get_bim_position(obj_type, 0)
                    if bim_pos:
                        alert = calculate_deviation(detected_pos, bim_pos)
                        if alert:
                            alert_count += 1
                            alert_message = alert
                            analysis_result = f"DESVIO: {alert}"
                            cv2.putText(frame, alert, (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        else:
                            analysis_result = f"OK - {obj_type} conforme BIM"
                    else:
                        analysis_result = f"Detectado: {class_name} (sem dados BIM)"
                    break
            
            # Adiciona informação de análise à lista
            detection_info.append({
                "class": class_name,
                "confidence": confidence,
                "position": detected_pos,
                "analysis": analysis_result,
                "alert": alert_message
            })

    # Calcula porcentagem de conformidade
    compliance_percentage = calculate_compliance_percentage(detection_info, bim_data)
    
    # Determina cor e status baseado na conformidade
    if compliance_percentage >= 80:
        compliance_color = (0, 255, 0)  # Verde
        compliance_status = "EXCELENTE"
    elif compliance_percentage >= 60:
        compliance_color = (0, 255, 255)  # Amarelo
        compliance_status = "BOM"
    elif compliance_percentage >= 40:
        compliance_color = (0, 165, 255)  # Laranja
        compliance_status = "REGULAR"
    else:
        compliance_color = (0, 0, 255)  # Vermelho
        compliance_status = "CRÍTICO"

    # Exibe informações na tela
    y_offset = 30
    cv2.putText(frame, "BIM + YOLO Integration", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    y_offset += 30
    
    cv2.putText(frame, f"BIM: {bim_data['type'] if bim_data else 'N/A'}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    y_offset += 25
    
    # Informações de conformidade
    cv2.putText(frame, f"Conformidade: {compliance_percentage:.1f}%", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, compliance_color, 2)
    y_offset += 25
    
    cv2.putText(frame, f"Status: {compliance_status}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, compliance_color, 1)
    y_offset += 25
    
    cv2.putText(frame, f"Detecções: {current_detections} | Total: {detection_count} | Alertas: {alert_count}", 
               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    y_offset += 25

    # Barra de progresso visual da conformidade
    bar_width = 300
    bar_height = 15
    bar_x, bar_y = 10, y_offset
    
    # Fundo da barra
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                 (100, 100, 100), -1)
    
    # Preenchimento da barra
    fill_width = int((compliance_percentage / 100) * bar_width)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                 compliance_color, -1)
    
    # Borda da barra
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                 (255, 255, 255), 1)
    
    y_offset += 30

    # Exibe informações de cada detecção
    for i, info in enumerate(detection_info):
        if y_offset < frame.shape[0] - 50:  # Evita sair da tela
            color = (0, 0, 255) if info["alert"] else (0, 255, 0)
            text = f"{i+1}. {info['class']} ({info['confidence']:.2f}) - {info['analysis']}"
            cv2.putText(frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            y_offset += 20

    # Imprime informações no console também
    if detection_info:
        print(f"\n--- Frame {detection_count} ---")
        print(f"Conformidade BIM: {compliance_percentage:.1f}% - Status: {compliance_status}")
        for i, info in enumerate(detection_info):
            status = "⚠️ ALERTA" if info["alert"] else "✅ OK"
            print(f"{status} {info['class']} (conf: {info['confidence']:.2f}) - {info['analysis']}")
    else:
        print(f"\n--- Frame {detection_count} ---")
        print(f"Conformidade BIM: {compliance_percentage:.1f}% - Status: {compliance_status}")
        print("Nenhuma detecção neste frame")
    
    detection_count += 1

    cv2.imshow("BIM + YOLO Integration", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite("bim_yolo_screenshot.jpg", frame)
        print("Screenshot salvo como 'bim_yolo_screenshot.jpg'")

cap.release()
cv2.destroyAllWindows()
print(f"\nPrograma finalizado. Total de frames: {detection_count}, Alertas: {alert_count}")





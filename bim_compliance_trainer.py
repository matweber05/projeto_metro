import cv2
import numpy as np
import json
import os
from ultralytics import YOLO
import pickle
from datetime import datetime

class BIMComplianceTrainer:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.training_data = []
        self.bim_data = None
        self.load_bim_data()
        
    def load_bim_data(self):
        """Carrega dados BIM do arquivo JSON"""
        try:
            with open("metrosp.json", 'r', encoding='utf-8') as f:
                self.bim_data = json.load(f)
            print("Dados BIM carregados com sucesso!")
        except FileNotFoundError:
            print("Arquivo BIM não encontrado. Criando dados padrão...")
            self.create_default_bim()
    
    def create_default_bim(self):
        """Cria dados BIM padrão se não existir"""
        self.bim_data = {
            "project": {
                "name": "Projeto Metro SP",
                "description": "Projeto de exemplo para treinamento",
                "version": "1.0"
            },
            "elements": {
                "walls": [
                    {
                        "id": "wall_1",
                        "name": "Parede Norte",
                        "geometry": {"start": [100, 100], "end": [400, 100]},
                        "expected_position": [250, 100]
                    },
                    {
                        "id": "wall_2",
                        "name": "Parede Leste", 
                        "geometry": {"start": [400, 100], "end": [400, 300]},
                        "expected_position": [400, 200]
                    }
                ],
                "beams": [
                    {
                        "id": "beam_1",
                        "name": "Viga Norte",
                        "geometry": {"start": [150, 150], "end": [350, 150]},
                        "expected_position": [250, 150]
                    }
                ]
            }
        }
        
        # Salva o arquivo
        with open("metrosp.json", 'w', encoding='utf-8') as f:
            json.dump(self.bim_data, f, indent=2)
        print("Arquivo BIM padrão criado: metrosp.json")
    
    def calculate_compliance_percentage(self, detections):
        """Calcula porcentagem de conformidade entre BIM e detecções"""
        if not detections:
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
            for wall in self.bim_data['elements']['walls']:
                if 'wall' in class_name or 'parede' in class_name or 'person' in class_name:
                    expected_pos = wall['expected_position']
                    deviation = np.linalg.norm(np.array(expected_pos) - np.array(detected_pos))
                    total_deviation += deviation
                    total_elements += 1
                    matched_elements += 1
                    element_found = True
                    break
            
            # Verifica vigas
            if not element_found:
                for beam in self.bim_data['elements']['beams']:
                    if 'beam' in class_name or 'viga' in class_name or 'chair' in class_name:
                        expected_pos = beam['expected_position']
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
    
    def collect_training_data(self):
        """Coleta dados de treinamento da câmera"""
        print("=== COLETA DE DADOS DE TREINAMENTO ===")
        print("Pressione 'c' para capturar dados")
        print("Pressione 'q' para sair")
        print("Pressione 's' para salvar dados")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro: Não foi possível abrir a câmera!")
            return
        
        sample_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detecta objetos
            results = self.model.predict(frame, conf=0.5, verbose=False)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls]
                    confidence = float(box.conf[0])
                    position = ((x1 + x2) / 2, (y1 + y2) / 2)
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'position': position
                    })
                    
                    # Desenha caixa
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                               (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Calcula conformidade atual
            current_compliance = self.calculate_compliance_percentage(detections)
            
            # Mostra informações na tela
            cv2.putText(frame, f"Amostras: {sample_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Conformidade: {current_compliance:.1f}%", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Pressione 'c' para capturar", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Coleta de Dados", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Captura dados
                self.training_data.append({
                    'compliance': current_compliance,
                    'timestamp': datetime.now().isoformat(),
                    'detections': detections,
                    'detection_count': len(detections)
                })
                
                sample_count += 1
                print(f"Amostra {sample_count} capturada - Conformidade: {current_compliance:.1f}%")
                
            elif key == ord('s'):
                if sample_count > 0:
                    print(f"\nSalvando {sample_count} amostras...")
                    self.save_training_data()
                    break
                else:
                    print("Nenhuma amostra coletada ainda!")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def save_training_data(self):
        """Salva dados de treinamento"""
        with open("metrosp.json", 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, indent=2, ensure_ascii=False)
        print("Dados de treinamento salvos em: metrosp.json")
        
        # Calcula estatísticas
        if self.training_data:
            compliances = [sample['compliance'] for sample in self.training_data]
            avg_compliance = np.mean(compliances)
            min_compliance = np.min(compliances)
            max_compliance = np.max(compliances)
            
            print(f"\nEstatísticas dos dados coletados:")
            print(f"  - Média de conformidade: {avg_compliance:.1f}%")
            print(f"  - Mínima: {min_compliance:.1f}%")
            print(f"  - Máxima: {max_compliance:.1f}%")
            print(f"  - Total de amostras: {len(self.training_data)}")
    
    def load_training_data(self):
        """Carrega dados de treinamento existentes"""
        try:
            with open("metrosp.json", 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)   
            print(f"Dados de treinamento carregados: {len(self.training_data)} amostras")
            return True
        except FileNotFoundError:
            print("Nenhum dado de treinamento encontrado")
            return False
    
    def test_real_time_prediction(self):
        """Testa predição de conformidade em tempo real"""
        print("=== TESTE DE CONFORMIDADE EM TEMPO REAL ===")
        print("Pressione 'q' para sair")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro: Não foi possível abrir a câmera!")
            return
        
        frame_count = 0
        compliance_history = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detecta objetos
            results = self.model.predict(frame, conf=0.5, verbose=False)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls]
                    confidence = float(box.conf[0])
                    position = ((x1 + x2) / 2, (y1 + y2) / 2)
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'position': position
                    })
                    
                    # Desenha caixa
                    color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                               (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Calcula conformidade
            compliance = self.calculate_compliance_percentage(detections)
            compliance_history.append(compliance)
            
            # Mantém apenas os últimos 30 frames para média móvel
            if len(compliance_history) > 30:
                compliance_history.pop(0)
            
            avg_compliance = np.mean(compliance_history) if compliance_history else 0
            
            # Determina cor baseada na conformidade
            if compliance >= 80:
                color = (0, 255, 0)  # Verde
                status = "EXCELENTE"
            elif compliance >= 60:
                color = (0, 255, 255)  # Amarelo
                status = "BOM"
            elif compliance >= 40:
                color = (0, 165, 255)  # Laranja
                status = "REGULAR"
            else:
                color = (0, 0, 255)  # Vermelho
                status = "CRÍTICO"
            
            # Desenha informações na tela
            cv2.putText(frame, f"Conformidade BIM: {compliance:.1f}%", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Status: {status}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Média (30f): {avg_compliance:.1f}%", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Detecções: {len(detections)}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Barra de progresso visual
            bar_width = 300
            bar_height = 20
            bar_x, bar_y = 10, 140
            
            # Fundo da barra
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (100, 100, 100), -1)
            
            # Preenchimento da barra
            fill_width = int((compliance / 100) * bar_width)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                         color, -1)
            
            # Borda da barra
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (255, 255, 255), 2)
            
            cv2.imshow("Conformidade BIM em Tempo Real", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Mostra estatísticas finais
        if compliance_history:
            print(f"\nEstatísticas da sessão:")
            print(f"  - Frames processados: {frame_count}")
            print(f"  - Conformidade média: {np.mean(compliance_history):.1f}%")
            print(f"  - Conformidade mínima: {np.min(compliance_history):.1f}%")
            print(f"  - Conformidade máxima: {np.max(compliance_history):.1f}%")

def main():
    trainer = BIMComplianceTrainer()
    
    print("=== SISTEMA DE CONFORMIDADE BIM ===")
    print("1. Coletar dados de treinamento")
    print("2. Carregar dados existentes")
    print("3. Testar conformidade em tempo real")
    
    choice = input("Escolha uma opção (1-3): ")
    
    if choice == "1":
        trainer.collect_training_data()
    elif choice == "2":
        trainer.load_training_data()
    elif choice == "3":
        trainer.test_real_time_prediction()
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main() 
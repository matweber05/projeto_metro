import json
import numpy as np

def create_simple_bim_data():
    """Cria dados BIM simples em formato JSON"""
    
    bim_data = {
        "project": {
            "name": "Projeto Metro SP",
            "description": "Projeto de exemplo para integração BIM + YOLO",
            "version": "1.0"
        },
        "elements": {
            "walls": [
                {
                    "id": "wall_1",
                    "name": "Parede Norte",
                    "type": "IfcWall",
                    "geometry": {
                        "start": [0, 0, 0],
                        "end": [5, 0, 0],
                        "height": 3,
                        "thickness": 0.2
                    },
                    "properties": {
                        "material": "Concreto",
                        "fire_rating": "2h"
                    }
                },
                {
                    "id": "wall_2", 
                    "name": "Parede Leste",
                    "type": "IfcWall",
                    "geometry": {
                        "start": [5, 0, 0],
                        "end": [5, 5, 0],
                        "height": 3,
                        "thickness": 0.2
                    },
                    "properties": {
                        "material": "Concreto",
                        "fire_rating": "2h"
                    }
                },
                {
                    "id": "wall_3",
                    "name": "Parede Sul", 
                    "type": "IfcWall",
                    "geometry": {
                        "start": [5, 5, 0],
                        "end": [0, 5, 0],
                        "height": 3,
                        "thickness": 0.2
                    },
                    "properties": {
                        "material": "Concreto",
                        "fire_rating": "2h"
                    }
                },
                {
                    "id": "wall_4",
                    "name": "Parede Oeste",
                    "type": "IfcWall", 
                    "geometry": {
                        "start": [0, 5, 0],
                        "end": [0, 0, 0],
                        "height": 3,
                        "thickness": 0.2
                    },
                    "properties": {
                        "material": "Concreto",
                        "fire_rating": "2h"
                    }
                }
            ],
            "beams": [
                {
                    "id": "beam_1",
                    "name": "Viga Norte",
                    "type": "IfcBeam",
                    "geometry": {
                        "start": [0, 0, 3],
                        "end": [5, 0, 3],
                        "width": 0.3,
                        "height": 0.4
                    },
                    "properties": {
                        "material": "Aço",
                        "load_capacity": "50 kN/m"
                    }
                },
                {
                    "id": "beam_2",
                    "name": "Viga Central",
                    "type": "IfcBeam",
                    "geometry": {
                        "start": [0, 2.5, 3],
                        "end": [5, 2.5, 3],
                        "width": 0.3,
                        "height": 0.4
                    },
                    "properties": {
                        "material": "Aço",
                        "load_capacity": "50 kN/m"
                    }
                },
                {
                    "id": "beam_3",
                    "name": "Viga Sul",
                    "type": "IfcBeam",
                    "geometry": {
                        "start": [0, 5, 3],
                        "end": [5, 5, 3],
                        "width": 0.3,
                        "height": 0.4
                    },
                    "properties": {
                        "material": "Aço",
                        "load_capacity": "50 kN/m"
                    }
                }
            ],
            "columns": [
                {
                    "id": "column_1",
                    "name": "Pilar 1",
                    "type": "IfcColumn",
                    "geometry": {
                        "position": [0, 0, 0],
                        "height": 3,
                        "width": 0.3,
                        "depth": 0.3
                    },
                    "properties": {
                        "material": "Concreto",
                        "load_capacity": "500 kN"
                    }
                },
                {
                    "id": "column_2",
                    "name": "Pilar 2", 
                    "type": "IfcColumn",
                    "geometry": {
                        "position": [5, 0, 0],
                        "height": 3,
                        "width": 0.3,
                        "depth": 0.3
                    },
                    "properties": {
                        "material": "Concreto",
                        "load_capacity": "500 kN"
                    }
                },
                {
                    "id": "column_3",
                    "name": "Pilar 3",
                    "type": "IfcColumn", 
                    "geometry": {
                        "position": [5, 5, 0],
                        "height": 3,
                        "width": 0.3,
                        "depth": 0.3
                    },
                    "properties": {
                        "material": "Concreto",
                        "load_capacity": "500 kN"
                    }
                },
                {
                    "id": "column_4",
                    "name": "Pilar 4",
                    "type": "IfcColumn",
                    "geometry": {
                        "position": [0, 5, 0],
                        "height": 3,
                        "width": 0.3,
                        "depth": 0.3
                    },
                    "properties": {
                        "material": "Concreto",
                        "load_capacity": "500 kN"
                    }
                }
            ]
        }
    }
    
    # Salva em arquivo JSON
    with open("metro_sp_bim.json", "w", encoding="utf-8") as f:
        json.dump(bim_data, f, indent=2, ensure_ascii=False)
    
    print("Dados BIM criados com sucesso: metro_sp_bim.json")
    print(f"Total de elementos:")
    print(f"  - Paredes: {len(bim_data['elements']['walls'])}")
    print(f"  - Vigas: {len(bim_data['elements']['beams'])}")
    print(f"  - Pilares: {len(bim_data['elements']['columns'])}")
    
    return bim_data

def create_bim_from_sketch():
    """Cria dados BIM a partir de um esboço simples"""
    
    print("=== Criador de BIM Simples ===")
    print("Digite as informações do seu projeto:")
    
    project_name = input("Nome do projeto: ") or "Projeto Metro SP"
    
    # Cria estrutura básica
    bim_data = {
        "project": {
            "name": project_name,
            "description": "Projeto criado via interface simples",
            "version": "1.0"
        },
        "elements": {
            "walls": [],
            "beams": [],
            "columns": []
        }
    }
    
    # Adiciona paredes
    print("\n--- Adicionando Paredes ---")
    while True:
        add_wall = input("Adicionar parede? (s/n): ").lower()
        if add_wall != 's':
            break
            
        wall_name = input("Nome da parede: ") or f"Parede_{len(bim_data['elements']['walls'])+1}"
        start_x = float(input("Posição inicial X: ") or "0")
        start_y = float(input("Posição inicial Y: ") or "0")
        end_x = float(input("Posição final X: ") or "5")
        end_y = float(input("Posição final Y: ") or "0")
        height = float(input("Altura: ") or "3")
        
        wall = {
            "id": f"wall_{len(bim_data['elements']['walls'])+1}",
            "name": wall_name,
            "type": "IfcWall",
            "geometry": {
                "start": [start_x, start_y, 0],
                "end": [end_x, end_y, 0],
                "height": height,
                "thickness": 0.2
            },
            "properties": {
                "material": "Concreto",
                "fire_rating": "2h"
            }
        }
        bim_data['elements']['walls'].append(wall)
    
    # Adiciona vigas
    print("\n--- Adicionando Vigas ---")
    while True:
        add_beam = input("Adicionar viga? (s/n): ").lower()
        if add_beam != 's':
            break
            
        beam_name = input("Nome da viga: ") or f"Viga_{len(bim_data['elements']['beams'])+1}"
        start_x = float(input("Posição inicial X: ") or "0")
        start_y = float(input("Posição inicial Y: ") or "0")
        start_z = float(input("Posição inicial Z: ") or "3")
        end_x = float(input("Posição final X: ") or "5")
        end_y = float(input("Posição final Y: ") or "0")
        end_z = float(input("Posição final Z: ") or "3")
        
        beam = {
            "id": f"beam_{len(bim_data['elements']['beams'])+1}",
            "name": beam_name,
            "type": "IfcBeam",
            "geometry": {
                "start": [start_x, start_y, start_z],
                "end": [end_x, end_y, end_z],
                "width": 0.3,
                "height": 0.4
            },
            "properties": {
                "material": "Aço",
                "load_capacity": "50 kN/m"
            }
        }
        bim_data['elements']['beams'].append(beam)
    
    # Salva o arquivo
    filename = input("\nNome do arquivo para salvar (sem extensão): ") or "meu_projeto"
    filename = f"{filename}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bim_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProjeto salvo em: {filename}")
    print(f"Total de elementos: {len(bim_data['elements']['walls'])} paredes, {len(bim_data['elements']['beams'])} vigas")
    
    return bim_data

if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1. Criar BIM padrão (metro_sp_bim.json)")
    print("2. Criar BIM personalizado")
    
    choice = input("Opção (1 ou 2): ")
    
    if choice == "2":
        create_bim_from_sketch()
    else:
        create_simple_bim_data() 
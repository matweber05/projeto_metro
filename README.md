# Sistema BIM + YOLO Integration

Este projeto integra detecção de objetos com YOLO e análise de conformidade com modelos BIM (Building Information Modeling).

## 📁 Arquivos do Projeto

- `bim.py` - Programa principal que integra YOLO com análise BIM
- `create_bim.py` - Cria arquivos IFC complexos usando ifcopenshell
- `simple_bim_generator.py` - Cria dados BIM simples em formato JSON
- `yolov8n.pt` - Modelo YOLO pré-treinado
- `camera.py` - Script de teste da câmera

## 🚀 Como Usar

### 1. Executar o Programa Principal

```bash
python bim.py
```

O programa irá:
- Carregar o modelo YOLO
- Tentar carregar dados BIM (IFC ou JSON)
- Abrir a câmera
- Detectar objetos em tempo real
- Comparar com o modelo BIM
- Mostrar alertas de desvios

### 2. Criar Dados BIM

#### Opção A: Dados BIM Simples (Recomendado)

```bash
python simple_bim_generator.py
```

Escolha:
- **Opção 1**: Criar BIM padrão (`metro_sp_bim.json`)
- **Opção 2**: Criar BIM personalizado (interface interativa)

#### Opção B: Arquivo IFC Completo

```bash
python create_bim.py
```

Cria um arquivo `metro_sp.ifc` com estrutura completa.

## 📊 Formatos de Dados BIM Suportados

### 1. Arquivo IFC (.ifc)
- Formato padrão da indústria
- Estrutura completa com hierarquia
- Requer ifcopenshell

### 2. Arquivo JSON (.json)
- Formato simples e legível
- Fácil de criar e modificar
- Estrutura:
```json
{
  "project": {
    "name": "Nome do Projeto",
    "description": "Descrição"
  },
  "elements": {
    "walls": [...],
    "beams": [...],
    "columns": [...]
  }
}
```

### 3. Dados Simulados
- Usado quando nenhum arquivo BIM está disponível
- Dados básicos para teste

## 🎯 Funcionalidades

### Detecção de Objetos
- Pessoas
- Cadeiras
- Paredes (se treinado)
- Vigas (se treinado)
- Outros objetos do modelo YOLO

### Análise BIM
- Comparação de posições
- Detecção de desvios
- Alertas em tempo real
- Estatísticas de conformidade

### Interface Visual
- Caixas de detecção coloridas
- Informações na tela
- Alertas destacados
- Contadores de estatísticas

## 🔧 Configuração

### Dependências
```bash
pip install ultralytics opencv-python ifcopenshell numpy
```

### Modelo YOLO
- Usa `yolov8n.pt` por padrão
- Pode ser substituído por modelo customizado
- Suporta treinamento específico para elementos de construção

### Câmera
- Usa câmera padrão (índice 0)
- Pode ser configurada para outras fontes de vídeo

## 📈 Personalização

### Adicionar Novos Tipos de Objetos
1. Modifique a lista `obj_type` no código
2. Adicione dados correspondentes no BIM
3. Ajuste a função `get_bim_position()`

### Ajustar Tolerâncias
```python
def calculate_deviation(detected_pos, bim_pos, tolerance=50):
    # tolerance em pixels
```

### Modificar Dados BIM
- Edite arquivo JSON diretamente
- Use `simple_bim_generator.py` para interface
- Modifique `create_bim.py` para IFC complexo

## 🎮 Controles

- **Q**: Sair do programa
- **S**: Salvar screenshot
- **Console**: Mostra informações detalhadas de cada frame

## 📝 Exemplos de Uso

### Criação Rápida de BIM
```bash
# 1. Criar dados BIM
python simple_bim_generator.py
# Escolha opção 1 para dados padrão

# 2. Executar análise
python bim.py
```

### BIM Personalizado
```bash
# 1. Criar BIM interativo
python simple_bim_generator.py
# Escolha opção 2 e siga as instruções

# 2. Executar análise
python bim.py
```

## 🔍 Troubleshooting

### Erro: "Arquivo não encontrado"
- Execute `python simple_bim_generator.py` para criar dados BIM
- Verifique se os arquivos estão no diretório correto

### Erro: "Não foi possível abrir a câmera"
- Verifique se a câmera está conectada
- Teste com `python camera.py`

### Performance Lenta
- Use modelo YOLO menor (yolov8n.pt)
- Reduza resolução da câmera
- Ajuste confiança de detecção

## 📚 Próximos Passos

1. **Treinamento Customizado**: Treinar YOLO para elementos específicos de construção
2. **Integração 3D**: Adicionar análise tridimensional
3. **Banco de Dados**: Armazenar histórico de análises
4. **Interface Web**: Dashboard online para monitoramento
5. **Alertas Automáticos**: Notificações por email/SMS

## 🤝 Contribuição

Para contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes. 
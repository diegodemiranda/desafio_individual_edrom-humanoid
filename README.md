# Desafio Individual EDROM - Robô A*


## O desafio:

O objetivo é programar a "inteligência" de um robô de futebol para que ele navegue em um campo 2D. 
A tarefa consistiu em duas fases:
1.  Levar o robô de sua posição inicial até a bola, desviando de robôs adversários.
2.  Após capturar a bola, levá-la até o gol adversário para marcar o ponto da vitória.

O caminho encontrado precisava ser **ótimo**, não apenas em distância, mas considerando diversas outras variáveis de custo que simulam um ambiente de jogo real.

## Estrutura dos arquivos:

### 📄 `simulador.py` (O Simulador)

Este arquivo é o ambiente de simulação. Ele é responsável por:
-   Criar a janela do jogo e desenhar o campo, o robô, a bola e os obstáculos.
-   Gerenciar o loop principal do jogo e a interface (botões de Play/Reset).
-   Chamar a sua função no arquivo `candidato.py` para obter o caminho que o robô deve seguir.

### 👨‍💻 `candidato.py` (Sua Área de Trabalho)

Ele contém uma única função principal: `encontrar_caminho()`. É dentro desta função que toda a lógica explicada abaixo foi implementada:

#### 1. Arquitetura geral

**Classe AStar**: Encapsula toda a lógica do algoritmo, mantendo o código organizado e reutilizável
Separação de responsabilidades: Cada método tem uma função específica e bem definida
Configurações centralizadas: Constantes definidas no início facilitam ajustes e manutenção
<br>

#### 2. Sistema de movimentação (8 Direções)
```python
DIRECOES = [
    (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinais
    (1, 1), (1, -1), (-1, -1), (-1, 1) # Diagonais
]
```

-   Movimento completo: O robô pode se mover em 8 direções
-   Custos diferenciados: Movimento reto (custo 10) vs diagonal (custo 14, aproximadamente √2×10)
<br>

#### 3. Sistema de custos de rotação
O algoritmo implementa um sistema sofisticado de penalização por rotação:

```python
pythondef _calcular_custo_rotacao(self, dir_anterior, dir_atual, tem_bola):
```

Tipos de rotação e custos:<br>
-   **Ajuste suave (< 45°)**: Custo 2
-   **Curva suave (45-90°)**: Custo 5
-   **Curva fechada (90-135°)**: Custo 15
-   **Inversão (> 135°)**: Custo 25

Por que isso é importante:<br>
-   Simula o comportamento real de um robô
-   Evita mudanças bruscas de direção
-   Prioriza caminhos mais suaves e naturais
<br>

#### 4. Estados diferenciados (com/sem bola)
```python
pythonif tem_bola:
    custo_rotacao *= self.MULT_COM_BOLA  # Multiplica por 2.0
```
   
**Comportamento sem bola**:<br>
-   Movimentos mais ágeis
-   Rotações com menor penalização
-   Foco na velocidade para alcançar a bola

**Comportamento com bola**:<br>
-   Movimentos mais cuidadosos
-   Rotações fortemente penalizadas (×2.0)
-   Prioriza estabilidade para não perder a bola
<br>

#### 5. Zonas de perigo
```python
pythondef _calcular_zonas_perigo(self):
# Marca células próximas aos obstáculos como perigosas
```
    
**Implementação:**
-   **Raio de perigo**: 1 célula ao redor de cada obstáculo
-   **Custo adicional**: +8 pontos para passar por zona perigosa
-   **Flexibilidade**: Não proíbe o movimento, apenas desencoraja

**Benefícios**:
-   Robô evita passar muito próximo aos adversários
-   Mantém distância segura quando possível
-   Permite passagem em situações necessárias
<br>

#### 6. Heurística otimizada
```python
pythondef _calcular_heuristica(self, pos_atual, pos_objetivo):
    # Distância diagonal otimizada
    diagonal = min(dx, dy)
    reto = abs(dx - dy)
    return diagonal * CUSTO_DIAGONAL + reto * CUSTO_RETO
```

**Características**:<br>
-   **Admissível**: Nunca superestima o custo real
-   **Consistente**: Garante optimalidade do A*
-   **Precisa**: Considera movimento em 8 direções
<br>

#### 7. Eficiência e performance
Estruturas de dados eficientes:
-   ```heapq``` para fila de prioridade O(log n)
-   ```set()``` para obstáculos e visitados O(1) lookup
-   ```dict()``` para custos e caminhos O(1) acesso

**Otimizações implementadas**:
-   Verificação precoce de obstáculos
-   Evita processamento de nós já visitados
-   Reconstrói caminho de forma eficiente
<br>

#### 8. Tratamento de casos especiais
**Situações tratadas**:<br>
-   Sem caminho possível: Retorna lista vazia
-   Obstáculos no caminho: Desvia automaticamente
-   Primeira movimentação: Sem penalização de rotação
-   Limites do campo: Validação de boundaries
-   <br>

#### 9. Melhores práticas aplicadas
**Código limpo**:
-   Nomes descritivos para variáveis e métodos
-   Documentação clara em cada função
-   Separação lógica de responsabilidades

**Manutenibilidade**:
-   Constantes configuráveis
-   Métodos pequenos e específicos
-   Estrutura modular

**Robustez**:
-   Tratamento de casos de borda
-   Validações de entrada
-   Mensagens de erro informativas
  <br>

#### 10. Como o algoritmo resolve o desafio

**Fase 1 (Ir até a bola)**:<br>
```tem_bola = False```
-   Movimentos mais ágeis
-   Foco na velocidade


**Fase 2 (Ir ao gol com a bola)**:<br>
```tem_bola = True```
-   Movimentos mais cautelosos
-   Penalizações de rotação dobradas
-   Maior cuidado com zonas de perigo


## Como testar:

1.  **Instale as dependências:** Certifique-se de que você tem Python e a biblioteca Pygame instalados.
    ```bash
    pip install pygame
    ```
2.  **Execute o simulador:** Abra um terminal na pasta do projeto e execute o comando:
    ```bash
    python simulador.py
    ```


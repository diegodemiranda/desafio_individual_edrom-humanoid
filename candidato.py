# NOME DO CANDIDATO: Diego de Miranda da Silva
# CURSO DO CANDIDATO: Ciência da Computação
# AREAS DE INTERESSE: Inteligência Artificial, Robótica, UX Design

import heapq
import math
from typing import List, Tuple, Set, Dict, Optional

def encontrar_caminho(
    pos_inicial: Tuple[int, int],
    pos_objetivo: Tuple[int, int],
    obstaculos: List[Tuple[int, int]],
    largura_grid: int,
    altura_grid: int,
    tem_bola: bool = False
) -> List[Tuple[int, int]]:
    # Verifica se o objetivo é um obstáculo
    if pos_objetivo in obstaculos:
        return []
        # Verifica se há pelo menos um vizinho livre ao redor do objetivo
    direcoes = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, -1), (-1, 1)
    ]
    vizinho_livre = False
    for dx, dy in direcoes:
        nx, ny = pos_objetivo[0] + dx, pos_objetivo[1] + dy
        if 0 <= nx < largura_grid and 0 <= ny < altura_grid and (nx, ny) not in obstaculos:
            vizinho_livre = True
            break
    if not vizinho_livre:
        return []
    return AStar(largura_grid, altura_grid, obstaculos).encontrar_caminho_otimo(
            pos_inicial, pos_objetivo, tem_bola
        )
    """
    Implementação completa do algoritmo A* para RoboCup com múltiplos níveis de complexidade:
    - Movimento em 8 direções (incluindo diagonais)
    - Custos diferenciados para rotação
    - Estados diferentes com/sem bola
    - Zonas de perigo próximas aos obstáculos
    """
    return AStar(largura_grid, altura_grid, obstaculos).encontrar_caminho_otimo(
        pos_inicial, pos_objetivo, tem_bola
    )

class AStar:
    """Implementação do algoritmo A* com suporte a múltiplos custos e estados"""

    # Direções possíveis: 8 direções (4 cardinais + 4 diagonais)
    DIRECOES: List[Tuple[int, int]] = [
        (0, 1),  # Norte
        (1, 0),  # Leste
        (0, -1),  # Sul
        (-1, 0),  # Oeste
        (1, 1),  # Nordeste
        (1, -1),  # Sudeste
        (-1, -1),  # Sudoeste
        (-1, 1)  # Noroeste
    ]

    # Custos base de movimento
    CUSTO_RETO: int = 10  # Movimento horizontal/vertical
    CUSTO_DIAGONAL: int = 14  # Movimento diagonal (aproximadamente √2 * 10)

    # Custos de rotação (penalidades por mudança de direção)
    CUSTO_CURVA_SUAVE: int = 5  # Reto -> Diagonal ou vice-versa
    CUSTO_CURVA_FECHADA: int = 15  # Horizontal -> Vertical ou perpendicular
    CUSTO_INVERSAO: int = 25  # Inversão completa (180°)

    # Multiplicadores quando o robô tem a bola (mais cuidadoso)
    MULT_COM_BOLA: float = 2.0  # Multiplica custos de rotação quando tem bola

    # Custos de zona de perigo (proximidade com obstáculos)
    CUSTO_ZONA_PERIGO: int = 8  # Custo adicional para células próximas a obstáculos
    RAIO_PERIGO: int = 1  # Raio de células consideradas perigosas

    def __init__(self, largura: int, altura: int, obstaculos: List[Tuple[int, int]]):
        self.largura = largura
        self.altura = altura
        self.obstaculos: Set[Tuple[int, int]] = set(obstaculos)
        self.zonas_perigo: Optional[Set[Tuple[int, int]]] = None  # Cache para zonas de perigo

    def _calcular_zonas_perigo(self) -> Set[Tuple[int, int]]:
        """
        Calcula e armazena as zonas de perigo próximas aos obstáculos.
        Utiliza cache para evitar recomputação.
        """
        if self.zonas_perigo is not None:
            return self.zonas_perigo
        zonas = set()
        for obs_x, obs_y in self.obstaculos:
            for dx in range(-self.RAIO_PERIGO, self.RAIO_PERIGO + 1):
                for dy in range(-self.RAIO_PERIGO, self.RAIO_PERIGO + 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = obs_x + dx, obs_y + dy
                    if self._posicao_valida(nx, ny) and (nx, ny) not in self.obstaculos:
                        zonas.add((nx, ny))
        self.zonas_perigo = zonas
        return zonas

    def _posicao_valida(self, x: int, y: int) -> bool:
        """Verifica se a posição está dentro dos limites do grid"""
        return 0 <= x < self.largura and 0 <= y < self.altura

    def _eh_obstaculo(self, pos: Tuple[int, int]) -> bool:
        """Verifica se a posição é um obstáculo"""
        return pos in self.obstaculos

    def _calcular_heuristica(self, pos_atual: Tuple[int, int], pos_objetivo: Tuple[int, int]) -> float:
        """
        Heurística de distância de Manhattan com ajuste diagonal (mais precisa que Manhattan pura)
        Esta heurística é admissível e consistente para movimento em 8 direções
        """
        dx = abs(pos_atual[0] - pos_objetivo[0])
        dy = abs(pos_atual[1] - pos_objetivo[1])
        # Distância diagonal otimizada: usa movimentos diagonais quando possível
        diagonal = min(dx, dy)
        reto = abs(dx - dy)
        return diagonal * self.CUSTO_DIAGONAL + reto * self.CUSTO_RETO

    @staticmethod
    def _obter_direcao(de: Tuple[int, int], para: Tuple[int, int]) -> Tuple[int, int]:
        """Obtém a direção do movimento entre duas posições"""
        dx = para[0] - de[0]
        dy = para[1] - de[1]
        # Normaliza a direção
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        return dx, dy

    def _calcular_custo_rotacao(self, dir_anterior: Optional[Tuple[int, int]],
                                dir_atual: Tuple[int, int], tem_bola: bool) -> float:
        """
        Calcula o custo adicional baseado na mudança de direção
        """
        if dir_anterior is None:
            return 0.0  # Primeiro movimento, sem rotação
        # Se mantém a mesma direção, sem custo adicional
        if dir_anterior == dir_atual:
            return 0.0
        # Calcula o ângulo entre as direções
        def direcao_para_angulo(direcao):
            dx, dy = direcao
            return math.atan2(dy, dx)
        angulo_anterior = direcao_para_angulo(dir_anterior)
        angulo_atual = direcao_para_angulo(dir_atual)
        # Diferença angular (normalizada para [-π, π])
        diff_angular = abs(angulo_atual - angulo_anterior)
        if diff_angular > math.pi:
            diff_angular = 2 * math.pi - diff_angular
        # Classifica o tipo de rotação e aplica custo correspondente
        if diff_angular < math.pi / 4:  # < 45° - ajuste muito suave
            custo_rotacao = 2.0
        elif diff_angular < math.pi / 2:  # < 90° - curva suave
            custo_rotacao = self.CUSTO_CURVA_SUAVE
        elif diff_angular < 3 * math.pi / 4:  # < 135° - curva fechada
            custo_rotacao = self.CUSTO_CURVA_FECHADA
        else:  # >= 135° - inversão
            custo_rotacao = self.CUSTO_INVERSAO
        # Multiplica o custo se o robô estiver com a bola
        if tem_bola:
            custo_rotacao *= self.MULT_COM_BOLA
        return custo_rotacao

    def _calcular_custo_movimento(self, pos_atual: Tuple[int, int], pos_destino: Tuple[int, int],
        dir_anterior: Optional[Tuple[int, int]], tem_bola: bool) -> float:
        """
        Calcula o custo total de um movimento considerando:
        - Distância base (reto vs diagonal)
        - Custo de rotação
        - Zona de perigo
        """
        # Custo base do movimento
        dx = abs(pos_destino[0] - pos_atual[0])
        dy = abs(pos_destino[1] - pos_atual[1])
        if dx == 1 and dy == 1:  # Movimento diagonal
            custo_base = self.CUSTO_DIAGONAL
        else:  # Movimento reto
            custo_base = self.CUSTO_RETO
        # Custo de rotação
        dir_atual = self._obter_direcao(pos_atual, pos_destino)
        custo_rotacao = self._calcular_custo_rotacao(dir_anterior, dir_atual, tem_bola)
        # Custo de zona de perigo
        zonas_perigo = self._calcular_zonas_perigo()
        custo_perigo = self.CUSTO_ZONA_PERIGO if pos_destino in zonas_perigo else 0.0
        return custo_base + custo_rotacao + custo_perigo

    def encontrar_caminho_otimo(self, pos_inicial: Tuple[int, int],
                                pos_objetivo: Tuple[int, int], tem_bola: bool) -> List[Tuple[int, int]]:
        """
        Implementa o algoritmo A* completo com todos os custos
        """
        # Estruturas de dados do A*
        heap: List[Tuple[float, Tuple[int, int], Optional[Tuple[int, int]]]] = []  # Fila de prioridade
        visitados: Dict[Tuple[int, int], float] = {}  # Nós já processados e seus menores custos
        custos_g: Dict[Tuple[int, int], float] = {}  # Custo real do início até cada nó
        pais: Dict[Tuple[int, int], Tuple[int, int]] = {}  # Para reconstruir o caminho

        # Estado inicial
        custos_g[pos_inicial] = 0.0
        h_inicial = self._calcular_heuristica(pos_inicial, pos_objetivo)
        f_inicial = custos_g[pos_inicial] + h_inicial

        heapq.heappush(heap, (f_inicial, pos_inicial, None))  # (f, posição, direção_anterior)

        while heap:
            f_atual, pos_atual, dir_anterior = heapq.heappop(heap)
            # Se já foi processado com custo menor ou igual, pula
            if pos_atual in visitados and visitados[pos_atual] <= custos_g[pos_atual]:
                continue
            visitados[pos_atual] = custos_g[pos_atual]
            # Verifica se chegou ao objetivo
            if pos_atual == pos_objetivo:
                return self._reconstruir_caminho(pais, pos_inicial, pos_objetivo)
            # Explora vizinhos
            for direcao in self.DIRECOES:
                dx, dy = direcao
                nova_pos = (pos_atual[0] + dx, pos_atual[1] + dy)
                # Verifica se a posição é válida
                if not self._posicao_valida(nova_pos[0], nova_pos[1]):
                    continue
                # Verifica se não é obstáculo
                if self._eh_obstaculo(nova_pos):
                    continue
                # Calcula custos
                custo_movimento = self._calcular_custo_movimento(
                    pos_atual, nova_pos, dir_anterior, tem_bola
                )
                novo_g = custos_g[pos_atual] + custo_movimento
                # Se encontrou um caminho melhor ou é a primeira vez visitando
                if nova_pos not in custos_g or novo_g < custos_g[nova_pos]:
                    custos_g[nova_pos] = novo_g
                    h = self._calcular_heuristica(nova_pos, pos_objetivo)
                    f = novo_g + h
                    pais[nova_pos] = pos_atual
                    heapq.heappush(heap, (f, nova_pos, direcao))
        # Se chegou aqui, não encontrou caminho
        print(f"AVISO: Nenhum caminho encontrado de {pos_inicial} para {pos_objetivo}")
        return []

    @staticmethod
    def _reconstruir_caminho(pais: Dict[Tuple[int, int], Tuple[int, int]],
        inicio: Tuple[int, int], fim: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstrói o caminho a partir do dicionário de pais
        Retorna o caminho SEM incluir a posição inicial
        """
        caminho = []
        atual = fim
        while atual != inicio:
            caminho.append(atual)
            atual = pais[atual]
        caminho.reverse()
        return caminho
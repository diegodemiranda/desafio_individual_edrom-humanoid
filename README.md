# EDROM Individual Challenge - A* 🤖

## The challenge:

The goal is to program the “intelligence” of a soccer robot so it can navigate a 2D field.
The task consisted of two phases:
1. Take the robot from its starting position to the ball, avoiding opponent robots.
2. After capturing the ball, take it to the opponent’s goal to score the winning point.

The path found needed to be optimal, not only in distance, but considering several other cost variables that simulate a real game environment.

## File structure:

#### `simulador.py` (The simulator)

This file is the simulation environment.<br>
It is responsible for:
- Creating the game window and drawing the field, the robot, the ball, and obstacles.
- Managing the game’s main loop and the interface (Play/Reset buttons).
- Calling your function in `candidato.py` to obtain the path the robot should follow.

#### `candidato.py` (Algorithm implementation)

It contains a single main function: `encontrar_caminho()`.<br>
Inside this function, all the logic explained below was implemented:

#### 1. Overall architecture

- AStar class: Encapsulates all the algorithm logic, keeping the code organized and reusable
- Separation of concerns: Each method has a specific and well-defined function
- Centralized configuration: Constants defined at the beginning facilitate tuning and maintenance
<br>

#### 2. Movement system (8 directions)
```python
DIRECOES = [
    (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinals
    (1, 1), (1, -1), (-1, -1), (-1, 1) # Diagonals
]
```

- Full movement: The robot can move in 8 directions
- Differentiated costs: Straight move (cost 10) vs. diagonal (cost 14, approximately √2 × 10)
<br>

#### 3. Rotation cost system
The algorithm implements a sophisticated rotation penalty system:

```python
def _calcular_custo_rotacao(self, dir_anterior, dir_atual, tem_bola):
    ...
```

Types of rotation and costs:<br>
- Smooth adjustment (< 45°): Cost 2
- Gentle turn (45–90°): Cost 5
- Sharp turn (90–135°): Cost 15
- Reversal (> 135°): Cost 25

Why this matters:<br>
- Simulates realistic robot behavior
- Avoids abrupt direction changes
- Prioritizes smoother, more natural paths
<br>

#### 4. Differentiated states (with/without ball)
```python
if tem_bola:
    custo_rotacao *= self.MULT_COM_BOLA  # Multiply by 2.0
```

Without the ball:<br>
- More agile movements
- Lower rotation penalties
- Focus on speed to reach the ball

With the ball:<br>
- More careful movements
- Rotation penalties strongly increased (×2.0)
- Prioritizes stability to avoid losing the ball
<br>

#### 5. Danger zones
```python
def _calcular_zonas_perigo(self):
    # Marks cells near obstacles as dangerous
    ...
```

Implementation:
- Danger radius: 1 cell around each obstacle
- Additional cost: +8 points for traversing a danger zone
- Flexibility: Does not forbid movement, only discourages it
- Efficient data structures and danger-zone caching

Benefits:
- Robot avoids passing too close to opponents
- Keeps a safe distance when possible
- Allows passage in necessary situations
<br>

#### 6. Optimized heuristic
```python
def _calcular_heuristica(self, pos_atual, pos_objetivo):
    # Optimized diagonal distance
    dx = abs(pos_objetivo[0] - pos_atual[0])
    dy = abs(pos_objetivo[1] - pos_atual[1])
    diagonal = min(dx, dy)
    straight = abs(dx - dy)
    return diagonal * CUSTO_DIAGONAL + straight * CUSTO_RETO
```

Characteristics:<br>
- Admissible: Never overestimates the true cost
- Consistent: Ensures A* optimality
- Accurate: Considers 8-direction movement, optimized for diagonal movement
<br>

#### 7. Efficiency and performance
Efficient data structures:
- `heapq` for O(log n) priority queue
- `set()` for obstacles and visited with O(1) lookup
- `dict()` for costs and paths with O(1) access

Implemented optimizations:
- Early obstacle check and validation that at least one neighbor is free
- Danger-zone caching
- Visited control with dictionary of lowest cost
- Avoids processing already-visited nodes
- Explicit typing
- Efficient path reconstruction
<br>

#### 8. Special case handling
Handled situations:<br>
- No possible path: Returns an empty list
- Obstacles in the way: Automatically detours
- First movement: No rotation penalty
- Field boundaries: Boundary validation
<br>

#### 9. Best practices applied
Clean code:
- Descriptive names for variables and methods
- Clear documentation in each function
- Logical separation of responsibilities

Maintainability:
- Configurable constants
- Small, specific methods
- Modular structure

Robustness:
- Edge case handling
- Input validations
- Informative error messages
<br>

#### 10. How the algorithm solves the challenge

Phase 1 (Go to the ball):<br>
`tem_bola = False`
- More agile movements
- Focus on speed

Phase 2 (Go to the goal with the ball):<br>
`tem_bola = True`
- More cautious movements
- Doubled rotation penalties
- Greater care with danger zones

## How to test:

1. Install dependencies: Make sure you have Python and the Pygame library installed.
    ```bash
    pip install pygame
    ```
2. Run the simulator: Open a terminal in the project folder and run:
    ```bash
    python simulador.py
    ```

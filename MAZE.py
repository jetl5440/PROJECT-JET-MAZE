import pygame
import random
from collections import deque

# CONFIG
WIDTH, HEIGHT = 800, 800
FPS = 60

DIFFICULTIES = {
    "EASY": 15,
    "MEDIUM": 25,
    "HARD": 40
}

STATE_MENU = 0
STATE_GAME = 1
STATE_PAUSE = 2

BG_COLOR = (20, 20, 30)
WALL_COLOR = (240, 240, 240)
PLAYER_COLOR = (50, 200, 50)
EXIT_COLOR = (200, 80, 80)
AI_PATH_COLOR = (255, 255, 0)  # Yellow light

MOVE_DELAY = 120  # ms between moves


# MAZE GENERATION
def generate_maze(rows, cols):
    """
    Generates a perfect maze using Depth‑First Search (DFS) backtracking.

    A perfect maze has:
    - No loops
    - Exactly one unique path between any two cells

    Each cell stores 4 booleans representing walls:
        [top, right, bottom, left]
    """
    grid = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def neighbors(r, c):
        """Yields all unvisited neighbors with wall indices."""
        for dr, dc, w, ow in [
            (-1, 0, 0, 2),
            (1, 0, 2, 0),
            (0, 1, 1, 3),
            (0, -1, 3, 1),
        ]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                yield nr, nc, w, ow

    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        nbrs = list(neighbors(r, c))
        if not nbrs:
            stack.pop()
            continue
        nr, nc, w, ow = random.choice(nbrs)
        grid[r][c][w] = False
        grid[nr][nc][ow] = False
        visited[nr][nc] = True
        stack.append((nr, nc))

    return grid


# SHORTEST PATH SOLVER
def bfs_shortest_path(grid, start, goal):
    """
    Computes the shortest path between two cells using Breadth‑First Search (BFS).

    BFS guarantees the shortest path in an unweighted maze.
    """
    rows, cols = len(grid), len(grid[0])
    q = deque([start])
    prev = {start: None}

    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            break

        walls = grid[r][c]
        moves = [
            ((r - 1, c), not walls[0]),
            ((r + 1, c), not walls[2]),
            ((r, c + 1), not walls[1]),
            ((r, c - 1), not walls[3]),
        ]

        for (nr, nc), open_path in moves:
            if open_path and 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in prev:
                prev[(nr, nc)] = (r, c)
                q.append((nr, nc))

    if goal not in prev:
        return []

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path))


# MAZE SURFACE RENDERING
def build_maze_surface(grid, cell_size):
    """
    Draws the maze walls onto a static surface.
    This surface never changes, improving performance.
    """
    rows, cols = len(grid), len(grid[0])
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(BG_COLOR)

    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size
            walls = grid[r][c]

            if walls[0]:
                pygame.draw.line(surf, WALL_COLOR, (x, y), (x + cell_size, y), 2)
            if walls[1]:
                pygame.draw.line(surf, WALL_COLOR, (x + cell_size, y),
                                 (x + cell_size, y + cell_size), 2)
            if walls[2]:
                pygame.draw.line(surf, WALL_COLOR, (x, y + cell_size),
                                 (x + cell_size, y + cell_size), 2)
            if walls[3]:
                pygame.draw.line(surf, WALL_COLOR, (x, y),
                                 (x, y + cell_size), 2)

    return surf


# GAME RENDERING
def draw_game(screen, maze_surf, cell_size, player, exit_cell, ai_path, timer_text):
    """
    Draws:
    - Maze
    - Yellow light path highlight
    - Player
    - Exit
    - Timer
    """
    screen.blit(maze_surf, (0, 0))

    # Yellow light highlight
    if ai_path:
        for (r, c) in ai_path:
            x = c * cell_size
            y = r * cell_size
            light_size = cell_size // 3
            pygame.draw.ellipse(
                screen,
                AI_PATH_COLOR,
                (
                    x + (cell_size - light_size) // 2,
                    y + (cell_size - light_size) // 2,
                    light_size,
                    light_size
                )
            )

    # Exit
    er, ec = exit_cell
    pygame.draw.rect(screen, EXIT_COLOR,
                     (ec * cell_size + cell_size // 4,
                      er * cell_size + cell_size // 4,
                      cell_size // 2, cell_size // 2))

    # Player
    pr, pc = player
    pygame.draw.circle(screen, PLAYER_COLOR,
                       (pc * cell_size + cell_size // 2,
                        pr * cell_size + cell_size // 2),
                       cell_size // 3)

    # Timer
    screen.blit(timer_text, (20, 20))

    pygame.display.flip()


# MENU RENDERING
def draw_menu(screen):
    """Draws the main menu with difficulty options and controls."""
    screen.fill((15, 15, 25))
    font = pygame.font.SysFont("arial", 70)
    small = pygame.font.SysFont("arial", 36)
    tiny = pygame.font.SysFont("arial", 28)

    title = font.render("Menu", True, (255, 255, 255))

    e = small.render("1 - Easy", True, (200, 200, 200))
    m = small.render("2 - Medium", True, (200, 200, 200))
    h = small.render("3 - Hard", True, (200, 200, 200))

    controls_title = small.render("Controls", True, (255, 255, 255))
    c1 = tiny.render("Arrow Keys / WASD - Move", True, (200, 200, 200))
    c2 = tiny.render("ESC - Pause", True, (200, 200, 200))
    c3 = tiny.render("SPACE - Continue", True, (200, 200, 200))
    c4 = tiny.render("ENTER - Highlight Shortest Path", True, (200, 200, 200))
    c5 = tiny.render("R - Restart", True, (200, 200, 200))

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    screen.blit(e, (WIDTH // 2 - e.get_width() // 2, 260))
    screen.blit(m, (WIDTH // 2 - m.get_width() // 2, 310))
    screen.blit(h, (WIDTH // 2 - h.get_width() // 2, 360))

    screen.blit(controls_title, (WIDTH // 2 - controls_title.get_width() // 2, 450))
    screen.blit(c1, (WIDTH // 2 - c1.get_width() // 2, 500))
    screen.blit(c2, (WIDTH // 2 - c2.get_width() // 2, 540))
    screen.blit(c3, (WIDTH // 2 - c3.get_width() // 2, 580))
    screen.blit(c4, (WIDTH // 2 - c4.get_width() // 2, 620))
    screen.blit(c5, (WIDTH // 2 - c5.get_width() // 2, 660))

    pygame.display.flip()


# PAUSE MENU
def draw_pause(screen):
    """Draws the pause menu."""
    screen.fill((10, 10, 20))
    font = pygame.font.SysFont("arial", 70)
    small = pygame.font.SysFont("arial", 36)

    paused = font.render("Paused", True, (255, 255, 255))
    resume = small.render("SPACE - Continue", True, (200, 200, 200))
    restart = small.render("R - Restart", True, (200, 200, 200))
    quitg = small.render("Q - Quit", True, (200, 200, 200))

    screen.blit(paused, (WIDTH // 2 - paused.get_width() // 2, 250))
    screen.blit(resume, (WIDTH // 2 - resume.get_width() // 2, 330))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 380))
    screen.blit(quitg, (WIDTH // 2 - quitg.get_width() // 2, 430))

    pygame.display.flip()


# WIN SCREEN
def draw_win(screen, final_time):
    """Draws the win screen with final time."""
    screen.fill((10, 30, 10))
    font = pygame.font.SysFont("arial", 80)
    small = pygame.font.SysFont("arial", 40)

    win = font.render("YOU WIN!", True, (255, 255, 255))
    msg = small.render(f"Time: {final_time:.2f} seconds", True, (200, 200, 200))
    ret = small.render("Returning to menu...", True, (200, 200, 200))

    screen.blit(win, (WIDTH // 2 - win.get_width() // 2, 250))
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 350))
    screen.blit(ret, (WIDTH // 2 - ret.get_width() // 2, 420))

    pygame.display.flip()


# MAIN GAME LOOP
def main():
    """
    Main game loop:
    - Handles menu, pause, and gameplay states
    - Processes input
    - Updates timer
    - Draws frames
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("PROJECT: JET MAZE")
    clock = pygame.time.Clock()

    game_state = STATE_MENU
    difficulty = DIFFICULTIES["MEDIUM"]

    rows = cols = difficulty
    cell_size = WIDTH // cols

    grid = generate_maze(rows, cols)
    maze_surf = build_maze_surface(grid, cell_size)
    player = [0, 0]
    exit_cell = (rows - 1, cols - 1)
    ai_path = []

    last_move_time = 0
    start_time = 0
    paused_time = 0

    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # MENU
        if game_state == STATE_MENU:
            draw_menu(screen)

            if keys[pygame.K_1]:
                difficulty = DIFFICULTIES["EASY"]
                game_state = STATE_GAME
            if keys[pygame.K_2]:
                difficulty = DIFFICULTIES["MEDIUM"]
                game_state = STATE_GAME
            if keys[pygame.K_3]:
                difficulty = DIFFICULTIES["HARD"]
                game_state = STATE_GAME

            if game_state == STATE_GAME:
                rows = cols = difficulty
                cell_size = WIDTH // cols
                grid = generate_maze(rows, cols)
                maze_surf = build_maze_surface(grid, cell_size)
                player = [0, 0]
                exit_cell = (rows - 1, cols - 1)
                ai_path = []
                last_move_time = current_time
                start_time = current_time
            continue

        # PAUSE
        if game_state == STATE_PAUSE:
            draw_pause(screen)

            if keys[pygame.K_SPACE]:
                start_time += (current_time - paused_time)
                game_state = STATE_GAME

            if keys[pygame.K_r]:
                grid = generate_maze(rows, cols)
                maze_surf = build_maze_surface(grid, cell_size)
                player = [0, 0]
                ai_path = []
                last_move_time = current_time
                start_time = current_time
                game_state = STATE_GAME

            if keys[pygame.K_q]:
                running = False

            continue

        # GAME
        if keys[pygame.K_ESCAPE]:
            paused_time = current_time
            game_state = STATE_PAUSE

        if keys[pygame.K_r]:
            grid = generate_maze(rows, cols)
            maze_surf = build_maze_surface(grid, cell_size)
            player = [0, 0]
            ai_path = []
            last_move_time = current_time
            start_time = current_time

        # Highlight path (ENTER)
        if keys[pygame.K_RETURN]:
            ai_path = bfs_shortest_path(grid, tuple(player), exit_cell)

        # Movement with cooldown
        if current_time - last_move_time > MOVE_DELAY:
            dr = dc = 0

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dr = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dr = 1
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dc = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dc = 1

            if dr or dc:
                r, c = player
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    walls = grid[r][c]
                    if dr == -1 and not walls[0]:
                        player[0] -= 1
                    elif dr == 1 and not walls[2]:
                        player[0] += 1
                    elif dc == 1 and not walls[1]:
                        player[1] += 1
                    elif dc == -1 and not walls[3]:
                        player[1] -= 1

                ai_path = []  # Clear highlight on movement
                last_move_time = current_time

        # Timer
        elapsed = (current_time - start_time) / 1000
        font = pygame.font.SysFont("arial", 32)
        timer_text = font.render(f"Time: {elapsed:.2f}", True, (255, 255, 255))

        # Win check
        if tuple(player) == exit_cell:
            draw_win(screen, elapsed)
            pygame.time.delay(2000)
            game_state = STATE_MENU
            continue

        draw_game(screen, maze_surf, cell_size, player, exit_cell, ai_path, timer_text)

    pygame.quit()


if __name__ == "__main__":
    main()

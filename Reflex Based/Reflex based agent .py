import pygame
import random
import time
import sys


GRID_SIZE = 9
CELL_SIZE = 50
MARGIN = 2
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 300


GREEN = (180, 255, 180)
RED = (255, 180, 180)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize environment
room = [[random.choice([0, 1]) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
memory = [[-1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # -1 = unknown, 0 = clean, 1 = dirty
room_cleaned_popup_shown = False

vx, vy = 3, 3
visited = set()
move_count = 0

# Init Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Reflex Based Vacuum Cleaner Agent")
font = pygame.font.SysFont("consolas", 16)

def draw_text(surface, text, x, y, color=WHITE):
    for i, line in enumerate(text.split("\n")):
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y + i * 18))
        

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = GREEN if room[y][x] == 0 else RED
            pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN))

           
            label = "D" if room[y][x] == 1 else "C"
            label_color = WHITE if room[y][x] == 1 else BLACK
            text = font.render(label, True, label_color)
            screen.blit(text, (x*CELL_SIZE + 18, y*CELL_SIZE + 14))

            
            if (x, y) in get_neighbors(vx, vy):
                pygame.draw.rect(screen, YELLOW, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN), 2)

          
            if (x, y) == (vx, vy):
                pygame.draw.rect(screen, BLUE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN), 3)

def get_neighbors(x, y):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue  
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbors.append((nx, ny))
    return neighbors

def all_clean():
    return all(cell == 0 for row in room for cell in row)

log = []

running = True

while running:
    screen.fill(GRAY)
    draw_grid()


    mem_str = "Agent's Memory:\n" + "\n".join(str([0 if c == 0 else 1 if c == 1 else 0 for c in row]) for row in memory)
    log_str = "Action Log:\n" + "\n".join(log[-5:])

    memory_y = GRID_SIZE * CELL_SIZE + 30
    draw_text(screen, f"Total Agent Moves: {move_count}", 10, memory_y - 25, color=YELLOW)
    draw_text(screen, mem_str, 10, memory_y)


    memory_lines = mem_str.count('\n') + 1
    log_y = memory_y + memory_lines * 18 + 10
    draw_text(screen, log_str, 10, log_y)
    log_lines = log_str.count('\n') + 1
    prompt_y = log_y + log_lines * 18 + 10
    draw_text(screen, "Press Enter for the next move...", 10, prompt_y)
    pygame.display.flip()

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not all_clean():
                # Clean if dirty
                if room[vy][vx] == 1:
                    room[vy][vx] = 0
                    memory[vy][vx] = 1 
                    log.append(f"Agent cleaned cell ({vx}, {vy})")
                else:
                     if memory[vy][vx] == -1:
                         memory[vy][vx] = 0
                     log.append(f"Agent at clean cell ({vx}, {vy})")

     
            moved = False
            neighbors = get_neighbors(vx, vy)
            random.shuffle(neighbors)

            for nx, ny in neighbors:
                 if room[ny][nx] == 1 and memory[ny][nx] == -1:
                     vx, vy = nx, ny
                     move_count += 1 
                     log.append(f"Agent moved to dirty cell ({vx}, {vy})")
                     moved = True
                     break

            if not moved:
                for nx, ny in neighbors:
                 if memory[ny][nx] == -1:
                    vx, vy = nx, ny
                    move_count += 1 
                    log.append(f"Agent moved to unvisited cell ({vx}, {vy})")
                    moved = True
                    break

         
            if not moved:
                 for nx, ny in neighbors:
                     if (nx, ny) != (vx, vy):  
                        vx, vy = nx, ny
                        move_count += 1 
                        log.append(f"Agent moved to visited cell ({vx}, {vy}) for exploration")
                        break


    if all_clean() and "Room fully clean " not in log:
        log.append("Room fully clean ")
    if all_clean() and not room_cleaned_popup_shown:
        room_cleaned_popup_shown = True


        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        font_big = pygame.font.SysFont("consolas", 28)
        text_surface = font_big.render("Room fully clean! Exiting...", True, BLACK)
        text_width, text_height = text_surface.get_size()
        padding_x = 40
        padding_y = 30
        popup_width = text_width + padding_x
        popup_height = text_height + padding_y
        popup_rect = pygame.Rect(
            (WINDOW_WIDTH - popup_width) // 2,
            (WINDOW_HEIGHT - popup_height) // 2,
            popup_width,
            popup_height
        )

        pygame.draw.rect(screen, WHITE, popup_rect)
        pygame.draw.rect(screen, BLACK, popup_rect, 3)
        text_rect = text_surface.get_rect(center=popup_rect.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

pygame.quit()
sys.exit()
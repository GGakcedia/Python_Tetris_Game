import pygame 
import random
import sys

pygame.init()
W, H, BS = 300, 660, 30
ROWS, COLS = (H - 60) // BS, W // BS
COLORS = [(0,255,255),(0,0,255),(255,165,0),(255,255,0),(0,255,0),(128,0,128),(255,0,0)]
SHAPES = [[[1,1,1,1]],
          [[1,0,0],[1,1,1]],
          [[0,0,1],[1,1,1]],
          [[1,1],[1,1]],
          [[0,1,1],[1,1,0]],
          [[0,1,0],[1,1,1]],
          [[1,1,0],[0,1,1]]]

def grid(lock={}):
    return [[lock.get((x,y),(0,0,0)) for x in range(COLS)] for y in range(ROWS)]

class Piece:
    def __init__(s,x,y,sh): s.x,s.y,s.shape,s.color,s.rot = x,y,sh,random.choice(COLORS),0
    def rot_shape(s): return list(zip(*s.shape[::-1]))

def shape_pos(p):
    return [(p.x+j, p.y+i) for i,l in enumerate(p.shape) for j,c in enumerate(l) if c]

def valid(p,g):
    pos = [(x,y) for y in range(ROWS) for x in range(COLS) if g[y][x]==(0,0,0)]
    return all((x,y) in pos or y<0 for x,y in shape_pos(p))

def check_lost(lock): return any(y < 2 for x,y in lock)
def new_piece(): return Piece(3,2,random.choice(SHAPES))

def draw_grid(surf,g):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surf,g[y][x],(x*BS,y*BS+60,BS,BS))
    for y in range(ROWS): pygame.draw.line(surf,(128,128,128),(0,y*BS+60),(W,y*BS+60))
    for x in range(COLS): pygame.draw.line(surf,(128,128,128),(x*BS,60),(x*BS,H))

def clear_rows(g,lock):
    cleared = 0
    for y in reversed(range(ROWS)):
        if (0,0,0) not in g[y]:
            cleared += 1
            for x in range(COLS): lock.pop((x,y),None)
    for x,y in sorted(lock,key=lambda k:k[1])[::-1]:
        if y < ROWS-cleared: lock[(x,y+cleared)] = lock.pop((x,y))
    return cleared

def draw_win(surf,g,sc):
    surf.fill((0,0,0))
    lbl = pygame.font.SysFont("comicsans",30).render(f"Score: {sc}",1,(255,255,255))
    surf.blit(lbl,(W//2 - lbl.get_width()//2,20))
    draw_grid(surf,g)
    pygame.display.update()

def game_over(surf,sc):
    f = pygame.font.SysFont("comicsans",40)
    surf.fill((0,0,0))
    lbls = [f.render(t,1,c) for t,c in [("Game Over",(255,0,0)),(f"Score: {sc}",(255,255,255)),("Retry",(255,255,255)),("Exit",(255,255,255))]]
    rects = [lbls[i].get_rect(center=(W//2, y)) for i,y in enumerate([100,160,250,320])]
    for i in range(4): surf.blit(lbls[i], rects[i])
    pygame.display.update()
    while 1:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if rects[2].collidepoint(e.pos): return True
                if rects[3].collidepoint(e.pos): pygame.quit(); sys.exit()

def main():
    screen = pygame.display.set_mode((W,H))
    pygame.display.set_caption("Tetris")
    lock = {}; fall, score = 0, 0
    run, clock = True, pygame.time.Clock()
    piece, ch = new_piece(), False

    while run:
        g = grid(lock)
        fall += clock.get_rawtime(); clock.tick()
        if fall/1000 >= 0.5:
            fall = 0; piece.y += 1
            if not valid(piece,g): piece.y -= 1; ch = True

        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT: piece.x -= 1; valid(piece,g) or setattr(piece,'x',piece.x+1)
                elif e.key == pygame.K_RIGHT: piece.x += 1; valid(piece,g) or setattr(piece,'x',piece.x-1)
                elif e.key == pygame.K_DOWN: piece.y += 1; valid(piece,g) or setattr(piece,'y',piece.y-1)
                elif e.key == pygame.K_UP:
                    old = piece.shape
                    piece.shape = piece.rot_shape()
                    valid(piece,g) or setattr(piece,'shape',old)

        for x,y in shape_pos(piece):
            if y > -1: g[y][x] = piece.color

        if ch:
            for p in shape_pos(piece): lock[p] = piece.color
            piece = new_piece(); ch = False
            if not valid(piece, g):
                if game_over(screen, score): main()
                else: break
            score += clear_rows(g, lock) * 10

        draw_win(screen, g, score)
    pygame.quit()

if __name__ == "__main__": main()
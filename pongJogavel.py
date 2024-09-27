import pygame
import random
import numpy as np


# Inicialização do Pygame
pygame.init()

# Configurações da janela
WIDTH, HEIGHT = 800, 600
FPS = 30
WINDOW_SIZE = (WIDTH, HEIGHT)
WINDOW = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Pong Game")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Barra do jogador
PLAYER_WIDTH, PLAYER_HEIGHT = 10, 100
player = pygame.Rect(50, HEIGHT // 2 - PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)

# Barra do adversário
opponent = pygame.Rect(WIDTH - 50 - PLAYER_WIDTH, HEIGHT // 2 - PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)

# Bola
BALL_WIDTH, BALL_HEIGHT = 10, 10
ball = pygame.Rect(WIDTH // 2 - BALL_WIDTH // 2, HEIGHT // 2 - BALL_HEIGHT // 2, BALL_WIDTH, BALL_HEIGHT)
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))

# Velocidade das barras
PLAYER_SPEED = 20
OPPONENT_SPEED = 20

# Pontuação
player_score = 0
opponent_score = 0
font = pygame.font.Font(None, 36)



# Função para atualizar a posição da bola
def update_ball_position():
    global ball_speed_x, ball_speed_y

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Colisões com as bordas
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Colisão com as barras
    if ball.colliderect(player) or ball.colliderect(opponent):
        ball_speed_x *= -1

# Função para verificar se alguém marcou ponto
def check_score():
    global player_score, opponent_score

    if ball.left <= 0:
        opponent_score += 1
        reset_ball()
    elif ball.right >= WIDTH:
        player_score += 1
        reset_ball()

# Função para reiniciar a bola
def reset_ball():
    global ball_speed_x, ball_speed_y

    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))

# Função para mover o jogador
def move_player():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
        player.y += PLAYER_SPEED
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= PLAYER_SPEED

# Função principal do jogo
def main_game_loop():
    global player_score, opponent_score

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        move_player()
        update_ball_position()
        check_score()

        # Limpa a tela
        WINDOW.fill(BLACK)

        # Desenha as barras e a bola
        pygame.draw.rect(WINDOW, VERDE, player)
        pygame.draw.rect(WINDOW, WHITE, opponent)
        pygame.draw.rect(WINDOW, VERMELHO, ball)

        # Desenha a pontuação
        player_text = font.render(f"Jogador: {player_score}", True, WHITE)
        opponent_text = font.render(f"Professor: {opponent_score}", True, WHITE)
        WINDOW.blit(player_text, (20, 20))
        WINDOW.blit(opponent_text, (WIDTH - opponent_text.get_width() - 20, 20))

        # Atualiza a tela
        pygame.display.flip()
        clock.tick(FPS)

# Executa o loop principal do jogo
if __name__ == "__main__":
  
    main_game_loop()

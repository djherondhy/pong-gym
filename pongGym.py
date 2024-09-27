import pygame
import random
import gym
from gym import spaces
import numpy as np

class PongEnv(gym.Env):
    def __init__(self):
        super(PongEnv, self).__init__()

        # Inicialização do Pygame
        pygame.init()

        # Configurações do ambiente
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 30
        self.WINDOW_SIZE = (self.WIDTH, self.HEIGHT)
        self.WINDOW = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()

        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.VERDE = (0, 255, 0)
        self.VERMELHO = (255, 0, 0)

        # Barra do jogador
        self.PLAYER_WIDTH, self.PLAYER_HEIGHT = 10, 100
        self.player = pygame.Rect(50, self.HEIGHT // 2 - self.PLAYER_HEIGHT // 2, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)

        # Barra do adversário
        self.opponent = pygame.Rect(self.WIDTH - 50 - self.PLAYER_WIDTH, self.HEIGHT // 2 - self.PLAYER_HEIGHT // 2, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)

        # Bola
        self.BALL_WIDTH, self.BALL_HEIGHT = 10, 10
        self.ball = pygame.Rect(self.WIDTH // 2 - self.BALL_WIDTH // 2, self.HEIGHT // 2 - self.BALL_HEIGHT // 2, self.BALL_WIDTH, self.BALL_HEIGHT)
        self.ball_speed_x = 7 * random.choice((1, -1))
        self.ball_speed_y = 7 * random.choice((1, -1))

        # Velocidade das barras
        self.PLAYER_SPEED = 20
        self.OPPONENT_SPEED = 20

        # Pontuação
        self.player_score = 0
        self.opponent_score = 0
        self.font = pygame.font.Font(None, 36)

        self.play_human = True
        # Tempo de reação aleatório
        self.frame_count =0 
        self.time_to_move = random.randint(30, 90)

        # Definir o espaço de ação e o espaço de observação do Gym
        self.action_space = spaces.Discrete(3)  # Ação binária: 0 (não se move), 1 (move para cima), 2 mover para baixo
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

    def reset(self):
        # Reiniciar o estado do ambiente
        self.player_score = 0
        self.opponent_score = 0
        self.player = pygame.Rect(50, self.HEIGHT // 2 - self.PLAYER_HEIGHT // 2, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.opponent = pygame.Rect(self.WIDTH - 50 - self.PLAYER_WIDTH, self.HEIGHT // 2 - self.PLAYER_HEIGHT // 2, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.ball = pygame.Rect(self.WIDTH // 2 - self.BALL_WIDTH // 2, self.HEIGHT // 2 - self.BALL_HEIGHT // 2, self.BALL_WIDTH, self.BALL_HEIGHT)
        self.ball_speed_x = 7 * random.choice((1, -1))
        self.ball_speed_y = 7 * random.choice((1, -1))
        return self._get_observation()

    def _get_observation(self):
        # Captura a imagem atual do jogo como observação (tela)
        surface = pygame.surfarray.array3d(self.WINDOW)
        return surface

    def step(self, action):
        # Executar a ação (mover o jogador)
        if action == 1 and self.opponent.top > 0:
            self.opponent.y -= self.OPPONENT_SPEED
        elif action == 2 and self.opponent.bottom < self.HEIGHT:
            self.opponent.y += self.OPPONENT_SPEED
        else:
            self.opponent.y += 0


        self.frame_count +=1

        if self.frame_count >= self.time_to_move:
            if self.player.bottom < self.HEIGHT and self.ball.x <=150:
                if self.ball.y  > self.player.y + 50:
                    self.player.y += self.PLAYER_SPEED

            if self.player.top > 0 and self.ball.x <=150:
                if self.ball.y  < self.player.y + 50:
                    self.player.y -= self.PLAYER_SPEED
        
        
        #movimentacao por humano
        #keys = pygame.key.get_pressed()
        #if keys[pygame.K_DOWN] and self.player.bottom < self.HEIGHT:
        #    self.player.y += self.PLAYER_SPEED
        #if keys[pygame.K_UP] and self.player.top > 0:
        #    self.player.y -= self.PLAYER_SPEED
        

        # Atualizar a posição da bola e a lógica do jogo
        self.update_ball_position()
        self.check_score()

        # Determinar o estado, recompensa e se o episódio terminou
        observation = self._get_observation()
        done = False
        reward = 0

        if self.player_score >= 10 or self.opponent_score >= 10:
            done = True

        return observation, reward, done, {}

    def update_ball_position(self):
        # Lógica para atualizar a posição da bola (mesma função do jogo original)
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        if self.ball.top <= 0 or self.ball.bottom >= self.HEIGHT:
            self.ball_speed_y *= -1

        if self.ball.colliderect(self.player) or self.ball.colliderect(self.opponent):
            self.ball_speed_x *= -1

    def check_score(self):
        # Lógica para verificar a pontuação (mesma função do jogo original)
        if self.ball.left <= 0:
            self.opponent_score += 1
            self.reset_ball()
        elif self.ball.right >= self.WIDTH:
            self.player_score += 1
            self.reset_ball()

    def reset_ball(self):
        # Lógica para reiniciar a bola (mesma função do jogo original)
        self.ball.center = (self.WIDTH // 2, self.HEIGHT // 2)
        self.ball_speed_x = 7 * random.choice((1, -1))
        self.ball_speed_y = 7 * random.choice((1, -1))

    def render(self, mode='human'):
        # Renderizar o ambiente (mostrar a tela)
        if mode == 'human':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.WINDOW.fill(self.BLACK)
            pygame.draw.rect(self.WINDOW, self.VERDE, self.player)
            pygame.draw.rect(self.WINDOW, self.WHITE, self.opponent)
            pygame.draw.rect(self.WINDOW, self.VERMELHO, self.ball)
            player_text = self.font.render(f"Jogador: {self.player_score}", True, self.WHITE)
            opponent_text = self.font.render(f"Oponente: {self.opponent_score}", True, self.WHITE)
            self.WINDOW.blit(player_text, (20, 20))
            self.WINDOW.blit(opponent_text, (self.WIDTH - opponent_text.get_width() - 20, 20))
            pygame.display.flip()
            self.clock.tick(self.FPS)
        elif mode == 'rgb_array':
            return self._get_observation()
        else:
            super(PongEnv, self).render(mode=mode)

    def close(self):
        pygame.quit()

env = PongEnv()
observation = env.reset()
done = False

while not done:
    action = env.action_space.sample()  # Escolhe uma ação aleatória (substitua por sua estratégia de agente)
    observation, reward, done, _ = env.step(action)
    env.render()  # Renderiza a tela (modo 'human')

env.close()  # Fecha o ambiente

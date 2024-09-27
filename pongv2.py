import gym
import pygame
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
# Defina as cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class PongEnv(gym.Env):
    def __init__(self):
        super(PongEnv, self).__init__()

        # Inicialização do Pygame
        pygame.init()

        # Configurações da tela
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong")

        # Defina os limites da mesa (retângulo)
        self.table_rect = pygame.Rect(50, 50, self.WIDTH - 100, self.HEIGHT - 100)

        # Inicialização das posições e velocidades da bola e das raquetes
        self.ball_x, self.ball_y = self.WIDTH // 2, self.HEIGHT // 2
        self.ball_speed_x, self.ball_speed_y = 14 * np.random.choice((1, -1)), 14 * np.random.choice((1, -1))
        self.left_paddle_y, self.right_paddle_y = self.HEIGHT // 2 - 50, self.HEIGHT // 2 - 50

        # Velocidade da raquete
        self.paddle_speed = 20

        # Pontuação
        self.left_score, self.right_score = 0, 0

        # Inicialização da rede neural
        self.model = self.create_model()
        self.epsilon = 0.1  # Parâmetro epsilon para a política epsilon-greedy
        self.alpha = 0.1  # Taxa de aprendizado
        self.gamma = 0.99  # Fator de desconto

        # Fonte para exibir a pontuação na tela
        self.font = pygame.font.Font(None, 36)

        # Variável para rastrear a recompensa total do episódio
        self.total_reward = 0

        # Variável para rastrear o modo de jogo da raquete esquerda (humano ou automático)
        self.human_play_mode = False

        # Variável para rastrear as ações do jogador humano
        self.human_action = 1  # Começa com a ação de ficar parado

    def create_model(self):
        # Crie uma rede neural simples para escolher a ação
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(32, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dense(3, activation='linear')  # 3 ações: mover para cima, ficar parado, mover para baixo
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def reset(self):
        # Reinicializa o ambiente para um novo episódio
        self.ball_x, self.ball_y = self.WIDTH // 2, self.HEIGHT // 2
        self.ball_speed_x, self.ball_speed_y = 14 * np.random.choice((1, -1)), 14 * np.random.choice((1, -1))
        self.left_paddle_y, self.right_paddle_y = self.HEIGHT // 2 - 50, self.HEIGHT // 2 - 50
        self.left_score, self.right_score = 0, 0  # Reinicia a pontuação

        # Reinicializa a recompensa total
        self.total_reward = 0

        return np.array([self.ball_x, self.ball_y, self.left_paddle_y, self.right_paddle_y])

    def reset_ball(self):
        # Reinicializa a posição da bola
        self.ball_x, self.ball_y = self.WIDTH // 2, self.HEIGHT // 2
        self.ball_speed_x, self.ball_speed_y = 14 * np.random.choice((1, -1)), 14 * np.random.choice((1, -1))

    def step(self, action):
        # Inicialize a recompensa
        reward = 0

        # Inicialize q_values_current como um array de zeros
        q_values_current = np.zeros(3)  # 3 ações possíveis

        # Raquete esquerda segue a bola automaticamente
        if self.left_paddle_y + 50 < self.ball_y:
            self.left_paddle_y = min(self.left_paddle_y + self.paddle_speed, self.table_rect.bottom - 100)
        elif self.left_paddle_y + 50 > self.ball_y:
            self.left_paddle_y = max(self.left_paddle_y - self.paddle_speed, self.table_rect.top)

        # Ação epsilon-greedy
        if np.random.rand() < self.epsilon:
            action = np.random.choice([0, 1, 2])  # Escolha uma ação aleatória com probabilidade epsilon
        else:
            state = np.array([self.ball_x, self.ball_y, self.left_paddle_y, self.right_paddle_y])
            q_values_current = self.model.predict(state.reshape(1, -1))[0]

        # Mantenha uma cópia do estado atual
        state = np.array([self.ball_x, self.ball_y, self.left_paddle_y, self.right_paddle_y])

        # Movimento da raquete esquerda (controlada pelo agente)
        if action == 0:  # Ação 0: Mover para cima
            self.right_paddle_y = max(self.right_paddle_y - self.paddle_speed, self.table_rect.top)
        elif action == 1:  # Ação 1: Ficar parado
            pass
        elif action == 2:  # Ação 2: Mover para baixo
            self.right_paddle_y = min(self.right_paddle_y + self.paddle_speed, self.table_rect.bottom - 100)

        # Movimento da bola
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Verifica colisão da bola com as raquetes esquerda e direita
        if (self.ball_x <= 20 and self.left_paddle_y <= self.ball_y <= self.left_paddle_y + 100) or \
        (self.ball_x >= self.WIDTH - 30 and self.right_paddle_y <= self.ball_y <= self.right_paddle_y + 100):
            self.ball_speed_x *= -1

        # Verifica se a bola atingiu as paredes superior ou inferior
        if self.ball_y <= self.table_rect.top or self.ball_y >= self.table_rect.bottom - 20:
            self.ball_speed_y *= -1

        # Verifica se a bola saiu da tela pela esquerda (ponto para o jogador direito)
        if self.ball_x <= 0:
            self.right_score += 1
            reward = +1  # Pontuação do adversário, recompensa negativa
            self.reset_ball()

        # Verifica se a bola saiu da tela pela direita (ponto para o jogador esquerdo)
        if self.ball_x >= self.WIDTH:
            self.left_score += 1
            reward = -1  # Pontuação do agente, recompensa positiva
            self.reset_ball()

        # Atualiza a recompensa total do episódio
        self.total_reward += reward

        # Verifica se o episódio terminou (um dos lados atingiu 10 pontos)
        done = self.left_score >= 4 or self.right_score >= 4

        # Atualize as Q-values com base na equação Q-learning
        if not done:
            q_values_next = self.model.predict(state.reshape(1, -1))[0]
            td_error = reward + self.gamma * np.max(q_values_next) - q_values_current[action]
            q_values_current[action] += self.alpha * td_error
            self.model.fit(state.reshape(1, -1), q_values_current.reshape(1, -1), epochs=1, verbose=0)

        return np.array([self.ball_x, self.ball_y, self.left_paddle_y, self.right_paddle_y]), reward, done, {}


    def render(self):
        # Renderiza a tela
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.table_rect, 2)  # Desenha o retângulo da mesa
        pygame.draw.rect(self.screen, WHITE, (self.ball_x, self.ball_y, 20, 20))
        pygame.draw.rect(self.screen, WHITE, (10, self.left_paddle_y, 10, 100))
        pygame.draw.rect(self.screen, WHITE, (self.WIDTH - 20, self.right_paddle_y, 10, 100))

        # Exiba a pontuação na tela
        left_score_text = self.font.render(f"Player 1: {self.left_score}", True, WHITE)
        right_score_text = self.font.render(f"Player 2: {self.right_score}", True, WHITE)
        reward_text = self.font.render(f"Reward: {self.total_reward}", True, WHITE)
        self.screen.blit(left_score_text, (20, 20))
        self.screen.blit(right_score_text, (self.WIDTH - 150, 20))
        self.screen.blit(reward_text, (self.WIDTH - 200, self.HEIGHT - 60))

        pygame.display.update()

    def close(self):
        # Encerra o ambiente
        pygame.quit()

    def train(self, num_episodes):
        for episode in range(num_episodes):
            state = self.reset()
            done = False
            self.total_reward = 0  # Inicializa a recompensa total para este episódio
            while not done:
                self.render()
                q_values = self.model.predict(np.array([state]).reshape(1, -1))
                action = np.argmax(q_values)
                next_state, reward, done, _ = self.step(action)
                state = next_state

            # Exibe o número do episódio e a recompensa total
            print(f"Episodio {episode + 1}/{num_episodes}, Recompensa: {self.total_reward}")

            # Verifica se o episódio terminou (um dos lados atingiu 10 pontos) e reinicia o episódio
            if self.left_score >= 4 or self.right_score >= 4:
                state = self.reset()

        # Salve o modelo treinado
        self.model.save('pong_model.h5')

if __name__ == "__main__":
    env = PongEnv()
    #num_episodes = 50  # Número de episódios para treinamento
    #env.train(num_episodes)
     # Carregue o modelo treinado
    model_path = 'pong_model.h5'
    model = tf.keras.models.load_model(model_path)

    state = env.reset()
    running = True
    while running:
        env.render()

        # Ação do agente (rede neural) para a raquete direita
        q_values = model.predict(np.array([state]).reshape(1, -1))
        agent_action = np.argmax(q_values)

        # Ação da raquete esquerda (humano ou automático)
        env.step(agent_action)

        next_state, _, done, _ = env.step(agent_action)
        state = next_state

        if done:
            state = env.reset()

    env.close()

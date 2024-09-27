# Pong com Aprendizado por Reforço

🎮 Este projeto implementa um jogo de Pong utilizando a biblioteca **Gym** para o ambiente e **Pygame** para a renderização. O agente utiliza uma rede neural treinada para controlar a raquete direita, enquanto a raquete esquerda pode ser controlada por um humano ou seguir automaticamente a bola.

## 📦 Dependências

Certifique-se de ter as seguintes bibliotecas instaladas:

```bash
pip install gym pygame tensorflow numpy
```

## ⚙️ Estrutura do Código

### Classes e Métodos Principais

### PongEnv
Classe que representa o ambiente do jogo.

- **`__init__()`**: Inicializa o ambiente, configura a tela, as raquetes, a bola e a rede neural.
- **`create_model()`**: Cria a rede neural para a tomada de decisão do agente.
- **`reset()`**: Reinicializa o jogo para um novo episódio.
- **`step(action)`**: Executa a ação do agente e atualiza a posição da bola e das raquetes.
- **`render()`**: Renderiza o jogo na tela.
- **`train(num_episodes)`**: Treina a rede neural em múltiplos episódios.

### Algoritmo de Aprendizado

O agente utiliza um algoritmo de Q-learning com uma rede neural para estimar os valores de Q para as ações possíveis. A política epsilon-greedy é utilizada para equilibrar exploração e exploração, permitindo que o agente aprenda a jogar ao longo do tempo.

## 🚀 Executando o Jogo

Para treinar o agente:
```bash
if __name__ == "__main__":
    env = PongEnv()
    num_episodes = 50  # Número de episódios para treinamento
    env.train(num_episodes)
```

Para jogar com o modelo treinado:
```bash
if __name__ == "__main__":
    env = PongEnv()
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

```

## 🎯 Objetivos

- Treinar um agente que jogue Pong de forma autônoma.
- Experimentar com diferentes arquiteturas de rede neural e parâmetros de treinamento.
- Permitir que o usuário jogue contra um agente treinado.

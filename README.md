# 🃏 Duelo de Cartas Probabilístico

Um jogo de estratégia em turnos desenvolvido para demonstrar visualmente o comportamento de **eventos aleatórios em tempo real** e a convergência da **frequência empírica** para a **probabilidade teórica** (Lei dos Grandes Números).

Projeto desenvolvido para a disciplina de Estatística do Prof. Guilherme Pereira.

-----

## 📸 Screenshots

*(Espaço reservado para colocar prints do jogo: uma mostrando o campo de batalha e outra focando no gráfico lateral)*

-----

## 🎯 Objetivo do Projeto

O objetivo principal não é apenas vencer o oponente, mas observar como a aleatoriedade se comporta ao longo do tempo. O jogo possui uma tela dividida (Split Screen):

1.  **Esquerda (Game):** Simulação em tempo real de um duelo de cartas (Ataque, Defesa, Cura).
2.  **Direita (Stats):** Um histograma dinâmico que compara:
      * **Linha Tracejada:** Probabilidade Teórica (o que *deveria* acontecer matematicamente).
      * **Barra Sólida:** Frequência Empírica (o que *realmente* aconteceu na partida).

-----

## 🎮 Como Jogar

### Regras Básicas

O jogo é um duelo 1v1 contra uma Inteligência Artificial (IA).

  * **Vida (HP):** Ambos começam com 20 HP.
  * **Cartas:** Existem 3 tipos de cartas no baralho:
      * ⚔️ **Ataque (50% do deck):** Causa 5 de dano.
      * 🛡️ **Defesa (30% do deck):** Adiciona 5 de escudo (máx 10).
      * 💚 **Cura (20% do deck):** Recupera 3 de vida.
  * **Turnos:**
    1.  O jogador compra uma carta.
    2.  Escolhe uma carta da mão para jogar.
    3.  A IA joga o turno dela.
  * **Vitória:** Reduza o HP do oponente a zero.

### Controles

  * **Mouse:** Clicar para comprar e selecionar cartas.
  * **R:** Reiniciar o jogo (Disponível na tela de Game Over).
  * **F11:** Alternar Tela Cheia.
  * **ESC:** Sair do jogo.

-----

## 📊 Conceitos Estatísticos Abordados

### 1\. Distribuição de Probabilidade

O baralho é construído com uma distribuição fixa:

  * Total: 20 Cartas.
  * 10 de Ataque ($P(A) = 0.50$).
  * 6 de Defesa ($P(D) = 0.30$).
  * 4 de Cura ($P(C) = 0.20$).

### 2\. Validação via Monte Carlo

O projeto inclui um script de validação (`simulacao_monte_carlo.py`) que roda 10.000 partidas simuladas instantaneamente. Isso serve para provar que o algoritmo de embaralhamento (`random.shuffle`) é imparcial e que, no longo prazo, os resultados do jogo convergem para a curva ideal.

-----

## 🛠️ Instalação e Execução

### Pré-requisitos

  * Python 3.10 ou superior.
  * Biblioteca `pygame`.

### Passo a Passo

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/Vinib80/jogo-estatistica.git
    cd jogo-estatistica
    ```

2.  **Instale as dependências:**

    ```bash
    pip install pygame
    ```

3.  **Execute o Jogo:**

    ```bash
    python main.py
    ```

4.  **Execute a Simulação Estatística (Opcional):**

    ```bash
    python simulacao_monte_carlo.py
    ```

-----

## 📂 Estrutura do Projeto

  * `main.py`: Loop principal, renderização gráfica e gerenciamento de estados.
  * `baralho.py`: Lógica de probabilidade, embaralhamento e reciclagem de descarte.
  * `jogador.py`: Classes para o Jogador e IA (Vida, Mão, Defesa).
  * `carta.py`: Renderização híbrida (Sprite ou Geometria) e atributos das cartas.
  * `simulacao_monte_carlo.py`: Script matemático de validação de dados.
  * `assets/`: Pasta contendo sprites (`.png`) para cartas e avatares.

-----

## 👥 Autores

Trabalho desenvolvido pelos alunos:

  * **Henrique Figuêiredo Tefil**
  * **Julia Torres de Barros**
  * **Maria Clara Neves**
  * **Vinícius Bernardo da Silva**

-----

## ✅ Checklist de Requisitos (Professor)

  - [x] Simulação de eventos aleatórios em tempo real.
  - [x] Visualização simultânea da distribuição de probabilidade.
  - [x] Comparação entre curva ideal (teórica) e resultados empíricos.
  - [x] Jogo funcional (Criatividade/Jogabilidade).
  - [x] Código organizado e documentado.

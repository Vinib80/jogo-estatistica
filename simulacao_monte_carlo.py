import statistics
import pygame
from baralho import Deck
from carta import Card


def run_simulation():
    """
    Executa uma simulação de Monte Carlo para validar as probabilidades do baralho.

    Realiza múltiplas simulações de compra de cartas para verificar se a distribuição
    empírica converge para as probabilidades teóricas esperadas.
    """
    pygame.init()
    NUM_SIMULACOES = 10000

    print(f"Iniciando {NUM_SIMULACOES} simulações de Monte Carlo...")
    print("Objetivo: Validar integridade do baralho e probabilidades.")

    # Armazena a porcentagem de cada tipo em cada simulação
    historico_porcentagens = {
        Card.ATAQUE: [],
        Card.DEFESA: [],
        Card.CURA: []
    }

    for i in range(NUM_SIMULACOES):
        deck = Deck()
        cartas_compradas = []

        # Esvazia o baralho
        while not deck.esta_vazio():
            carta = deck.comprar_carta()
            if carta:
                cartas_compradas.append(carta.tipo)

        total_cartas = len(cartas_compradas)
        if total_cartas == 0:
            continue

        contagem = {
            Card.ATAQUE: cartas_compradas.count(Card.ATAQUE),
            Card.DEFESA: cartas_compradas.count(Card.DEFESA),
            Card.CURA: cartas_compradas.count(Card.CURA)
        }

        for tipo in historico_porcentagens:
            pct = (contagem[tipo] / total_cartas) * 100
            historico_porcentagens[tipo].append(pct)

    print("-" * 65)
    print(f"{'TIPO':<10} | {'TEÓRICA':<10} | {'MÉDIA OBS.':<12} | {'DESVIO PAD.':<12} | {'ERRO':<10}")
    print("-" * 65)

    prob_teorica = {
        Card.ATAQUE: 50.0,
        Card.DEFESA: 30.0,
        Card.CURA: 20.0
    }

    erro_maximo_detectado = 0.0

    for tipo in [Card.ATAQUE, Card.DEFESA, Card.CURA]:
        dados = historico_porcentagens[tipo]
        media = statistics.mean(dados)
        desvio = statistics.stdev(dados) if len(dados) > 1 else 0.0
        teorica = prob_teorica[tipo]
        erro = abs(media - teorica)

        if erro > erro_maximo_detectado:
            erro_maximo_detectado = erro

        print(
            f"{tipo:<10} | {teorica:>9.2f}% | {media:>11.4f}% | {desvio:>11.4f} | {erro:>9.4f}%")

    print("-" * 65)

    if erro_maximo_detectado > 1.0:
        print("\n[ALERTA] ⚠️  Viés detectado! O erro é maior que 1%.")
        print("Verifique a lógica de criação do baralho ou o random.shuffle.")
    else:
        print("\n[SUCESSO] ✅ A simulação confirmou as probabilidades teóricas.")
        print("O desvio é mínimo ou inexistente, indicando consistência no baralho.")


if __name__ == "__main__":
    run_simulation()

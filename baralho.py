import logging
import random
from carta import Card


class Deck:
    """Representa o baralho do jogo"""

    def __init__(self):
        """Inicializa o baralho com 20 cartas"""
        self.cartas = []
        self.cartas_iniciais = {
            Card.ATAQUE: 10,
            Card.DEFESA: 6,
            Card.CURA: 4
        }
        self.criar_baralho()

    def criar_baralho(self):
        """Cria o baralho completo com todas as cartas"""
        self.cartas = []
        self.historico_cartas = []
        self.descarte = []

        # Adiciona 10 cartas de Ataque
        for _ in range(self.cartas_iniciais[Card.ATAQUE]):
            self.cartas.append(Card(Card.ATAQUE))

        # Adiciona 6 cartas de Defesa
        for _ in range(self.cartas_iniciais[Card.DEFESA]):
            self.cartas.append(Card(Card.DEFESA))

        # Adiciona 4 cartas de Cura
        for _ in range(self.cartas_iniciais[Card.CURA]):
            self.cartas.append(Card(Card.CURA))

        # Embaralha o baralho
        self.embaralhar()

    def embaralhar(self):
        """Embaralha as cartas do baralho"""
        random.shuffle(self.cartas)

    def comprar_carta(self):
        """
        Remove e retorna a primeira carta do baralho.
        Se o baralho estiver vazio, recicla o descarte.

        Returns:
            Card: A carta comprada, ou None se o baralho e descarte estiverem vazios
        """
        if len(self.cartas) == 0 and len(self.descarte) > 0:
            logging.info("Baralho vazio! Embaralhando descarte...")
            self.cartas = self.descarte[:]
            self.descarte = []
            self.embaralhar()

        if len(self.cartas) > 0:
            carta = self.cartas.pop(0)
            self.historico_cartas.append(carta.tipo)
            return carta
        return None

    def adicionar_ao_descarte(self, carta):
        """Adiciona uma carta usada ao monte de descarte"""
        if carta:
            self.descarte.append(carta)

    def cartas_restantes(self):
        """
        Retorna a quantidade de cartas restantes no baralho

        Returns:
            int: Número de cartas no baralho
        """
        return len(self.cartas)

    def contar_por_tipo(self):
        """
        Conta quantas cartas de cada tipo ainda restam no baralho

        Returns:
            dict: Dicionário com a contagem de cada tipo
                  Ex: {'Ataque': 5, 'Defesa': 3, 'Cura': 2}
        """
        contagem = {
            Card.ATAQUE: 0,
            Card.DEFESA: 0,
            Card.CURA: 0
        }

        for carta in self.cartas:
            contagem[carta.tipo] += 1

        return contagem

    def calcular_probabilidades(self):
        """
        Calcula a probabilidade de comprar cada tipo de carta

        Returns:
            dict: Dicionário com as probabilidades em percentual
                  Ex: {'Ataque': 50.0, 'Defesa': 30.0, 'Cura': 20.0}
        """
        total = self.cartas_restantes()

        if total == 0:
            return {
                Card.ATAQUE: 0.0,
                Card.DEFESA: 0.0,
                Card.CURA: 0.0
            }

        contagem = self.contar_por_tipo()
        probabilidades = {}

        for tipo, quantidade in contagem.items():
            # Calcula a probabilidade como percentual
            probabilidades[tipo] = (quantidade / total) * 100

        return probabilidades

    def calcular_frequencia_empirica(self):
        """
        Calcula a frequência empírica de cada tipo de carta baseada no histórico

        Returns:
            dict: Dicionário com as frequências em percentual
        """
        total_comprado = len(self.historico_cartas)

        if total_comprado == 0:
            return {
                Card.ATAQUE: 0.0,
                Card.DEFESA: 0.0,
                Card.CURA: 0.0
            }

        contagem = {
            Card.ATAQUE: 0,
            Card.DEFESA: 0,
            Card.CURA: 0
        }

        for tipo in self.historico_cartas:
            contagem[tipo] += 1

        frequencias = {}
        for tipo, quantidade in contagem.items():
            frequencias[tipo] = (quantidade / total_comprado) * 100

        return frequencias

    def esta_vazio(self):
        """
        Verifica se o baralho está vazio

        Returns:
            bool: True se vazio, False caso contrário
        """
        return len(self.cartas) == 0

    def resetar(self):
        """Recria e embaralha o baralho do zero"""
        self.criar_baralho()

    def __str__(self):
        """Representação em string do baralho"""
        contagem = self.contar_por_tipo()
        return f"Deck({self.cartas_restantes()} cartas: {contagem})"

    def __repr__(self):
        return self.__str__()

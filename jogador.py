import pygame
from carta import Card


class Player:
    """Representa um jogador do jogo"""

    HP_MAXIMO = 20
    TAMANHO_MAO = 4  # Aumentado para 4 (compra 1, depois joga 1)
    MAX_DEFESA = 10

    def __init__(self, nome, x=0, y=0, avatar=None):
        """
        Inicializa um jogador

        Args:
            nome: Nome do jogador (ex: "Jogador", "IA")
            x: Posição X para desenhar o jogador
            y: Posição Y para desenhar o jogador
            avatar: Imagem (Surface) do avatar do jogador
        """
        self.nome = nome
        self.hp = self.HP_MAXIMO
        self.mao = []  # Lista de cartas na mão
        self.defesa_ativa = 0  # Pontos de defesa acumulados
        self.x = x
        self.y = y
        self.avatar = avatar

        # Fontes para renderizar
        self.fonte_nome = pygame.font.Font(None, 32)
        self.fonte_hp = pygame.font.Font(None, 28)

    def adicionar_carta(self, carta):
        """
        Adiciona uma carta à mão do jogador

        Args:
            carta: Objeto Card a ser adicionado

        Returns:
            bool: True se conseguiu adicionar, False se a mão está cheia
        """
        if len(self.mao) < self.TAMANHO_MAO:
            self.mao.append(carta)
            return True
        return False

    def comprar_carta(self, deck):
        """
        Compra uma carta do baralho e adiciona à mão

        Args:
            deck: Objeto Deck de onde comprar a carta

        Returns:
            bool: True se conseguiu comprar, False se a mão está cheia ou deck vazio
        """
        if len(self.mao) >= self.TAMANHO_MAO:
            return False

        carta = deck.comprar_carta()
        if carta is not None:
            self.mao.append(carta)
            return True
        return False

    def jogar_carta(self, indice):
        """
        Joga (remove) uma carta da mão pelo índice (0 a 3)

        Args:
            indice: Índice da carta na mão (0 a 3)

        Returns:
            Card ou None: A carta jogada, ou None se índice inválido
        """
        if 0 <= indice < len(self.mao):
            return self.mao.pop(indice)
        return None

    def receber_dano(self, dano):
        """
        Recebe dano, considerando a defesa ativa

        Args:
            dano: Quantidade de dano a receber

        Returns:
            int: Dano real recebido (após defesa)
        """
        if self.defesa_ativa > 0:
            # A defesa bloqueia o dano
            dano_bloqueado = min(dano, self.defesa_ativa)
            self.defesa_ativa -= dano_bloqueado
            dano -= dano_bloqueado

        # Aplica o dano restante
        self.hp -= dano
        if self.hp < 0:
            self.hp = 0

        return dano

    def curar(self, quantidade):
        """
        Cura o jogador

        Args:
            quantidade: Quantidade de HP a recuperar

        Returns:
            int: HP real curado (limitado ao máximo)
        """
        hp_antes = self.hp
        self.hp += quantidade
        if self.hp > self.HP_MAXIMO:
            self.hp = self.HP_MAXIMO

        return self.hp - hp_antes

    def adicionar_defesa(self, quantidade):
        """
        Adiciona pontos de defesa

        Args:
            quantidade: Quantidade de defesa a adicionar
        """
        self.defesa_ativa += quantidade
        if self.defesa_ativa > self.MAX_DEFESA:
            self.defesa_ativa = self.MAX_DEFESA

    def resetar_defesa(self):
        """Remove toda a defesa ativa (usado no início do turno)"""
        self.defesa_ativa = 0

    def esta_vivo(self):
        """
        Verifica se o jogador ainda está vivo

        Returns:
            bool: True se HP > 0, False caso contrário
        """
        return self.hp > 0

    def atualizar(self):
        """Atualiza o estado do jogador e suas cartas"""
        for carta in self.mao:
            carta.atualizar()

    def desenhar(self, tela):
        """Desenha as informações do jogador na tela"""
        # Desenha o avatar se existir
        offset_x = 0
        if self.avatar:
            tela.blit(self.avatar, (self.x, self.y))
            # Desloca o texto para a direita (assumindo avatar ~100px)
            offset_x = 110

        # Nome do jogador
        cor_nome = (255, 255, 255)
        texto_nome = self.fonte_nome.render(self.nome, True, cor_nome)
        tela.blit(texto_nome, (self.x + offset_x, self.y))

        # HP (com cor baseada na vida)
        if self.hp > 14:
            cor_hp = (50, 200, 80)  # Verde (vida alta)
        elif self.hp > 7:
            cor_hp = (255, 200, 50)  # Amarelo (vida média)
        else:
            cor_hp = (220, 50, 50)  # Vermelho (vida baixa)

        texto_hp = self.fonte_hp.render(
            f"HP: {self.hp}/{self.HP_MAXIMO}", True, cor_hp)
        tela.blit(texto_hp, (self.x + offset_x, self.y + 35))

        # Defesa ativa (se houver)
        if self.defesa_ativa > 0:
            if self.defesa_ativa >= self.MAX_DEFESA:
                cor_defesa = (0, 255, 255)  # Ciano para defesa máxima
            else:
                cor_defesa = (50, 120, 220)

            texto_defesa = self.fonte_hp.render(
                f"[DEF: {self.defesa_ativa}]", True, cor_defesa)
            tela.blit(texto_defesa, (self.x + offset_x, self.y + 65))

    def desenhar_mao(self, tela, x_inicio, y_inicio, assets=None, espacamento=120):
        """
        Desenha as cartas da mão do jogador

        Args:
            tela: Superfície do Pygame onde desenhar
            x_inicio: Posição X inicial da primeira carta
            y_inicio: Posição Y das cartas
            assets: Dicionário de imagens (sprites) das cartas
            espacamento: Distância entre cartas
        """
        for i, carta in enumerate(self.mao):
            carta.definir_posicao(x_inicio + (i * espacamento), y_inicio)

            imagem = None
            if assets:
                imagem = assets.get(carta.tipo)

            carta.desenhar(tela, imagem_sprite=imagem)

    def __str__(self):
        """Representação em string do jogador"""
        return f"Player({self.nome}, HP:{self.hp}, Cartas:{len(self.mao)})"

    def __repr__(self):
        return self.__str__()

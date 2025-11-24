import pygame


class Card:
    """Representa uma carta do jogo"""

    # Tipos de carta
    ATAQUE = "Ataque"
    DEFESA = "Defesa"
    CURA = "Cura"

    # Dimensões da carta
    LARGURA = 100
    ALTURA = 140

    # Cores por tipo de carta
    CORES = {
        ATAQUE: (220, 50, 50),   # Vermelho
        DEFESA: (50, 120, 220),  # Azul
        CURA: (50, 200, 80)      # Verde
    }

    # Fontes (Carregadas sob demanda)
    fonte_nome = None
    fonte_valor = None

    def __init__(self, tipo, x=0, y=0):
        """
        Inicializa uma carta

        Args:
            tipo: Tipo da carta (ATAQUE, DEFESA ou CURA)
            x: Posição X inicial
            y: Posição Y inicial
        """
        self.tipo = tipo
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.rect = pygame.Rect(x, y, self.LARGURA, self.ALTURA)

        # Inicializa fontes da classe se necessário
        if Card.fonte_nome is None:
            Card.fonte_nome = pygame.font.Font(None, 24)
        if Card.fonte_valor is None:
            Card.fonte_valor = pygame.font.Font(None, 48)

        # Cores
        self.cor_fundo = self.CORES.get(tipo, (100, 100, 100))
        self.cor_borda = (255, 255, 255)
        self.cor_texto = (255, 255, 255)

        # Valores das cartas
        self.valores = {
            self.ATAQUE: 5,
            self.DEFESA: 5,
            self.CURA: 3
        }

        # Estado visual
        self.destacada = False  # Para quando passar o mouse

    def definir_posicao(self, x, y):
        """Define a posição alvo da carta"""
        self.target_x = x
        self.target_y = y

    def contem_ponto(self, x, y):
        """Verifica se um ponto (x, y) está dentro da carta"""
        return self.rect.collidepoint(x, y)

    def desenhar(self, tela, imagem_sprite=None):
        """Desenha a carta na tela"""
        # Fundo da carta
        pygame.draw.rect(tela, self.cor_fundo, self.rect, border_radius=10)

        # Imagem (Sprite)
        if imagem_sprite:
            tela.blit(imagem_sprite, (self.rect.x, self.rect.y))
        else:
            # Fallback: Desenha textos apenas se não houver imagem
            # Nome do tipo (topo)
            texto_nome = Card.fonte_nome.render(
                self.tipo, True, self.cor_texto)
            nome_rect = texto_nome.get_rect(
                center=(self.rect.centerx, self.rect.y + 25))
            tela.blit(texto_nome, nome_rect)

            # Valor (centro)
            valor = self.valores.get(self.tipo, 0)
            texto_valor = Card.fonte_valor.render(
                str(valor), True, self.cor_texto)
            valor_rect = texto_valor.get_rect(center=self.rect.center)
            tela.blit(texto_valor, valor_rect)

            # Símbolo ASCII (abaixo do valor)
            simbolos = {
                self.ATAQUE: "ATK",
                self.DEFESA: "DEF",
                self.CURA: "HP+"
            }
            simbolo = simbolos.get(self.tipo, "?")
            fonte_simbolo = pygame.font.Font(None, 28)
            texto_simbolo = fonte_simbolo.render(simbolo, True, self.cor_texto)
            simbolo_rect = texto_simbolo.get_rect(
                center=(self.rect.centerx, self.rect.bottom - 30))
            tela.blit(texto_simbolo, simbolo_rect)

        # Borda (mais grossa se destacada)
        espessura_borda = 4 if self.destacada else 2
        pygame.draw.rect(tela, self.cor_borda, self.rect,
                         espessura_borda, border_radius=10)

    def __str__(self):
        """Representação em string da carta"""
        return f"Card({self.tipo})"

    def __repr__(self):
        return self.__str__()

    def atualizar(self):
        """Atualiza a posição da carta com animação suave (Lerp)"""
        # Interpolação linear para X
        self.x += (self.target_x - self.x) * 0.1
        if abs(self.target_x - self.x) < 1:
            self.x = self.target_x

        # Interpolação linear para Y
        self.y += (self.target_y - self.y) * 0.1
        if abs(self.target_y - self.y) < 1:
            self.y = self.target_y

        # Atualiza o rect para colisão e desenho
        self.rect.topleft = (int(self.x), int(self.y))

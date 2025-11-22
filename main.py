from jogador import Player
import pygame
import sys
import random
from carta import Card
from baralho import Deck

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA_TELA = 1200
ALTURA_TELA = 600
FPS = 60

# Cores (RGB)
COR_FUNDO = (20, 20, 30)
COR_AREA_JOGO = (40, 40, 60)
COR_AREA_STATS = (30, 50, 40)
COR_BORDA = (100, 100, 120)
COR_TEXTO = (255, 255, 255)

# Divisão da Tela
LARGURA_JOGO = int(LARGURA_TELA * 0.65)  # 65% para o jogo
LARGURA_STATS = LARGURA_TELA - LARGURA_JOGO  # 35% para estatísticas


class JogoDuelo:
    def __init__(self):
        # Configuração da janela
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Duelo de Cartas Probabilístico")
        self.relogio = pygame.time.Clock()
        self.rodando = True

        # Fonte para textos
        self.fonte_titulo = pygame.font.Font(None, 36)
        self.fonte_texto = pygame.font.Font(None, 24)

        # Baralho do jogo
        self.deck = Deck()

        # Jogadores
        self.ia = Player("IA", 50, 80)
        self.jogador = Player("VOCÊ", 50, 500)

        # Distribuir cartas iniciais (3 para cada)
        for _ in range(3):
            self.jogador.comprar_carta(self.deck)
            self.ia.comprar_carta(self.deck)

        # Sistema de turnos
        self.turno_jogador = True  # True = vez do jogador, False = vez da IA
        self.fase_turno = "comprar"  # "comprar" ou "jogar"
        self.carta_selecionada = None

        # Mensagens de feedback
        self.mensagem = "Seu turno! Clique para comprar uma carta."
        self.cor_mensagem = (255, 255, 100)

        # Controle de tempo da IA
        self.aguardando_ia = False
        self.tempo_espera_ia = 0
        self.estado_ia = None

    def processar_eventos(self):
        """Processa todos os eventos do Pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique esquerdo
                    self.processar_clique(evento.pos)
            elif evento.type == pygame.MOUSEMOTION:
                self.processar_hover(evento.pos)

    def atualizar(self):
        """Atualiza a lógica do jogo"""
        # Verifica se alguém morreu
        if not self.jogador.esta_vivo():
            self.mensagem = "VOCÊ PERDEU! A IA venceu!"
            self.cor_mensagem = (255, 50, 50)
        elif not self.ia.esta_vivo():
            self.mensagem = "VOCÊ VENCEU! Parabéns!"
            self.cor_mensagem = (50, 255, 50)

        # Verifica se é hora da IA jogar
        if self.aguardando_ia:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual >= self.tempo_espera_ia:
                self.executar_passo_ia()

    def processar_hover(self, pos):
        """Processa o movimento do mouse para destacar cartas"""
        if self.turno_jogador and self.fase_turno == "jogar":
            # Destaca cartas do jogador ao passar o mouse
            for carta in self.jogador.mao:
                carta.destacada = carta.contem_ponto(pos[0], pos[1])

    def processar_clique(self, pos):
        """Processa cliques do mouse"""
        if not self.turno_jogador:
            return  # Não é o turno do jogador

        if self.fase_turno == "comprar":
            # Qualquer clique compra uma carta
            self.comprar_carta_turno()
        elif self.fase_turno == "jogar":
            # Verifica se clicou em alguma carta da mão
            for i, carta in enumerate(self.jogador.mao):
                if carta.contem_ponto(pos[0], pos[1]):
                    self.jogar_carta_turno(i)
                    break

    def comprar_carta_turno(self):
        """Jogador compra uma carta no início do turno"""
        if self.jogador.comprar_carta(self.deck):
            self.mensagem = "Carta comprada! Agora escolha uma carta para jogar."
            self.cor_mensagem = (100, 255, 100)
            self.fase_turno = "jogar"
        else:
            self.mensagem = "Não foi possível comprar carta!"
            self.cor_mensagem = (255, 100, 100)

    def jogar_carta_turno(self, indice):
        """Jogador joga uma carta"""
        carta = self.jogador.jogar_carta(indice)
        if carta:
            # Adiciona ao descarte
            self.deck.adicionar_ao_descarte(carta)

            # Aplica o efeito da carta
            self.aplicar_efeito_carta(carta, self.jogador, self.ia)

            # Passa o turno para a IA
            self.passar_turno()

            # Agenda o turno da IA
            self.aguardando_ia = True
            self.estado_ia = "IA_COMPRAR"
            self.tempo_espera_ia = pygame.time.get_ticks() + 500

    def aplicar_efeito_carta(self, carta, jogador_ativo, oponente):
        """Aplica o efeito de uma carta"""
        if carta.tipo == Card.ATAQUE:
            dano = carta.valores[Card.ATAQUE]
            dano_real = oponente.receber_dano(dano)
            self.mensagem = f"{jogador_ativo.nome} atacou! {dano_real} de dano!"
            self.cor_mensagem = (255, 100, 100)

        elif carta.tipo == Card.DEFESA:
            defesa = carta.valores[Card.DEFESA]
            jogador_ativo.adicionar_defesa(defesa)
            self.mensagem = f"{jogador_ativo.nome} defendeu! +{defesa} de defesa!"
            self.cor_mensagem = (100, 150, 255)

        elif carta.tipo == Card.CURA:
            cura = carta.valores[Card.CURA]
            cura_real = jogador_ativo.curar(cura)
            self.mensagem = f"{jogador_ativo.nome} se curou! +{cura_real} HP!"
            self.cor_mensagem = (100, 255, 100)

    def passar_turno(self):
        """Passa o turno para o outro jogador"""
        self.turno_jogador = not self.turno_jogador
        self.fase_turno = "comprar"

    def executar_passo_ia(self):
        """Executa um passo do turno da IA (máquina de estados)"""
        #Verifica se o jogo terminou
        if not self.ia.esta_vivo() or not self.jogador.esta_vivo():
            self.aguardando_ia = False
            self.estado_ia = None
            return
        
        if self.estado_ia == "IA_COMPRAR":

            # IA compra uma carta
            self.ia.comprar_carta(self.deck)

            # Próximo estado: Jogar (após 300ms)
            self.estado_ia = "IA_JOGAR"
            self.tempo_espera_ia = pygame.time.get_ticks() + 300

        elif self.estado_ia == "IA_JOGAR":
            if len(self.ia.mao) > 0:
                indice = random.randint(0, len(self.ia.mao) - 1)
                carta = self.ia.jogar_carta(indice)

                if carta:
                    # Adiciona ao descarte
                    self.deck.adicionar_ao_descarte(carta)

                    # Aplica o efeito
                    self.aplicar_efeito_carta(carta, self.ia, self.jogador)

            # Próximo estado: Finalizar (após 500ms)
            self.estado_ia = "IA_FINALIZAR"
            self.tempo_espera_ia = pygame.time.get_ticks() + 500

        elif self.estado_ia == "IA_FINALIZAR":
            # Volta para o turno do jogador
            self.passar_turno()
            self.mensagem = "Seu turno! Clique para comprar uma carta."
            self.cor_mensagem = (255, 255, 100)
            self.aguardando_ia = False
            self.estado_ia = None

    def desenhar_interface(self):
        """Desenha a interface dividida do jogo"""
        # Fundo principal
        self.tela.fill(COR_FUNDO)

        # Área do Jogo (Esquerda)
        area_jogo = pygame.Rect(10, 10, LARGURA_JOGO - 20, ALTURA_TELA - 20)
        pygame.draw.rect(self.tela, COR_AREA_JOGO, area_jogo)
        pygame.draw.rect(self.tela, COR_BORDA, area_jogo, 3)

        # Título da área de jogo
        texto_jogo = self.fonte_titulo.render(
            "CAMPO DE BATALHA", True, COR_TEXTO)
        self.tela.blit(texto_jogo, (area_jogo.x + 20, area_jogo.y + 15))

        # Mensagem de feedback do jogo
        texto_msg = self.fonte_texto.render(
            self.mensagem, True, self.cor_mensagem)
        msg_rect = texto_msg.get_rect(
            center=(area_jogo.centerx, area_jogo.centery))
        self.tela.blit(texto_msg, msg_rect)

        # Área de Estatísticas (Direita)
        area_stats = pygame.Rect(
            LARGURA_JOGO + 10, 10, LARGURA_STATS - 20, ALTURA_TELA - 20)
        pygame.draw.rect(self.tela, COR_AREA_STATS, area_stats)
        pygame.draw.rect(self.tela, COR_BORDA, area_stats, 3)

        # Título da área de estatísticas
        texto_stats = self.fonte_titulo.render("ESTATÍSTICAS", True, COR_TEXTO)
        self.tela.blit(texto_stats, (area_stats.x + 20, area_stats.y + 15))

        # Desenha as estatísticas do baralho
        self.desenhar_estatisticas(area_stats)

    def desenhar_estatisticas(self, area):
        """Desenha as estatísticas do baralho no painel direito"""
        x_base = area.x + 20
        y_atual = area.y + 70

        # Total de cartas no baralho
        total = self.deck.cartas_restantes()
        texto_total = self.fonte_texto.render(
            f"Cartas no Baralho: {total}", True, COR_TEXTO)
        self.tela.blit(texto_total, (x_base, y_atual))
        y_atual += 40

        # Separador
        pygame.draw.line(self.tela, COR_BORDA, (x_base, y_atual),
                         (area.right - 20, y_atual), 2)
        y_atual += 20

        # Título: Contagem Empírica
        texto_empirica = self.fonte_titulo.render(
            "Contagem:", True, (255, 200, 100))
        self.tela.blit(texto_empirica, (x_base, y_atual))
        y_atual += 40

        # Contagem por tipo
        contagem = self.deck.contar_por_tipo()
        cores_tipo = {
            Card.ATAQUE: (220, 50, 50),
            Card.DEFESA: (50, 120, 220),
            Card.CURA: (50, 200, 80)
        }

        # Símbolos das cartas (igual às cartas do jogo)
        simbolos = {
            Card.ATAQUE: "ATK",
            Card.DEFESA: "DEF",
            Card.CURA: "HP+"
        }

        for tipo, quantidade in contagem.items():
            cor = cores_tipo[tipo]
            simbolo = simbolos[tipo]
            texto = self.fonte_texto.render(
                f"[{simbolo}] {tipo}: {quantidade}", True, cor)
            self.tela.blit(texto, (x_base + 10, y_atual))
            y_atual += 30

        y_atual += 20

        # Separador
        pygame.draw.line(self.tela, COR_BORDA, (x_base, y_atual),
                         (area.right - 20, y_atual), 2)
        y_atual += 20

        # Título: Probabilidades Teóricas
        texto_prob = self.fonte_titulo.render(
            "Probabilidades:", True, (100, 200, 255))
        self.tela.blit(texto_prob, (x_base, y_atual))
        y_atual += 40

        # Probabilidades por tipo
        probabilidades = self.deck.calcular_probabilidades()

        for tipo, prob in probabilidades.items():
            cor = cores_tipo[tipo]
            texto = self.fonte_texto.render(
                f"P({tipo}): {prob:.1f}%", True, cor)
            self.tela.blit(texto, (x_base + 10, y_atual))
            y_atual += 30

    def renderizar(self):
        """Renderiza tudo na tela"""
        self.desenhar_interface()

        # Desenha os jogadores
        self.ia.desenhar(self.tela)
        self.jogador.desenhar(self.tela)

        # Desenha as mãos dos jogadores
        self.ia.desenhar_mao(self.tela, 150, 150)
        self.jogador.desenhar_mao(self.tela, 150, 380)

        pygame.display.flip()

    def executar(self):
        """Loop principal do jogo"""
        print("🎮 Jogo iniciado! Pressione ESC para sair.")

        while self.rodando:
            self.processar_eventos()
            self.atualizar()
            self.renderizar()
            self.relogio.tick(FPS)

        self.encerrar()

    def encerrar(self):
        """Encerra o jogo corretamente"""
        print("👋 Encerrando o jogo...")
        pygame.quit()
        sys.exit()


# Ponto de entrada do programa
if __name__ == "__main__":
    jogo = JogoDuelo()
    jogo.executar()

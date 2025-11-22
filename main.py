from jogador import Player
import pygame
import sys
import random
from carta import Card
from baralho import Deck

# Inicialização do Pygame
pygame.init()

# Configurações da Janela (Resolução Virtual)
LARGURA_VIRTUAL = 1200
ALTURA_VIRTUAL = 600
FPS = 60

# Cores (RGB)
COR_FUNDO = (20, 20, 30)
COR_AREA_JOGO = (40, 40, 60)
COR_AREA_STATS = (30, 50, 40)
COR_BORDA = (100, 100, 120)
COR_TEXTO = (255, 255, 255)

# Divisão da Tela (Baseada na resolução virtual)
LARGURA_JOGO = int(LARGURA_VIRTUAL * 0.65)  # 65% para o jogo
LARGURA_STATS = LARGURA_VIRTUAL - LARGURA_JOGO  # 35% para estatísticas


class JogoDuelo:
    def __init__(self):
        # Configuração inicial das dimensões
        self.tela_cheia = False

        # Configuração da janela (física)
        self.tela = pygame.display.set_mode(
            (LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.RESIZABLE)

        # Superfície virtual para renderização (resolução fixa)
        self.superficie = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))

        pygame.display.set_caption("Duelo de Cartas Probabilístico")
        self.relogio = pygame.time.Clock()
        self.rodando = True

        # Fonte para textos
        self.fonte_titulo = pygame.font.Font(None, 36)
        self.fonte_texto = pygame.font.Font(None, 24)

        # Baralho do jogo
        self.deck = Deck()

        # Flag de debug: Pré-popular histórico
        DEBUG_HISTORICO = True
        if DEBUG_HISTORICO:
            for _ in range(10):
                self.deck.historico_cartas.append(Card.ATAQUE)

        # Jogadores (posições fixas na resolução virtual)
        self.ia = Player("IA", 50, 80)
        self.jogador = Player("VOCÊ", 50, 500)  # 500 é fixo na altura 600

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

    def converter_pos_mouse(self, pos):
        """Converte a posição do mouse da janela para a resolução virtual"""
        largura_janela, altura_janela = self.tela.get_size()
        scale_x = LARGURA_VIRTUAL / largura_janela
        scale_y = ALTURA_VIRTUAL / altura_janela
        return (int(pos[0] * scale_x), int(pos[1] * scale_y))

    def alternar_tela_cheia(self):
        """Alterna entre modo janela e tela cheia"""
        self.tela_cheia = not self.tela_cheia
        if self.tela_cheia:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.tela = pygame.display.set_mode(
                (LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.RESIZABLE)

    def processar_eventos(self):
        """Processa todos os eventos do Pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.VIDEORESIZE:
                if not self.tela_cheia:
                    self.tela = pygame.display.set_mode(
                        evento.size, pygame.RESIZABLE)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                elif evento.key == pygame.K_F11:
                    self.alternar_tela_cheia()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique esquerdo
                    pos_virtual = self.converter_pos_mouse(evento.pos)
                    self.processar_clique(pos_virtual)
            elif evento.type == pygame.MOUSEMOTION:
                pos_virtual = self.converter_pos_mouse(evento.pos)
                self.processar_hover(pos_virtual)

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
        # Verifica se o jogo terminou
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
        self.superficie.fill(COR_FUNDO)

        # Área do Jogo (Esquerda)
        area_jogo = pygame.Rect(10, 10, LARGURA_JOGO - 20, ALTURA_VIRTUAL - 20)
        pygame.draw.rect(self.superficie, COR_AREA_JOGO, area_jogo)
        pygame.draw.rect(self.superficie, COR_BORDA, area_jogo, 3)

        # Título da área de jogo
        texto_jogo = self.fonte_titulo.render(
            "CAMPO DE BATALHA", True, COR_TEXTO)
        self.superficie.blit(texto_jogo, (area_jogo.x + 20, area_jogo.y + 15))

        # Mensagem de feedback do jogo
        texto_msg = self.fonte_texto.render(
            self.mensagem, True, self.cor_mensagem)
        msg_rect = texto_msg.get_rect(
            center=(area_jogo.centerx, area_jogo.centery))
        self.superficie.blit(texto_msg, msg_rect)

        # Área de Estatísticas (Direita)
        area_stats = pygame.Rect(
            LARGURA_JOGO + 10, 10, LARGURA_STATS - 20, ALTURA_VIRTUAL - 20)
        pygame.draw.rect(self.superficie, COR_AREA_STATS, area_stats)
        pygame.draw.rect(self.superficie, COR_BORDA, area_stats, 3)

        # Desenha as estatísticas do baralho
        self.desenhar_estatisticas(area_stats)

    def desenhar_estatisticas(self, area):
        """Desenha as estatísticas do baralho no painel direito como histograma"""
        x_base = area.x + 20
        y_base = area.y + 60

        # Defensive calculation for graph dimensions with clamping
        largura_grafico = max(1, area.width - 40)
        altura_grafico = max(1, area.height - 100)

        # Check for minimum space requirements to draw meaningful graph
        if largura_grafico < 50 or altura_grafico < 50:
            texto_aviso = self.fonte_texto.render(
                "Área muito pequena", True, (255, 100, 100))
            self.superficie.blit(texto_aviso, (area.x + 10, area.y + 50))
            return

        # Título
        texto_titulo = self.fonte_titulo.render(
            "Probabilidades", True, COR_TEXTO)
        self.superficie.blit(texto_titulo, (x_base, area.y + 15))

        # Eixos
        eixo_x_start = (x_base, y_base + altura_grafico)
        eixo_x_end = (x_base + largura_grafico, y_base + altura_grafico)
        eixo_y_start = (x_base, y_base)
        eixo_y_end = (x_base, y_base + altura_grafico)

        pygame.draw.line(self.superficie, COR_TEXTO, eixo_x_start,
                         eixo_x_end, 2)  # Eixo X
        pygame.draw.line(self.superficie, COR_TEXTO, eixo_y_start,
                         eixo_y_end, 2)  # Eixo Y

        # Dados
        tipos = [Card.ATAQUE, Card.DEFESA, Card.CURA]
        prob_teorica = {Card.ATAQUE: 50, Card.DEFESA: 30, Card.CURA: 20}
        prob_empirica = self.deck.calcular_frequencia_empirica()

        cores_tipo = {
            Card.ATAQUE: (220, 50, 50),
            Card.DEFESA: (50, 120, 220),
            Card.CURA: (50, 200, 80)
        }

        # Configuração das barras
        num_tipos = len(tipos)
        if num_tipos == 0:
            return

        espaco_entre_grupos = 20
        largura_disponivel = largura_grafico - \
            (num_tipos + 1) * espaco_entre_grupos

        # Ensure positive width for groups
        if largura_disponivel <= 0:
            return

        largura_grupo = largura_disponivel / num_tipos
        largura_barra = largura_grupo / 2

        max_valor = 100  # Escala de 0 a 100%

        for i, tipo in enumerate(tipos):
            x_grupo = x_base + espaco_entre_grupos + \
                i * (largura_grupo + espaco_entre_grupos)

            # Barra Empírica - Sólida
            altura_empirica = (
                prob_empirica[tipo] / max_valor) * altura_grafico
            rect_empirica = pygame.Rect(
                x_grupo + largura_barra,
                y_base + altura_grafico - altura_empirica,
                largura_barra,
                altura_empirica
            )
            if rect_empirica.height > 0 and rect_empirica.width > 0:
                pygame.draw.rect(
                    self.superficie, cores_tipo[tipo], rect_empirica)  # Sólido

            # Texto Empírico
            texto_empirico = self.fonte_texto.render(
                f"E:{prob_empirica[tipo]:.1f}%", True, COR_TEXTO)
            rect_txt_empirico = texto_empirico.get_rect(
                midbottom=(rect_empirica.centerx, rect_empirica.top - 5))
            self.superficie.blit(texto_empirico, rect_txt_empirico)

            # Legenda do Eixo X
            texto_tipo = self.fonte_texto.render(tipo, True, COR_TEXTO)
            rect_txt_tipo = texto_tipo.get_rect(
                midtop=(x_grupo + largura_grupo/2, y_base + altura_grafico + 5))
            self.superficie.blit(texto_tipo, rect_txt_tipo)

        # Legenda Geral
        y_legenda = y_base + altura_grafico + 40

        # Check if we have space for legend
        if y_legenda + 20 < area.y + area.height:
            # Legenda Teórica
            pygame.draw.rect(self.superficie, (200, 200, 200),
                             (x_base, y_legenda, 20, 20), 2)
            texto_leg_teorica = self.fonte_texto.render(
                "Teórica (Fixo)", True, COR_TEXTO)
            self.superficie.blit(
                texto_leg_teorica, (x_base + 25, y_legenda + 2))

            # Legenda Empírica
            pygame.draw.rect(self.superficie, (200, 200, 200),
                             (x_base + 150, y_legenda, 20, 20))
            texto_leg_empirica = self.fonte_texto.render(
                "Empírica (Histórico)", True, COR_TEXTO)
            self.superficie.blit(texto_leg_empirica,
                                 (x_base + 175, y_legenda + 2))

    def renderizar(self):
        """Renderiza tudo na tela"""
        self.desenhar_interface()

        # Desenha os jogadores
        self.ia.desenhar(self.superficie)
        self.jogador.desenhar(self.superficie)

        # Desenha as mãos dos jogadores
        self.ia.desenhar_mao(self.superficie, 150, 150)
        self.jogador.desenhar_mao(self.superficie, 150, 380)

        # Escala a superfície virtual para o tamanho da janela
        scaled_surface = pygame.transform.smoothscale(
            self.superficie, self.tela.get_size())
        self.tela.blit(scaled_surface, (0, 0))

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

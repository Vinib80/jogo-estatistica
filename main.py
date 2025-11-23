from jogador import Player
import pygame
import sys
import random
import logging
from carta import Card
from baralho import Deck

# Configuração de Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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


class FloatingText:
    """
    Representa um texto flutuante que aparece na tela e desaparece gradualmente.
    Usado para feedback visual de dano, cura e defesa.
    """

    def __init__(self, texto, x, y, cor):
        """
        Inicializa o texto flutuante.

        Args:
            texto (str): O texto a ser exibido.
            x (int): Posição X inicial.
            y (int): Posição Y inicial.
            cor (tuple): Cor do texto em RGB.
        """
        self.texto = texto
        self.x = x
        self.y = y
        self.cor = cor
        self.alpha = 255
        self.vida = 60  # Duração em frames (1 segundo a 60 FPS)

    def atualizar(self):
        """Atualiza a posição e a transparência do texto."""
        self.y -= 1  # Sobe 1 pixel por frame
        self.vida -= 1
        if self.vida < 20:  # Fade out nos últimos 20 frames
            self.alpha = int((self.vida / 20) * 255)

    def desenhar(self, superficie, fonte):
        """
        Desenha o texto na superfície fornecida.

        Args:
            superficie (pygame.Surface): Superfície onde desenhar.
            fonte (pygame.font.Font): Fonte a ser usada.
        """
        if self.vida > 0:
            texto_surf = fonte.render(self.texto, True, self.cor)
            texto_surf.set_alpha(self.alpha)
            superficie.blit(texto_surf, (self.x, self.y))


class JogoDuelo:
    """
    Classe principal que gerencia o jogo de duelo de cartas.
    Controla o loop do jogo, eventos, renderização e lógica de turnos.
    """

    def __init__(self):
        """Inicializa o jogo, configurando janela, baralho e jogadores."""
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
        DEBUG_HISTORICO = False
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

        # Estado de Game Over
        self.game_over = False

        # Efeitos Visuais
        self.textos_flutuantes = []
        self.flash_dano_timer = 0

    def adicionar_texto_flutuante(self, texto, x, y, cor):
        """Adiciona um texto flutuante à lista"""
        self.textos_flutuantes.append(FloatingText(texto, x, y, cor))

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
                elif self.game_over and evento.key == pygame.K_r:
                    self.reiniciar_jogo()
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
            self.game_over = True
        elif not self.ia.esta_vivo():
            self.mensagem = "VOCÊ VENCEU! Parabéns!"
            self.cor_mensagem = (50, 255, 50)
            self.game_over = True

        if self.game_over:
            return

        # Atualiza efeitos visuais
        if self.flash_dano_timer > 0:
            self.flash_dano_timer -= 1

        for texto in self.textos_flutuantes[:]:
            texto.atualizar()
            if texto.vida <= 0:
                self.textos_flutuantes.remove(texto)

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

            # Texto flutuante de ação
            cor_texto_flutuante = (255, 255, 50)  # Amarelo
            self.adicionar_texto_flutuante(
                f"Jogou {carta.tipo}!",
                self.jogador.x + 20, self.jogador.y - 40, cor_texto_flutuante)

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

            # Visual: Texto flutuante no oponente
            self.adicionar_texto_flutuante(
                f"-{dano_real} HP", oponente.x + 20, oponente.y - 20, (255, 50, 50))

            # Visual: Flash de tela se houve dano
            if dano_real > 0:
                self.flash_dano_timer = 10

        elif carta.tipo == Card.DEFESA:
            defesa = carta.valores[Card.DEFESA]
            jogador_ativo.adicionar_defesa(defesa)
            self.mensagem = f"{jogador_ativo.nome} defendeu! +{defesa} de defesa!"
            self.cor_mensagem = (100, 150, 255)

            # Visual: Texto flutuante no jogador ativo
            self.adicionar_texto_flutuante(
                f"+{defesa} DEF", jogador_ativo.x + 20, jogador_ativo.y - 20, (100, 150, 255))

        elif carta.tipo == Card.CURA:
            cura = carta.valores[Card.CURA]
            cura_real = jogador_ativo.curar(cura)
            self.mensagem = f"{jogador_ativo.nome} se curou! +{cura_real} HP!"
            self.cor_mensagem = (100, 255, 100)

            # Visual: Texto flutuante no jogador ativo
            self.adicionar_texto_flutuante(
                f"+{cura_real} HP", jogador_ativo.x + 20, jogador_ativo.y - 20, (100, 255, 100))

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

            # Próximo estado: Jogar (após 1000ms = 1s)
            self.estado_ia = "IA_JOGAR"
            self.tempo_espera_ia = pygame.time.get_ticks() + 1000

        elif self.estado_ia == "IA_JOGAR":
            if len(self.ia.mao) > 0:
                indice = random.randint(0, len(self.ia.mao) - 1)
                carta = self.ia.jogar_carta(indice)

                if carta:
                    # Adiciona ao descarte
                    self.deck.adicionar_ao_descarte(carta)

                    # Aplica o efeito
                    self.aplicar_efeito_carta(carta, self.ia, self.jogador)

            # Próximo estado: Finalizar (após 1500ms = 1.5s)
            self.estado_ia = "IA_FINALIZAR"
            self.tempo_espera_ia = pygame.time.get_ticks() + 1500

        elif self.estado_ia == "IA_FINALIZAR":
            # Volta para o turno do jogador
            self.passar_turno()
            self.mensagem = "Seu turno! Clique para comprar uma carta."
            self.cor_mensagem = (255, 255, 100)
            self.aguardando_ia = False
            self.estado_ia = None

    def reiniciar_jogo(self):
        """Reinicia o jogo completamente"""
        logging.info("🔄 Reiniciando o jogo...")

        # Reseta o Deck (recria e embaralha)
        self.deck.resetar()

        # Reseta os Jogadores (HP máximo, mão vazia, defesa 0)
        self.ia = Player("IA", 50, 80)
        self.jogador = Player("VOCÊ", 50, 500)

        # Distribuir cartas iniciais (3 para cada)
        for _ in range(3):
            self.jogador.comprar_carta(self.deck)
            self.ia.comprar_carta(self.deck)

        # Reseta estado do jogo
        self.turno_jogador = True
        self.fase_turno = "comprar"
        self.carta_selecionada = None
        self.mensagem = "Seu turno! Clique para comprar uma carta."
        self.cor_mensagem = (255, 255, 100)
        self.aguardando_ia = False
        self.tempo_espera_ia = 0
        self.estado_ia = None
        self.game_over = False

    def desenhar_game_over(self):
        """Desenha a tela de Game Over"""
        # Overlay escuro
        overlay = pygame.Surface(
            (LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.superficie.blit(overlay, (0, 0))

        # Mensagem de Resultado
        texto_msg = self.fonte_titulo.render(
            self.mensagem, True, self.cor_mensagem)
        rect_msg = texto_msg.get_rect(
            center=(LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2 - 50))
        self.superficie.blit(texto_msg, rect_msg)

        # Botão de Reiniciar
        texto_restart = self.fonte_titulo.render(
            "Pressione R para Reiniciar", True, (255, 255, 255))
        rect_restart = texto_restart.get_rect(
            center=(LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2 + 50))

        # Fundo do botão
        padding = 20
        bg_rect = rect_restart.inflate(padding * 2, padding)
        pygame.draw.rect(self.superficie, (50, 50, 80),
                         bg_rect, border_radius=10)
        pygame.draw.rect(self.superficie, (100, 100, 150),
                         bg_rect, 3, border_radius=10)

        self.superficie.blit(texto_restart, rect_restart)

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

        # O fundo e borda agora são desenhados dentro de desenhar_estatisticas
        # para permitir um visual mais customizado (painel arredondado)

        # Desenha as estatísticas do baralho
        self.desenhar_estatisticas(area_stats)

    def desenhar_estatisticas(self, area):
        """Desenha as estatísticas do baralho no painel direito como histograma"""
        # 1. Fundo do Painel (Estilo Profissional)
        painel_surf = pygame.Surface(
            (area.width, area.height), pygame.SRCALPHA)
        cor_fundo_painel = (30, 35, 45, 240)  # Fundo escuro semi-transparente
        pygame.draw.rect(painel_surf, cor_fundo_painel,
                         painel_surf.get_rect(), border_radius=15)
        pygame.draw.rect(painel_surf, (80, 90, 110),
                         painel_surf.get_rect(), 2, border_radius=15)  # Borda
        self.superficie.blit(painel_surf, (area.x, area.y))

        # Margens internas
        margin_x = 25
        margin_top = 60
        margin_bottom = 90  # Aumentado para caber a legenda detalhada

        x_base = area.x + margin_x
        y_base = area.y + margin_top

        largura_grafico = area.width - (2 * margin_x)
        altura_grafico = area.height - margin_top - margin_bottom

        # Check for minimum space requirements
        if largura_grafico < 50 or altura_grafico < 50:
            texto_aviso = self.fonte_texto.render(
                "Área muito pequena", True, (255, 100, 100))
            self.superficie.blit(texto_aviso, (area.x + 10, area.y + 50))
            return

        # Título
        texto_titulo = self.fonte_titulo.render(
            "Probabilidades", True, (220, 220, 220))
        rect_titulo = texto_titulo.get_rect(center=(area.centerx, area.y + 30))
        self.superficie.blit(texto_titulo, rect_titulo)

        # Eixos
        eixo_x_start = (x_base, y_base + altura_grafico)
        eixo_x_end = (x_base + largura_grafico, y_base + altura_grafico)
        eixo_y_start = (x_base, y_base)
        eixo_y_end = (x_base, y_base + altura_grafico)

        pygame.draw.line(self.superficie, (150, 150, 150),
                         eixo_x_start, eixo_x_end, 2)
        pygame.draw.line(self.superficie, (150, 150, 150),
                         eixo_y_start, eixo_y_end, 2)

        # Dados
        tipos = [Card.ATAQUE, Card.DEFESA, Card.CURA]
        prob_teorica = {Card.ATAQUE: 50, Card.DEFESA: 30, Card.CURA: 20}
        prob_empirica = self.deck.calcular_frequencia_empirica()

        cores_tipo = {
            Card.ATAQUE: (220, 60, 60),
            Card.DEFESA: (60, 130, 220),
            Card.CURA: (60, 210, 90)
        }

        num_tipos = len(tipos)
        if num_tipos == 0:
            return

        espaco_entre_grupos = 30
        largura_disponivel = largura_grafico - \
            (num_tipos + 1) * espaco_entre_grupos

        if largura_disponivel <= 0:
            return

        largura_grupo = largura_disponivel / num_tipos
        largura_barra = largura_grupo  # Barra ocupa largura do grupo

        max_valor = 100  # Escala de 0 a 100%

        for i, tipo in enumerate(tipos):
            x_grupo = x_base + espaco_entre_grupos + \
                i * (largura_grupo + espaco_entre_grupos)

            # --- Barra Empírica (Sólida) ---
            altura_empirica = (
                prob_empirica[tipo] / max_valor) * altura_grafico
            rect_empirica = pygame.Rect(
                x_grupo,
                y_base + altura_grafico - altura_empirica,
                largura_barra,
                altura_empirica
            )

            if rect_empirica.height > 0:
                pygame.draw.rect(
                    self.superficie, cores_tipo[tipo], rect_empirica, border_radius=4)

            # --- Linha Tracejada (Teórica) ---
            altura_teorica = (prob_teorica[tipo] / max_valor) * altura_grafico
            y_teorica = y_base + altura_grafico - altura_teorica

            # Desenhar linha tracejada
            dash_len = 6
            x_start = x_grupo - 5
            x_end = x_grupo + largura_barra + 5
            for x_dash in range(int(x_start), int(x_end), dash_len * 2):
                pygame.draw.line(self.superficie, (255, 255, 255),
                                 (x_dash, y_teorica),
                                 (min(x_dash + dash_len, x_end), y_teorica), 2)

            # --- Texto Empírico ---
            texto_str = f"{prob_empirica[tipo]:.1f}%"
            texto_empirico = self.fonte_texto.render(
                texto_str, True, (255, 255, 255))

            # Lógica para evitar sobreposição
            # Se a barra estiver muito alta (perto do topo), desenha o texto dentro da barra
            if rect_empirica.top < y_base + 25:
                # Desenha dentro (parte superior da barra)
                rect_txt_empirico = texto_empirico.get_rect(
                    midtop=(rect_empirica.centerx, rect_empirica.top + 5))
                # Adiciona contorno preto para contraste
                texto_outline = self.fonte_texto.render(
                    texto_str, True, (0, 0, 0))
                self.superficie.blit(
                    texto_outline, (rect_txt_empirico.x + 1, rect_txt_empirico.y + 1))
            else:
                # Desenha acima
                rect_txt_empirico = texto_empirico.get_rect(
                    midbottom=(rect_empirica.centerx, rect_empirica.top - 5))

            self.superficie.blit(texto_empirico, rect_txt_empirico)

            # Legenda do Eixo X (Tipo da Carta)
            texto_tipo = self.fonte_texto.render(tipo, True, (200, 200, 200))
            rect_txt_tipo = texto_tipo.get_rect(
                midtop=(rect_empirica.centerx, y_base + altura_grafico + 8))
            self.superficie.blit(texto_tipo, rect_txt_tipo)

        # --- Legenda Explicativa ---
        y_legenda_start = y_base + altura_grafico + 40
        font_legenda = pygame.font.Font(None, 20)

        # Item 1: Linha Tracejada
        pygame.draw.line(self.superficie, (255, 255, 255), (x_base,
                         y_legenda_start + 10), (x_base + 30, y_legenda_start + 10), 2)
        # Simular tracejado visualmente na legenda (apagando pedaços)
        pygame.draw.rect(
            self.superficie, cor_fundo_painel[:3], (x_base + 10, y_legenda_start + 8, 10, 4))

        lbl_teorica = font_legenda.render(
            "Linha Tracejada = Probabilidade Teórica (Esperado)", True, (220, 220, 220))
        self.superficie.blit(lbl_teorica, (x_base + 40, y_legenda_start))

        # Item 2: Barras Sólidas
        y_legenda_item2 = y_legenda_start + 20
        pygame.draw.rect(self.superficie, (150, 150, 150),
                         (x_base, y_legenda_item2 + 2, 30, 12), border_radius=2)
        lbl_empirica = font_legenda.render(
            "Barras Sólidas = Realidade (Empírico)", True, (220, 220, 220))
        self.superficie.blit(lbl_empirica, (x_base + 40, y_legenda_item2))

    def renderizar(self):
        """Renderiza tudo na tela"""
        self.desenhar_interface()

        # Desenha os jogadores
        self.ia.desenhar(self.superficie)
        self.jogador.desenhar(self.superficie)

        # Desenha as mãos dos jogadores
        self.ia.desenhar_mao(self.superficie, 150, 150)
        self.jogador.desenhar_mao(self.superficie, 150, 380)

        # Desenha textos flutuantes
        for texto in self.textos_flutuantes:
            texto.desenhar(self.superficie, self.fonte_titulo)

        # Flash de dano
        if self.flash_dano_timer > 0:
            overlay = pygame.Surface(
                (LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.SRCALPHA)
            alpha = int((self.flash_dano_timer / 10) * 100)  # Max alpha 100
            overlay.fill((255, 0, 0, alpha))
            self.superficie.blit(overlay, (0, 0))

        if self.game_over:
            self.desenhar_game_over()

        # Escala a superfície virtual para o tamanho da janela
        scaled_surface = pygame.transform.smoothscale(
            self.superficie, self.tela.get_size())
        self.tela.blit(scaled_surface, (0, 0))

        pygame.display.flip()

    def executar(self):
        """Loop principal do jogo"""
        logging.info("🎮 Jogo iniciado! Pressione ESC para sair.")

        while self.rodando:
            self.processar_eventos()
            self.atualizar()
            self.renderizar()
            self.relogio.tick(FPS)

        self.encerrar()

    def encerrar(self):
        """Encerra o jogo corretamente"""
        logging.info("👋 Encerrando o jogo...")
        pygame.quit()
        sys.exit()


# Ponto de entrada do programa
if __name__ == "__main__":
    jogo = JogoDuelo()
    jogo.executar()

import pygame
import sys
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
        
        # Cartas de exemplo (para testar)
        self.cartas_exemplo = [
            Card(Card.ATAQUE, 100, 200),
            Card(Card.DEFESA, 220, 200),
            Card(Card.CURA, 340, 200)
        ]
    
    def processar_eventos(self):
        """Processa todos os eventos do Pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
    
    def atualizar(self):
        """Atualiza a lógica do jogo"""
        pass
    
    def desenhar_interface(self):
        """Desenha a interface dividida do jogo"""
        # Fundo principal
        self.tela.fill(COR_FUNDO)
        
        # Área do Jogo (Esquerda)
        area_jogo = pygame.Rect(10, 10, LARGURA_JOGO - 20, ALTURA_TELA - 20)
        pygame.draw.rect(self.tela, COR_AREA_JOGO, area_jogo)
        pygame.draw.rect(self.tela, COR_BORDA, area_jogo, 3)
        
        # Título da área de jogo
        texto_jogo = self.fonte_titulo.render("CAMPO DE BATALHA", True, COR_TEXTO)
        self.tela.blit(texto_jogo, (area_jogo.x + 20, area_jogo.y + 15))
        
        # Área de Estatísticas (Direita)
        area_stats = pygame.Rect(LARGURA_JOGO + 10, 10, LARGURA_STATS - 20, ALTURA_TELA - 20)
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
        texto_total = self.fonte_texto.render(f"Cartas no Baralho: {total}", True, COR_TEXTO)
        self.tela.blit(texto_total, (x_base, y_atual))
        y_atual += 40
        
        # Separador
        pygame.draw.line(self.tela, COR_BORDA, (x_base, y_atual), (area.right - 20, y_atual), 2)
        y_atual += 20
        
        # Título: Contagem Empírica
        texto_empirica = self.fonte_titulo.render("Contagem:", True, (255, 200, 100))
        self.tela.blit(texto_empirica, (x_base, y_atual))
        y_atual += 40
        
        # Contagem por tipo
        contagem = self.deck.contar_por_tipo()
        cores_tipo = {
            Card.ATAQUE: (220, 50, 50),
            Card.DEFESA: (50, 120, 220),
            Card.CURA: (50, 200, 80)
        }
        
        for tipo, quantidade in contagem.items():
            cor = cores_tipo[tipo]
            texto = self.fonte_texto.render(f"⚫ {tipo}: {quantidade}", True, cor)
            self.tela.blit(texto, (x_base + 10, y_atual))
            y_atual += 30
        
        y_atual += 20
        
        # Separador
        pygame.draw.line(self.tela, COR_BORDA, (x_base, y_atual), (area.right - 20, y_atual), 2)
        y_atual += 20
        
        # Título: Probabilidades Teóricas
        texto_prob = self.fonte_titulo.render("Probabilidades:", True, (100, 200, 255))
        self.tela.blit(texto_prob, (x_base, y_atual))
        y_atual += 40
        
        # Probabilidades por tipo
        probabilidades = self.deck.calcular_probabilidades()
        
        for tipo, prob in probabilidades.items():
            cor = cores_tipo[tipo]
            texto = self.fonte_texto.render(f"P({tipo}): {prob:.1f}%", True, cor)
            self.tela.blit(texto, (x_base + 10, y_atual))
            y_atual += 30
    
    def renderizar(self):
        """Renderiza tudo na tela"""
        self.desenhar_interface()
        
        # Desenha as cartas de exemplo
        for carta in self.cartas_exemplo:
            carta.desenhar(self.tela)
        
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

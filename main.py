import pygame
import random
import os

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 600, 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bunny Adventure")
relogio = pygame.time.Clock()

# --- CAMINHOS ABSOLUTOS ---
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_ASSETS = DIRETORIO_BASE

# --- DEBUG: VERIFICAR ARQUIVOS ---
print(f"Procurando arquivos em: {DIRETORIO_ASSETS}")
if os.path.exists(DIRETORIO_ASSETS):
    print("Arquivos encontrados:", os.listdir(DIRETORIO_ASSETS))
else:
    print("ERRO CRÍTICO: O diretório base não foi encontrado!")

# --- CARREGAMENTO DE ASSETS ---
def carregar_imagem(nome, tamanho):
    caminho = os.path.join(DIRETORIO_ASSETS, nome)
    
    # Tenta encontrar o arquivo mesmo se o nome estiver com maiúsculas/minúsculas diferentes
    if not os.path.exists(caminho):
        for arquivo in os.listdir(DIRETORIO_ASSETS):
            if arquivo.lower() == nome.lower():
                caminho = os.path.join(DIRETORIO_ASSETS, arquivo)
                break

    if os.path.exists(caminho):
        try:
            img = pygame.image.load(caminho).convert_alpha()
            img = pygame.transform.scale(img, tamanho)
            print(f"SUCESSO: '{nome}' carregado.")
            return img
        except Exception as e:
            print(f"ERRO ao abrir '{nome}': {e}")
    else:
        print(f"FALHA: '{nome}' não encontrado na pasta.")
    return None

def carregar_som(nome):
    caminho = os.path.join(DIRETORIO_ASSETS, nome)
    if os.path.exists(caminho):
        return pygame.mixer.Sound(caminho)
    return None

def carregar_musica(nome):
    caminho = os.path.join(DIRETORIO_ASSETS, nome)
    if os.path.exists(caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.3) # Volume mais baixo (30%) para fundo
            pygame.mixer.music.play(-1) # -1 faz a música repetir em loop infinito
            print(f"Música de fundo '{nome}' carregada.")
        except Exception as e:
            print(f"ERRO ao carregar música '{nome}': {e}")
    else:
        print(f"AVISO: O arquivo de música '{nome}' não foi encontrado na pasta.")

def carregar_fonte(tamanho):
    # Define o caminho da pasta midia
    caminho_midia = os.path.join(DIRETORIO_ASSETS, "midia")
    
    # Tenta encontrar um arquivo .ttf na pasta midia
    if os.path.exists(caminho_midia):
        for arquivo in os.listdir(caminho_midia):
            if arquivo.lower().endswith(".ttf"):
                caminho = os.path.join(caminho_midia, arquivo)
                try:
                    fonte = pygame.font.Font(caminho, tamanho)
                    print(f"SUCESSO: Fonte '{arquivo}' carregada de midia.")
                    return fonte
                except Exception as e:
                    print(f"Erro ao carregar fonte personalizada: {e}")
    print("AVISO: Nenhuma fonte .ttf encontrada na pasta midia. Usando padrão.")
    return pygame.font.SysFont("Consolas", tamanho, bold=True)

# Imagens
img_player = carregar_imagem("midia/coelhinho.png", (90, 90))
img_bom = carregar_imagem("midia/morango.png", (45, 45))
img_ruim = carregar_imagem("midia/pedra.png", (45, 45))
img_fundo = carregar_imagem("midia/fundo.png", (LARGURA, ALTURA))
# Sons
som_bom = carregar_som("midia/good-6081.mp3")
if som_bom: som_bom.set_volume(0.2)
som_ruim = carregar_som("midia/spin-fail-295088.mp3")
if som_ruim: som_ruim.set_volume(0.2)
carregar_musica("midia/lofi-relax-beat-loop-bpm-88-eb-major-ii-v-i-361752.mp3")

# Fontes - Usando fonte estilo VS Code (Consolas)
fonte_menu = carregar_fonte(60)
fonte_hud = carregar_fonte(30)

# --- CLASSE PRINCIPAL ---
class Jogo:
    def __init__(self):
        self.resetar()

    def resetar(self):
        self.estado = "MENU"
        self.player_x = LARGURA // 2 - 35
        self.pontos = 0
        self.vidas = 3
        self.itens = []
        self.shake = 0

    def criar_item(self):
        x = random.randint(30, LARGURA - 70)
        tipo = "bom" if random.random() > 0.3 else "ruim"
        self.itens.append({"pos": [x, -50], "tipo": tipo})

    def atualizar(self):
        if self.estado != "JOGANDO":
            return

        if self.shake > 0: self.shake -= 1

        # Movimentação suave
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and self.player_x > 0: self.player_x -= 8
        if teclas[pygame.K_RIGHT] and self.player_x < LARGURA - 70: self.player_x += 8

        # Spawn de itens
        if len(self.itens) < 4 and random.random() < 0.025:
            self.criar_item()

        for item in self.itens[:]:
            item["pos"][1] += 5 # Velocidade de queda
            
            p_rect = pygame.Rect(self.player_x, ALTURA - 90, 70, 70)
            i_rect = pygame.Rect(item["pos"][0], item["pos"][1], 45, 45)

            if p_rect.colliderect(i_rect):
                if item["tipo"] == "bom":
                    self.pontos += 10
                    if som_bom: som_bom.play()
                else:
                    self.vidas -= 1
                    self.shake = 12
                    if som_ruim: som_ruim.play()
                    if self.vidas <= 0: self.estado = "GAME_OVER"
                self.itens.remove(item)
            elif item["pos"][1] > ALTURA:
                self.itens.remove(item)

    def desenhar(self):
        # Efeito de tremor (offset aleatório)
        off_x = random.randint(-self.shake, self.shake)
        off_y = random.randint(-self.shake, self.shake)

        # Fundo
        if img_fundo:
            tela.blit(img_fundo, (0, 0))
        else:
            tela.fill((255, 240, 245))

        if self.estado == "MENU":
            msg_sombra = fonte_menu.render("Bunny Adventure", True, (0, 0, 0))
            msg = fonte_menu.render("Bunny Adventure", True, (255, 80, 150))
            
            sub_sombra = fonte_hud.render("Pressione ESPAÇO", True, (0, 0, 0))
            sub = fonte_hud.render("Pressione ESPAÇO", True, (255, 255, 255))
            
            tela.blit(msg_sombra, (LARGURA//2 - msg.get_width()//2 + 3, 250 + 3))
            tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 250)) 
            tela.blit(sub_sombra, (LARGURA//2 - sub.get_width()//2 + 2, 350 + 2))
            tela.blit(sub, (LARGURA//2 - sub.get_width()//2, 350))

        elif self.estado == "JOGANDO":
            # Jogador Sra Coelha
            if img_player:
                tela.blit(img_player, (self.player_x + off_x, ALTURA - 90 + off_y))
            else:
                pygame.draw.rect(tela, (255, 150, 200), (self.player_x + off_x, ALTURA - 90 + off_y, 70, 70))

            # Itens
            for item in self.itens:
                img = img_bom if item["tipo"] == "bom" else img_ruim
                if img:
                    tela.blit(img, (item["pos"][0] + off_x, item["pos"][1] + off_y))
                else:
                    cor = (150, 255, 150) if item["tipo"] == "bom" else (150, 50, 200)
                    pygame.draw.circle(tela, cor, (item["pos"][0]+22, item["pos"][1]+22), 22)

            # Vidas (bolinhas rosa)
            for i in range(self.vidas):
                # Desenha uma bolinha rosa mais escura
                pygame.draw.circle(tela, (255, 105, 180), (35 + i * 40, 35), 15)
                pygame.draw.circle(tela, (255, 20, 147), (35 + i * 40, 35), 15, 2)
            
            # Pontos com sombra para ler melhor
            txt_pontos = f"Pontos: {self.pontos}"
            sombra = fonte_hud.render(txt_pontos, True, (0, 0, 0))
            texto = fonte_hud.render(txt_pontos, True, (255, 255, 255))
            tela.blit(sombra, (LARGURA - 182, 22)) # Sombra
            tela.blit(texto, (LARGURA - 180, 20)) # Texto principal

        elif self.estado == "GAME_OVER":
            over_sombra = fonte_menu.render("GAME OVER", True, (0, 0, 0))
            over = fonte_menu.render("GAME OVER", True, (255, 215, 0))
            final_sombra = fonte_hud.render(f"Pontos Finais: {self.pontos}", True, (0, 0, 0))
            final = fonte_hud.render(f"Pontos Finais: {self.pontos}", True, (255, 255, 255))
            
            restart_sombra = fonte_hud.render("Pressione R para recomeçar", True, (0, 0, 0))
            restart = fonte_hud.render("Pressione R para recomeçar", True, (255, 255, 255))
            
            tela.blit(over_sombra, (LARGURA//2 - over.get_width()//2 + 3, 200 + 3))
            tela.blit(over, (LARGURA//2 - over.get_width()//2, 200))
            tela.blit(final_sombra, (LARGURA//2 - final.get_width()//2 + 2, 300 + 2))
            tela.blit(final, (LARGURA//2 - final.get_width()//2, 300))
            tela.blit(restart_sombra, (LARGURA//2 - restart.get_width()//2 + 2, 400 + 2))
            tela.blit(restart, (LARGURA//2 - restart.get_width()//2, 400))

# --- LOOP PRINCIPAL ---
jogo = Jogo()
executando = True

while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        
        if evento.type == pygame.KEYDOWN:
            if jogo.estado == "MENU" and evento.key == pygame.K_SPACE:
                jogo.estado = "JOGANDO"
            if jogo.estado == "GAME_OVER" and evento.key == pygame.K_r:
                jogo.resetar()
                jogo.estado = "JOGANDO"

    jogo.atualizar()
    jogo.desenhar()
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
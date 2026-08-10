import pygame
import math

pygame.init()

LARGURA = 1000
ALTURA = 680
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("FillPoly - (CG)")
relogio = pygame.time.Clock()

# Cores em RGB
COR_FUNDO = (30, 30, 35)
COR_PAINEL = (45, 45, 52)
COR_TEXTO = (230, 230, 230)
COR_BRANCA = (255, 255, 255)
COR_SELECAO = (255, 220, 50)
COR_LINHA_GUIA = (180, 180, 180)

# Paleta de cores para os poligonos
PALETA_CORES = [
    (220, 60, 60),    # Vermelho
    (60, 180, 90),    # Verde
    (50, 120, 220),   # Azul
    (240, 180, 40),   # Amarelo / Laranja
    (170, 70, 210),   # Roxo
    (40, 190, 210),   # Ciano
    (230, 100, 160),  # Rosa
    (160, 160, 160)   # Cinza
]


class Aresta:
    """Estrutura para armazenar informacoes da aresta na Tabela de Arestas (ET)."""
    def __init__(self, y_min, y_max, x, dx):
        self.y_min = y_min
        self.y_max = y_max
        self.x = x      # Intersecao X atual (sera atualizada incrementalmente)
        self.dx = dx    # Incremento 1/m = (x2 - x1) / (y2 - y1)


class Poligono:
    """Representa um poligono com seu contorno principal, buracos e cor."""
    def __init__(self, pontos, cor):
        self.pontos = pontos        # Contorno externo [(x1, y1), ...]
        self.buracos = []           # Lista de buracos [[(x1, y1), ...], ...]
        self.cor = cor

    def desenhar(self, superficie, mostrar_arestas):
        # Preenche a regiao interna com o algoritmo fillpoly
        preencher_poligono(superficie, self)

        # Se a opcao estiver ativa, desenha as arestas externas e dos buracos em branco (1px)
        if mostrar_arestas:
            desenhar_contorno(superficie, self.pontos, COR_BRANCA)
            for buraco in self.buracos:
                desenhar_contorno(superficie, buraco, COR_BRANCA)


def definir_pixel(superficie, x, y, cor):
    """Pinta um unico pixel na tela se estiver dentro dos limites."""
    if 0 <= x < LARGURA and 0 <= y < ALTURA:
        superficie.set_at((int(x), int(y)), cor)


def desenhar_linha(superficie, p1, p2, cor):
    """Desenha uma linha entre dois pontos usando DDA (aritmética incremental)."""
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1
    passos = max(abs(dx), abs(dy))

    if passos == 0:
        definir_pixel(superficie, x1, y1, cor)
        return

    # Incrementos fixos por passo (aritmética incremental)
    inc_x = dx / passos
    inc_y = dy / passos

    x = x1
    y = y1
    for _ in range(passos + 1):
        definir_pixel(superficie, round(x), round(y), cor)
        x += inc_x  # Novo valor calculado a partir do anterior + parcela fixa
        y += inc_y


def desenhar_contorno(superficie, pontos, cor):
    """Desenha as arestas de um contorno fechado usando o algoritmo DDA."""
    qtd = len(pontos)
    for i in range(qtd):
        p1 = pontos[i]
        p2 = pontos[(i + 1) % qtd]
        desenhar_linha(superficie, p1, p2, cor)


def preencher_poligono(superficie, poligono):
    """Algoritmo FillPoly (Scanline com Tabela de Arestas e Aritmética Incremental)."""
    todos_contornos = [poligono.pontos] + poligono.buracos
    tabela_arestas = {}

    # 1. Construcao da Tabela de Arestas (Edge Table - ET)
    for contorno in todos_contornos:
        qtd = len(contorno)
        if qtd < 3:
            continue
        for i in range(qtd):
            x1, y1 = contorno[i]
            x2, y2 = contorno[(i + 1) % qtd]

            # Arestas horizontais sao descartadas no algoritmo scanline
            if y1 == y2:
                continue

            # Garante que y1 seja o ponto inferior (menor Y)
            if y1 > y2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1

            # Incremento dx = 1/m = (x2 - x1) / (y2 - y1)
            dx = (x2 - x1) / (y2 - y1)
            aresta = Aresta(y1, y2, x1, dx)

            if y1 not in tabela_arestas:
                tabela_arestas[y1] = []
            tabela_arestas[y1].append(aresta)

    if not tabela_arestas:
        return

    y_min = min(tabela_arestas.keys())
    y_max = max(a.y_max for arestas in tabela_arestas.values() for a in arestas)

    arestas_ativas = []  # Active Edge Table (AET)

    # 2. Processamento scanline por scanline (linha Y a linha Y)
    for y in range(y_min, y_max):
        # Adiciona novas arestas que comecam na linha Y atual
        if y in tabela_arestas:
            arestas_ativas.extend(tabela_arestas[y])

        # Remove arestas que ja atingiram seu y_max
        arestas_ativas = [a for a in arestas_ativas if y < a.y_max]

        # Ordena as arestas ativas pela coordenada X da intersecao
        arestas_ativas.sort(key=lambda a: a.x)

        # Preenche os pixels da scanline em pares (Regra Par-Impar / Even-Odd)
        for i in range(0, len(arestas_ativas) - 1, 2):
            x_inicio = round(arestas_ativas[i].x)
            x_fim = round(arestas_ativas[i + 1].x)

            if x_inicio > x_fim:
                x_inicio, x_fim = x_fim, x_inicio

            for x in range(x_inicio, x_fim):
                definir_pixel(superficie, x, y, poligono.cor)

        # 3. Atualizacao INCREMENTAL da intersecao X para a proxima scanline (y + 1)
        for a in arestas_ativas:
            a.x += a.dx  # x_novo = x_anterior + dx (aritmética incremental)


def ponto_no_contorno(ponto, contorno):
    """Verifica se um ponto esta dentro de um contorno via ray-casting (par-impar)."""
    x, y = ponto
    dentro = False
    j = len(contorno) - 1
    for i in range(len(contorno)):
        xi, yi = contorno[i]
        xj, yj = contorno[j]
        if (yi > y) != (yj > y):
            intersecao_x = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < intersecao_x:
                dentro = not dentro
        j = i
    return dentro


def ponto_no_poligono(ponto, poligono):
    """Ponto esta na regiao interna se esta no contorno externo e FORA dos buracos."""
    if not ponto_no_contorno(ponto, poligono.pontos):
        return False
    for buraco in poligono.buracos:
        if ponto_no_contorno(ponto, buraco):
            return False
    return True


def desenhar_painel_ui(superficie, poligonos, selecionado, mostrar_arestas, modo_buraco, cor_atual):
    """Desenha a barra de ferramentas e os botoes da interface."""
    pygame.draw.rect(superficie, COR_PAINEL, (0, 0, LARGURA, 70))
    pygame.draw.line(superficie, (80, 80, 90), (0, 70), (LARGURA, 70), 2)

    fonte = pygame.font.SysFont("arial", 15)
    fonte_bold = pygame.font.SysFont("arial", 15, bold=True)

    # Texto de instrucoes
    txt1 = fonte.render("Clicar: Adicionar Ponto | ENTER: Finalizar | ESC: Cancelar", True, COR_TEXTO)
    txt2 = fonte.render("Clique em um Poligono para Selecionar | DEL: Excluir", True, COR_TEXTO)
    superficie.blit(txt1, (15, 12))
    superficie.blit(txt2, (15, 38))

    # Botao Arestas
    cor_btn_arestas = (70, 150, 70) if mostrar_arestas else (100, 100, 110)
    rect_arestas = pygame.Rect(400, 15, 130, 40)
    pygame.draw.rect(superficie, cor_btn_arestas, rect_arestas, border_radius=6)
    txt_arestas = fonte_bold.render(f"Pintura das Arestas: {'LIGADO' if mostrar_arestas else 'DESLIGADO'}", True, COR_BRANCA)
    superficie.blit(txt_arestas, (410, 25))

    # Botao Modo Buraco
    cor_btn_buraco = (200, 120, 40) if modo_buraco else (100, 100, 110)
    rect_buraco = pygame.Rect(540, 15, 130, 40)
    pygame.draw.rect(superficie, cor_btn_buraco, rect_buraco, border_radius=6)
    txt_buraco = fonte_bold.render("Modo: Buraco" if modo_buraco else "Modo: Poligono", True, COR_BRANCA)
    superficie.blit(txt_buraco, (550, 25))

    # Paleta de cores para troca de cor
    superficie.blit(fonte.render("Paleta de Cores:", True, COR_TEXTO), (685, 8))
    for idx, cor in enumerate(PALETA_CORES):
        bx = 685 + (idx % 4) * 28
        by = 28 + (idx // 4) * 20
        rect_cor = pygame.Rect(bx, by, 22, 16)
        pygame.draw.rect(superficie, cor, rect_cor, border_radius=3)
        if cor == cor_atual:
            pygame.draw.rect(superficie, COR_BRANCA, rect_cor, 2, border_radius=3)

    return rect_arestas, rect_buraco


def main():
    poligonos = []
    pontos_desenho = []
    poligono_selecionado = None
    mostrar_arestas = True
    modo_buraco = False
    cor_atual = PALETA_CORES[0]

    rodando = True
    while rodando:
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Clique na barra de ferramentas superior
                if pos_mouse[1] <= 70:
                    rect_arestas = pygame.Rect(400, 15, 130, 40)
                    rect_buraco = pygame.Rect(540, 15, 130, 40)

                    if rect_arestas.collidepoint(pos_mouse):
                        mostrar_arestas = not mostrar_arestas
                    elif rect_buraco.collidepoint(pos_mouse):
                        modo_buraco = not modo_buraco

                    # Clique na paleta de cores
                    for idx, cor in enumerate(PALETA_CORES):
                        bx = 685 + (idx % 4) * 28
                        by = 28 + (idx // 4) * 20
                        if pygame.Rect(bx, by, 22, 16).collidepoint(pos_mouse):
                            cor_atual = cor
                            if poligono_selecionado is not None:
                                poligono_selecionado.cor = cor
                else:
                    # Clique na area de desenho
                    if pontos_desenho:
                        # Adiciona mais um ponto ao contorno em construcao
                        pontos_desenho.append(pos_mouse)
                    else:
                        # Tenta selecionar um poligono existente
                        poligono_clicado = None
                        for p in reversed(poligonos):
                            if ponto_no_poligono(pos_mouse, p):
                                poligono_clicado = p
                                break

                        if poligono_clicado is not None:
                            poligono_selecionado = poligono_clicado
                            cor_atual = poligono_selecionado.cor
                            if modo_buraco:
                                pontos_desenho.append(pos_mouse)
                        else:
                            poligono_selecionado = None
                            modo_buraco = False
                            pontos_desenho.append(pos_mouse)

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Finaliza o contorno atual (poligono ou buraco)
                    if len(pontos_desenho) >= 3:
                        if modo_buraco and poligono_selecionado is not None:
                            poligono_selecionado.buracos.append(pontos_desenho.copy())
                        else:
                            novo_p = Poligono(pontos_desenho.copy(), cor_atual)
                            poligonos.append(novo_p)
                            poligono_selecionado = novo_p
                    pontos_desenho.clear()

                elif evento.key == pygame.K_ESCAPE:
                    pontos_desenho.clear()

                elif evento.key == pygame.K_DELETE:
                    if poligono_selecionado in poligonos:
                        poligonos.remove(poligono_selecionado)
                        poligono_selecionado = None

                elif evento.key == pygame.K_e:
                    mostrar_arestas = not mostrar_arestas

                elif evento.key == pygame.K_b:
                    modo_buraco = not modo_buraco

                elif evento.key == pygame.K_c:
                    poligonos.clear()
                    pontos_desenho.clear()
                    poligono_selecionado = None

        # Limpeza da tela
        tela.fill(COR_FUNDO)

        # 1. Desenha todos os poligonos usando o algoritmo fillpoly
        for p in poligonos:
            p.desenhar(tela, mostrar_arestas)

        # Destaca o poligono selecionado
        if poligono_selecionado is not None and not pontos_desenho:
            desenhar_contorno(tela, poligono_selecionado.pontos, COR_SELECAO)

        # 2. Desenha o contorno que esta sendo criado no momento
        if pontos_desenho:
            cor_guia = (240, 160, 50) if modo_buraco else COR_LINHA_GUIA
            qtd_p = len(pontos_desenho)
            for i in range(qtd_p - 1):
                desenhar_linha(tela, pontos_desenho[i], pontos_desenho[i + 1], cor_guia)
            # Linha guia ate o ponteiro do mouse
            desenhar_linha(tela, pontos_desenho[-1], pos_mouse, cor_guia)

            # Desenha os pontos dos vertices
            for pt in pontos_desenho:
                pygame.draw.circle(tela, COR_BRANCA, pt, 3)

        # 3. Desenha o painel da interface
        desenhar_painel_ui(tela, poligonos, poligono_selecionado, mostrar_arestas, modo_buraco, cor_atual)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
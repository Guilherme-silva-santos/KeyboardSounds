import pygame
import os
import tkinter as tk
from tkinter import filedialog
import keyboard
import time
import json

pygame.init()

tamanho_da_tela = (1700, 1000)
screen = pygame.display.set_mode(tamanho_da_tela)
pygame.display.set_caption('Teclas e Sons')

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA_CLARO = (200, 200, 200)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

fonte = pygame.font.Font(None, 24)
fonte_titulo = pygame.font.Font(None, 36)
fonte_toast = pygame.font.Font(None, 28)

teclas = {k: None for k in range(pygame.K_a, pygame.K_z + 1)}
teclas.update({k: None for k in range(pygame.K_0, pygame.K_9 + 1)})
teclas.update({
    pygame.K_BACKSPACE: None,
    pygame.K_TAB: None,
    pygame.K_RETURN: None,
    pygame.K_ESCAPE: None,
    pygame.K_SPACE: None,
    pygame.K_DELETE: None,
    pygame.K_UP: None,
    pygame.K_DOWN: None,
    pygame.K_LEFT: None,
    pygame.K_RIGHT: None,
    pygame.K_LSHIFT: None,
    pygame.K_RSHIFT: None,
    pygame.K_LCTRL: None,
    pygame.K_RCTRL: None,
    pygame.K_LALT: None,
    pygame.K_RALT: None,
    pygame.K_CAPSLOCK: None,
    pygame.K_F1: None,
    pygame.K_F2: None,
    pygame.K_F3: None,
    pygame.K_F4: None,
    pygame.K_F5: None,
    pygame.K_F6: None,
    pygame.K_F7: None,
    pygame.K_F8: None,
    pygame.K_F9: None,
    pygame.K_F10: None,
    pygame.K_F11: None,
    pygame.K_F12: None,
})

som_ativo = None
som_global = None
esperando_tecla_individual = False
removendo_som_individual = False
mensagem_toast = ""
tempo_toast = 0

def carregar_som(nome_do_arquivo):
    if os.path.exists(nome_do_arquivo):
        try:
            return pygame.mixer.Sound(nome_do_arquivo)
        except pygame.error as e:
            print(f"Erro ao carregar som: {e}")
            return None
    else:
        print(f"Arquivo de som não encontrado: {nome_do_arquivo}")
        return None

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    caminho_do_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de som", "*.wav *.mp3")])
    root.destroy()
    return caminho_do_arquivo

def salvar_configuracoes():
    with open('configuracoes.json', 'w') as f:
        json.dump(teclas, f)

def carregar_configuracoes():
    global teclas
    try:
        with open('configuracoes.json', 'r') as f:
            teclas = json.load(f)
        teclas = {int(k): v for k, v in teclas.items()}  # Converte as chaves para inteiros
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON de configurações")

def desenhar_teclas():
    y = 70
    margem_esquerda = 50
    margem_topo = 50
    espaco_vertical = 30
    largura_coluna = 300
    coluna = 0

    for i, tecla in enumerate(teclas.keys()):
        nome_tecla = pygame.key.name(tecla)
        som_tecla = os.path.basename(teclas[tecla]) if teclas[tecla] else "Sem som"
        texto = f"{nome_tecla}: {som_tecla}"
        texto_surface = fonte.render(texto, True, PRETO)
        rect = pygame.Rect(margem_esquerda + (coluna * largura_coluna), margem_topo + (i % 18) * espaco_vertical, largura_coluna, espaco_vertical - 5)
        pygame.draw.rect(screen, CINZA_CLARO, rect)
        pygame.draw.rect(screen, AZUL, rect, 2)
        screen.blit(texto_surface, (rect.x + 5, rect.y + 5))

        if (i + 1) % 18 == 0:
            coluna += 1

def desenhar_botoes():
    botoes = []
    botoes_texto = ["Definir Som Global", "Remover Todos os Sons", "Definir Som Individual", "Remover Som Individual"]
    for i, botao_texto in enumerate(botoes_texto):
        botao_surface = fonte.render(botao_texto, True, PRETO)
        botao_rect = pygame.Rect(tamanho_da_tela[0] - 200, 20 + i * 50, 180, 40)
        pygame.draw.rect(screen, VERDE if "Definir" in botao_texto else VERMELHO, botao_rect)
        pygame.draw.rect(screen, AZUL, botao_rect, 2)
        screen.blit(botao_surface, (botao_rect.x + 10, botao_rect.y + 10))
        botoes.append(botao_rect)
    return botoes

def desenhar_toast(mensagem):
    if mensagem:
        toast_surface = fonte_toast.render(mensagem, True, BRANCO)
        rect = toast_surface.get_rect(center=(tamanho_da_tela[0] // 2, tamanho_da_tela[1] - 50))
        pygame.draw.rect(screen, PRETO, rect.inflate(20, 20))
        pygame.draw.rect(screen, BRANCO, rect.inflate(20, 20), 2)
        screen.blit(toast_surface, rect)

def on_key_event(event):
    global som_ativo, som_global, esperando_tecla_individual, removendo_som_individual, mensagem_toast, tempo_toast

    key_name = event.name
    try:
        tecla = pygame.key.key_code(key_name)
    except ValueError:
        return

    if esperando_tecla_individual:
        caminho_do_som = selecionar_arquivo()
        if caminho_do_som:
            teclas[tecla] = caminho_do_som
        esperando_tecla_individual = False
        mensagem_toast = ""
    elif removendo_som_individual:
        if tecla in teclas:
            teclas[tecla] = None
        removendo_som_individual = False
        mensagem_toast = "Som removido individualmente"
    else:
        if tecla in teclas:
            som = carregar_som(teclas[tecla]) if teclas[tecla] else som_global
            if som:
                if som_ativo:
                    som_ativo.stop()
                som_ativo = som
                som_ativo.play()

def main():
    global teclas, som_global, esperando_tecla_individual, removendo_som_individual, mensagem_toast, tempo_toast

    carregar_configuracoes()

    keyboard.hook(on_key_event)

    while True:
        screen.fill(PRETO)
        
        titulo = fonte_titulo.render("Mapa de Teclas e Sons", True, BRANCO)
        screen.blit(titulo, (tamanho_da_tela[0] // 2 - titulo.get_width() // 2, 20))

        desenhar_teclas()
        botoes = desenhar_botoes()
        desenhar_toast(mensagem_toast)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salvar_configuracoes()
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botoes[0].collidepoint(evento.pos):  
                    caminho_do_som = selecionar_arquivo()
                    if caminho_do_som:
                        som_global = carregar_som(caminho_do_som)
                        for tecla in teclas:
                            if teclas[tecla] is None:
                                teclas[tecla] = caminho_do_som
                        salvar_configuracoes()
                elif botoes[1].collidepoint(evento.pos):  
                    teclas = {k: None for k in teclas}
                    som_global = None
                    mensagem_toast = "Todos os sons foram removidos"
                    tempo_toast = time.time()
                    salvar_configuracoes()
                elif botoes[2].collidepoint(evento.pos):  
                    esperando_tecla_individual = True
                    mensagem_toast = "Pressione uma tecla para definir seu som"
                    tempo_toast = time.time()
                elif botoes[3].collidepoint(evento.pos):  
                    removendo_som_individual = True
                    mensagem_toast = "Pressione uma tecla para remover seu som"
                    tempo_toast = time.time()

        if time.time() - tempo_toast > 3:
            mensagem_toast = ""

        pygame.display.flip()

if __name__ == "__main__":
    main()

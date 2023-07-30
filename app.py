import pygame
import os
import sys
from config import *
from utils import *
from editor import Editor

class App:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCRW, SCRH))
        self.clock = pygame.time.Clock()
    def start(self):
        EventHandler.init()

        self.editor = Editor(self.screen)

        # loop
        while self.is_open():
            self.run()
        self.close()
    def run(self):
        self.screen.fill('black')
        EventHandler.poll_events()

        self.editor.run()

        self.clock.tick(FPS)
        pygame.display.update()
    def is_open(self) -> bool:
        return not EventHandler.is_close_requested() and not EventHandler.keydown(pygame.K_q)
    def close(self):
        pygame.quit()
        sys.exit()
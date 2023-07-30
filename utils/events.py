import pygame

class EventHandler:
    events: list[pygame.event.Event] = []
    @staticmethod
    def init():
        EventHandler.poll_events()
    def poll_events():
        EventHandler.events = pygame.event.get()
    def keydown(key: pygame.key) -> bool:
        for e in EventHandler.events:
            if e.type == pygame.KEYDOWN:
                if e.key == key:
                    return True
        return False
    @staticmethod
    def clicked(key: int = 1) -> bool:
        for e in EventHandler.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == key:
                    return True
        return False
    @staticmethod
    def is_close_requested() -> bool:
        for e in EventHandler.events:
            if e.type == pygame.QUIT:
                return True
        return False
    @staticmethod
    def scroll_wheel_up() -> bool:
        for e in EventHandler.events:
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 4:
                    return True
        return False
    @staticmethod
    def scroll_wheel_down() -> bool:
        for e in EventHandler.events:
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 5:
                    return True
        return False
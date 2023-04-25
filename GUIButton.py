import pygame
 
class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, screen, text, pos = (0,0), font = 30, bg="black", feedback=""):
        self.screen = screen
        self.text = text
        self.bg = bg
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.rect = None
        # self.change_text(text, bg)
 
    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self):
        ## NEW ##
        if self.rect is None:
            self.change_text(self.text, self.bg)
        self.screen.blit(self.surface, (self.x, self.y))
 
    def click(self, event, handler):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    return handler()
                
        return False
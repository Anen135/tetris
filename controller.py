import pygame

class Controller:
    def __init__(self, fUP = None, fDOWN = None, fLEFT = None, fRIGHT = None, fESC = None, fSPACE = None, fRETURN = None, fQUIT = None):
        pygame.init()
        self.keydown = {
            pygame.K_UP: fUP,
            pygame.K_DOWN: fDOWN,
            pygame.K_LEFT: fLEFT,
            pygame.K_RIGHT: fRIGHT,
            pygame.K_RETURN: fRETURN,
        }
        self.keyup = {
            pygame.K_SPACE: fSPACE,
            pygame.K_ESCAPE: fESC,
        }
        self.fQUIT = fQUIT
        self.going = [0,0]

        

    def checkKeys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.fQUIT()
            elif event.type == pygame.KEYUP:
                self.keyup[event.key]()
            elif event.type == pygame.KEYDOWN:
                self.keydown[event.key]()
            

def test():
    pygame.display.set_caption('Тетрис')
    screen = pygame.display.set_mode((500, 500))
    fps_clock = pygame.time.Clock()
    fps_clock.tick(1)
    controller = Controller()
    print('                        ', end='\r')
    print(controller.checkKeys(), end='\r')

if __name__ == '__main__':
    while True:
        test()
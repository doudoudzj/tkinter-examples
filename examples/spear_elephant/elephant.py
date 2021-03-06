#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# python elephant

#Import Modules
import os, pygame
from pygame.locals import *

if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')


def load_image(name, colorkey=None):
    '''functions to create our resources'''
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fullname)
        raise (SystemExit, message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    '''加载声音'''

    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound:', fullname)
        raise (SystemExit, message)
    return sound


#classes for our game objects
class Spear(pygame.sprite.Sprite):
    """moves a clenched spear on the screen, following the mouse"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image, self.rect = load_image('spear-w.png', -1)
        self.punching = 0

    def update(self):
        "move the spear based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        "returns true if the spear collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        "called to pull the spear back"
        self.punching = 0


class Elephant(pygame.sprite.Sprite):
    """moves a elephant critter across the screen. it can spin the
       monkey when it is punched."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  #call Sprite intializer
        self.image, self.rect = load_image('elephant-nw.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        "move the monkey across the screen, and turn at the ends"
        newpos = self.rect.move((self.move, 0))
        if self.rect.left < self.area.left or \
           self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos

    def _spin(self):
        "spin the monkey image"
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        "this will cause the monkey to start spinning"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((468, 60))
    pygame.display.set_caption('Monkey Fever')
    pygame.mouse.set_visible(0)

    #Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    #Put Text On The Background, Centered
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Pummel The Elephant, And Win $$$", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width() / 2)
        background.blit(text, textpos)

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    #Prepare Game Objects
    clock = pygame.time.Clock()
    whiff_sound = load_sound('elephant-jump.wav')
    punch_sound = load_sound('elephant-mmove.wav')
    elephant = Elephant()
    spear = Spear()
    allsprites = pygame.sprite.RenderPlain((spear, elephant))

    #Main Loop
    while 1:
        clock.tick(60)

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if spear.punch(elephant):
                    punch_sound.play()  #punch
                    elephant.punched()
                else:
                    whiff_sound.play()  #miss
            elif event.type is MOUSEBUTTONUP:
                spear.unpunch()

        allsprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()


#Game Over

#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()

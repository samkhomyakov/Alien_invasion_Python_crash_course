import pygame
from pygame.sprite import Sprite


class Ship(Sprite):

    def __init__(self, ai_settings, screen):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Load the ship image and get it's rect
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Start each new ship at the bottom center of the screen
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Saving the real coordinate of the center of the ship
        self.center = float(self.rect.centerx)

        # Movement flags
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Updates the ship's position based on the flag."""
        # Updates an attribute center, not rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > -0:
            self.center -= self.ai_settings.ship_speed_factor

        # Updates the rect attribute based on self.center
        self.rect.centerx = self.center

    def center_ship(self):
        """Places the ship in the center of the bottom side."""
        self.center = self.screen_rect.centerx

    def blitme(self):
        """Draws the ship at the current position."""
        self.screen.blit(self.image, self.rect)
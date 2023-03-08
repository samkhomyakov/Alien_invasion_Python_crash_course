import sys
from time import sleep

import pygame

from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Responds to key presses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fires a bullet if the maximum has not yet been reached."""
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
    bullets.add(new_bullet)


def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    """Handles key presses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button,
                              ship, aliens, bullets, mouse_x, mouse_y)
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets,
                      mouse_x, mouse_y):
    """Starts a new game when the Play button is pressed."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:

        # Reset game settings
        ai_settings.initialize_dynamic_settings()

        # Hides the mouse pointer
        pygame.mouse.set_visible(False)

        # Reset game statistics
        stats.reset_stats()
        stats.game_active = True

        # Resetting score and level images
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # Clearing aliens and bullets lists
        aliens.empty()
        bullets.empty()

        # Creating a new fleet and placing the ship in the center
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Update images on the screen and flip to the new screen."""
    # A screen is drawn on each iteration of the loop
    screen.fill(ai_settings.bg_color)

    # All bullets are displayed behind the image of the ship and aliens
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    # Displays score
    sb.show_score()

    # The play button is displayed when the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    # Displaying the last drawn screen
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Updates bullet positions and destroys old bullets."""

    # Bullet position update
    bullets.update()

    # Removing bullets that have gone off the edge of the screen
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Aliens bullets collision handling."""
    # Removal of bullets and aliens involved in collisions
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
            check_high_score(stats, sb)

    # If the fleet is destroyed, the next level begins
    if len(aliens) == 0:
        bullets.empty()
        ai_settings.increase_speed()

        # Level up
        stats.level +=1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)


def get_number_aliens_x(ai_settings, alien_width):
    """Calculates the number of aliens in a row."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return  number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """Specifies the number of rows to fit on the screen."""
    available_space_y = (ai_settings.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Creates an alien and places it in a row."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Creates an alien fleet."""
    # Creating an alien and calculating the number of aliens in a row
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
                                  alien.rect.height)

    # Create an alien fleet
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x) :
            create_alien(ai_settings, screen, aliens, alien_number,
                         row_number)


def check_fleet_edges(ai_settings, aliens):
    """Reacts when an alien reaches the edge of the screen."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Lowers the entire fleet and changes the direction of the fleet."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Handles ship collision with alien."""
    # Decrease ships_left
    if stats.ships_left > 0:
        # Decrease ships_left
        stats.ships_left -= 1

        # Game information update
        sb.prep_ships()

        # Clearing aliens and bullets lists
        aliens.empty()
        bullets.empty()

        # Creating a new fleet and placing the ship in the center
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause.
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Checks if the aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # The same happens as in a collision with a ship
            ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Checks if the fleet has reached the edge of the screen,

    after which it updates the positions of all aliens in the fleet.

    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Alien-ship collision check
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)

    # Checking for aliens that have reached the bottom of the screen
    check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets)


def check_high_score(stats, sb):
    """Checks if there is a new record."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
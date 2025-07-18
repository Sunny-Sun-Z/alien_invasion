import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from time import sleep
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # set fullscreen mode and set setting screen width and height
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        # end setting fullscreen mode
        self.screen = pygame.display.set_mode(
            # (1200, 800)
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")
        # Create an instance to store game statistics.
        self.stats = GameStats(self)
         # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.sb = Scoreboard(self)
        # self.bg_color = (230, 230, 230)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.game_active = False
         # Make the Play button.
        self.play_button = Button(self, "Play")
        
        
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            # print("Main loop running, game_active:", self.game_active)
            self._check_events()
            if self.game_active:          
                self.ship.update()
                self._update_bullets()
                self._update_aliens()            
            
            self._update_screen()
            # Redraw the screen during each pass through the loop.
            # self.screen.fill(self.bg_color)
            self.clock.tick(60)
            
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.        
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            # print(len(self.bullets))
        self._check_bullet_alien_collisions()
            
     
    def _check_bullet_alien_collisions(self):    
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()        
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()  
            self.settings.increase_speed()
            # self.game_active = False
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()
            
             
    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)  
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)     
                 
    def _update_screen(self): 
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        # Draw the score information.
        self.sb.show_score()
        # Draw the play button if the game is inactive
        if not self.game_active:
            # print("Drawing play button")
            self.play_button.draw_button()
        pygame.display.flip()


    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
                
                
    def _check_keyup_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            # self.ship.rect.x -=2
            self.ship.moving_right = False        
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        # Add more movement logic here if needed.


    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
            
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        # Make an alien.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        self.aliens.add(alien)
        # alien_width = alien.rect.width

        # current_x = alien_width
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
                      
             # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height
            
                                  
    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.y = y_position
        new_alien.rect.x = x_position
        self.aliens.add(new_alien)
    
    
    def _update_aliens(self):
        """Update the position of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()
        
        
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):   
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
             alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
       
       
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        # Decrement ships_left.
        self.stats.ships_left -= 1
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
        # Pause.
            sleep(0.5) 
        else:
            print("Game over! Setting game_active to False")
            self.game_active = False
            pygame.mouse.set_visible(True)
    
    # def _ship_hit(self):
    #     self.stats.ships_left -= 1
    #     if self.stats.ships_left == 0:
    #         self.game_active = False
    #         pygame.mouse.set_visible(True)
    #     else:
    #         # Get rid of any remaining bullets and aliens.
    #         self.bullets.empty()
    #         self.aliens.empty()
    #         # Create a new fleet and center the ship.
    #         self._create_fleet()
    #         self.ship.center_ship()
    #         sleep(0.5)
            
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
             if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break  
        
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        # if self.play_button.rect.collidepoint(mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)
    
            
if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
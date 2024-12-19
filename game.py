import random
import arcade
from multiprocessing import Process, Array, Lock

# import pandas as pd
# import numpy as np
# import serial

SCREEN_WIDTH = arcade.get_screens()[0].width * 4 // 5
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Man Vs. Mind"

CHARACTER_SCALING = 1
TILE_SCALING = 1
GRAVITY = 1500
PLAYER_JUMP_SPEED = 800

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 800

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

#how many of each state
amount_of_images = {"idle": 4, "attack":6, "jump":4}
# 6 6 5 3 2 2
attack_frame = [3, 7, 12, 17, 25, 30] # how many ticks should the program stay in each frame
attack_frame = [num // 3 for num in attack_frame]
ATTACK_FRAME = attack_frame[3] + 1 # which frame the attack frame should read as
TOTAL_ATTACK_FRAME = attack_frame[-1]

arr = None
lock = None

hurt_frame = [4, 10]

# arduino = serial.Serial(port='COM4', baudrate=115200, timeout=1)

queue = None

class PlayerSprite(arcade.Sprite): 
    def __init__(self, character): #takes input as which character (biker/punk)
        super().__init__(scale=1, hit_box_algorithm="Detailed")
        self.state_number = 0
        self.facing_actual = 0 #what it's actually facing
        self.state = "idle"
        self.scale = CHARACTER_SCALING
        self.facing_direction = 0 # 1 for right 0 for left
        self.health = 100
        self._hit_box_algorithm = "Detailed"
        self.attack_state = 0
        path = f"images/{character}"


        #idle animation
        self.idle_textures = []
        for i in range(1, amount_of_images["idle"] + 1):
            # print(f"{path}/Idle/image{i}x1.png")
            texture = arcade.load_texture_pair(f"{path}/Idle/image{i}x1.png", hit_box_algorithm="Detailed")
            self.idle_textures.append(texture)
        
        
        # attack animation
        self.attack_textures = []
        self.attack2_textures = []
        for i in range(1, amount_of_images["attack"] + 1):
            # print(f"{path}/Attack1/image{i}x1.png")
            texture = arcade.load_texture_pair(f"{path}/Attack1/image{i}x1.png", hit_box_algorithm="Detailed")
            self.attack_textures.append(texture)
            texture = arcade.load_texture_pair(f"{path}/Attack2/image{i}x1.png", hit_box_algorithm="Detailed")
            self.attack2_textures.append(texture)
        


        # jump animation
        self.jump_textures = []
        for i in range(1, amount_of_images["jump"] + 1):
            # print(f"{path}/Jump/image{i}x1.png")
            texture = arcade.load_texture_pair(f"{path}/Jump/image{i}x1.png", hit_box_algorithm="Detailed")
            self.jump_textures.append(texture)
        
        self.texture = self.idle_textures[0][0]
        self._hit_box_detail = 1
        self.texture._hit_box_detail = 1

        #hurt animation
        self.hurt_textures = []
        for i in range(1,3):
            texture = arcade.load_texture_pair(f"{path}/Hurt/image{i}x1.png", hit_box_algorithm="Detailed")
            self.hurt_textures.append(texture)
        
    def check_face_direction(self, other_player:arcade.Sprite = None):
        if other_player.center_x > self.center_x:
            self.facing_direction = 1
        elif other_player.center_x < self.center_x:
            self.facing_direction = 0


class GameOverView(arcade.View):
    """ Class to manage the game over view """

    def set_message(self, win_message):
        self.win_message = win_message

    def on_show_view(self):
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """ Draw the game over view """
        self.clear()
        arcade.draw_text(f"Game Over - {self.win_message}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, 30, anchor_x="center")

    def on_key_press(self, key, _modifiers):
        """ If user hits escape, go back to the main menu view """
        if key == arcade.key.ESCAPE:
            self.window.close()


class MyGame(arcade.View):
    """
    Main application class.
    """
    
    def draw_health_bar(self, player_sprite, x, y, width, height):
        """
        Draws a health bar at the given x, y position.
        """
        # Calculate health percentage
        health_percentage = player_sprite.health / self.max_health

        # Background (gray bar)
        arcade.draw_rectangle_filled(x, y, width, height, arcade.color.GRAY)

        # Foreground (green bar based on health)
        arcade.draw_rectangle_filled(
            x - (width * (1 - health_percentage)) / 2,  # Adjust based on health
            y,
            width * health_percentage,  # Adjust width based on health
            height,
            arcade.color.GREEN
        )



    def __init__(self):
        # super().__init__(width, height, title)
        super().__init__()

        self.background = None

        # These are 'lists' that keep track of our sprites. Each sprite should

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite1 = None
        self.player_sprite2 = None

        self.max_health = 100

        self.sprite_list = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        # Our physics engine
        # Create the physics engine
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(gravity=gravity)

        # arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Initialize Scene
        self.scene = arcade.Scene()

        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        

        self.background = arcade.load_texture("images/background.png")


        # Add to scene
        self.scene.add_sprite_list("Player 1")
        self.scene.add_sprite_list("Player 2")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # Initialize first player
        self.player_sprite1 = PlayerSprite("Biker")
        # self.player_sprite1 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite1.center_x = SCREEN_WIDTH * 2 // 3
        self.player_sprite1.center_y = 150
        self.player_sprite1.width = 100
        self.player_sprite1.height = 170
        self.scene.add_sprite("Player 1", self.player_sprite1)
        self.physics_engine.add_sprite(self.player_sprite1,
                                       elasticity=0,
                                       friction=1.5,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       max_horizontal_velocity=PLAYER_MOVEMENT_SPEED,
                                       max_vertical_velocity=PLAYER_JUMP_SPEED)
        
        # Initialize second player
        # self.player_sprite2 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite2 = PlayerSprite("Punk")
        self.player_sprite2.center_x = SCREEN_WIDTH // 3
        self.player_sprite2.center_y = 150
        self.player_sprite2.width = 100
        self.player_sprite2.height = 170
        self.player_sprite2.facing_direction = 1
        self.scene.add_sprite("Player 2", self.player_sprite2)
        self.physics_engine.add_sprite(self.player_sprite2,
                                       elasticity=0,
                                       friction=1,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       max_horizontal_velocity=PLAYER_MOVEMENT_SPEED,
                                       max_vertical_velocity=PLAYER_JUMP_SPEED)

        self.player_sprite2.texture = self.player_sprite2.idle_textures[0][1]

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        self.wall_list = []
        for x in range(128, SCREEN_WIDTH -128, 32):
            wall = arcade.Sprite("images/Tiles/GroundTop.png", TILE_SCALING)
            wall.width = 32
            wall.height = 32
            wall.center_x = x
            wall.center_y = 16
            self.scene.add_sprite("Walls", wall)
            self.wall_list.append(wall)
        self.physics_engine.add_sprite_list(self.wall_list,
                                    collision_type="wall",
                                    body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.debug_draw_options = True
        
    def on_draw(self):
        """
        Render the screen.
        """
        # arcade.draw_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_texture)

        # This command should happen before we start drawing. It will clear
        # the screen to thex background color, and erase what we drew last frame.
        self.clear()

        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        # Activate our Camera
        self.camera.use()

        # Call draw() on all your sprite lists below
        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        self.draw_health_bar(self.player_sprite2, x=100, y=self.height - 50, width=200, height=20)  # Top left for player 1
        self.draw_health_bar(self.player_sprite1, x=self.width - 100, y=self.height - 50, width=200, height=20)  # Top right for player 2


        # to visualize hit box
        # self.player_sprite1.draw_hit_box()
        # self.player_sprite2.draw_hit_box()

        


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        # player2 (UnoController), player1 (BCI)

        if key == arcade.key.UP: # player 1 jump
            if self.physics_engine.is_on_ground(self.player_sprite1):
                self.physics_engine.set_vertical_velocity(self.player_sprite1, PLAYER_JUMP_SPEED)
                self.player_sprite1.state = "jump"

        if key == arcade.key.W: # player 2 jump
            if self.physics_engine.is_on_ground(self.player_sprite2):
                self.physics_engine.set_vertical_velocity(self.player_sprite2, PLAYER_JUMP_SPEED)
                self.player_sprite2.state = "jump"
                
        if key == arcade.key.DOWN : # player 1 attack
            # if self.player_sprite1.collides_with_sprite(self.player_sprite2):
            #     self.player_sprite2.health -= 10
            if(self.player_sprite1.state != "attack"):
                self.player_sprite1.state_number = 0
                self.player_sprite1.attack_state = random.randint(0,1)
                self.player_sprite1.state = "attack"
            
            
        if  key == arcade.key.S: #player 2 attack
            # if self.player_sprite2.collides_with_sprite(self.player_sprite1):
            #     self.player_sprite1.health -= 10
            if(self.player_sprite2.state != "attack" ):
                self.player_sprite2.state_number = 0
                self.player_sprite2.attack_state = random.randint(0,1)
                self.player_sprite2.state = "attack"

        if key == arcade.key.LEFT: # player 1 left movement
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, -PLAYER_MOVEMENT_SPEED)
        if key == arcade.key.A: # player 2 left movement
            self.physics_engine.set_horizontal_velocity(self.player_sprite2, -PLAYER_MOVEMENT_SPEED)

        if key == arcade.key.RIGHT: # player 1 right movement
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, PLAYER_MOVEMENT_SPEED)
        if key == arcade.key.D: # player 2 right movement
            self.physics_engine.set_horizontal_velocity(self.player_sprite2, PLAYER_MOVEMENT_SPEED)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP:
            self.player_sprite1.change_y = 0
        if key == arcade.key.W:
            self.player_sprite2.change_y = 0
        if key == arcade.key.DOWN:
            self.player_sprite1.change_y = 0
        if  key == arcade.key.S:
            self.player_sprite2.change_y = 0
            
        if key == arcade.key.LEFT:
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, 0)
        if key == arcade.key.A:
            self.physics_engine.set_horizontal_velocity(self.player_sprite2, 0)
        if key == arcade.key.RIGHT:
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, 0)
        if key == arcade.key.D:
            self.physics_engine.set_horizontal_velocity(self.player_sprite2, 0)

        

    def on_update(self, delta_time):
        """Movement and game logic"""
        # if arduino.in_waiting > 0:  # Check if there is data available to read
        #     line = arduino.readline().decode('utf-8').strip()  # Read the line and decode it
            
        # if ManVsMind.action == 'BCI_JUMP': # player 1 jump
        #         if self.physics_engine.is_on_ground(self.player_sprite1):
        #             self.physics_engine.set_vertical_velocity(self.player_sprite1, PLAYER_JUMP_SPEED)

        # if line == 'JUMP': # player 2 jump
        #     if self.physics_engine.is_on_ground(self.player_sprite2):
        #         self.physics_engine.set_vertical_velocity(self.player_sprite2, PLAYER_JUMP_SPEED)
                    
        # if ManVsMind.action == 'BCI_ATTACK': # player 1 attack
        #     if self.player_sprite1.collides_with_sprite(self.player_sprite2):
        #         self.player_sprite2.health -= 10
        #     self.player_sprite1.state = "ATTACK"
        #     self.player_sprite1.state_number = 0

        # if line == 'ATTACK': #player 2 attack
        #     if self.player_sprite2.collides_with_sprite(self.player_sprite1):
        #         self.player_sprite1.health -= 10
        #     self.player_sprite2.state = "attack"
        #     self.player_sprite2.state_number = 0

            
        # if line == 'LEFT': # player 2 left movement
        #     self.physics_engine.set_horizontal_velocity(self.player_sprite2, -PLAYER_MOVEMENT_SPEED)

        # if line == 'RIGHT': # player 2 right movement
        #         self.physics_engine.set_horizontal_velocity(self.player_sprite2, PLAYER_MOVEMENT_SPEED)

        # Move the player with the physics engine
        self.physics_engine.step()


        self.player_sprite1.check_face_direction(self.player_sprite2)
        self.player_sprite1.set_hit_box(self.player_sprite1.texture.hit_box_points)
        self.player_sprite2.check_face_direction(self.player_sprite1)
        self.player_sprite2.set_hit_box(self.player_sprite2.texture.hit_box_points)
        self.update_animation()
        
        # if self.player_sprite2.state == "attack" or self.player_sprite1.state == "attack":
        #     self.check_hits() #to check if there are any hits
        if(self.player_sprite1.state == "attack" and self.player_sprite1.state_number == ATTACK_FRAME):
            # if(self.player_sprite1.center_x)
            # arcade.draw_point(self.player_sprite1.center_x, self.player_sprite1.center_y, arcade.color.GREEN, 50)
            # print(self.player_sprite1.state_number, self.player_sprite1.center_x, self.player_sprite1.center_y, self.player_sprite1.facing_direction)
            # attack_point = ((75 * (-1) ** self.player_sprite2.facing_direction ) + self.player_sprite1.center_x, self.player_sprite1.center_y)
            attack_point = (75 * (-1 if self.player_sprite2.facing_direction else 1 ) + self.player_sprite1.center_x, self.player_sprite1.center_y)

            # print(attack_point, self.player_sprite2.center_x, self.player_sprite2.center_y, self.player_sprite1.facing_direction, (-1) ** self.player_sprite1.facing_direction * 100)
            if(self.player_sprite2.collides_with_point(attack_point)):
                self.player_sprite2.health -= 10
                self.player_sprite2.state = "hurt"
                self.player_sprite2.state_number = 0

        if(self.player_sprite2.state == "attack" and self.player_sprite2.state_number == ATTACK_FRAME):
            # if(self.player_sprite1.center_x)
            # arcade.draw_point(self.player_sprite1.center_x, self.player_sprite1.center_y, arcade.color.GREEN, 50)
            # print(self.player_sprite1.state_number, self.player_sprite1.center_x, self.player_sprite1.center_y, self.player_sprite1.facing_direction)
            attack_point = ((75 * (-1) ** self.player_sprite1.facing_direction ) + self.player_sprite2.center_x, self.player_sprite2.center_y)
            attack_point = (75 * (-1 if self.player_sprite1.facing_direction else 1 ) + self.player_sprite2.center_x, self.player_sprite2.center_y)

            # print(attack_point, self.player_sprite1.center_x, self.player_sprite2.center_y, self.player_sprite1.facing_direction, (-1) ** self.player_sprite1.facing_direction * 100)
            if(self.player_sprite1.collides_with_point(attack_point)):
                self.player_sprite1.health -= 10
                self.player_sprite1.state = "hurt"
                self.player_sprite1.state_number = 0


        if self.player_sprite1.health <= 0:
            # window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Different Views Minimal Example")
            
            # window.show_view(GameOverView())
            game_over = GameOverView()
            game_over.set_message("Player 2 Wins!")
            # self.game_over.window.self = self
            self.window.show_view(game_over)
        elif self.player_sprite2.health <= 0:
            # window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Different Views Minimal Example")
            # window.show_view(GameOverView())
            game_over = GameOverView()
            game_over.set_message("Player 1 Wins!")
            # self.game_over.window.self = self
            self.window.show_view(game_over)

        # print("player 1:: ", self.player_sprite1.texture.hit_box_points)
        # print("player 2:: ", self.player_sprite2.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1 / 5):
            # print(self.player_sprite1.state_number)
            # check for player 1
            if(self.player_sprite1.state == "idle"):
                #4 * 7
                if(self.player_sprite1.state_number >= 28):
                    self.player_sprite1.state_number = 0
                self.player_sprite1.texture = self.player_sprite1.idle_textures[int(self.player_sprite1.state_number / 7)][self.player_sprite2.facing_direction]
                self.player_sprite1.state_number += 1
            if(self.player_sprite2.state == "idle"):
                if(self.player_sprite2.state_number >= 28):
                    self.player_sprite2.state_number = 0
                self.player_sprite2.texture = self.player_sprite2.idle_textures[int(self.player_sprite2.state_number / 7)][1 - self.player_sprite2.facing_direction]
                self.player_sprite2.state_number += 1
            if(self.player_sprite1.state == "attack"):
                if(self.player_sprite1.state_number >= TOTAL_ATTACK_FRAME):
                    self.player_sprite1.state_number = 0
                    self.player_sprite1.state = "idle"
                else:
                    find_attack_index1 = find_index(attack_frame, self.player_sprite1.state_number)
                    # self.player_sprite1.texture = self.player_sprite1.(attack_textures if self.player_sprite1.attack_state == 0 else )[find_attack_index1][self.player_sprite2.facing_direction]
                    self.player_sprite1.texture = (self.player_sprite1.attack_textures[find_attack_index1][self.player_sprite2.facing_direction] if self.player_sprite1.attack_state == 0 else self.player_sprite1.attack2_textures[find_attack_index1][self.player_sprite2.facing_direction])
                    self.player_sprite1.state_number += 1
            if(self.player_sprite2.state == "attack"):
                if(self.player_sprite2.state_number >= TOTAL_ATTACK_FRAME):
                    self.player_sprite2.state_number = 0
                    self.player_sprite2.state = "idle"
                else:
                    find_attack_index2 = find_index(attack_frame, self.player_sprite2.state_number)
                    # self.player_sprite2.texture = self.player_sprite2.attack_textures[find_attack_index2][1 - self.player_sprite2.facing_direction]
                    self.player_sprite2.texture = (self.player_sprite2.attack_textures[find_attack_index2][self.player_sprite1.facing_direction] if self.player_sprite2.attack_state == 0 else self.player_sprite2.attack2_textures[find_attack_index2][self.player_sprite1.facing_direction])
                    self.player_sprite2.state_number += 1
            if(self.player_sprite1.state == "jump"):
                # if(self.player_sprite1.state_number):
                self.player_sprite1.texture = self.player_sprite1.jump_textures[1][1 - self.player_sprite1.facing_direction]
                if(self.physics_engine.is_on_ground(self.player_sprite1)):
                    self.player_sprite1.state = "idle"
            if(self.player_sprite2.state == "jump"):
                # if(self.player_sprite2.state_number):
                self.player_sprite2.texture = self.player_sprite2.jump_textures[1][1 - self.player_sprite2.facing_direction]
                if(self.physics_engine.is_on_ground(self.player_sprite2)):
                    self.player_sprite2.state = "idle"

            if(self.player_sprite1.state == "hurt"):
                if(self.player_sprite1.state_number == hurt_frame[-1]):
                    self.player_sprite1.state = "idle"
                    self.player_sprite1.state_number = 0
                else:
                    find_hurt_index1 = find_index(hurt_frame, self.player_sprite1.state_number)
                    self.player_sprite1.texture = (self.player_sprite1.hurt_textures[find_hurt_index1][self.player_sprite2.facing_direction])
                    self.player_sprite1.state_number += 1

            if(self.player_sprite2.state == "hurt"):
                if(self.player_sprite2.state_number == hurt_frame[-1]):
                    self.player_sprite2.state = "idle"
                    self.player_sprite2.state_number = 0
                else:
                    find_hurt_index2 = find_index(hurt_frame, self.player_sprite2.state_number)
                    self.player_sprite2.texture = (self.player_sprite2.hurt_textures[find_hurt_index2][self.player_sprite1.facing_direction])
                    self.player_sprite2.state_number += 1
            

                
            
def find_index(frames, value):
    for i in range(len(frames)):
        if(frames[i] > value):
            return i

def main(data_arr: Array, data_lock: Lock):
    """ Main function """
    arr = data_arr
    lock = data_lock
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_window = MyGame()
    main_window.setup()
    window.show_view(main_window)
    arcade.run()

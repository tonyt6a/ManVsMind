import arcade
import threading
import time

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Man Vs. Mind"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
GRAVITY = 1500
PLAYER_JUMP_SPEED = 800

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 800

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

#how many of each state
amount_of_images = {"idle": 4}


class PlayerSprite(arcade.Sprite): 
    def __init__(self, character): #takes input as which character (biker/punk)
        super().__init__()
        self.state_number = 0
        self.state = "idle"
        self.scale = CHARACTER_SCALING

        path = f"images/{character}"

        self.idle_textures = []
        for i in range(1, amount_of_images["idle"] + 1):
            # print(f"{path}/Idle/image{i}x1.png")
            texture = arcade.load_texture_pair(f"{path}/Idle/image{i}x1.png")
            self.idle_textures.append(texture)

        self.texture = self.idle_textures[0][0]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # These are 'lists' that keep track of our sprites. Each sprite should

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite1 = None
        self.player_sprite2 = None

        self.sprite_list = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Player health
        self.player1_health = 100
        self.player2_health = 100

        # Our physics engine
        # Create the physics engine
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(gravity=gravity)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Initialize Scene
        self.scene = arcade.Scene()

        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)


        # Add to scene
        self.scene.add_sprite_list("Player 1")
        self.scene.add_sprite_list("Player 2")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # Initialize first player
        image_source = "images/testSprite.png"
        self.player_sprite1 = PlayerSprite("Biker")
        # self.player_sprite1 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite1.center_x = 1000
        self.player_sprite1.center_y = 150
        self.player_sprite1.width = 192
        self.player_sprite1.height = 192
        self.scene.add_sprite("Player 1", self.player_sprite1)
        self.physics_engine.add_sprite(self.player_sprite1,
                                       elasticity=0,
                                       friction=1.5,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       max_horizontal_velocity=PLAYER_MOVEMENT_SPEED,
                                       max_vertical_velocity=PLAYER_JUMP_SPEED)
        # Initialize second player
        # self.player_sprite2 = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite2 = PlayerSprite("Biker")
        self.player_sprite2.center_x = 120
        self.player_sprite2.center_y = 150
        self.player_sprite2.width = 192
        self.player_sprite2.height = 192
        self.scene.add_sprite("Player 2", self.player_sprite2)
        self.physics_engine.add_sprite(self.player_sprite2,
                                       elasticity=0,
                                       friction=1,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       max_horizontal_velocity=PLAYER_MOVEMENT_SPEED,
                                       max_vertical_velocity=PLAYER_JUMP_SPEED)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        self.wall_list = []
        for x in range(0, 1500, 32):
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
        
    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Activate our Camera
        self.camera.use()

        # Call draw() on all your sprite lists below
        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()



    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite1):
                self.physics_engine.set_vertical_velocity(self.player_sprite1, PLAYER_JUMP_SPEED)
        if key == arcade.key.W:
            if self.physics_engine.is_on_ground(self.player_sprite2):
                self.physics_engine.set_vertical_velocity(self.player_sprite2, PLAYER_JUMP_SPEED)
        if key == arcade.key.DOWN:
            self.player_sprite1.change_y = -PLAYER_MOVEMENT_SPEED
        if  key == arcade.key.S:
            self.player_sprite2.change_y = -PLAYER_MOVEMENT_SPEED
        if key == arcade.key.LEFT:
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, -PLAYER_MOVEMENT_SPEED)
        if key == arcade.key.A:
            self.physics_engine.set_horizontal_velocity(self.player_sprite2, -PLAYER_MOVEMENT_SPEED)
        if key == arcade.key.RIGHT:
            self.physics_engine.set_horizontal_velocity(self.player_sprite1, PLAYER_MOVEMENT_SPEED)
        if key == arcade.key.D:
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


        # Move the player with the physics engine
        self.physics_engine.step()

        self.update_animation()

    def update_animation(self, delta_time: float = 1 / 5):
            # print(self.player_sprite1.state_number)
            #check for player 1
            if(self.player_sprite1.state == "idle"):
                #4 * 7
                if(self.player_sprite1.state_number >= 28):
                    self.player_sprite1.state_number = 0
                self.player_sprite1.texture = self.player_sprite1.idle_textures[int(self.player_sprite1.state_number / 7)][0]
                self.player_sprite1.state_number += 1

def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

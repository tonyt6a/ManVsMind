import arcade

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Man Vs. Mind"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
GRAVITY = .3
PLAYER_JUMP_SPEED = 10

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5


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
            texture = arcade.load_texture_pair(f"{path}/Idle/image{i}x1.png", hit_box_algorithm="Detailed")
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

        # Our physics engine
        self.physics_engine = None

        # player sprite list
        self.player_sprite1 = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Initialize Scene
        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # Initialize first player
        # image_source = "images/Biker/Idle/image1x1.png"
        self.player_sprite1 = PlayerSprite("Biker")
        self.player_sprite1.center_x = 64
        self.player_sprite1.center_y = 67
        self.player_sprite1.width = 192
        self.player_sprite1.height = 192
        # for i in range(amount_of_images["idle"]):
        #     texture =  arcade.load_texture_pair(f"{player_states['idle']}/image{i+1}x1.png")
        #     self.player_sprite1.idle_textures.append(texture)
        self.scene.add_sprite("Player 1", self.player_sprite1)
        

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally

        for x in range(0, 1500, 32):
            wall = arcade.Sprite("images/Tiles/GroundTop.png", TILE_SCALING)
            wall.width = 32
            wall.height = 32
            wall.center_x = x
            wall.center_y = 16
            self.scene.add_sprite("Walls", wall)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite1, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )
        

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        # Draw our Scene
        self.scene.draw()


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite1.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.S:
            self.player_sprite1.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.A:
            self.player_sprite1.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_sprite1.change_x = PLAYER_MOVEMENT_SPEED
            

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.W:
            self.player_sprite1.change_y = 0
        elif key == arcade.key.S:
            self.player_sprite1.change_y = 0
        elif key == arcade.key.A:
            self.player_sprite1.change_x = 0
        elif key == arcade.key.D:
            self.player_sprite1.change_x = 0

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

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

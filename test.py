import arcade

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Man Vs. Mind"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.wall_list = None
        self.player_list = None

        self.player_sprite = None

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        #create the sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        #set up the player
        image_source = 
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below

    # def on_update(self, delta_time):
    #     """
    #     All the logic to move, and the game logic goes here.
    #     Normally, you'll call update() on the sprite lists that
    #     need it.
    #     """
    #     pass

    # def on_key_press(self, key, key_modifiers):
    #     """
    #     Called whenever a key on the keyboard is pressed.

    #     For a full list of keys, see:
    #     https://api.arcade.academy/en/latest/arcade.key.html
    #     """
    #     pass

    # def on_key_release(self, key, key_modifiers):
    #     """
    #     Called whenever the user lets off a previously pressed key.
    #     """
    #     pass

    # def on_mouse_motion(self, x, y, delta_x, delta_y):
    #     """
    #     Called whenever the mouse moves.
    #     """
    #     pass

    # def on_mouse_press(self, x, y, button, key_modifiers):
    #     """
    #     Called when the user presses a mouse button.
    #     """
    #     pass

    # def on_mouse_release(self, x, y, button, key_modifiers):
    #     """
    #     Called when a user releases a mouse button.
    #     """
    #     pass


def main():
    """ Main function """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

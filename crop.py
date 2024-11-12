from PIL import Image
import os

def crop_image(image_path, output_path, crop_size=(150, 185)):
    """Crops the bottom-left part of an image and saves it."""
    with Image.open(image_path) as img:
        width, height = img.size
        
        # Ensure the image is large enough to crop from the bottom-left
        if width < crop_size[0] or height < crop_size[1]:
            print(f"Image {image_path} is too small to crop to {crop_size}. Skipping.")
            return

        # Crop the bottom-left corner: (left=0, top=height-crop_size[1], right=crop_size[0], bottom=height)
        cropped_img = img.crop((0, height - crop_size[1], crop_size[0], height))
        
        # Save the cropped image, overwriting the original
        cropped_img.save(output_path)
        print(f"Cropped image saved: {output_path}")

def process_images_in_folder(folder_path, crop_size=(150, 185)):
    """Processes 4 specific images in a folder and crops them."""
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # Define the 4 specific image file names (assuming they are in png format)
    image_files = [
        "image1x1.png",
        "image2x1.png",
        "image3x1.png",
        "image4x1.png",
        "image5x1.png",
        "image6x1.png",   
    ]

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        
        # Check if the image file exists
        if os.path.exists(image_path):
            # Crop the image and save it
            crop_image(image_path, image_path, crop_size)
        else:
            print(f"Image file {image_path} not found. Skipping.")

# if __name__ == "__main__":
#     # Specify the folder path where the images are located
#     folder_path = "C:\\Users\\zahee\\OneDrive\\Desktop\\Projects\\ManVsMind\\images\\Biker\\Hurt"
#     # Run the image processing
#     process_images_in_folder(folder_path)

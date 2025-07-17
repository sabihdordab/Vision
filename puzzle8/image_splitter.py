from PIL import Image
import os

def split_image(image_path, output_folder, grid_size=(3, 3)):
    img = Image.open(image_path)
    width, height = img.size
    tile_width = width // grid_size[0]
    tile_height = height // grid_size[1]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tiles = []
    index = 0
    for row in range(grid_size[1]):
        for col in range(grid_size[0]):
            left = col * tile_width
            upper = row * tile_height
            right = left + tile_width
            lower = upper + tile_height
            crop = img.crop((left, upper, right, lower))

            if index == grid_size[0] * grid_size[1] - 1:
                white_tile = Image.new("RGB", (tile_width, tile_height), color=(255, 255, 255))
                white_tile.save(f"{output_folder}/tile_{index}.png")
                tiles.append(white_tile)
            else:
                crop.save(f"{output_folder}/tile_{index}.png")
                tiles.append(crop)
            index += 1

    print(f"{index} tile(s) saved in '{output_folder}'")
    return tiles


base_dir = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = base_dir + "/images"
OUTPUT_DIR = base_dir + "/tiles"
GRID_SIZE = (3, 3)

if __name__ == "__main__":
    for filename in os.listdir(IMAGES_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            image_path = os.path.join(IMAGES_DIR, filename)
            image_name = os.path.splitext(filename)[0]
            output_path = os.path.join(OUTPUT_DIR, image_name)
            split_image(image_path, output_path, grid_size=GRID_SIZE)

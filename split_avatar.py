from PIL import Image

img = Image.open("avatars_2.jpg")
width, height = img.size
num = 2
rows, cols = 3, 3  # сетка
tile_w, tile_h = width // cols, height // rows

for r in range(rows):
    for c in range(cols):
        box = (c*tile_w, r*tile_h, (c+1)*tile_w, (r+1)*tile_h)
        tile = img.crop(box)
        tile.save(f"avatar_{num}_{r}_{c}.png")

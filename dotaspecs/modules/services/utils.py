from PIL import Image, ImageOps


def image_compress(image_path, height, width):
    """Оптимизация изображений"""
    img = Image.open(image_path)

    if img.mode != 'P':
        if img.mode != 'RGB':
            img = img.convert('RGB')

    if img.height > height or img.width > width:
        output_size = (height, width)
        img.thumbnail(output_size)

    if img.mode != 'P':
        img = ImageOps.exif_transpose(img)
        img.save(image_path, format='JPEG', quality=90, optimize=True)

from PIL import Image, ImageSequence, ImageEnhance

def toBlackAndWhite(file_path, path_to_edited_photo):
    img = Image.open(file_path)
    try:
        if img.is_animated:
            frames = []
            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert('L'))
            #ImageSequence.write(frames, path_to_edited_photo, format='GIF')
            frames[0].save(path_to_edited_photo ,save_all = True, append_images=frames[1:], duration=40)
        else:
            img = img.convert("L")
            img.save(path_to_edited_photo)
    except AttributeError:
        img = img.convert("L")
        img.save(path_to_edited_photo)



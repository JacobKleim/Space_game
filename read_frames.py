import os


def read_frames(folder_path):
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        with open(os.path.join(folder_path, filename), 'r') as file:
            frames.append(file.read())
    return frames

from pickle import dump, load
from os.path import getsize
from copy import deepcopy
from os import (listdir, mkdir)


database_file = "binary_fun_crossword.data"
images_dir = "images"


def load_database(filename):

    game_dir_contents = listdir('.')
    if filename not in game_dir_contents:
        f = open(filename, 'w+')
        f.close()

    if getsize(filename) > 0:
        with open(filename, 'rb') as f:
            database = load(f)
    else:
        database = {
            # image_name : score
            'highscores' :   {},
            'settings' : {
                'cell width' :           5,
                'cell height' :          2,
                'random plane size' :    [8, 8],
                'time' :                 False,
                'show line count hint' : True,
                'show binary hint' :     True,
                'show line complete hint': True
                },
            # would be somethnig like this "image name" : plane
            'images' :       {},
            'image choice' : 'random'
        }

    return database


def save_database(database, filename):

    with open(filename, 'wb') as f:
        dump(database, f)


def make_database(highscores, settings, images, image_choice):

    database = {
        'highscores' :   deepcopy(highscores),
        'settings' :     deepcopy(settings),
        'images' :       deepcopy(images),
        'image choice' : deepcopy(image_choice)
    }

    return database


def add_highscore(highscores, image, score):

    dp_highscores = deepcopy(highscores)

    if ( image not in dp_highscores ) or ( score < dp_highscores[image] ):
        dp_highscores[image] = score

    return dp_highscores


def remove_image(images, highscores, name):
    dp_images = deepcopy(images)
    dp_highscores = deepcopy(highscores)
    dp_images.pop(name)
    if name in dp_highscores:
        dp_highscores.pop(name)
    return dp_images, dp_highscores


def list_files_in_dir(directory):

    game_dir_contents = listdir('.')
    if directory not in game_dir_contents:
        mkdir(directory)
        image_list = []
    else:
        image_list = list(filter(lambda a: a.endswith('.txt'),
                                 listdir(directory)))

    return image_list


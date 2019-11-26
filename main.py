#!/usr/bin/env python3

import curses
from copy import deepcopy
from time import time
from curses_funcs import (draw_plane, run_selection_menu, show_message)

from game_funcs import (load_file, check_image, calc_image_sizes, create_plane,
                        load_image_on_plane, create_random_image,
                        calc_binaries_per_line, get_plane, update_position,
                        flip_number_on_plane, planes_binaries_match)

from database_funcs import (load_database, save_database, make_database,
                            add_highscore, remove_image, list_files_in_dir,
                            database_file, images_dir)


help_text = '''
This is Binary Fun Crossword game.
You should combine cells to make binary numbers that equals to the
decimal numbers in each row and column.
Number order:
     --> row
    |
    V
    column

In game:
    To move you can use arrows or hjkl ( hi vimers =) )
    To flip cell number (from 0 to 1 or from 1 to 0) press space
    Press q to quit
In menus:
    To move you can user arrows or jk
    Press Enter to choose item in menu
To hide message boxes press any key.
Enjoy.
'''


def start_game(screen, images, image_choice, highscores, settings):

    if image_choice == 'random':
        plane = create_random_image(create_plane(*settings['random plane size']))
    else:
        plane = images[image_choice]

    dp_highscores = deepcopy(highscores)
    numbers = calc_binaries_per_line(plane)
    user_plane = create_plane(len(plane[0]), len(plane))
    user_numbers = calc_binaries_per_line(user_plane)
    cur_pos = (0, 0)

    draw_plane(screen, user_plane, cur_pos, numbers, user_numbers, settings)

    running = True
    start_time = time()
    while running:

        key = screen.getch()

        if key == ord('q'):
            show_message(screen, 'Game Info', 'You ended the game.', 40)
            running = False
            return dp_highscores

        elif key == curses.KEY_UP or key == ord('k'):
            cur_pos = update_position(plane, cur_pos, row = -1, col = 0)

        elif key == curses.KEY_DOWN or key == ord('j'):
            cur_pos = update_position(plane, cur_pos, row = 1, col = 0)

        elif key == curses.KEY_LEFT or key == ord('h'):
            cur_pos = update_position(plane, cur_pos, row = 0, col = -1)

        elif key == curses.KEY_RIGHT or key == ord('l'):
            cur_pos = update_position(plane, cur_pos, row = 0, col = 1)

        elif key == ord(' '):
            user_plane = flip_number_on_plane(user_plane, cur_pos)
            user_numbers = calc_binaries_per_line(user_plane)
            if planes_binaries_match(numbers, user_numbers):
                end_time = round(time() - start_time)
                running = False
                continue

        draw_plane(screen, user_plane, cur_pos, numbers, user_numbers, settings)

    show_message(screen, 'Game Info', 'You Win', 40)

    if settings['time']:
        show_message(screen, 'Game Info',
                     'Your time {}'.format(str(end_time)), 40)
        dp_highscores = add_highscore(dp_highscores, image_choice, end_time)

    return dp_highscores


def show_manage_images_menu(screen, images, highscores):

    dp_images = deepcopy(images)
    dp_highscores = deepcopy(highscores)


    def run_add_image_menu(img_dict):

        new_img_dict = deepcopy(img_dict)

        files = list_files_in_dir(images_dir)
        if files:
            chosen_file = run_selection_menu(screen, files + ['go back'],
                                             'Choose file')
            if chosen_file != 'go back':
                image_txt = load_file(images_dir + '/' + chosen_file)
                if check_image(image_txt):
                    plane = create_plane(*calc_image_sizes(image_txt))
                    plane = load_image_on_plane(plane, image_txt, '1')
                    new_img_dict[chosen_file.split('.')[0]] = plane
                else:
                    show_message(screen, 'Error', 'Not valid image.', 40)
        else:
            show_message(screen, 'Error', 'No file found.', 40)

        return new_img_dict


    def run_remove_image_menu(img_dict, hs_dict):

        new_img_dict, new_hs_dict = deepcopy(img_dict), deepcopy(hs_dict)

        if img_dict:
            img_name = run_selection_menu(screen,
                                          list(img_dict.keys()) + ['go back'],
                                          'Remove Image')
            if img_name != 'go back':
                confirm = run_selection_menu(screen, ['yes', 'no'],
                                            ('Are you sure that you want to ' +
                                             'delete this image ' +
                                             '"{}"'.format(img_name)))
                if confirm == 'yes':
                    new_img_dict, new_hs_dict = remove_image(new_img_dict,
                                                            new_hs_dict,
                                                            img_name)
        else:
            show_message(screen, 'Error', 'Image list is empty.', 40)

        return new_img_dict, new_hs_dict

    running = True
    while running:
        choice = run_selection_menu(screen,
                                    ['add image', 'remove image',
                                     'go to main menu'],
                                    'Manage Images')
        if choice == 'go to main menu':
            running = False
            continue

        elif choice == 'add image':
            dp_images = run_add_image_menu(dp_images)

        elif choice == 'remove image':
            dp_images, dp_highscores = run_remove_image_menu(dp_images,
                                                             dp_highscores)

    return dp_images, dp_highscores


def show_highscores(screen, highscores):

    highscores_names = list(highscores.keys())
    highscores_scores = list(map(lambda a: str(a), highscores.values()))
    largest_name = max([len(a) for a in highscores_names])
    largest_score = max([len(a) for a in highscores_scores])
    width = max(largest_name + largest_score + 1, len('Highscores'))

    highscores_string = ''
    for key, value in highscores.items():
        name = ('{:<' + str(largest_name) + '}').format(key)
        score = ('{:<' + str(largest_score) + '}').format(value)
        highscores_string += name + ' ' + score + '\n'

    show_message(screen, 'Highscores', highscores_string, width)


def show_settings_menu(screen, settings):


    def choose_number(num_range, title):
        return int(run_selection_menu(screen,
                                      [str(num) for num in num_range],
                                      title))

    def choose_boolean(title):
        choice = run_selection_menu(screen, ['yes', 'no'], title)
        return True if choice == 'yes' else False


    dp_settings = deepcopy(settings)
    menu_list = sorted(dp_settings.keys()) + ['go to main menu']

    running = True
    while running:
        menu_item = run_selection_menu(screen, menu_list, 'Settings')

        if menu_item == 'go to main menu':
            running = False
            continue

        elif menu_item == 'cell width':
            dp_settings[menu_item] = choose_number(range(1, 6), 'Cell Width')

        elif menu_item == 'cell height':
            dp_settings[menu_item] = choose_number(range(1, 3), 'Cell Height')

        elif menu_item == 'random plane size':
            p_width = choose_number(range(4, 11), 'Random Plane Width')
            p_height = choose_number(range(4, 11), 'Random Plane Height')
            dp_settings[menu_item] = [p_width, p_height]

        elif menu_item == 'time':
            dp_settings[menu_item] = choose_boolean('Count time and save ' +
                                                    'to highscores?')

        elif menu_item == 'show line count hint':
            dp_settings[menu_item] = choose_boolean('Show line count per line?')

        elif menu_item == 'show binary hint':
            dp_settings[menu_item] = choose_boolean('Show binary hint below ' +
                                                    'plane?')
        elif menu_item == 'show line complete hint':
            dp_settings[menu_item] = choose_boolean('Highlight number if line' +
                                                    'is complete?')

    return dp_settings


def main(stdscr):

    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdscr.clear()
    stdscr.keypad(True)

    database = load_database(database_file)
    highscores = deepcopy(database['highscores'])
    settings = deepcopy(database['settings'])
    images = deepcopy(database['images'])
    image_choice = deepcopy(database['image choice'])
    main_menu_title = 'Binary Fun Crossword'
    main_menu_list =  ['play game', 'select image', 'manage image',
                       'show highscores', 'settings', 'help', 'quit']


    running = True
    while running:
        command = run_selection_menu(stdscr, main_menu_list, main_menu_title)

        if command == "play game":
            highscores = start_game(stdscr, images, image_choice,
                                    highscores, settings)

        elif command == "select image":
            image_choice = run_selection_menu(stdscr,
                                              list(images.keys()) + ['random'],
                                              'Image Selection Menu')
        elif command == 'manage image':
            images, highscores = show_manage_images_menu(stdscr, images,
                                                         highscores)

        elif command == 'show highscores':
            show_highscores(stdscr, highscores)

        elif command == "settings":
            settings = show_settings_menu(stdscr, settings)

        elif command == "help":
            show_message(stdscr, 'Help', help_text, 80)

        elif command == "quit":
            database = make_database(highscores, settings, images, image_choice)
            save_database(database, database_file)
            running = False

if __name__ == "__main__":
    curses.wrapper(main)

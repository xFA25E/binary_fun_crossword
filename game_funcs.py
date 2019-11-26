from copy import deepcopy
from random import choice


def transponse(plane):
    return [list(row) for row in zip(*plane)]


def load_file(image_path):

    with open(image_path, 'r') as f:
        image_txt = f.read()
        image_txt = image_txt.rstrip()

    return image_txt


def check_image(image_txt):


    def check_sizes(image):

        def check(plane):
            sizes = [len(a) for a in plane]
            if len(sizes) == sizes.count(sizes[0]):
                return True

        img_list = [a.strip().split() for a in image_txt.splitlines()]

        if check(img_list) and check(transponse(img_list)):
            print('Image true')
            return True


    def check_characters(image):

        def check_char(char):
            if char != ' ' and char != '\n':
                return True

        def find_all_chars(array):
            res = []
            for char in array:
                if char not in res:
                    res.append(char)
            return res


        all_chars = find_all_chars(filter(check_char, image))
        if len(all_chars) == 2:
            print('characters true')
            return True

    if check_sizes(image_txt) and check_characters(image_txt):
        return True


def calc_image_sizes(image_txt):

    lines = image_txt.splitlines()

    width = len(lines[0].rstrip().split())
    height = len(lines)
    return width, height


def create_plane(width, height):
    return [[0 for i in range(width)] for j in range(height)]


def load_image_on_plane(plane, image_txt, one):

    dp_plane = deepcopy(plane)
    lines = image_txt.splitlines()

    for l_inx in range(len(lines)):
        line = lines[l_inx].split()

        for c_inx in range(len(line)):
            if line[c_inx] == one:
                dp_plane[l_inx][c_inx] = 1
        print()

    return dp_plane


def get_plane(filename):

    image_string = load_file(filename)

    if check_image(image_string):
        sizes = calc_image_sizes(image_string)
        plane = create_plane(*sizes)
        plane = load_image_on_plane(plane, image_string, "1")
    else:
        plane = create_plane(10, 10)
        plane = create_random_image(plane)

    return plane


def create_random_image(plane):

    dp_plane = deepcopy(plane)

    for i in range(len(dp_plane)):
        for j in range(len(dp_plane[i])):
            dp_plane[i][j] = choice([0, 1])

    return dp_plane


def calc_binaries_per_line(plane):

    numbers = {'rows': [], 'cols': []}

    for row in plane:
        numbers['rows'].append(int(''.join([str(i) for i in row]),
                                   2))

    for col in transponse(plane):
        numbers['cols'].append(int(''.join([str(i) for i in col]),
                                   2))

    return numbers


def flip_number_on_plane(plane, pos):
    dp_plane = deepcopy(plane)

    if dp_plane[pos[0]][pos[1]]:
        dp_plane[pos[0]][pos[1]] = 0
    else:
        dp_plane[pos[0]][pos[1]] = 1

    return dp_plane


def planes_binaries_match(dict_plane_one, dict_plane_two):

    if (dict_plane_one['rows'] == dict_plane_two['rows'] and
        dict_plane_one['cols'] == dict_plane_two['cols']):
        return True


def update_position(plane, cur_pos, row, col):

    next_row, next_col = cur_pos[0] + row, cur_pos[1] + col
    height, width = len(plane), len(plane[0])

    if ( 0 <= next_row < height and
         0 <= next_col < width ):
        return next_row, next_col
    else:
        return cur_pos

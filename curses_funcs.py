import curses
from copy import deepcopy


def split_text_by_size(text, size):

    result = []
    current_line = ''

    for letter in text:
        if (letter == '\n') or (len(current_line + letter) > size):
            result.append(current_line)
            current_line = ''
        else:
            current_line += letter
    else:
        if result and (current_line != result[-1]):
            result.append(current_line)
        elif not result:
            result.append(current_line)

    return result


def draw_plane(screen, plane, cur_pos, numbers, user_numbers, settings):

    count_hint = settings['show line count hint']
    bin_hint = settings['show binary hint']
    highlight_hint = settings['show line complete hint']
    height = len(plane)
    width = len(plane[0])
    cw = settings['cell width']
    ch = settings['cell height']
    y_offset = round((curses.LINES - ((ch + 1) * height + 1)) / 2)
    x_offset = round((curses.COLS - ((cw + 1) * width + 1)) / 2)

    top = '┌' + (('┬' + ('─' * cw)) * width + '┐')[1:]
    mid = '├' + (('┼' + ('─' * cw)) * width + '┤')[1:]
    bot = '└' + (('┴' + ('─' * cw)) * width + '┘')[1:]

    screen.clear()

    screen.addstr(y_offset - 1, x_offset - 1, top)

    for row in range(height):

        for o in range(ch):
            screen.addstr((row * (ch + 1)) + y_offset + o, x_offset - 1, '│')

            for col in range(width):

                if plane[row][col]:
                    cell = ("{:^" + str(cw) + "}").format("1" if o == 0 else " ")
                    attr = curses.A_REVERSE
                else:
                    cell = ("{:^" + str(cw) + "}").format("0" if o == 0 else " ")
                    attr = curses.A_NORMAL

                if (row, col) == cur_pos: attr = curses.color_pair(1)

                screen.addstr((row * (ch + 1)) + y_offset + o,
                              (col * (cw + 1)) + x_offset,
                              cell, attr)
                screen.addstr((row * (ch + 1)) + y_offset + o,
                              (col * (cw + 1)) + x_offset + cw,
                              "│", curses.A_NORMAL)
        if count_hint:
            line_count_string = '{} {}'.format(str(numbers['rows'][row]),
                                               str(user_numbers['rows'][row]))
        else:
            line_count_string = str(numbers['rows'][row])

        if ( highlight_hint and
             ( numbers['rows'][row] == user_numbers['rows'][row] ) ):
            attr = curses.A_REVERSE
        else:
            attr = curses.A_NORMAL
        screen.addstr((row * (ch + 1)) + y_offset,
                      (width * (cw + 1)) + x_offset,
                      line_count_string, attr)
        screen.addstr((row * (ch + 1)) + y_offset + ch, x_offset - 1,
                      mid)

    screen.addstr((height * (ch + 1)) + y_offset - 1, x_offset - 1, bot)
    screen.addstr((height * (ch + 1)) + y_offset, x_offset - 1,
                  ' ' + ' '.join([("{:^" + str(cw) + "}").format(str(num))
                                  for num in numbers['cols']]))
    if count_hint:
        screen.addstr((height * (ch + 1)) + y_offset + 1, x_offset - 1,
                      ' ' + ' '.join([("{:^" + str(cw) + "}").format(str(num))
                                      for num in user_numbers['cols']]))
    if bin_hint:
        binary_count = [str(2 ** n) for n in range(max(width, height) - 1,
                                                   -1,
                                                   -1)]
        binary_count = [('{:^' + str(cw) + '}').format(num)
                        for num in binary_count]
        screen.addstr((height * (ch + 1)) + y_offset + 3, x_offset - 1,
                      ' ' + ' '.join(binary_count),
                      curses.color_pair(4))


def run_selection_menu(screen, menu_list, title):

    attr = curses.color_pair(2)
    attr_sel = curses.color_pair(3)
    height = len(menu_list)
    width = max([len(word) for word in (menu_list + [title])])
    hb = '| '
    vb = hb + '-' * width + ''.join(reversed(hb))
    y_offset = round((curses.LINES - height - 2 - 2) / 2)
    x_offset = round((curses.COLS - width - (len(hb) * 2)) / 2)
    selected = 0


    def move_selected(num):
        next_position = selected + num
        if 0 <= next_position < height:
            return next_position
        else:
            return selected


    def draw_menu():
        screen.clear()
        screen.addstr(y_offset - 1, x_offset, vb, attr)
        f_title = ('{:<' + str(width) + '}').format(title)
        screen.addstr(y_offset, x_offset,
                      hb + f_title + ''.join(reversed(hb)),
                      attr)
        screen.addstr(y_offset, x_offset + len(hb),
                      f_title, attr | curses.A_BOLD)
        screen.addstr(y_offset + 1, x_offset, vb, attr)

        for row in range(height):
            menu_item = ("{:<" + str(width) + "}").format(menu_list[row])
            screen.addstr(y_offset + row + 2,
                          x_offset,
                          hb + menu_item + ''.join(reversed(hb)),
                          attr)

        screen.addstr(y_offset + height + 2, x_offset, vb, attr)
        menu_item = ("{:<" + str(width) + "}").format(menu_list[selected])
        screen.addstr(y_offset + selected + 2,
                      x_offset + len(hb),
                      menu_item, attr_sel)

    draw_menu()
    running = True
    while running:
        key = screen.getch()

        if key == ord('j') or key == curses.KEY_DOWN:
            selected = move_selected(1)

        elif key == ord('k') or key == curses.KEY_UP:
            selected = move_selected(-1)

        elif key == 10:
            item = deepcopy(menu_list[selected])
            running = False

        draw_menu()

    return item


def show_message(screen, title, content, content_width):

    attr = curses.color_pair(4)
    hb = '| '
    vb = hb + '-' * content_width + ''.join(reversed(hb))
    s_title = split_text_by_size(title, content_width)
    s_content = split_text_by_size(content, content_width)
    title_height = len(s_title)
    content_height = len(s_content)
    y_offset = round((curses.LINES - title_height - content_height - 4) / 2)
    x_offset = round((curses.COLS - content_width - (len(hb) * 2)) / 2)

    screen.clear()
    screen.refresh()

    screen.addstr(y_offset - 1, x_offset, vb, attr)

    for row in range(title_height):
        line = ('{:<' + str(content_width) + '}').format(s_title[row])
        line = hb + line + ''.join(reversed(hb))
        screen.addstr(y_offset + row, x_offset, line, attr)
        screen.addstr(y_offset + row, x_offset + len(hb),
                      s_title[row], attr | curses.A_BOLD)

    screen.addstr(y_offset + title_height, x_offset, vb, attr)

    for row in range(content_height):
        line = ('{:<' + str(content_width) + '}').format(s_content[row])
        line = hb + line + ''.join(reversed(hb))
        screen.addstr(y_offset + title_height + row + 1, x_offset, line, attr)

    screen.addstr(y_offset + title_height + content_height + 1, x_offset, vb, attr)
    screen.getch()

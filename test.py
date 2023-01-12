'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 17:03:41
LastEditTime: 2023-01-12 17:03:43
Software: VSCode
'''
import curses

def draw_rectangle(stdscr, x, y, width, height):
    stdscr.attron(curses.color_pair(1))
    for i in range(x, x+width):
        stdscr.addch(y, i, curses.ACS_CKBOARD)
        stdscr.addch(y+height, i, curses.ACS_CKBOARD)
    for i in range(y, y+height):
        stdscr.addch(i, x, curses.ACS_CKBOARD)
        stdscr.addch(i, x+width, curses.ACS_CKBOARD)
    stdscr.attroff(curses.color_pair(1))

stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
draw_rectangle(stdscr, 10, 5, 20, 10)
stdscr.refresh()
stdscr.getch()
curses.endwin()

if __name__ == "__main__":
    draw_rectangle(10,10)
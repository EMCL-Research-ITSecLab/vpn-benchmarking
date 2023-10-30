import curses


class Screen:	
    def __init__(self) -> None:  
        self.win = curses.initscr()
    
        curses.noecho()
        curses.cbreak()
        self.win.keypad(True)
  
    def __del__(self) -> None:
        curses.nocbreak()
        self.win.keypad(False)
        curses.echo()
        curses.endwin()
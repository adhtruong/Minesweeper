import random
import time

import tkinter
from tkinter import Button, messagebox

class Cell(Button):
    def __init__(self, is_mine, master=None, mine_count=0, visible=False, flagged=False, **options):
        super().__init__(master, **options)
        self.is_mine = is_mine
        self.mine_count = mine_count
        self.visible = visible
        self.flagged = flagged

    def reset(self, is_mine, mine_count=0, visible=False, flagged=False):
        self.is_mine = is_mine
        self.mine_count = mine_count
        self.visible = visible
        self.flagged = flagged

        self["relief"] = "raised"
        self.update_display()

    def place_mine(self):
        self.is_mine = True

    def increment_mine_count(self):
        self.mine_count += 1

    def get_mine_status(self):
        return self.is_mine

    def get_mine_count(self):
        return self.mine_count

    def get_visibility(self):
        return self.visible

    def show(self):
        self.visible = True
        self.update_display()

    def toggle_flagged(self):
        '''Simulate right click, return adjustment to mine count'''
        # if flagged already remove flag
        if self.flagged:
            self.flagged = False
            self.visible = False
            self.update_display()
            return 1
        else:
            # if visible and unflagged ignore
            if not self.visible:
                self.flagged = True
                self.visible = True
                self.update_display()
                return -1
        return 0

    def left_click(self):
        '''Left click simultion and return whether game should end'''

        # if not flagged, then show cell and return mine info
        if not self.flagged:
            self.show()

        return self.is_mine

    def update_display(self):
        if self.visible:
            self["text"] = self.get_content()
            #self["state"] = "disabled"
            if self.flagged:
                self["bg"] = "red"
            elif self.is_mine:
                self["bg"] = "purple"
            else:
                self["bg"] = "light blue"
        else:
            self["text"] = " "
            self["bg"] = "light grey"
            self["relief"] = "raised"

    def get_content(self):
        if self.flagged:
          return "F"
        elif self.is_mine:
            return "M"
        else:
            if self.mine_count == 0:
                return "-"
            else:
                return str(self.mine_count)

class Board(object):
    def __init__(self, mines=8, rows=10, columns=10):
        self.mines = mines
        self.remaining_mines = mines
        self.rows = rows
        self.columns = columns
        self.initilize_board()

    def initilize_board(self):
        self.root = tkinter.Tk()
        self.root.title("Minesweeper")

        self.controls = tkinter.Frame(self.root, borderwidth=1)
        self.controls.pack()

        self.remaining_mines_label = tkinter.Label(self.controls, text="Remaining mines: " + str(self.remaining_mines))
        self.remaining_mines_label.pack(side="left")

        self.restart_button = Button(self.controls, text="Restart", command=self.reset_game)
        self.restart_button.pack(side="left")

        self.timer_label = tkinter.Label(self.controls, text="Time: 0")
        self.timer_label.pack(side="left")

        self.resize_board()
        self.reset_game()

        self.root.mainloop()

    def resize_board(self):
        # add empty cells

        self.f = tkinter.Frame(self.root, width=20*self.columns, height=20*self.rows, borderwidth=10)
        self.f.pack()

        self.cells = []
        for i in range(self.columns):
            self.cells.append([])
            for j in range(self.rows):
              btn = Cell(False, self.f, width=2, height=2)
              btn.bind("<Button-1>", lambda event, i=i, j=j: self.left_click_cell(i, j))
              btn.bind("<Button-3>", lambda event, i=i, j=j: self.right_click_cell(i, j))
              btn.grid(column=i, row=j, sticky="NESW")
              self.cells[i].append(btn)

    def reset_game(self):
        self.active = True
        self.playing = False

        # reset cells
        for i in range(self.columns):
            for j in range(self.rows):
                self.cells[i][j].reset(False)

        # reset timer
        self.timer_label["text"] = "Time: 000"

        # reset remaining mines label
        self.remaining_mines = self.mines
        self.remaining_mines_label["text"] = "Remaining mines: " + str(self.remaining_mines)

    def start_game(self, col, row):
        '''On first click, place mines and start game'''

        # add mines
        available_positions = [(i,j) for i in range(self.columns) for j in range(self.rows)]
        available_positions.remove((col, row))
        mine_positions = random.sample(available_positions, self.mines)
        for i, j in mine_positions:
            self.place_mine(i,j)

        # start timer
        self.start_time = time.time()
        self.update_timer()

        self.playing = True

        self.left_click_cell(col, row)

    def update_cell_display(self):
        #self.root.title(str(self.remaining_mines))
        for i in range(self.rows):
            for j in range(self.columns):
                self.cells[i][j].update_display()

    def update_timer(self):
        if self.active:
            self.timer_label["text"] = "Time: " + str(int(time.time()-self.start_time)).rjust(3,"0")
            self.root.after(100, self.update_timer)
        else:
            self.end_time = time.time()

    def place_mine(self, col, row):
        # change cell to mine
        self.cells[col][row].place_mine()

        # increase the mine count of surrounding cells
        for i, j in self.get_surrounding_cells(col, row):
            self.cells[i][j].increment_mine_count()

    def get_surrounding_cells(self, col, row):
        surrounding = []
        for i in range(col-1,col+2):
            if i >= 0 and i < self.columns:
                for j in range(row-1,row+2):
                    if j >= 0 and j < self.rows:
                        surrounding.append((i,j))
        surrounding.remove((col,row))
        return surrounding

    def show_cell(self, col, row):
        self.cells[col][row].show()

    def no_mine(self, col, row):
        '''Show cells when there are no surrounding mines'''
        for (i,j) in self.get_surrounding_cells(col,row):
            if not self.cells[i][j].get_visibility():
                self.cells[i][j].show()
                if self.cells[i][j].get_mine_count() == 0:
                    self.no_mine(i,j)

    def left_click_cell(self, col, row):
        '''Simulate left click'''

        if self.active:
            if not self.playing:
                self.start_game(col, row)
            elif not self.cells[col][row].flagged and not self.cells[col][row].visible:
                is_mine = self.cells[col][row].is_mine
                self.cells[col][row].show()

                # if mine and unflagged, end game
                if is_mine:
                    self.end_game()
                else:
                    # act if there are no  mines
                    if self.cells[col][row].get_mine_count() == 0:
                        self.no_mine(col, row)

                    # check if player has won
                    if self.check_win():
                        self.active = False
                        messagebox.showinfo("You won!", "Click to play again")


    def right_click_cell(self, col, row):
        if self.active:
            self.remaining_mines += self.cells[col][row].toggle_flagged()
            self.remaining_mines_label["text"] = "Remaining mines: " + str(self.remaining_mines)

    def check_win(self):
        for i in range(self.columns):
            for j in range(self.rows):
                if not self.cells[i][j].get_mine_status() and not self.cells[i][j].get_visibility():
                    return False
        return True

    def end_game(self):
        self.active = False
        messagebox.showinfo("You lost!", "Click to play again")
        for i in range(self.columns):
            for j in range(self.rows):
                if self.cells[i][j].get_mine_status() and not self.cells[i][j].flagged:
                    self.cells[i][j].show()

    def get_cell_content(self):
        content = []
        for i in range(self.rows):
            content.append([])
            for j in range(self.columns):
                content[i].append(self.cells[i][j].get_content())
        return content

def main():
    b = Board()

if __name__ == '__main__':
    main()

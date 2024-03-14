import tkinter as tk
import random

class MineSweeper:
    def __init__(self, root, rows, columns, num_mines, on_update_mines, onFinish):
        
        self.root = root
        self.rows = rows
        self.columns = columns
        self.num_mines = num_mines
        self.on_update_mines = on_update_mines
        self.onFinish = onFinish

        self.mine_array = []
        self.all_tiles = []
        self.table = []
        
        self.timer = 0
        self.finished = False
        
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.create_table()
        
     
        
    def create_table(self):
       
        for i in range(self.num_mines): # Creates and stores Mines
            mine = Mine(self.root)
            self.table.append(mine)                                                                                                                                      #type:ignore
            self.mine_array.append(mine)
            self.all_tiles.append(mine)
        for i in range((self.rows * self.columns) - self.num_mines): # Creates and stores Tile
            tile =Tile(self.root)
            self.table.append(tile)                                                                                                                                             #type:ignore
            self.all_tiles.append(tile)
        random.shuffle(self.table) # Shuffles Mines and Tiles 
        self.table = [self.table[i:i+self.rows] for i in range(0, len(self.table), self.columns)] # Seperates table into a list of tiles (rows) and saves them to table
        
        for line_index, line in enumerate(self.table):
            for tile_index, tile in enumerate(line):

                tile.position = (line_index, tile_index)  # Sets individual tile positions                                                                                                                                                          #type:ignore

                if isinstance(tile, Mine):
                    # Finds tiles surrounding Mines and increase their value if it is not a Mine aswell
                             #            N.W   N   N.E
                             #              \   |   /
                             #               \  |  /
                             #            W----Mine----E
                             #                 / | \
                             #               /   |  \
                             #            S.W    S   S.E
 
                             #        Cell-->Current Cell (0,0)
                             #        N -->  North        (-1,0)
                             #        S -->  South        (1,0)
                             #        E -->  East         (0,1)
                             #        W -->  West         (0,-1)
                             #        N.E--> North-East   (-1,1)
                             #        N.W--> North-West   (-1,-1)
                             #        S.E--> South-East   (1,1)
                             #        S.W--> South-West   (1,-1)

                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            try:

                                if not isinstance(self.table[line_index + i][tile_index +j], Mine) and len(self.table) > line_index + i >= 0 and len(line) > tile_index + j >= 0 and (i != 0 or j != 0):
                                    # Checks if surrounding Tile isn't a Mine and if its within the boundaries
                                    self.table[line_index + i][tile_index +j].value += 1                                                                                                                        #type:ignore
                            except IndexError:
                                pass
                                
        for row_index, row in enumerate(self.table):
            for col_index, tile in enumerate(row):
                # Creates Buttons for each Tile which can be pressed to reveal the tile 
                tile_button = tk.Button(self.frame, command=lambda t=tile: self.reveal(t), width=2, height=1, bg='grey') # Needed t=tile as loop was saving the last instance of a Tile
                tile_button.grid(row=row_index, column=col_index)
                tile.button = tile_button #type:ignore
                tile.button.bind('<Button-3>', lambda event, t=tile: self.toggle_flag(event,t))  # Right click Button bind to flag a Tile                                                                                                                                                              #type:ignore
                
                    
    
    def toggle_flag(self, event, tile):
        if tile.hidden: # Checks so you cant flag a Tile that has been revealed
            if tile.flagged: # Unflags if already flagged
                tile.button["text"] = "" 
                tile.flagged = False
                self.on_update_mines(1) # Callback function to update the number of mines flagged
                
                
            else: # Flags if not already Flagged
                tile.button["text"] = "Flag"
                tile.flagged = True
                self.on_update_mines(-1)
                
                
        if all(mine.flagged for mine in self.mine_array): # Checks if all mines are flagged -> Game Won
            self.finished = True
            self.onFinish('Win') # Callback function indicating Game Won
        
    def reveal(self, tile):
        if self.timer == 0 or not tile.hidden or tile.flagged or self.finished: # Cannot reveal if game hasn't started / tile already revealed / tile flagged / game over
            return
        
        colour = tile.colours[str(tile.value)] # Finds colour of tile value
        tk.Label(self.frame, text=tile.value, fg=colour, width=2, height=1).grid(row=tile.position[0], column=tile.position[1]) # Reveals Tile
        tile.hidden = False 
        
        if isinstance(tile, Mine): # If revelaed Tile is a Mine then Game Over
            self.finished = True
            self.onFinish('Lose') # Callback function indicating Game Lost
            return

        if tile.value > 0: # If Tile is touching a mine then dont go on revealing Tiles
            return
        
        else:
            # Checks surround Tiles
            for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if self.rows > tile.position[0] + i >= 0 and self.columns > tile.position[1] + j >= 0 and (i != 0 or j != 0): #Within Boundaries
                                self.reveal(self.table[tile.position[0] + i][tile.position[1] +j])  # Run recursive on surrounding Tiles
        
class Tile:
    def __init__(self, root):
        self.root = root
        self.colours = {
            '0' : 'white',
            '1' : 'blue',
            '2' : 'red',
            '3' : 'green',
            '4' : 'orange',
            '5' : 'pink',
            'x' : 'black'
            }
        self.hidden = True
        self.value = 0
        self.position = None
        self.button = None
        self.flagged = False


class Mine(Tile):
    def __init__(self, root):
        super().__init__(root)
        self.value = 'x'


class App:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.game = MineSweeper(root, 30, 30, 95, self.on_update_mines, self.onFinish)  
        self.timer_label = tk.Label(self.frame, text=self.game.timer)
        self.timer_label.grid(row=1, column=1)
        self.mines_label = tk.Label(self.frame, text=self.game.num_mines)
        self.mines_label.grid(row=1, column=3)
        self.start_timer_button = tk.Button(self.frame, text='Start Timer', command=self.update_timer).grid(row=1, column=2)
        

    def update_timer(self):
        if self.game.finished:
            return
        self.game.timer += 1
        self.timer_label.config(text=self.game.timer)
        self.root.after(1000, self.update_timer)
        
    def onFinish(self, outcome):
        self.finish_label = tk.Label(self.frame, text=f'You {outcome}')
        self.finish_label.grid(row=3, column=2)
        self.replay_button = tk.Button(self.frame, text='Play Again', command=self.restart_game)
        self.replay_button.grid(row=4, column=2)
    
    def on_update_mines(self, amount):
        self.mines_label.config(text=int(self.mines_label['text'])+amount)
        
    def restart_game(self):
        for widget in self.game.frame.winfo_children():
            widget.destroy()
        self.game.table.clear()
        self.game.mine_array.clear()
        self.game.all_tiles.clear()
        self.game.timer = 0
        self.game.finished = False
        self.replay_button.destroy()
        self.finish_label.destroy()
        self.game.create_table()
        self.mines_label.config(text=self.game.num_mines)
        self.timer_label.config(text=self.game.timer)
        



root = tk.Tk()
root.geometry('1000x1000')
app = App(root)
root.mainloop()

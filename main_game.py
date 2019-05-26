from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import numpy as np
import time
import threading

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

w_height = 720      # game window height
w_width  = 1155     # max window width
win_height = 918    # max window height
egg_h    = 49       # egg height
egg_w    = 38       # egg width
egg_x    = 103.5    # egg initial x location
egg_y    = 145      # egg initial y location

basket_h = 150      # basket height
basket_w = 170      # basket width
basket_rw = basket_w / 2

# to determine collision
tot_lenx = egg_w + basket_w
tot_leny = egg_h + basket_h

egg_locs   = np.linspace(103.5, 1013.5, 8)  # array of initial egg 8 locations
max_score  = 50     # game's max score, determine game over
game_over  = False 
game_time  = 30     # game's max time in seconds, determine game over
start_time = 0
score      = 0

# initialize canvas
canvas = Canvas(root, height=win_height, width=w_width)
canvas.grid(column=0, row=0, sticky=(N, W, E, S))

def init_env(h, w):
    ''' 
    Initialize game environments
    loading all necessary images
    creating canvas objects

    Parameters:
    h : int
        game window height
    w : int
        game window width

    Returns:
        Image References. Needed so images will properly apper on canvas.
        Item IDs to dynamically reference them later in the game.

    itm_list : list
        Array of all image references. 

    egg1 : canvas item
        Egg1 ID. 

    egg2 : canvas item
        Egg2 ID. 

    basket : canvas item
        Basket ID. 

    score_text : canvas item
        Score Lable ID to display score on screen

    start_id : canvas item
        Start Button ID
    '''
    backg = ImageTk.PhotoImage(Image.open('images/background1.jpg').resize((1155, 918)))
    canvas.create_image(0,0, anchor=NW, image=backg)

    wood_plank  = ImageTk.PhotoImage(Image.open('images/wooden plank1.jpg').resize((1079, 74)))
    canvas.create_image(38, 150, anchor=NW, image=wood_plank)

    egg_img1 = ImageTk.PhotoImage(Image.open('images/egg1.jpg').resize((egg_w, egg_h)))
    egg1     = canvas.create_image(egg_x,egg_y, anchor=NW, image=egg_img1)
    egg2     = canvas.create_image(egg_x,egg_y, anchor=NW, image=egg_img1)

    wood_plank2 = ImageTk.PhotoImage(Image.open('images/wooden plank1.jpg').resize((w_width, 74)))
    canvas.create_image(0, 720, anchor=NW, image=wood_plank2)

    hens = init_hens()

    x = (w / 2) - (basket_rw)
    y = h - basket_h + 20
    basket_img = ImageTk.PhotoImage(Image.open('images/egg basket2.jpg'))
    basket     = canvas.create_image(x, y, anchor=NW, image=basket_img)

    desc_y = w_height + 100
    desc_x = egg_locs[2]
    score_desc  = canvas.create_text(desc_x, desc_y, anchor= NW, fill="white" ,font="Times 50 bold", text="Your score is")
    count_x = egg_locs[5]
    score_text  = canvas.create_text(count_x, desc_y, anchor= NW, fill="white" ,font="Times 50 bold", text="0")
    timer_x = egg_locs[7]
    timer_text  = canvas.create_text(timer_x, desc_y, anchor= NW, fill="white" ,font="Times 50 bold", text="00:00")

    start_img = ImageTk.PhotoImage(Image.open('images/start.jpg'))
    start_id  = canvas.create_image(w_width/2, win_height/2, anchor=CENTER, image=start_img)

    itm_list = [backg, wood_plank, wood_plank2, hens, basket_img, score_desc, start_img, egg_img1]
    return itm_list, egg1, egg2, basket, score_text, timer_text, start_id

def init_hens():
    ''' 
    Initialize hen images and put on canvas

    Returns:
    hens_img : list
        list of hen images
    '''
    hens_img = [
        ImageTk.PhotoImage(Image.open('images/hen1.jpg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen2.jpg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen3.jpeg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen4.jpg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen5.jpg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen1.jpg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen3.jpeg').resize((125, 144))),
        ImageTk.PhotoImage(Image.open('images/hen5.jpg').resize((125, 144)))
    ]

    x = np.linspace(60, 970, 8)
    y = 50
    for i in range(len(hens_img)):
        # display hen objects on canvas
        canvas.create_image(x[i],y, anchor=NW, image=hens_img[i])

    return hens_img

def move_basket(event):
    ''' 
    Move basket left or right
    Function bound to keyboard left and right keys
    Parameters:
    event : keyboard event
    '''
    global basket, game_over
    
    if game_over: return

    locx, locy = np.array(canvas.coords(basket))
    step = 20

    if event.keysym == 'Left':
        new_loc = locx - step
        if new_loc >= 0:
            locx = new_loc
        canvas.coords(basket, locx, locy)
    elif event.keysym == 'Right':
        new_loc = locx + step
        if new_loc <= w_width - basket_w:
            locx = new_loc
        canvas.coords(basket, locx, locy)

def check_caught(egg):
    ''' 
    Check if basket caught the egg
    Parameters:
    egg id: canvas item id (egg created on canvas)

    Returns:
    out : bool
        True if basket collided with egg
    '''
    global basket

    bx, by = canvas.coords(basket)
    ex, ey = canvas.coords(egg)

    minx = min(ex, bx)
    maxx = max(ex + egg_w, bx + basket_w)
    distx = abs(minx - maxx)

    miny = min(ey, by)
    maxy = max(ey + egg_h, by + basket_h)
    disty = abs(miny - maxy)

    # print(f'egg={egg} distx={distx} totx={tot_lenx} disty={disty} toty={tot_leny} egg_xy={ex}:{ey} basket_xy= {bx}:{by}')
    if distx < tot_lenx and disty < tot_leny:
        # print('Collision detected!')
        return True

    return False

def move_egg(egg_var):
    ''' 
    Function to control the egg in the game.
    Randomly select location from 0 to 3 or 4 to 7 locations based on Egg ID.
    Randomly set when egg matures and ready to fall.
    Checks if basket caught the egg.
    Sets the score and determine if game is over.

    Parameters:
    egg id: canvas item id (egg created on canvas)

    Returns:
    egg_var : egg object structure
        contains all information about the egg to such as id, location, status and timer
    '''
    global score, score_text, start_id, egg_locs, max_score, egg1, game_over

    speed = 10
    break_loc = w_height - egg_h                                            # value when egg reaches the floor
    start_chk = w_height - (egg_h + basket_h + 20)                          # Set value when to start cheking for collision
    nums      = ()

    # set location range for each egg id. egg1 = 0 - 3, egg2 4 - 7
    if egg_var['egg_id'] == egg1:
        nums = (0, 4)
    else:
        nums = (4, 8)

    if egg_var['egg_fall']:                                                 # if eggs ready to fall, move down
        egg_var['y'] += speed                                               # increment y to move egg down
        canvas.coords(egg_var['egg_id'], egg_var['x'], egg_var['y'])        # set egg's new coordinates

        if egg_var['y'] > start_chk and check_caught(egg_var['egg_id']):    # basket caught the egg
            score += 10
            canvas.itemconfigure(score_text, text=str(score))               # show new score
            egg_var['egg_fall'] = False                                     # prevent egg from falling until time ready
            egg_var['y']        = egg_y                                     # set egg to initial y location
            canvas.coords(egg_var['egg_id'], egg_var['x'], egg_var['y'])    # move egg to new location
            egg_var['timer']    = time.time()                               # start timer
            egg_var['ready']    = np.random.randint(4, 8)                   # set random time when next egg is ready to fall

            if score == max_score:
                game_over = True
                return egg_var

        if egg_var['y'] > break_loc:
            game_over = True
            return egg_var

    else:
        if time.time() - egg_var['timer'] >= egg_var['ready']:              # new egg ready to fall
            egg_var['egg_fall'] = True
            choice = np.random.randint(*nums)                               # select random initial location
            egg_var['x'] = egg_locs[choice]
            egg_var['y'] = egg_y
    
    return egg_var

def start_game():
    ''' 
    Run function for the game thread. Initializing and creating egg object structures.
    Randomly select location from 0 to 7 locations where the first egg falls.
    Loop through until the game ends.
    '''
    global score, egg1, egg2, egg_locs, game_over

    game_over = False
    egg1_var = {
        'egg_id':   egg1,
        'egg_fall': False,
        'timer':    None,
        'ready':    np.random.randint(4, 8),
        'x':        0,
        'y':        egg_y
    }

    egg2_var = {
        'egg_id':   egg2,
        'egg_fall': False,
        'timer':    None,
        'ready':    np.random.randint(4, 8),
        'x':        0,
        'y':        egg_y
    }

    choice = np.random.randint(0, 8)
    # choice = 1
    if choice < 4:
        egg1_var['egg_fall'] = True
        egg2_var['timer'] = time.time()  
        egg1_var['x']     = egg_locs[choice]
    else:
        egg2_var['egg_fall'] = True
        egg1_var['timer'] = time.time()  
        egg2_var['x']     = egg_locs[choice]

    while True:
        egg1_var = move_egg(egg1_var)
        if game_over: break

        egg2_var = move_egg(egg2_var)
        if game_over: break
        
        time.sleep(0.25)

    score = 0
    canvas.itemconfigure(start_id, state=NORMAL)

def start_timer():
    ''' 
    Timer thread to update timer on game screen.
    If game elapsed time >= to the game_time, Game over.
    '''
    global start_time, game_time, game_over, timer_text

    prev_txt = '00:00'
    while True:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        new_txt = '%02d:%02d'%(minutes, seconds)
        if prev_txt != new_txt:
            canvas.itemconfigure(timer_text, text=new_txt)
            prev_txt = new_txt

            if elapsed_time >= game_time:
                game_over = True
                break
        
        if game_over: return

def load_game(*args):
    ''' 
    Main function loaded when user clicks the start button.
    Initialize and set status of canvas objects.
    Create and start game thread to run the game.
    '''
    global start_id, score_text, timer_text, start_time

    # initialize canvas item objects
    canvas.coords(egg1, egg_x, egg_y)   
    canvas.coords(egg2, egg_x, egg_y)   
    canvas.itemconfigure(start_id, state=HIDDEN)
    canvas.itemconfigure(score_text, text='0')
    canvas.itemconfigure(timer_text, text='00:00')

    # bind keyboard keys to function
    root.bind('<Key>', move_basket)

    # initialize and start game thread
    game_thread = threading.Thread(target=start_game)
    game_thread.start()

    # initialize and start timer
    start_time   = time.time()
    timer_thread = threading.Thread(target=start_timer)
    timer_thread.start()
    
env_img, egg1, egg2, basket, score_text, timer_text, start_id = init_env(w_height, w_width)
canvas.tag_bind(start_id, "<Button-1>", load_game)  # bind mouse click to function


root.mainloop()
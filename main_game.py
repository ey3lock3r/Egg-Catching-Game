from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import numpy as np
import time
import threading

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

w_height = 720
w_width  = 1155
win_height = 918
egg_h    = 49
egg_w    = 38

basket_h = 150
basket_w = 170
basket_rw = basket_w / 2

# to determine collision
tot_lenx = egg_w + basket_w
tot_leny = egg_h + basket_h

egg_locs = np.linspace(103.5, 1013.5, 8)
left_batch = True
score      = 0

canvas = Canvas(root, height=win_height, width=w_width)
# canvas.pack()
canvas.grid(column=0, row=0, sticky=(N, W, E, S))

def init_env(h, w):
    backg = ImageTk.PhotoImage(Image.open('images/background1.jpg').resize((1155, 918)))
    canvas.create_image(0,0, anchor=NW, image=backg)

    egg_img = ImageTk.PhotoImage(Image.open('images/egg1.jpg').resize((egg_w, egg_h)))
    egg     = canvas.create_image(103.5,200, anchor=NW, image=egg_img)
    # egg     = Label(canvas, image=egg_img)

    wood_plank = ImageTk.PhotoImage(Image.open('images/wooden plank1.jpg').resize((1079, 74)))
    canvas.create_image(38, 150, anchor=NW, image=wood_plank)

    # floor_plank = ImageTk.PhotoImage(Image.open('images/wooden plank3.jpg').resize((1079, 74)))
    canvas.create_image(38, 720, anchor=NW, image=wood_plank)

    hens = init_hens()

    basket_img = ImageTk.PhotoImage(Image.open('images/egg basket2.jpg'))

    x = (w / 2) - (basket_rw)
    y = h - basket_h + 20
    basket     = canvas.create_image(x, y, anchor=NW, image=basket_img)

    desc_y = w_height + 100
    desc_x = egg_locs[2]
    score_desc  = canvas.create_text(desc_x, desc_y, anchor= NW, fill="white" ,font="Times 50 bold", text="Your score is")
    count_x = egg_locs[5]
    score_text  = canvas.create_text(count_x, desc_y, anchor= NW, fill="white" ,font="Times 50 bold", text="0")

    return [backg, wood_plank, hens, egg_img, basket_img, score_desc], egg, basket, score_text

def init_hens():
    hens_img = {
        0: ImageTk.PhotoImage(Image.open('images/hen1.jpg').resize((125, 144))),
        1: ImageTk.PhotoImage(Image.open('images/hen2.jpg').resize((125, 144))),
        2: ImageTk.PhotoImage(Image.open('images/hen3.jpeg').resize((125, 144))),
        3: ImageTk.PhotoImage(Image.open('images/hen4.jpg').resize((125, 144))),
        4: ImageTk.PhotoImage(Image.open('images/hen5.jpg').resize((125, 144))),
        5: ImageTk.PhotoImage(Image.open('images/hen1.jpg').resize((125, 144))),
        6: ImageTk.PhotoImage(Image.open('images/hen3.jpeg').resize((125, 144))),
        7: ImageTk.PhotoImage(Image.open('images/hen5.jpg').resize((125, 144)))
    }
    x = np.linspace(60, 970, 8)
    y = 50
    for i in range(len(hens_img)):
        canvas.create_image(x[i],y, anchor=NW, image=hens_img[i])

    return hens_img

def check_caught():
    global egg, basket
    # print ('Checking for overlap')
    bx, by = canvas.coords(basket)
    ex, ey = canvas.coords(egg)

    minx = min(ex, bx)
    maxx = max(ex + egg_w, bx + basket_w)
    distx = abs(minx - maxx)

    miny = min(ey, by)
    maxy = max(ey + egg_h, by + basket_h)
    disty = abs(miny - maxy)

    print(f'totx={tot_lenx} toty={tot_leny}')
    if distx < tot_lenx and disty < tot_leny:
        print(f'distx={distx} disty={disty} egg_xy={ex} {ey} basket_xy= {bx} {by}')
        return True

    return False
    

def move_egg(*args):
    global egg, left_batch, score, score_text
    caught = False
    choice = 0

    if left_batch: 
        choice = np.random.randint(0, 4)
        left_batch = False
    else: 
        choice = np.random.randint(4, 8)
        left_batch = True

    loc = np.array([egg_locs[choice], 200])
    
    canvas.coords(egg, *loc)
    # delta = 0.5 * np.random.random_sample() + 0.5 # create random floats from 0.5 - 1 to determine speed
    speed = np.array([0, 10])

    break_loc = w_height - egg_h
    start_chk = w_height - (egg_h + basket_h + 20)
    while loc[1] < break_loc:
        # print (f'loc={loc}')
        time.sleep(0.25)
        loc += speed
        canvas.coords(egg, *loc)
        if loc[1] > start_chk and check_caught():
            caught = True
            score += 10
            canvas.itemconfigure(score_text, text=str(score))
            break
    
    if score == 100:
        print('You won!')
        score = 0
        return

    if caught:
        move_egg()

def move_basket(event):
    global basket
    locx, locy = np.array(canvas.coords(basket))

    if event.keysym == 'Left':
        step = -20
        new_loc = locx + step
        if new_loc >= 0:
            locx = new_loc
        canvas.coords(basket, locx, locy)
    elif event.keysym == 'Right':
        step = 20
        new_loc = locx + step
        if new_loc <= w_width - basket_w:
            locx = new_loc
        canvas.coords(basket, locx, locy)

def start_game(*args):
    egg_thread = threading.Thread(target=move_egg, args=('egg',))
    egg_thread.start()

    root.bind('<Key>', move_basket)
    # basket_thread = threading.Thread(target=move_basket, args=('basket',))
    # basket_thread.start()

env_img, egg, basket, score_text = init_env(w_height, w_width)
button = ttk.Button(root, text="Start Game", command=start_game).grid()
root.bind('<Return>', start_game)

root.mainloop()
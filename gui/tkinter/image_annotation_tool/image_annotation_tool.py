from tkinter import *
from tkinter import colorchooser
from tkinterdnd2 import *
from PIL import ImageTk, ImageGrab
import os

"""
IMAGE ANNOTATION TOOL: annotate images
"""

DEFAULT_TEXT = "Offert pour tout achat"
BG_SETTINGS = '#555555'
SHIFT_KEYS = {"Shift_L", "Shift_R"}

is_shift_pressed = False

def Draw():
    canvas.itemconfig(textAddedWidget, 
                      text= text_to_add.get(),
                      angle=angleOfRotation.get(),
                      fill=text_color.get(), 
                      font=('calibri', 
                      fontsize.get(), 'bold'))

def DropImage(event):
    global img          # avoid img to be garbage collected

    droppedItem.set(event.data)
    currentFile.set(droppedItem.get())
    img = ImageTk.PhotoImage(file = currentFile.get()) # "./Images/source.png"    "C:\\temp\\F14-01.png"

    # resize canvas to image size
    canvas.config(width=img.width(), height=img.height())

    canvas_img = canvas.create_image(0,0, anchor=NW, image=img)
    # z-order: image must be below foreground elements
    canvas.tag_lower(canvas_img)

    Draw()


window = TkinterDnD.Tk()
window.title('ADD TEXT TO AN IMAGE')
window.geometry('700x700')
window.config(bg='grey')

droppedItem = StringVar()
currentFile = StringVar()
text_x = IntVar()
text_x.set(150)
text_y = IntVar()
text_y.set(100)

canvas = Canvas(window, width=600, height=400)
canvas.configure(bg='#333333')
textAddedWidget = canvas.create_text(200, 150, text="DRAG IMAGE HERE", anchor="nw", fill='red', font='calibri 20 bold')
canvas.pack(fill=None, expand=False, pady=10)

canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', DropImage)


# USER SETTINGS AREA

settingsArea = Frame(window, bg=BG_SETTINGS)
settingsArea.pack() 

# USER TEXT
text_to_add = StringVar()

def update_text(e):
    Draw()
   
lText = Label(settingsArea, text="TEXT", bg=BG_SETTINGS, fg='White')
lText.grid(row=0,column=0 , padx=10)
textbox = Entry(settingsArea, width=30, fg='blue', font=("calibri", 18), textvariable=text_to_add)
textbox.insert(0, DEFAULT_TEXT)
textbox.grid(row=0,column=1 , padx=10, pady=10)
textbox.bind("<FocusIn>", update_text)





# USER IMAGE PARAMS

imagePropertiesArea = Frame(settingsArea, bg=BG_SETTINGS)
imagePropertiesArea.grid(row=1,columnspan=3, padx=30, pady=10)

def choose_color():
    color_code = colorchooser.askcolor(title ="Choose color")
    text_color.set(color_code[1])

# USER TEXT COLOR
text_color = StringVar()
text_color.set('red')
text_color.trace("w", lambda name, index,mode, var=text_color: update_text(text_color))

color_button = Button(imagePropertiesArea, text = "Color", command = choose_color)
color_button.pack(side = LEFT, padx=20, pady=5)

# USER TEXT ROTATION
lRotation = Label(imagePropertiesArea, text="Rotation", bg=BG_SETTINGS, fg='White')
lRotation.pack(side = LEFT, padx=5)
angleOfRotation = DoubleVar()
angleOfRotation.set(-21)
rotation_slider = Scale(imagePropertiesArea, variable = angleOfRotation, from_ = -90, to = 90, orient = HORIZONTAL) 
rotation_slider.pack(side = LEFT, padx=20)

# USER FONT SIZE
lFontsize = Label(imagePropertiesArea, text="Text Size", bg=BG_SETTINGS, fg='White')
lFontsize.pack(side = LEFT, padx=5)
text_fontsize = IntVar()
text_fontsize.set(20)
fontsize = Scale(imagePropertiesArea, variable = text_fontsize,  from_ = 10, to = 40, orient = HORIZONTAL) 
fontsize.pack(side = LEFT, padx=10)

lArrowKeys = Label(settingsArea, text="Use keys [↑][↓][→][←] to move the text. Press shift for slow move", bg=BG_SETTINGS, fg='White')
lArrowKeys.grid(row=2, columnspan=3, pady=10)

# USER BUTTONS

def save_image():
    x = Canvas.winfo_rootx(canvas)
    y = Canvas.winfo_rooty(canvas)
    w = Canvas.winfo_width(canvas) 
    h = Canvas.winfo_height(canvas)
    
    path, filename = os.path.split(currentFile.get())
    targetFile = os.path.join(path, ("new_" if overwrite_file.get() == 0 else "") + filename )
    ImageGrab.grab((x, y, x+w, y+h)).save(targetFile)
        
save_button = Button(settingsArea, text="SAVE IMAGE", bg="black", fg="white", command=save_image)
save_button.grid(row=3, column=1, pady=10)
overwrite_file = IntVar()
overwrite_file.set(0)
overwrite_file_cb = Checkbutton(settingsArea, text='Overwrite file', bg=BG_SETTINGS,
    variable = overwrite_file, onvalue = 1, offvalue = 0, state="normal")
overwrite_file_cb.grid(row=3, column=2, pady=10)

# LISTENERS

text_to_add.trace("w", lambda name, index,mode, var=text_to_add: update_text(text_to_add))
angleOfRotation.trace("w", lambda name, index,mode, var=angleOfRotation: update_text(angleOfRotation))
text_fontsize.trace("w", lambda name, index,mode, var=text_fontsize: update_text(text_fontsize))


def MoveSpeed(x,y):
   global textAddedWidget
 
   dx = x + (0 if is_shift_pressed else x)
   dy = y + (0 if is_shift_pressed else y)
   canvas.move(textAddedWidget, dx, dy )
 
def left(e):
   MoveSpeed(-10,0)
      
def right(e):
    MoveSpeed(10,0)

def up(e):
    MoveSpeed(0,-10)
   
def down(e):
    MoveSpeed(0,10)

def shift_press(event):
    global is_shift_pressed
    if event.keysym in SHIFT_KEYS:
        is_shift_pressed = True

def shift_release(event):
    global is_shift_pressed
    if event.keysym in SHIFT_KEYS:
        is_shift_pressed = False

# Bind the move function
window.bind("<Left>", left)
window.bind("<Right>", right)
window.bind("<Up>", up)
window.bind("<Down>", down)
window.bind("<KeyPress>", shift_press)
window.bind("<KeyRelease>", shift_release)

window.mainloop()

# https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function
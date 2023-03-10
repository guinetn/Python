from tkinter import colorchooser
from tkinter import StringVar, IntVar, DoubleVar, Frame, Label, Canvas, Entry, Button, Checkbutton, Scale, PhotoImage, NW, LEFT, HORIZONTAL
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import ImageTk, ImageGrab # Pillow ImageTk: to have more image formats 
import sys, os, datetime

"""
IMAGE ANNOTATION TOOL

To annotate an image with a text that can be modified, resized, rotated, colorized
My wife use it to annotate pictures of her clothes for Vinted…  

Usage:

"""

__version__ = "0.0.1"
__author__ = "Nicols Guinet <nguinet.pro AT gmail.com>"

class App:

    DEFAULT_TEXT = "Offert pour tout achat"
    DEFAULT_BG_SETTINGS = '#555555'
    SHIFT_KEYS = {"Shift_L", "Shift_R"}
    IS_SHIFT_PRESSED = False

    def __init__(self, master):
        
        # Create labels, entries,buttons
        self.master = master
        self.master.title('ADD TEXT TO AN IMAGE')
        self.master.geometry('700x700')
        self.master.config(bg='grey')

        self.currentImgFile = None

        self.annotation_x = IntVar()
        self.annotation_x.set(150)
        self.annotation_y = IntVar()
        self.annotation_y.set(100)

        self.canvas = Canvas(master, width=600, height=400, bd=0)
        self.canvas.configure(bg='#333333')
        self.textAddedWidget = self.canvas.create_text(200, 150, text="DRAG IMAGE HERE", anchor="nw", fill='red', font='calibri 20 bold')
        self.canvas.pack(fill=None, expand=False, pady=10)

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.DropImage)


        # USER SETTINGS AREA

        self.settingsArea = Frame(master, bg=self.DEFAULT_BG_SETTINGS)
        self.settingsArea.pack() 

        # USER TEXT
        self.annotation = StringVar()

        self.lText = Label(self.settingsArea, text="TEXT", bg=self.DEFAULT_BG_SETTINGS, fg='White')
        self.lText.grid(row=0,column=0 , padx=10)
        self.AnnotationEntry = Entry(self.settingsArea, width=30, fg='blue', font=("calibri", 18), textvariable=self.annotation)
        self.AnnotationEntry.insert(0, self.DEFAULT_TEXT)
        self.AnnotationEntry.grid(row=0,column=1 , padx=10, pady=10)
        self.AnnotationEntry.bind("<FocusIn>", self.UpdateText)

        # USER IMAGE PARAMS

        self.imagePropertiesArea = Frame(self.settingsArea, bg=self.DEFAULT_BG_SETTINGS)
        self.imagePropertiesArea.grid(row=1,columnspan=3, padx=30, pady=10)

        # USER TEXT COLOR
        self.annotation_color = StringVar()
        self.annotation_color.set('red')
        self.annotation_color.trace("w", lambda name, index,mode, var=self.annotation_color: self.UpdateText())

        self.color_button = Button(self.imagePropertiesArea, text = "Color", command = self.ChooseColor)
        self.color_button.pack(side = LEFT, padx=20, pady=5)

        # USER TEXT ROTATION
        self.lRotation = Label(self.imagePropertiesArea, text="Rotation", bg=self.DEFAULT_BG_SETTINGS, fg='White')
        self.lRotation.pack(side = LEFT, padx=5)
        self.annotationAngleOfRotation = DoubleVar()
        self.annotationAngleOfRotation.set(-21)
        self.rotation_slider = Scale(self.imagePropertiesArea, variable = self.annotationAngleOfRotation, from_ = -90, to = 90, orient = HORIZONTAL) 
        self.rotation_slider.pack(side = LEFT, padx=20)

        # USER FONT SIZE
        self.lFontsize = Label(self.imagePropertiesArea, text="Text Size", bg=self.DEFAULT_BG_SETTINGS, fg='White')
        self.lFontsize.pack(side = LEFT, padx=5)
        self.annotationFontSize = IntVar()
        self.annotationFontSize.set(20)
        self.fontsize = Scale(self.imagePropertiesArea, variable = self.annotationFontSize,  from_ = 10, to = 40, orient = HORIZONTAL) 
        self.fontsize.pack(side = LEFT, padx=10)

        self.lArrowKeys = Label(self.settingsArea, text="Use keys [↑][↓][→][←] to move the text. Press shift for slow move", bg=self.DEFAULT_BG_SETTINGS, fg='White')
        self.lArrowKeys.grid(row=2, columnspan=3, pady=10)

        # USER BUTTONS

        self.save_img_button = Button(self.settingsArea, text="SAVE IMAGE", bg="black", fg="white", command=self.save_image)
        self.save_img_button.grid(row=3, column=1, pady=10)
        self.overwrite_file = IntVar()
        self.overwrite_file.set(0)
        self.overwrite_file_cb = Checkbutton(self.settingsArea, text='Overwrite file', bg=self.DEFAULT_BG_SETTINGS,
            variable = self.overwrite_file, onvalue = 1, offvalue = 0, state="normal")
        self.overwrite_file_cb.grid(row=3, column=2, pady=10)

        # LISTENERS

        self.annotation.trace("w", lambda name, index,mode, var=self.annotation: self.UpdateText())
        self.annotationAngleOfRotation.trace("w", lambda name, index,mode, var=self.annotationAngleOfRotation: self.UpdateText())
        self.annotationFontSize.trace("w", lambda name, index,mode, var=self.annotationFontSize: self.UpdateText())

        # Bind the move function
        self.master.bind("<Left>", self.left)
        self.master.bind("<Right>", self.right)
        self.master.bind("<Up>", self.up)
        self.master.bind("<Down>", self.down)
        self.master.bind("<KeyPress>", self.shift_press)
        self.master.bind("<KeyRelease>", self.shift_release)

        # First argument is a path to the image to be opened
        if  len(sys.argv) > 1:
            fileArg = sys.argv[1]
            if os.path.isfile(fileArg):
                self.ShowImage(fileArg)

    def UpdateText(self):
        self.canvas.itemconfig(self.textAddedWidget, 
            text= self.annotation.get(),
            angle=self.annotationAngleOfRotation.get(),
            fill=self.annotation_color.get(), 
            font=('calibri', self.fontsize.get(), 'bold'))

    def DropImage(self, event):
            self.ShowImage(event.data) # droppedItem

    def ShowImage(self, pathToImage):

        self.currentImgFile = pathToImage
        # ImageTk.PhotoImage can read more formats than the standard PhotoImage
        self.img = ImageTk.PhotoImage(file = self.currentImgFile) # valid: "./Images/source.png" or "C:\\temp\\F14-01.png"

        # resize canvas to image size
        self.canvas.config(width=self.img.width(), height=self.img.height())

        canvas_img = self.canvas.create_image(0,0, anchor=NW, image=self.img)
        # z-order: image must be below foreground elements
        self.canvas.tag_lower(canvas_img)

        self.UpdateText()

    def save_image(self):
        x = Canvas.winfo_rootx(self.canvas)
        y = Canvas.winfo_rooty(self.canvas)
        w = Canvas.winfo_width(self.canvas) 
        h = Canvas.winfo_height(self.canvas)
        
        if self.currentImgFile == None:
            path = os.path.dirname(os.path.realpath(__file__))
            filename = datetime.datetime.now().strftime('image_%Y%m%d-%H%M%S')
        else:
            path, filename = os.path.split(self.currentImgFile)
        targetFile = os.path.join(path, ("new_" if self.overwrite_file.get() == 0 else "") + filename )
        ImageGrab.grab((x, y, x+w, y+h)).save(targetFile)
        
    def ChooseColor(self):
        color_code = colorchooser.askcolor(title ="Choose a color for the text")
        self.annotation_color.set(color_code[1])

    def MoveText(self, x,y):
        dx = x + (0 if self.IS_SHIFT_PRESSED else x)
        dy = y + (0 if self.IS_SHIFT_PRESSED else y)
        self.canvas.move(self.textAddedWidget, dx, dy )
    
    def left(self, e):
        self.MoveText(-10,0)
        
    def right(self, e):
        self.MoveText(10,0)

    def up(self, e):
        self.MoveText(0,-10)
    
    def down(self, e):
        self.MoveText(0,10)

    def shift_press(self, event):
        if event.keysym in self.SHIFT_KEYS:
            self.IS_SHIFT_PRESSED = True

    def shift_release(self, event):
        if event.keysym in self.SHIFT_KEYS:
            self.IS_SHIFT_PRESSED = False

def main():
    guiRoot = TkinterDnD.Tk()
    app = App(guiRoot)
    guiRoot.mainloop()

if __name__ == '__main__':
    main()    
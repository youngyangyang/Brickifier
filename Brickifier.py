#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ImageConverter
from PIL import Image, ImageTk
from tkinter import *
import tkinter.filedialog as tkfd
import tkinter.messagebox as messagebox


class Brickifier():
    def __init__(self, master = None):
        self.blankImage = PhotoImage(file = 'Blank.png')
        self.master = master
        self.CreateWidgets()
        self.imageConverter = None

    def CreateWidgets(self):
        fm1 = Frame(self.master)
        fm1.pack(side = TOP, fill = X, expand = YES)
        self.readImageButton = Button(fm1, text = 'Read Image', command = self.OpenFileDialog)
        self.readImageButton.pack(side = LEFT, fill = X, padx = 10, expand = YES)
        self.xEntry = Entry(fm1)
        self.xEntry.pack(side = LEFT, fill = X, expand = YES)
        Label(fm1, text = 'X').pack(side = LEFT,  fill = X, expand = YES)
        self.yEntry = Entry(fm1)
        self.yEntry.pack(side = LEFT, fill = X, expand = YES)
        self.brickifyButton = Button(fm1, text = 'Brickify!', command = self.BrickifyImage)
        self.brickifyButton.pack(side = LEFT, fill = X, padx = 10, expand = YES)
        fm2 = Frame(self.master)
        fm2.pack(side = BOTTOM, fill = X, expand = YES)
        self.oriImCv = Canvas(fm2, background = 'white')
        self.image_on_oriImCv = self.oriImCv.create_image(0, 0, anchor = NW, image = self.blankImage)
        self.oriImCv.pack(side = LEFT, fill = X, expand = YES)
        self.oriImCv.update()
        print(self.oriImCv.winfo_width(), self.oriImCv.winfo_height())
        self.targetImCv = Canvas(fm2, background = 'black')
        self.image_on_targetImCv = self.targetImCv.create_image(0, 0, anchor = NW, image = self.blankImage)
        self.targetImCv.pack(side = LEFT, fill= X, expand = YES)
        self.targetImCv.update()
        print(self.targetImCv.winfo_width(), self.targetImCv.winfo_height())
    
    def OpenFileDialog(self):
        self.opennm = tkfd.askopenfilename()
        self.LoadImage()
    
    def BrickifyImage(self):
        try:
            self.targetX = int(self.xEntry.get())
            self.targetY = int(self.yEntry.get())
        except ValueError:
            messagebox.showinfo('WARNING','X and Y should be integers, please check again')
            return

    def LoadImage(self):
        if self.opennm is not None:
            self.imageConverter = ImageConverter.ImageConverter(self.opennm)
            image = self.imageConverter.oriIm.copy() 
            image.thumbnail((self.oriImCv.winfo_width(), self.oriImCv.winfo_height()))
            newPhotoImage = ImageTk.PhotoImage(image)
            self.oriImCv.itemconfig(self.image_on_oriImCv, image = newPhotoImage)

if __name__=='__main__':
    root=Tk()
    root.title("Brickifer")
    display = Brickifier(root)
    root.mainloop()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ImageConverter
from tkinter import *
import tkinter.filedialog as tkfd
import tkinter.messagebox as messagebox


class Brickifier():
    def __init__(self, master = None):
        self.master = master
        self.CreateWidgets()

    def CreateWidgets(self):
        fm1 = Frame(self.master)
        fm1.pack(side=TOP, fill=X, expand=YES)
        self.readImageButton = Button(fm1, text = 'Read Image', command = self.OpenFileDialog)
        self.readImageButton.pack(side = LEFT, fill = X, padx = 10, expand = YES)
        self.xEntry = Entry(fm1)
        self.xEntry.pack(side = LEFT, fill = X, expand = YES)
        Label(fm1, text = 'X').pack(side = LEFT,  fill = X, expand = YES)
        self.yEntry = Entry(fm1)
        self.yEntry.pack(side = LEFT, fill = X, expand = YES)
        self.brickifyButton = Button(fm1, text = 'Brickify!', command = self.BrickifyImage)
        self.brickifyButton.pack(side = LEFT, fill = X, padx = 10, expand = YES)
    
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
        self.imageConverter = ImageConverter(self.opennm)

if __name__=='__main__':
    root=Tk()
    root.title("Brickifer")
    display = Brickifier(root)
    root.mainloop()
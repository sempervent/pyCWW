#!/usr/bin/env python
# encoding: utf-8
###############################################################################
#                             pyCWW Frontend GUI                              #
###############################################################################

from Tkinter import Frame, Tk, BOTH, Text, Menu, END, RIGHT, RAISED
import tkFileDialog
from ttk import Frame, Button, Style
from PIL import Image, ImageTk
import os

###############################################################################
#                              Things to define:                              #
#  threshold = mean                                                           #
#  dilation_iterations = 15                                                   #
#  gauss_fit = 3                                                              #
#  binary_opening = [(3,3),1]                                                 #
#  area_max = 3000 pixels                                                     #
#  perimeter_max = 350 pixels                                                 #
#  pixel_conversion = 1                                                       #
###############################################################################
from cell_wall_erosion import *

class gui(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.parent.title("pyCWW GUI")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open File", command=self.onOpen)
        fileMenu.add_command(label="Open Directory", command=self.onOpenDir)
        menubar.add_cascade(label="File", menu=fileMenu)

        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=1)

        closeButton = Button(self, text="Exit", command=self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)

    def onOpen(self):
        ftypes = [('Image files', '*.tif, *.jpg, *.bmp, *.png')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        fl = dlg.show()

        if fl != '':
            print fl
            #text = self.readFile(fl)
            #self.txt.insert(END, text)
            run_this = "python cell_wall_erosion.py " + fl
            os.system(run_this)

    def onOpenDir(self):
        dirname = tkFileDialog.askdirectory(parent=root, initialdir="/",
                                            title="Please select a directory")
        directory = dirname.show()

        if directory != '':
            print directory
            run_this = "python frontend.py " + directory
            os.system(run_this)




def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = gui(root)
    root.mainloop()

if __name__ == '__main__':
    main()

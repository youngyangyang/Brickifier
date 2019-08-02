#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import math
import csv

class ImageConverter():
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)
        self.BrickColors = {}
        self.BrickColorsInUser = []

    def GetImage(self, path):
        im = Image.open(path)
        return im

    def ResizeImage(self, size):
        self.oriIm.thumbnail(size)   

    def ConvertImageToBricks(self):
        pix = self.oriIm.load()
        xsize, ysize = self.oriIm.size
        for i in range(xsize):
            for j in range(ysize):
                r, g, b = pix[i, j]
                minDist = -1
                closestKey = ""
                for key in self.BrickColors:
                    rr = int(self.BrickColors[key][0])
                    gg = int(self.BrickColors[key][1])
                    bb = int(self.BrickColors[key][2])
                    dist = math.pow(r - rr, 2) + math.pow(g - gg, 2) + math.pow(b - bb, 2)
                    if minDist < 0 :
                        minDist = dist
                        closestKey = key
                    elif minDist > dist:
                        minDist = dist
                        closestKey = key
                self.BrickColorsInUser.append(closestKey)
                pix[i, j] = (int(self.BrickColors[closestKey][0]), int(self.BrickColors[closestKey][1]), int(self.BrickColors[closestKey][2]))

    def NewImage(self, size):
        im = Image.new('RGB', size, (229, 106, 84))
        im.show()

    def GetBrickColors(self):
        with open('BrickColors.csv', 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                self.BrickColors[row[1]]= (row[2:])

if __name__=='__main__':
    imageConverter = ImageConverter('Jay.jpg')
    imageConverter.GetBrickColors()
    imageConverter.ResizeImage((32, 32))
    imageConverter.ConvertImageToBricks()
    imageConverter.oriIm.show()


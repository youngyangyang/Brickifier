#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import math
import csv

class ImageConverter():
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)
        self.targetIm = self.oriIm.copy()
        self.BrickColors = {}
        self.BrickColorsInUse = []
        self.ConnectedComponets = {}

    def GetImage(self, path):
        im = Image.open(path)
        return im

    def ResizeImage(self, size):
        self.targetIm.thumbnail(size)   

    def ConvertImageToBricks(self):
        pix = self.targetIm.load()
        xsize, ysize = self.targetIm.size
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
                self.BrickColorsInUse.append(closestKey)
                pix[i, j] = (int(self.BrickColors[closestKey][0]), int(self.BrickColors[closestKey][1]), int(self.BrickColors[closestKey][2]))
        
    def GetAllConnectedComponents(self):
        checkedPoints = set([])
        xsize, ysize = self.targetIm.size
        pix = pix = self.targetIm.load()
        for i in range(xsize):
            for j in range(ysize):
                if ((i,j) not in checkedPoints):
                    # Start searching point
                    checkedPoints.add((i,j))
                    self.BFS(i, j, self.targetIm.size, checkedPoints, pix)

    def BFS(self, startX, startY, size, checkedPoints, pix):
        pointsInCurrentComponent = [(startX, startY)]
        startIndex = 0
        endIndex = len(pointsInCurrentComponent)
        while startIndex < endIndex:
            currentPoint = pointsInCurrentComponent[startIndex]
            for i in range(-1, 2):
                for j in range(-1, 2):
                    newX = currentPoint[0] + i
                    newY = currentPoint[1] + j
                    if (newX >= 0 and newY >= 0 and newX < size[0] and newY < size[1]):
                        if ((newX, newY) not in checkedPoints and pix[currentPoint[0], currentPoint[1]] == pix[newX, newY]):
                            checkedPoints.add((newX, newY))
                            pointsInCurrentComponent.append((newX, newY))
            startIndex += 1
            endIndex = len(pointsInCurrentComponent)
            self.ConnectedComponets[(startX, startY)] = pointsInCurrentComponent

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
    imageConverter.GetAllConnectedComponents()
    imageConverter.targetIm.show()


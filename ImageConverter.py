#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import math
import csv
from copy import deepcopy
import math

class ImageConverter():
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)
        self.targetIm = self.oriIm.copy()
        self.BrickColors = {}
        self.BrickColorsInUse = []
        self.BrickSizes = []
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
                pix[i, j] = tuple(x for x in self.BrickColors[closestKey])
        
    def GetAllConnectedComponents(self):
        checkedPoints = set([])
        xsize, ysize = self.targetIm.size
        pix = self.targetIm.load()
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
                self.BrickColors[row[1]]= (int(x) for x in row[2:])

    def GetBrickSizes(self):
        with open('BrickSizes.csv', 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                self.BrickSizes.append((int(row[0]), int(row[1])))
    
    def GetBrickListForConnectedComponent(self, pointsInCurrentComponentSet):
        stateHistory = { () : () }
        totalSize = len(pointsInCurrentComponentSet)
        for step in range(1, totalSize + 1):
            # type: a list of sets
            lastStepStates = [set(x) for x in stateHistory.keys() if len(x) == step - 1]
            for lastStepState in lastStepStates:
                # type: a set of points
                availableStartPoint = pointsInCurrentComponentSet - lastStepState
                for point in availableStartPoint:
                    for brick in self.BrickSizes:
                        # type: a set of points
                        currentState = deepcopy(lastStepState)
                        for i in range(0, brick[0]):
                            for j in range(0, brick[1]):
                                currentState.add((point[0] + i, point[1]+j))
                        if currentState == pointsInCurrentComponentSet:
                            return self.GetBrickListFromStateHistory(stateHistory, lastStepState, brick)
                        if currentState < pointsInCurrentComponentSet:
                            stateHistory[tuple(list(currentState))] = tuple(list(lastStepState)) 
        return None
    def GetBrickFromPoints(self, points):
        for brick in self.BrickSizes:
            if len(points) == brick[0] * brick[1]:
                minX = min(point[0] for point in points)
                minY = min(point[1] for point in points)
                brickMatch = True
                for i in range(0, brick[0]):
                    for j in range(0, brick[1]):
                        if (minX+i, minY) not in points:
                            brickMatch = False
                if brickMatch:
                    return brick
        return None  

    def GetBrickListFromStateHistory(self, stateHistory, lastStepStateSet, lastBrick):
        brickDict = { lastBrick : 1 }
        lastStepState = tuple(list(lastStepStateSet))
        while stateHistory[lastStepState] != ():
            # a set of points
            points = lastStepStateSet - set(list(stateHistory[lastStepState]))
            brick = self.GetBrickFromPoints(points)
            if brick is None:
                raise AssertionError('cannot find brick')
            if brick in brickDict:
                brickDict[brick] += 1
            else:
                brickDict[brick] = 1
            lastStepState = stateHistory[lastStepState]
        return brickDict

if __name__=='__main__':
    imageConverter = ImageConverter('Jay.jpg')
    imageConverter.GetBrickColors()
    imageConverter.GetBrickSizes()
    pointsInSet = set([(0,0), (0,1), (0,2), (1,1),(1,2),(1,3)])
    imageConverter.GetBrickListForConnectedComponent(pointsInSet)
    #imageConverter.ResizeImage((32, 32))
    #imageConverter.ConvertImageToBricks()
    #imageConverter.GetAllConnectedComponents()
    #imageConverter.targetIm.show()


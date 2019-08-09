#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import math
import csv
from copy import deepcopy
from functools import reduce
import math

class ImageConverter():
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)
        self.BrickColors = {}
        self.BrickSizes = []
        self.ConnectedComponets = {}
        self.TotalBrickDict = {}

    def GetImage(self, path):
        im = Image.open(path)
        return im

    def ResizeImage(self, size):
        self.targetIm = self.oriIm.copy()
        self.targetIm.thumbnail(size)  
        self.pix = self.targetIm.load() 

    def ConvertImageToBricks(self):
        xsize, ysize = self.targetIm.size
        for i in range(xsize):
            for j in range(ysize):
                point = self.pix[i,j]
                minDist = -1
                closestKey = ""
                for key in self.BrickColors:
                    brickColor = self.BrickColors[key]
                    dist = reduce(lambda  x, y: x+y, [x * x for x in [point[k] - brickColor[k] for k in range(0, len(point))]])
                    if minDist < 0 or minDist > dist:
                        minDist = dist
                        closestKey = key
                    self.pix[i, j] = self.BrickColors[closestKey]
        
    def GetAllConnectedComponents(self):
        checkedPoints = set([])
        xsize, ysize = self.targetIm.size
        for i,j in [(i,j) for i in range(xsize) for j in range(ysize)]:
            if ((i,j) not in checkedPoints):
                # Start searching point
                checkedPoints.add((i,j))
                self.BFS(i, j, self.targetIm.size, checkedPoints)

    def BFS(self, startX, startY, size, checkedPoints):
        pointsInCurrentComponent = [(startX, startY)]
        startIndex = 0
        endIndex = len(pointsInCurrentComponent)
        while startIndex < endIndex:
            currentPoint = pointsInCurrentComponent[startIndex]
            for newX, newY in [(currentPoint[0] + i, currentPoint[0] + j) for i in range(-1, 2) for j in range(-1, 2)]:
                if (newX >= 0 and newY >= 0 and newX < size[0] and newY < size[1]):
                    if ((newX, newY) not in checkedPoints and self.pix[currentPoint[0], currentPoint[1]] == self.pix[newX, newY]):
                        checkedPoints.add((newX, newY))
                        pointsInCurrentComponent.append((newX, newY))
            startIndex += 1
            endIndex = len(pointsInCurrentComponent)
            self.ConnectedComponets[(startX, startY)] = set(pointsInCurrentComponent)

    def NewImage(self, size):
        im = Image.new('RGB', size, (229, 106, 84))
        im.show()

    def GetBrickColors(self):
        with open('BrickColors.csv', 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                self.BrickColors[row[1]]= tuple(int(x) for x in row[2:])

    def GetBrickSizes(self):
        with open('BrickSizes.csv', 'r') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                self.BrickSizes.append((int(row[0]), int(row[1])))
    
    def GetBricksFromBrickList(self, brickList, lastBrick):
        brickDict = { lastBrick : 1 }
        for brick in brickList:
            if brick in brickDict:
                brickDict[brick] += 1
            else:
                brickDict[brick] = 1
        return brickDict
    
    def GetBrickListGivenState(self, currentState, stateHistory):
        currentStep = currentState[0]
        currentPointsSet = set(currentState[1:])
        for state, brickList in stateHistory.items():
            step = state[0]
            if step == currentStep:
                pointsSet = set(state[1:])
                if pointsSet == currentPointsSet:
                    return brickList
        return []

    def GetBrickListForConnectedComponent(self, pointsInCurrentComponentSet):
        stateHistory = { (0,) : [] }
        totalSize = len(pointsInCurrentComponentSet)
        for step in range(1, totalSize + 1):
            # type: a list of sets
            lastStepStates = [set(x[1:]) for x in stateHistory.keys() if x[0] == step -1]
            for lastStepState in lastStepStates:
                # type: a set of points
                availableStartPoint = pointsInCurrentComponentSet - lastStepState
                lastStepStateList = list(lastStepState)
                lastStepStateList.insert(0, step - 1)
                lastStepStateTuple = tuple(lastStepStateList)
                for point in availableStartPoint:
                    for brick in self.BrickSizes:
                        # type: a set of points
                        currentState = deepcopy(lastStepState)
                        for i in range(0, brick[0]):
                            for j in range(0, brick[1]):
                                currentState.add((point[0] + i, point[1]+j))
                        if currentState == pointsInCurrentComponentSet:
                            return self.GetBricksFromBrickList(self.GetBrickListGivenState(lastStepStateTuple, stateHistory), brick)
                        if currentState < pointsInCurrentComponentSet:
                            if currentState not in [set(x[1:]) for x in stateHistory.keys() if x[0] == step]:
                                tempCurrentStateList = list(currentState)
                                tempCurrentStateList.insert(0, step)
                                lastStepStateBrickList = deepcopy(self.GetBrickListGivenState(lastStepStateTuple, stateHistory))
                                lastStepStateBrickList.append(brick)
                                # value is brick list
                                stateHistory[tuple(tempCurrentStateList)] = lastStepStateBrickList
        return None 

    def GetBrickListForImage(self):
        TotalBrickDict = {}
        for startPoint in self.ConnectedComponets:
            color = list(filter(lambda key: self.BrickColors[key] == self.pix[startPoint[0], startPoint[1]], self.BrickColors))[0]
            brickDictForCurrentConnectedComponent = self.GetBrickListForConnectedComponent(self.ConnectedComponets[startPoint])
            if brickDictForCurrentConnectedComponent is not None:
                for brick in brickDictForCurrentConnectedComponent:
                    if (brick, color) not in TotalBrickDict:
                        TotalBrickDict[(brick, color)] = 0
                    TotalBrickDict[(brick, color)] += brickDictForCurrentConnectedComponent[brick]
        return TotalBrickDict
if __name__=='__main__':
    imageConverter = ImageConverter('Jay.jpg')
    imageConverter.GetBrickColors()
    imageConverter.GetBrickSizes()
    #pointsInSet = set([(0,0), (0,1), (0,2), (1,1),(1,2),(1,3)])
    #imageConverter.GetBrickListForConnectedComponent(pointsInSet)
    imageConverter.ResizeImage((32, 32))
    imageConverter.ConvertImageToBricks()
    imageConverter.GetAllConnectedComponents()
    imageConverter.targetIm.show()
    brickDict = imageConverter.GetBrickListForImage()
    print(len(brickDict))

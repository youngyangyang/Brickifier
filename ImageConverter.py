#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import math
import csv
from copy import deepcopy
from functools import reduce
import math
import time, threading

class ImageConverter():
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)
        self.BrickColors = {}
        self.BrickSizes = []
        self.ConnectedComponents = {}
        self.TotalBrickDict = {}
        self.Matrix = []
        self.lock = threading.Lock()

    def GetImage(self, path):
        im = Image.open(path)
        return im

    def ResizeImage(self, size):
        self.targetIm = self.oriIm.copy()
        self.targetIm.thumbnail(size)  
        w, h = self.targetIm.size
        self.Matrix = [[0 for x in range(w)] for y in range(h)] 

    def ConvertImageToBricks(self):
        w, h = self.targetIm.size
        pix = self.targetIm.load()
        for i in range(w):
            for j in range(h):
                point = pix[i,j]
                minDist = -1
                closestKey = ""
                for key in self.BrickColors:
                    brickColor = self.BrickColors[key]
                    dist = reduce(lambda  x, y: x+y, [x * x for x in [point[k] - brickColor[k] for k in range(0, len(point))]])
                    if minDist < 0 or minDist > dist:
                        minDist = dist
                        closestKey = key
                    pix[i, j] = self.BrickColors[closestKey]
                    self.Matrix[j][i] = closestKey
        
    def GetAllConnectedComponents(self):
        checkedPoints = set([])
        w, h = self.targetIm.size
        for i,j in [(i,j) for i in range(h) for j in range(w)]:
            if ((i,j) not in checkedPoints):
                # Start searching point
                checkedPoints.add((i,j))
                self.BFS(i, j, (h, w), checkedPoints)

    def BFS(self, startX, startY, size, checkedPoints):
        pointsInCurrentComponent = [(startX, startY)]
        startIndex = 0
        endIndex = len(pointsInCurrentComponent)
        while startIndex < endIndex:
            currentPoint = pointsInCurrentComponent[startIndex]
            for newX, newY in [(currentPoint[0] + i, currentPoint[0] + j) for i in range(-1, 2) for j in range(-1, 2)]:
                if (newX >= 0 and newY >= 0 and newX < size[0] and newY < size[1]):
                    if ((newX, newY) not in checkedPoints and self.Matrix[currentPoint[0]][currentPoint[1]] == self.Matrix[newX][newY]):
                        checkedPoints.add((newX, newY))
                        pointsInCurrentComponent.append((newX, newY))
            startIndex += 1
            endIndex = len(pointsInCurrentComponent)
            self.ConnectedComponents[(startX, startY)] = set(pointsInCurrentComponent)

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

    def GetLeftTopPoint(self, points):
        x = min([point[0] for point in points])
        y = min([point[1] for point in points if point[0] == x])
        return (x, y)

    def CheckIfThisBrickIsGood(self, points, brickList, startPoint, brick, xlen, ylen, availablePoints):
        currentPointSet = deepcopy(points)
        currentBrickList = deepcopy(brickList)
        for i in range(xlen):
            for j in range(ylen):
                if (startPoint[0]+i, startPoint[1]+j) not in availablePoints:
                    return None, None
                else:
                    currentPointSet.add((startPoint[0]+i, startPoint[1]+j))
        currentBrickList.append(brick)
        return currentPointSet, currentBrickList

    def GetBrickListForConnectedComponent2(self, pointsInCurrentComponentSet):
        stateHistory = [({}, [])]
        startIndex = 0
        endIndex = 1
        while startIndex < endIndex:
            lastState = stateHistory[startIndex]
            # a set of points
            pointsInLastState = lastState[0]
            brickListOfLastState = lastState[1]
            availablePoints = pointsInCurrentComponentSet - pointsInLastState
            maxBrickSize = len(availablePoints)
            startPoint = self.GetLeftTopPoint(availablePoints)
            for brick in self.BrickSizes:
                if (maxBrickSize >= brick[0] * brick[1]):
                    (resultState1, resultBrickList1) = self.CheckIfThisBrickIsGood(pointsInLastState, brickListOfLastState, startPoint, brick, brick[0], brick[1], availablePoints)
                    if resultState1 is not None:
                        stateHistory.append((resultState1, resultBrickList1))
                    if brick[0] != brick[1]:
                        (resultState2, resultBrickList2) = self.CheckIfThisBrickIsGood(pointsInLastState, brickListOfLastState, startPoint, brick, brick[1], brick[0], availablePoints)
                        if resultState2 is not None:
                            stateHistory.append((resultState2, resultBrickList2))
            endIndex = len(stateHistory)
            startIndex += 1

    def GetBrickListForConnectedComponent(self, pointsInCurrentComponentSet):
        # CPU usage is super high, needs improvement
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
                        if (len(availableStartPoint) < brick[0] * brick[1]):
                            continue
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

    def UpdateTotalBrickDict(self, color, pointsInCurrentComponentSet):
        try:
            brickDictForCurrentConnectedComponent = self.GetBrickListForConnectedComponent(pointsInCurrentComponentSet)
            if brickDictForCurrentConnectedComponent is not None:
                self.lock.acquire()
                for brick in brickDictForCurrentConnectedComponent:
                    if (brick, color) not in self.TotalBrickDict:
                        self.TotalBrickDict[(brick, color)] = 0
                    self.TotalBrickDict[(brick, color)] += brickDictForCurrentConnectedComponent[brick]
        finally:
            self.lock.release()

    def GetBrickListForImage(self):
        TotalBrickDict = {}
        for startPoint in self.ConnectedComponents:
            color = self.Matrix[startPoint[0]][startPoint[1]]
            brickDictForCurrentConnectedComponent = self.GetBrickListForConnectedComponent(self.ConnectedComponents[startPoint])
            if brickDictForCurrentConnectedComponent is not None:
                for brick in brickDictForCurrentConnectedComponent:
                    if (brick, color) not in TotalBrickDict:
                        TotalBrickDict[(brick, color)] = 0
                    TotalBrickDict[(brick, color)] += brickDictForCurrentConnectedComponent[brick]
        return TotalBrickDict

    def GetBrickListForImageMultiThreads(self):
        threads = []
        for startPoint in self.ConnectedComponents:
            color = self.Matrix[startPoint[0]][startPoint[1]]
            t = threading.Thread(target=self.UpdateTotalBrickDict, args=(color, self.ConnectedComponents[startPoint]))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

if __name__=='__main__':
    imageConverter = ImageConverter('Jay.jpg')
    imageConverter.GetBrickColors()
    imageConverter.GetBrickSizes()
    #pointsInSet = set([(0,0), (0,1), (0,2), (1,1),(1,2),(1,3)])
    #imageConverter.GetBrickListForConnectedComponent(pointsInSet)
    imageConverter.ResizeImage((16, 16))
    imageConverter.ConvertImageToBricks()
    imageConverter.GetAllConnectedComponents()
    imageConverter.targetIm.show()
    brickDict = imageConverter.GetBrickListForImageMultiThreads()
    print(len(brickDict))

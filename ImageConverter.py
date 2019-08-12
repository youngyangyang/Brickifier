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

    def GetBrickListForConnectedComponent(self, pointsInCurrentComponentSet):
        stateHistory = [(set([]), [])]
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
                        if len(resultState1) == len(pointsInCurrentComponentSet):
                            return resultBrickList1
                        stateHistory.append((resultState1, resultBrickList1))
                    if brick[0] != brick[1]:
                        (resultState2, resultBrickList2) = self.CheckIfThisBrickIsGood(pointsInLastState, brickListOfLastState, startPoint, brick, brick[1], brick[0], availablePoints)
                        if resultState2 is not None:
                            if len(resultState2) == len(pointsInCurrentComponentSet):
                                return resultBrickList2
                            stateHistory.append((resultState2, resultBrickList2))
            endIndex = len(stateHistory)
            startIndex += 1

    def UpdateTotalBrickDict(self, color, pointsInCurrentComponentSet):
        try:
            brickList = self.GetBrickListForConnectedComponent(pointsInCurrentComponentSet)
            if brickList is not None:
                self.lock.acquire()
                for brick in brickList:
                    if (brick, color) not in self.TotalBrickDict:
                        self.TotalBrickDict[(brick, color)] = 0
                    self.TotalBrickDict[(brick, color)] += 1
        finally:
            self.lock.release()

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
    #pointsInSet = set([(0,0), (1,0),(2,0),(1,1),(2,1),(3,1)])
    #imageConverter.GetBrickListForConnectedComponent(pointsInSet)
    imageConverter.ResizeImage((16, 16))
    imageConverter.ConvertImageToBricks()
    imageConverter.GetAllConnectedComponents()
    imageConverter.targetIm.show()
    imageConverter.GetBrickListForImageMultiThreads()
    for key in imageConverter.TotalBrickDict:
        print(key, imageConverter.TotalBrickDict[key])



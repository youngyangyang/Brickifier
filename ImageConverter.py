#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image

class ImageConverter(object):
    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.oriIm = self.GetImage(self.inputPath)

    def GetImage(self, path):
        im = Image.open(path)
        return im

    def ResizeImage(self, size):
        self.oriIm.thumbnail(size)   
        self.oriIm.show()

if __name__=='__main__':
    imageConverter = ImageConverter('Jay.jpg')
    imageConverter.ResizeImage((32, 32))


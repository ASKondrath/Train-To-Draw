# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 23:49:52 2016

@author: ask
"""

import cv2, numpy as np

class Drawing:
    
    def __init__(self, filename = None):
        
        self.img = []

        self.intensities = range(125, -1, -25)
        self.intensityIdx = 0
        
        self.numBox = 8
        self.locXIdx = 0
        self.locYIdx = 0
        
        self.doQuit = False
        
        self.names = {'workImg' : None,
                      'subImg' : None,
                      'fixedImg' : None,
                      'origSubImg' : None}
                      
        self.updateImgFile(filename)
        
        self.doResize = {'workImg' : False,
                         'subImg' : True,
                         'fixedImg' : False,
                         'origSubImg' : False}
                         
        self.windowVar = {'workImg' : cv2.cv.CV_WINDOW_AUTOSIZE, 
                          'subImg' : cv2.cv.CV_WINDOW_NORMAL,
                          'fixedImg' : cv2.cv.CV_WINDOW_AUTOSIZE,
                          'origSubImg' : cv2.cv.CV_WINDOW_NORMAL}
                          
        self.windowNames = {'workImg' : 'subImg',
                            'subImg' : '0',
                            'fixedImg' : 'fixedImg',
                            'origSubImg' : '0'}
                          
        
        
    def run(self):
        
        self.showWindow('workImg')
        self.showWindow('fixedImg')
        
        while not self.doQuit:
            
            returnVal = self.showWindow('subImg')
            self.getInput(returnVal)
            
            

    def getInput(self, inputVal):

        # parsing inputVal to move the block, change the intensity, or quit              
        if inputVal.isdigit():
            
            inputVal = int(inputVal) - 1
            direction = [inputVal // 3 - 1, (inputVal % 3) - 1]
        
            self.moveImg(direction)
        
        elif inputVal == 'a':
        
            self.changeIntensity(1)
            
        elif inputVal == 's':
            
            self.changeIntensity(-1)
            
        elif inputVal == 'q':
            
            self.doQuit = True
            
            
        elif inputVal == 'R':
            
            direction = [-1, 0]
            self.moveImg(direction)
            
        elif inputVal == 'S':
            
            direction = [0, 1]
            self.moveImg(direction)
            
        elif inputVal == 'T':
            
            direction = [1, 0]
            self.moveImg(direction)
            
        elif inputVal == 'Q':

            direction = [0, -1]  
            self.moveImg(direction)
            
        elif inputVal == 'u':
            
            self.updateImgFile()
            
        else:
            
            print 'Unexpected input value'
            print inputVal
                    
        
        
    def getImg(self, filename):
        
        self.imgColor = cv2.imread(filename)
        self.img = cv2.imread(filename, 0)



    def fixSize(self):

        # resizing image to conform to preferred size
        [m, n] = np.shape(self.img)
        
        if m > 800 and n > 800:
            
            sc = min(800.0 / m, 800.0 / n)
            self.img = cv2.resize(self.img, (int(sc * n), int(sc * m)))
            
            [m, n] = np.shape(self.img)
        
        if (m / (1.0 * n)) > (7 / 8.0) and (n / (1.0 * m)) > (7 / 8.0):
    
            numBox = 7

        else:
    
            numBox = 8
            
        
        if m < n:

            newN = (n + numBox - n % numBox) if (n % numBox) != 0 else n
        
            boxWidth = newN / numBox
            
            res = int(boxWidth * np.ceil(m / (1.0 * boxWidth)) - m)
    
            newM = m + res
    
            self.fixedImg = np.ones((newM,newN), dtype=np.uint8)
            self.fixedImg *= 255
            
            self.fixedImg[0 : m, 0 : n] = self.img

            m = newM
            n = newN
    
        else:
    
            newM = m + numBox - m % numBox if (m % numBox) != 0 else m
       
            boxWidth = newM / numBox
    
            res = int(boxWidth * np.ceil(n / (1.0 * boxWidth)) - n)
    
            newN = n + res
    
            self.fixedImg = np.ones((newM, newN), dtype = np.uint8)
            self.fixedImg *= 255

            self.fixedImg[0 : m, 0 : n] = self.img
    
            m = newM
            n = newN
            
        self.m = m
        self.n = n
            
        self.numMs = m / boxWidth
        self.numNs = n / boxWidth
        
        self.boxBord = 20
        self.workImg = np.ones((newM + 2*self.boxBord, newN + 2*self.boxBord), 
                      dtype = np.uint8)
        self.workImg *= 255
                      
        self.workImg[self.boxBord : m + self.boxBord, 
            self.boxBord : n + self.boxBord] = self.fixedImg
            
        self.fixedImg = cv2.cvtColor(self.fixedImg, cv2.COLOR_GRAY2BGR)
            
        self.startMs = range(self.numMs)
        self.startNs = range(self.numNs)
        
        self.startMs = [boxWidth * val for val in self.startMs]
        self.startNs = [boxWidth * val for val in self.startNs]
        
        for val in self.startMs:
            
            if val != 0:
                
                cv2.line(self.fixedImg, (0, val), (self.n, val), (0, 255, 0))
                
        for val in self.startNs:
            
            if val != 0:
                
                cv2.line(self.fixedImg, (val, 0), (val, self.m), (0, 255, 0))
        
        self.boxWidth = boxWidth
        self.numBox = numBox  
        
        self.names['workImg'] = self.workImg
        self.names['fixedImg'] = self.fixedImg
                                   
        
        
    def updateSubImg(self):
        
        idxX = self.startMs[self.locXIdx]
        idxY = self.startNs[self.locYIdx]
                    
        boxWid = self.boxWidth + 2 * self.boxBord
        self.names['origSubImg'] = self.workImg[idxX : idxX + boxWid, 
            idxY : idxY + boxWid]
        self.names['subImg'] = self.names['origSubImg']
                                           
        self.names['subImg'] = cv2.add(self.names['subImg'], 
            self.intensities[self.intensityIdx])
            
        self.names['subImg'] = cv2.cvtColor(self.names['subImg'], 
            cv2.COLOR_GRAY2BGR)
        
        for xVal in range(5):
            
            xIdx = self.boxWidth // 4 * xVal
            xIdx += self.boxBord
            
            for yVal in range(5):
                
                yIdx = self.boxWidth // 4 * yVal
                yIdx += self.boxBord
                
                if xIdx % 2 == 1 or yIdx % 2 == 1:
                    
                    colorVal = (255, 0, 0)
                    
                else:
                    
                    colorVal = (0, 0, 255)
                
                cv2.line(self.names['subImg'], (xIdx, yIdx), (xIdx, yIdx), 
                         colorVal, 1)
    
    
    
    def moveImg(self, direction):
        
        currX = self.locXIdx + direction[0]
        currY = self.locYIdx + direction[1]
        
        self.getIdcs(currX, currY)
        self.updateSubImg()
        
        
        
    def getIdcs(self, currX, currY):
        
        if ((currX == self.numMs and currY == self.numNs) or 
        (currX == self.numMs and currY == (self.numNs - 1)) or 
        (currX == (self.numMs - 1) and currY == self.numNs)):
                
            self.doQuit = True
            
        else:
            
            if currX == self.numMs: currX -= 1
            if currX < 0: currX = 0
            if currY == self.numNs: currY -= 1
            if currY < 0: currY = 0
                
            self.locXIdx = currX
            self.locYIdx = currY
                
        
        
    def changeIntensity(self, amount):
        
        self.intensityIdx += amount
        self.intensityIdx = max(self.intensityIdx, 0)
        self.intensityIdx = min(self.intensityIdx, 5)
        
        self.updateSubImg()
        
        
        
    def showWindow(self, windowName):

        cv2.namedWindow(windowName, self.windowVar[windowName])
        cv2.imshow(windowName, self.names[windowName])
        
        if self.doResize[windowName]:

            cv2.resizeWindow(windowName, 4 * self.boxWidth, 4 * self.boxWidth)

            waitKeyReturn = cv2.waitKey(0)
            returnVal = str(chr(waitKeyReturn % 256))
            
        else:
            
            cv2.waitKey(0)
            returnVal = None
        
        return returnVal

        
    def updateImgFile(self, fileName = None):
        
        if fileName is None:
            fileName = input('Input file name:')
            
        print fileName
        self.getImg(fileName)
        self.fixSize()
        self.updateSubImg()
        

if __name__ == "__main__":
    
    filename = 'Achu2.jpg'
    drawObj = Drawing(filename)
    drawObj.run()

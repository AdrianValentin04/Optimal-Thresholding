import csv
import operator
from itertools import combinations, permutations
import math
import os
from datetime import datetime
import json
import time
from copy import deepcopy

class csvParser:
    """
    This class is an abstract representation for informations offered in a .csv file.

    This contains functionalities for:
    - parsing the .csv file
    - saving relevant data
    """
    tresholdings = [] # list of lists 
    pixelClass = []
    plusList = [] # a list with "+"
    minusList = [] # a list with "-"
    multiplyList = [] # a list with "*"
    divideList = [] # a list with "/"
    operationMap = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv
    } # a dictionary with all the possible operators

    def __init__(self):
        for i in range(0, 3):
            self.plusList.append("+")
            self.minusList.append("-")
            self.multiplyList.append("*")
            self.divideList.append("/")

    def readCSV(self, inputFile):
        with open(inputFile, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')

            for row in reader:
                self.tresholdings.append(row[2:])
                self.pixelClass.append(row[1])
        return 0


class Binarization:

    def __init__(self):
        self.parser = csvParser() # .csv file parser
        self.pixelClass = 0 # the value of the pixel class
        self.valuesTh = [] # values of all tresholds
        self.combPercentage = dict() # dict of all comb
        self.allCombinations = []

    def generateCombinations(self):
        operatorsList = self.parser.plusList + self.parser.minusList + self.parser.multiplyList + self.parser.divideList

        comb1 = list(set(list(combinations(operatorsList, 3))))
        comb2 = list(set(list(combinations(operatorsList, 3))))
        comb3 = list(set(list(combinations(operatorsList, 3))))

        return comb1, comb2, comb3

    def generateCombinationsList(self):
        allCombinations = []
        comb1, comb2, comb3 = self.generateCombinations()

        for e1 in comb1:
            for e2 in comb2:
                for e3 in comb3:
                    order = e1 + e2 + e3
                    nrPlus = order.count("+")
                    nrMinus = order.count("-")
                    nrDiv = order.count("/")
                    nrMul = order.count("*")

                    if (abs(nrPlus - nrMinus) == 0 and abs(nrMul - nrDiv) <= 1) or (abs(nrPlus - nrMinus) <= 1 and abs(nrMul - nrDiv) == 0):
                        allCombinations.append(order)

        return allCombinations

    def findSolutionForOneFile(self, inputFile, copyAllCombinations, limit):
        self.parser.readCSV(inputFile)
        self.valuesTh = self.parser.tresholdings
        self.pixelClass = self.parser.pixelClass

        returnList = []

        for order in copyAllCombinations:
            succes = 0
            for i in range(len(self.valuesTh)):
                pixelClass = self.pixelClass[i]
                result = float(self.valuesTh[i][0])
                for j in range(1, len(self.valuesTh[i])):
                    result = self.parser.operationMap[order[j - 1]](result, float(self.valuesTh[i][j]))

                if result >= 0 and result < 0.5:
                    if int(pixelClass) == 0:
                        succes += 1
                if result >= 0.5 and result <= 1:
                    if int(pixelClass) == 1:
                        succes += 1

            percent = float(succes) / len(self.valuesTh)

            if percent >= limit:
                returnList.append(order)

                if "".join(order) in self.combPercentage.keys():
                    self.combPercentage["".join(order)] = (self.combPercentage["".join(order)] + percent) / 2
                else:
                    self.combPercentage["".join(order)] = percent
        return returnList

class LocalSolver:

    def __init__(self):
        self.binarization = Binarization()

    def localTrain(self):
        inputPath = os.getcwd() + '/tests/local/train'
        dir_list = os.listdir(inputPath)

        self.binarization.allCombinations = self.binarization.generateCombinationsList()
        copyAllCombinations = deepcopy(self.binarization.allCombinations)
        
        counter = 0
        for inFile in dir_list:
            inputFilePath = inputPath + '/' + str(inFile)
            returnList = self.binarization.findSolutionForOneFile(inputFilePath, copyAllCombinations, 0.8)
            copyAllCombinations = deepcopy(returnList)
            if counter == 50:
                break
            else:
                counter += 1

        jsonObj = json.dumps(self.binarization.combPercentage, indent=4)
        with open("localResults/localTrainResults.json", "w") as outfile:
            outfile.write(jsonObj)

        self.binarization.allCombinations = deepcopy(copyAllCombinations)
        self.binarization.combPercentage.clear()
        
    def localValidation(self):
        inputPath = os.getcwd() + '/tests/local/validation'
        dir_list = os.listdir(inputPath)
        copyAllCombinations = deepcopy(self.binarization.allCombinations)

        counter = 0
        for inFile in dir_list:
            inputFilePath = inputPath + '/' + str(inFile)
            returnList = self.binarization.findSolutionForOneFile(inputFilePath, copyAllCombinations, 0.83)
            copyAllCombinations = deepcopy(returnList)
            if counter == 50:
                break
            else:
                counter += 1
        
        jsonObj = json.dumps(self.binarization.combPercentage, indent=4)
        with open("localResults/localValidationResults.json", "w") as outfile:
            outfile.write(jsonObj)

        self.binarization.allCombinations = deepcopy(copyAllCombinations)
        self.binarization.combPercentage.clear()

    def localTest(self):
        inputPath = os.getcwd() + '/tests/local/test'
        dir_list = os.listdir(inputPath)
        copyAllCombinations = deepcopy(self.binarization.allCombinations)

        counter = 0
        for inFile in dir_list:
            inputFilePath = inputPath + '/' + str(inFile)
            returnList = self.binarization.findSolutionForOneFile(inputFilePath, copyAllCombinations, 0.85)
            copyAllCombinations = deepcopy(returnList)
            if counter == 50:
                break
            else:
                counter += 1
        
        jsonObj = json.dumps(self.binarization.combPercentage, indent=4)
        with open("localResults/localTestResults.json", "w") as outfile:
            outfile.write(jsonObj)

        self.binarization.allCombinations = deepcopy(copyAllCombinations)

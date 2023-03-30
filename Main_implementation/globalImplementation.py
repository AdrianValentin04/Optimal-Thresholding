import csv
import operator
from itertools import combinations, permutations
import math
import os
from datetime import datetime
import json

class csvParser:
    """
    This class is an abstract representation for informations offered in a .csv file.

    This contains functionalities for:
    - parsing the .csv file
    - saving relevant data
    """
    tresholdings = [] # values for thresholdings obtained from different algorithms
    fMeasures = [] # list of percentages
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
        for i in range(0, 4):
            self.plusList.append("+")
            self.minusList.append("-")
            self.multiplyList.append("*")
            self.divideList.append("/")

    def readCSV(self, inputFile):
        with open(inputFile, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            csv_info = []

            for row in reader:
                csv_info.append(row)

            self.tresholdings = csv_info[0]
            self.fMeasures = csv_info[1]
        return 0

class Binarization:

    def __init__(self):
        self.parser = csvParser() # .csv file parser
        self.idealTh = 0 # the value of the ideal treshold
        self.valuesTh = [] # values of all tresholds
        self.combFreq = dict() # dict of all comb (train)
        self.allCombinations = []

    def generateCombinations(self):
        operatorsList = self.parser.plusList + self.parser.minusList + self.parser.multiplyList + self.parser.divideList

        comb1 = list(set(list(combinations(operatorsList, 4))))
        comb2 = list(set(list(combinations(operatorsList, 4))))
        comb3 = list(set(list(combinations(operatorsList, 4))))
        comb4 = list(set(list(combinations(operatorsList, 2))))

        return comb1, comb2, comb3, comb4

    def generateCombinationsList(self):
        allCombinations = []
        comb1, comb2, comb3, comb4 = self.generateCombinations()

        for e1 in comb1:
            for e2 in comb2:
                for e3 in comb3:
                    for e4 in comb4:
                        order = e1 + e2 + e3 + e4
                        nrPlus = order.count("+")
                        nrMinus = order.count("-")
                        nrDiv = order.count("/")
                        nrMul = order.count("*")

                        if abs(nrPlus - nrMinus) <= 0 and abs(nrMul - nrDiv) <= 0:
                            allCombinations.append(order)
        return allCombinations

    def printCombinations(self):
        for combination in self.goodCombinations:
            print(combination)

    def computeResult(self, order):
        result = float(self.valuesTh[0])
        for i in range(1, len(self.valuesTh)):
            result = self.parser.operationMap[order[i - 1]](result, float(self.valuesTh[i]))

        if result >= 0 and result <= 1 :
            index = math.floor(result * 255)
            if float(self.parser.fMeasures[index]) > 80:
                return True
            else:
                return False

    def findSolutionForOneFile(self, inputFile):
        self.parser.readCSV(inputFile)
        self.idealTh = self.parser.tresholdings[0]
        self.valuesTh = self.parser.tresholdings[1:15]

        for order in self.allCombinations:
            if self.computeResult(order) is True:
                if "".join(order) in self.combFreq.keys():
                    self.combFreq["".join(order)] += 1
                else:
                    self.combFreq["".join(order)] = 1

class GlobalSolver:

    def __init__(self):
        self.binarization = Binarization()
        self.trainFilteredResults = dict() # filtered after train
        self.validationResults = dict() # after validation
        
        self.validationFilteredResults = dict() # filtered after validation
        self.testResults = dict() #after test

        self.bestCombinationsTested = dict()

    def globalTrain(self):
        inputPath = os.getcwd() + '/tests/global/train'
        dir_list = os.listdir(inputPath)

        self.binarization.allCombinations = self.binarization.generateCombinationsList()

        for inFile in dir_list:
            # print(inFile + "...")
            inputFilePath = inputPath + '/' + str(inFile)
            self.binarization.findSolutionForOneFile(inputFilePath)

        jsonObj = json.dumps(self.binarization.combFreq, indent=4)
        with open("globalResults/trainResults.json", "w") as outfile:
            outfile.write(jsonObj)

        maximumValue = max(self.binarization.combFreq.values())
        for key, value in self.binarization.combFreq.items():
            if value >= maximumValue / 2:
                self.trainFilteredResults[key] = value

        jsonObj = json.dumps(self.trainFilteredResults, indent=4)
        with open("globalResults/filteredTrainResult.json", "w") as outfile:
            outfile.write(jsonObj)

    def globalValidation(self):
        inputPath = os.getcwd() + '/tests/global/validation'
        dir_list = os.listdir(inputPath)

        for inFile in dir_list:
            # print(inFile + "...")
            inputFilePath = inputPath + '/' + str(inFile)
            self.binarization.parser.readCSV(inputFilePath)
            self.binarization.idealTh = self.binarization.parser.tresholdings[0]
            self.binarization.valuesTh = self.binarization.parser.tresholdings[1:15]

            for key, _ in self.trainFilteredResults.items():
                operations = list(key)
                if self.binarization.computeResult(operations) == True:
                    if "".join(operations) in self.validationResults.keys():
                        self.validationResults["".join(operations)] += 1
                    else:
                        self.validationResults["".join(operations)] = 1

        jsonObj = json.dumps(self.validationResults, indent=4)
        with open("globalResults/validationResults.json", "w") as outfile:
            outfile.write(jsonObj)

        maximumValue = max(self.validationResults.values())
        for key, value in self.validationResults.items():
            if value >= maximumValue * 0.75:
                self.validationFilteredResults[key] = value

        jsonObj = json.dumps(self.validationFilteredResults, indent=4)
        with open("globalResults/filteredValidationResults.json", "w") as outfile:
            outfile.write(jsonObj)


    def globalTest(self):
        inputPath = os.getcwd() + '/tests/global/test'
        dir_list = os.listdir(inputPath)

        for inFile in dir_list:
            # print(inFile + "...")
            inputFilePath = inputPath + '/' + str(inFile)
            self.binarization.parser.readCSV(inputFilePath)
            self.binarization.idealTh = self.binarization.parser.tresholdings[0]
            self.binarization.valuesTh = self.binarization.parser.tresholdings[1:15]

            for key, _ in self.validationFilteredResults.items():
                operations = list(key)
                if self.binarization.computeResult(operations) == True:
                    if "".join(operations) in self.testResults.keys():
                        self.testResults["".join(operations)] += 1
                    else:
                        self.testResults["".join(operations)] = 1

        jsonObj = json.dumps(self.testResults, indent=4)
        with open("globalResults/testResults.json", "w") as outfile:
            outfile.write(jsonObj)

        maximumValue = max(self.testResults.values())
        for key, value in self.testResults.items():
            if value >= maximumValue * 0.9:
                self.bestCombinationsTested[key] = value

        jsonObj = json.dumps(self.bestCombinationsTested, indent=4)
        with open("globalResults/bestResults.json", "w") as outfile:
            outfile.write(jsonObj)

    def globalAll(self):
        self.globalTrain()
        self.globalValidation()
        self.globalTest()

def main():
    # GS = GlobalSolver()
    # # GS.globalAll()
    # GS.globalTrain()
    # GS.globalValidation()
    # GS.globalTest()
    pass

if __name__ == "__main__":
    main()

    """
    TODO:
    - take the same idea for local
    """

# self.binarization.combFreq = dict(sorted(self.binarization.combFreq.items(), key=lambda item: item[1]))
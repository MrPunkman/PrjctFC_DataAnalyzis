from dataclasses import asdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from collectAllMeasureDataInOneFile import*
from ExperimentClass import*
from thesis_general_imports import*
# import seaborn as sns



class Investigation:
    '''Class to handle two experiments and get the differential B-Field'''
    def readSensorMatrix(self):
        # read Sensor file
        sensorPath = r'C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\00-Dataplots\\'
        sensorFilename = "PYTHON_GENEPAC_Sensors_3_Plan_AV_C_AR.txt"
        sensorMatrix = pd.read_csv(sensorPath + sensorFilename, sep="	", header = None)
        print(sensorMatrix)
        self.sensoMatrix = np.asarray(sensorMatrix)
        return self.sensoMatrix
    
    def creatSensorMapping(self):
        self.sensorsOfInterestArray = np.zeros((len(self.sensorArray),7))
        # fill sensormatrix with x y z u v w B-Field
        lengthOfSensorArray = len(self.sensorArray)
        sensorData = np.multiply(self.diffBField,1)
        for i in range(0,lengthOfSensorArray):
            line = self.sensorArray[i]
            self.sensorsOfInterestArray [i, 0:6] = self.sensoMatrix[line, :]
            self.sensorsOfInterestArray [i, -1] = sensorData[line]*self.FaultExperiment.arrayScaleFactor

        print(self.sensorsOfInterestArray)
        # Save as .txt
        np.savetxt(self.savepath+'SensorPositionsWithFields.txt', np.multiply(self.sensorsOfInterestArray,1), delimiter='\t')  
        return self.sensorsOfInterestArray

    def plotHealthyAndFaultyField(self):
        # vizualize both, the healthy and the faulty B-Field
        if self.FaultExperiment.year == 2020:
            ylimBFieldUp = 250
            ylimBFieldDown = -250
        elif self.FaultExperiment.year == 2021:
            ylimBFieldUp = 100
            ylimBFieldDown = -100
        print("Visualization of healthy, faulty and diff Field")
        f2 = plt.subplots(1, 1, figsize=set_size(), sharey=True)
        plt.plot(np.multiply(self.RefExperiment.scaledField, self.FaultExperiment.arrayPlotFactor), label = "Reference Fuel Cell B-Field in $\mu$T", color = specific_colors['G2EGreen'])
        plt.plot(np.multiply(self.FaultExperiment.scaledField, self.FaultExperiment.arrayPlotFactor), label = "Investigated Fuel Cell B-Field in $\mu$T", color = specific_colors['FaultyCell'])
        plt.plot(np.multiply(self.diffBField,self.FaultExperiment.arrayPlotFactor), label = "Dif B-Field in $\mu$T", color = specific_colors['MPM_red'])
        plt.xlim(0,len(self.diffBField)-1)
        plt.ylim(ylimBFieldDown,ylimBFieldUp)
        plt.legend()
        plt.title('B-Field comparison:\n {date} between {ref} and {faulty} for {amps} A'.format(date = self.FaultExperiment.date, ref = self.RefExperiment.name, faulty = self.FaultExperiment.name, amps = self.FaultExperiment.scaleCurrentTo))
        plt.xlabel("Sensor number")
        plt.ylabel("B-Field Strength ($\mu$T)")
        plt.savefig(self.savepath + self.FaultExperiment.name + "_B_diffFields.pdf")

    def plotDiffField(self):
        # vizualize both, the faulty B-Field
        print("Visualization of diff Field")
        f3 = plt.subplots(1, 1, figsize=set_size(), sharey=True)
        plt.plot(np.multiply(self.diffBField,self.FaultExperiment.arrayPlotFactor), label = "Dif B-Field in $\mu$T", color = specific_colors['MPM_red'])
        plt.xlim(0,len(self.diffBField)-1)
        plt.ylim(-50,50)
        #plt.title('Differential B-Field caused by {faulty} for {amps} A the {date}'.format(date = self.FaultExperiment.date, faulty = self.FaultExperiment.name, amps = self.FaultExperiment.scaleCurrentTo))
        plt.legend()
        plt.xlabel("Sensor number")
        plt.ylabel("B-Field Strength ($\mu$T)")
        plt.savefig(self.savepath + self.FaultExperiment.name + "_B_diffField.pdf")

    def plotInvestiagtedField(self):
        # vizualize the faulty B-Field
        print("Visualization of Investigated diff Field")
        f4 = plt.subplots(1, 1, figsize=set_size(), sharey=True)
        # plt.tight_layout()
        plt.plot(np.multiply(self.sensorsOfInterestArray[:,-1],self.FaultExperiment.arrayDiffFieldFactor), label = " Investigated dif B-Field in $\mu$T", color = specific_colors['MPM_red'])
        plt.xlim(0,len(self.sensorsOfInterestArray)-1)
        plt.ylim(-40,40)
        #plt.title('Differential B-Field caused by {faulty} for {amps} A the {date}'.format(date = self.FaultExperiment.date, faulty = self.FaultExperiment.name, amps = self.FaultExperiment.scaleCurrentTo))
        plt.legend()
        plt.xlabel("Sensor number")
        plt.ylabel("B-Field Strength ($\mu$T)")
        plt.savefig(self.savepath + self.FaultExperiment.name + "_Investig_B_diffField.pdf")





    def __init__(self, RefExperiment, FaultExperiment, sensorList):
        self.RefExperiment = RefExperiment
        self.FaultExperiment = FaultExperiment
        self.sensorArray = sensorList
        self.sensorsOfInterestArray = np.zeros((len(sensorList),7))
        self.sensoMatrix = self.readSensorMatrix()
        self.savepath = FaultExperiment.bFieldPath
        self.diffBField = np.subtract(RefExperiment.scaledField, FaultExperiment.scaledField)
        self.sensorsOfInterestArray = self.creatSensorMapping()
        self.plotHealthyAndFaultyField()
        self.plotDiffField()
        self.plotInvestiagtedField()


        
        
## Test:
# RefExperiment = 1
# FaultExperiment = 2
# sensorList = [1,2,3,4,5,6,8,9]
# testInv = Investigation(RefExperiment, FaultExperiment, sensorList)
# print(testInv.sensorsOfInterestArray)


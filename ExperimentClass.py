from dataclasses import asdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from collectAllMeasureDataInOneFile import*
from thesis_general_imports import*

# import seaborn as sns



class Experiment():
    # for 2020: 64.86 (50 A); 60 to 100 A
    # scaleVCurrentToAmps = 64.86
    # scaleCurrentTo = 50
    
    def __init__(self, year, name, date, measuredCurrent, scaleCurrentTo, noiseBFieldPath, filenamenoiseAV, filenamenoiseCenter, filenamenoiseAR, bFieldPath, filenameAV, filenameC, filenameAR):
        self.year = year
        self.scaleCurrentTo = scaleCurrentTo
        self.measuredCurrent = measuredCurrent
        self.name = name
        self.date = date

        ## define factors for 
        if self.year == 2020:
            ## check for current factor
            if self.measuredCurrent <= 50:
                self.scaleVCurrentToAmps = 60
            elif 51 <= self.measuredCurrent <= 110:
                self.scaleVCurrentToAmps = 60

            
            self.Tension1 = 'V_Menbrane1'
            self.Tension2 = 'V_Menbrane2'
            self.stackGlobalTensionName = 'V_Menbrane3'
            self.Tension4 = 'V_Menbrane4'
            self.Tension5 = 'V_Menbrane5'
            self.Tension6 = 'V_Menbrane6'

            self.stackGlobalCurrentName = 'CourantV'
            self.arrayPlotFactor = 1E6
            self.arrayScaleFactor = 1E6
            self.arrayDataFactor = 1E6

        elif self.year == 2021:

            self.Tension1 = 'V_C10'
            self.Tension2 = 'V_C11'
            self.stackGlobalTensionName = 'V_Pile_0_32'
            self.Tension4 = 'V_C13'
            self.Tension5 = 'V_C16'
            self.Tension6 = 'V_C20'
            self.stackGlobalCurrentName = 'CourantV'
            self.scaleVCurrentToAmps = 100
            self.arrayPlotFactor = 1E2
            self.arrayScaleFactor = 1E-4
            self.arrayDataFactor = 1E-2

        ## Define path and files for noise Data
        self.noiseBFieldPath = noiseBFieldPath
        self.filenamenoiseAV = filenamenoiseAV
        self.filenamenoiseCenter = filenamenoiseCenter
        self.filenamenoiseAR = filenamenoiseAR

        self.bFieldPath = bFieldPath
        self.filenameAV = filenameAV
        self.filenameC = filenameC
        self.filenameAR = filenameAR
        

        ## create clean data Frames
        ## noise
        self.noiseDataAV = createDF(self.noiseBFieldPath, self.filenamenoiseAV)
        self.noiseDataC = createDF(self.noiseBFieldPath, self.filenamenoiseCenter)
        self.noiseDataAR = createDF(self.noiseBFieldPath, self.filenamenoiseAR)
        ## MeasurmentData
        self.bFieldDataAV = createDF(self.bFieldPath, self.filenameAV)
        self.bFieldDataC = createDF(self.bFieldPath, self.filenameC)
        self.bFieldDataAR = createDF(self.bFieldPath, self.filenameAR)

        ## call Sensor Names:
        self.sensorNames = self.bFieldDataAV.columns

        ## calculate mean value of measured B-Field to substract from real measurements
        self.noiseBFieldMeanvalueAV = self.BFieldMeanValueNoise(self.noiseDataAV)   
        self.noiseBFieldMeanvalueC = self.BFieldMeanValueNoise(self.noiseDataC)     
        self.noiseBFieldMeanvalueAR = self.BFieldMeanValueNoise(self.noiseDataAR)
        ## Noise mean field in one
        self.measuredMeanNoiseField = np.append(self.noiseBFieldMeanvalueAV, np.append(self.noiseBFieldMeanvalueC,self.noiseBFieldMeanvalueAR))
        
        ## for vizualization: calculate mean value of measured B-Field
        self.BFieldMeanvalueWithNoiseAV = self.BFieldMeanValueNoise(self.bFieldDataAV)
        self.BFieldMeanvalueWithNoiseC = self.BFieldMeanValueNoise(self.bFieldDataC)
        self.BFieldMeanvalueWithNoiseAR = self.BFieldMeanValueNoise(self.bFieldDataAR)

        ## mean field in one
        self.measuredMeanFieldWithNoise = np.append(self.BFieldMeanvalueWithNoiseAV, np.append(self.BFieldMeanvalueWithNoiseC,self.BFieldMeanvalueWithNoiseAR))

        ## clean measurements
        self.BFieldCleanMeasurementAV = self.clearNoiseFromBFieldMeasurements(self.bFieldDataAV,self.noiseBFieldMeanvalueAV)
        self.BFieldCleanMeasurementC = self.clearNoiseFromBFieldMeasurements(self.bFieldDataC,self.noiseBFieldMeanvalueC)
        self.BFieldCleanMeasurementAR = self.clearNoiseFromBFieldMeasurements(self.bFieldDataAR,self.noiseBFieldMeanvalueAR)
        
        ## Clean mean B-Field on Sensors
        self.meanBFieldCleanMeasurementAV = self.BFieldMeanValueClean(self.BFieldCleanMeasurementAV)
        self.meanBFieldCleanMeasurementC = self.BFieldMeanValueClean(self.BFieldCleanMeasurementC)
        self.meanBFieldCleanMeasurementAR = self.BFieldMeanValueClean(self.BFieldCleanMeasurementAR)

        ## clean mean field in one
        self.measuredCleanField = np.append(self.meanBFieldCleanMeasurementAV, np.append(self.meanBFieldCleanMeasurementC,self.meanBFieldCleanMeasurementAR))

        
        ## ACHTUNG!!! The column index must be addopted respectivly the year!
        self.stackGlobalTensionAV = self.bFieldDataAV.loc[:,self.stackGlobalTensionName]
        self.stackGlobalTensionC = self.bFieldDataC.loc[:,self.stackGlobalTensionName]
        self.stackGlobalTensionAR = self.bFieldDataAR.loc[:,self.stackGlobalTensionName]
        print(self.stackGlobalTensionC)
        self.stackGlobalCurrent = self.bFieldDataAV.loc[:,self.stackGlobalCurrentName]
        print(self.stackGlobalCurrent)

        self.meanCurrent = self.stackGlobalCurrent.mean()*self.scaleVCurrentToAmps
        print(self.meanCurrent)
        self.scaleFieldFactor = self.scaleCurrentTo/self.meanCurrent
        print(self.scaleFieldFactor)
        self.scaledField = np.multiply(self.measuredCleanField, self.scaleFieldFactor)
        
        ## Plot B-Field Mean values on sensors
        plotFieldMeasurementDataAndSavePlots(self.measuredMeanFieldWithNoise, self.measuredMeanNoiseField, self.measuredCleanField, self.year, self.bFieldPath,self.name)

# ____________________________________________________________Start new Functions_____________________________________________________________________________________________
    ## for noise treatment: subtract vector with 60 entries
    def clearNoiseFromBFieldMeasurements(self, df, subtractor):
        print("Clean Noise from measurements start")
        c = 0
        result = pd.DataFrame(columns=self.sensorNames[2:62])
        for i in range(2,62):
            result.iloc[:,c] = df.iloc[:,i].sub(subtractor[c])
            c = c+1
        print("Clean Noise from measurements end")
        return result

    ## calculate B-Field mean values of a Noise frame
    def BFieldMeanValueNoise(self, df):
        print("Calculate Mean values start")
        BFieldArray = np.zeros(60)
        i = 0
        for sensors in range(2,62):
            BFieldArray[i] = df.iloc[:,sensors].mean(axis=0)
            i = i+1
        print("Calculate Mean values end")
        return BFieldArray

    ## calculate B-Field mean values of a noise-free DF
    def BFieldMeanValueClean(self, df):
        print("Calculate Mean values noise free start")
        BFieldArray = np.zeros(60)
        i = 1
        for sensors in range(0,59):
            BFieldArray[sensors] = df.iloc[:,sensors].mean(axis=0)
            i = i+1
        print("Calculate Mean values noise free end")
        return BFieldArray
        



    def createDF(self, bFieldPath, filename):
        '''This function is to read a .lvm file and read the data without the header'''
        ## import file and set file path
        print("reading Data start")
        df = pd.read_csv(bFieldPath + filename, sep="	",skiprows = [i for i in range(0, 23)])

        ## change , to . for later calculations. Otherwise, the cell is declared as string and no calculation can be done
        df = df.replace(',','.',regex=True)

        # change type to float
        df = df.astype(float)
        print("reading Data end")
        return df

# ____________________________________________________________Start Old Functions_____________________________________________________________________________________________






    # def getMeanValueOfCurrentAndVoltage(df):                           # this function returns the mean values of current and Voltage of the DataFrame
    #     # create list with mean value of every sensor column
    #     meanData = []
    #     columnMean = []
    #     investigationValues = [0, ]
    #     for i in range(0,68):
    #         columnMean = df.iloc[1:,i]
    #         meanData.append(mean(columnMean))

    #     # get V values in a list
    #     vValuesMeanData = meanData[0:len(meanData):1] 
    #     return vValuesMeanData

    def getMeanValueBFieldOfDF(df):                           # this function returns a mean value in v per column of the DataFrame
        # create list with mean value of every sensor column
        meanData = []
        columnMean = []

        for i in range(2,68):
            columnMean = df.iloc[1:,i]
            meanData.append(mean(columnMean))

        # get V values in a list
        vValuesMeanData = meanData[0:len(meanData):1] 
        return vValuesMeanData

    def getMeanValueVoltAndCurrentOfDF(self, df):                                                                                                    # returns B-field meanvalues in V as np.array
        meanValuesForEachCol = getMeanValueOfDFColumnInVolt(df)
        # get V values for B-field in a list
        currentMeanVoltage = meanValuesForEachCol[0]
        cellVoltageValues = meanValuesForEachCol[61,63,64]
        return np.asarray(cellVoltageValues), np.asarray(currentMeanVoltage)


    def getMeanValueBFieldOfDFInVolt(df):                                                                                                    # returns B-field meanvalues in V as np.array
        meanValuesForEachCol = getMeanValueOfDFColumnInVolt(df)
        # get V values for B-field in a list
        vValuesBFieldData = meanValuesForEachCol[1:61:1]
        return np.asarray(vValuesBFieldData)

    def returnAllColumnsOfDFasArray(bFieldPath, filename):                                                                                   # return measurements as n x m array
        df = np.asarray(createDF(bFieldPath, filename))
        return df

    def normalizeBFieldsToCurrents(dataframeWithCurrentInfo, BbFieldWithoutNoiseMean, desiredCorruntNormalization, scalevCurrentToAmps):    # normalize B-Fields to current
        ## get mean value of current
        vVlauesOfCurrent = dataframeWithCurrentInfo[:,1]
        currentMeanValue = np.multiply(np.mean(vVlauesOfCurrent), scalevCurrentToAmps)

        ## calc factor for normalization
        normalizationFactor = desiredCorruntNormalization/currentMeanValue
        ## scale with the factor
        scaledBFieldWithoutNoiseMean = np.multiply(BbFieldWithoutNoiseMean, normalizationFactor)
        return scaledBFieldWithoutNoiseMean

    def calculateCleanFields(self):
        # read file MeasurmentData AR
        readDataAR = pd.read_csv(self.bFieldPath + self.filenameAR, sep="	",skiprows = [i for i in range(0, 23) ])

        # read file MeasurmentData Centre
        readDataCenter = pd.read_csv(self.bFieldPath + self.filenameC, sep="	",skiprows = [i for i in range(0, 23) ])

        # read file MeasurmentData AV
        readDataAV = pd.read_csv(self.bFieldPath + self.filenameAV, sep="	",skiprows = [i for i in range(0, 23) ])

        print('Importing files')
        self.readDataNoiseAR = createDF(self.noiseBFieldPath, self.filenamenoiseAR)
        self.readDataNoiseCenter = createDF(self.noiseBFieldPath, self.filenamenoiseCenter)
        self.readDataNoiseAV = createDF(self.noiseBFieldPath, self.filenamenoiseAV)

        ## Boxplot for measured values
        # xbp = np.linspace(0,59,60)

        # sns.boxplot(x = xbp, y = self.readDataNoiseCenter.all, data = self.readDataNoiseCenter)

        #create NP arrays from data
        readDataAR = returnAllColumnsOfDFasArray(self.bFieldPath, self.filenameAR)
        readDataCenter = returnAllColumnsOfDFasArray(self.bFieldPath, self.filenameC)
        readDataAV  = returnAllColumnsOfDFasArray(self.bFieldPath, self.filenameAV)

        print('Files were imported')
        print('Handling noise on data')
        # get meanvalue of the noise
        noiseMeanOnEachSensorAR = getMeanValueBFieldOfDFInVolt(self.readDataNoiseAR)
        noiseMeanOnEachSensorCenter = getMeanValueBFieldOfDFInVolt(self.readDataNoiseCenter)
        noiseMeanOnEachSensorAV = getMeanValueBFieldOfDFInVolt(self.readDataNoiseAV)

        # subtract noise from each each B-field cell of each dataframe
        ## create df as array with B-Fields from DF
        vValuesofBFieldARWithNoise = readDataAR[:, 2:62]
        vValuesofBbFieldCenterWithNoise = readDataCenter[:, 2:62]
        vValuesofBbFieldAVWithNoise = readDataAV[:, 2:62]

        ## subtract from each cell the meanvalue of noise from each sample
        self.vValuesofBbFieldARWithoutNoise = np.subtract(vValuesofBFieldARWithNoise, noiseMeanOnEachSensorAR)
        self.vValuesofBbFieldCenterWithoutNoise = np.subtract(vValuesofBbFieldCenterWithNoise, noiseMeanOnEachSensorCenter)
        self.vValuesofBbFieldAVWithoutNoise = np.subtract(vValuesofBbFieldAVWithNoise, noiseMeanOnEachSensorAV)

        print('Noise from data deleted')

        print('Calculating mean values for each B-Field sensor')
        # generate mean value of the measurements for each sensor
        self.vValuesofBbFieldARWithoutNoiseMean = np.mean(self.vValuesofBbFieldARWithoutNoise, axis=0)
        self.vValuesofBbFieldCenterWithoutNoiseMean = np.mean(self.vValuesofBbFieldCenterWithoutNoise, axis=0)
        self.vValuesofBbFieldAVWithoutNoiseMean = np.mean(self.vValuesofBbFieldAVWithoutNoise, axis=0)


        bFieldARWithoutNoiseMean = self.vValuesofBbFieldARWithoutNoiseMean

        bFieldCenterWithoutNoiseMean = self.vValuesofBbFieldCenterWithoutNoiseMean
        bFieldCenterWithoutNoiseMean = bFieldCenterWithoutNoiseMean

        bFieldAVWithoutNoiseMean = self.vValuesofBbFieldAVWithoutNoiseMean

        ## Plot measured values and noise
        noiseField = np.append(noiseMeanOnEachSensorAR,(noiseMeanOnEachSensorCenter, noiseMeanOnEachSensorAV))
        measuredField = np.append(vValuesofBFieldARWithNoise,(vValuesofBbFieldCenterWithNoise, vValuesofBbFieldAVWithNoise))
        self.measuredCleanField = np.append(bFieldAVWithoutNoiseMean,(bFieldCenterWithoutNoiseMean, bFieldARWithoutNoiseMean))

        plotFieldMeasurementDataAndSavePlots(measuredField, noiseField, self.measuredCleanField, 2020, self.bFieldPath, self.filenameC)

        ## Boxplot for measured values
        # xbp = np.linspace(0,59,60)
        # df = pd.DataFrame(vValuesofBbFieldARWithoutNoise, columns = xbp)
        # sns.boxplot(x = xbp, y = 1, data = df)

        ## normalize for X Amps

        scaledBFieldARWithoutNoiseMean = normalizeBFieldsToCurrents(readDataAR, bFieldARWithoutNoiseMean, self.scaleCurrentTo, self.scaleVCurrentToAmps)
        scaledBFieldCenterWithoutNoiseMean = normalizeBFieldsToCurrents(readDataCenter, bFieldCenterWithoutNoiseMean, self.scaleCurrentTo, self.scaleVCurrentToAmps)
        scaledBFieldAVWithoutNoiseMean = normalizeBFieldsToCurrents(readDataAR, bFieldAVWithoutNoiseMean, self.scaleCurrentTo, self.scaleVCurrentToAmps)


        ## export 180 x 1 measurement data for B-Fields
        # self.scaledField = np.append(scaledBFieldAVWithoutNoiseMean,(scaledBFieldCenterWithoutNoiseMean, scaledBFieldARWithoutNoiseMean))
        # cleanBFieldArray = scaledBFieldCenterWithoutNoiseMean
        ## write values to csv
        print("Export DataFrame to: " + self.bFieldPath + self.filenameC[0: -11]+"_Scaled_B_Fieldclean.dat")
        # np.savetxt(bFieldPath + filenameC[0: -11]+"_Ref_B_Fieldclean.csv", 
        #            cleanBFieldArray,
        #            delimiter =", ", 
        #            fmt ='% s')

        # # scaledFile = np.multiply(self.scaledField,1)

        # np.savetxt(self.bFieldPath + self.filenameC[0: -11]+"_Scaled_B_Fieldclean.dat", 
        #         scaledFile,
        #         delimiter =", ", 
        #         fmt ='% s')           

        # print("Export finished")
        # return scaledFile




# noiseBFieldPath = r'C:\Users\Mein\tubCloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_22\Bruit\\'
# filenamenoiseAV = "Ref_Bruit_Ambiant_FM_Aux_On_AV_2.lvm"
# filenamenoiseCenter = "Ref_Bruit_Ambiant_FM_Aux_On_Centre_1.lvm"
# filenamenoiseAR = "Ref_Bruit_Ambiant_FM_Aux_On_AR_1.lvm"


# bFieldPath = r"C:\Users\Mein\tubCloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_22\Stochio_1_5\Def_Stoch_1_5\\"

# # call file name
# filenameAR = 'Def_Stoch1_5_I48A_AR.lvm'                     ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!
# filenameC = 'Def_Stoch1_5_I48A_Centre.lvm'                 ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!
# filenameAV = 'Def_Stoch1_5_I48A_AV.lvm'                     ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!


# TestExperiment = Experiment(2020, 50, "22.01.2020", 48, 100, noiseBFieldPath, filenamenoiseAV, filenamenoiseCenter,filenamenoiseAR, bFieldPath, filenameAV, filenameC, filenameAR)
# TestExperiment.calculateCleanFields()

## Humidity 2020_01_24 #####################################################################################
# noiseBFieldPath = r'C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_24\Bruit\\'
# filenamenoiseAV = "Ref_Bruit_Ambiant_FM_Aux_On_AV.lvm"
# filenamenoiseCenter = "Ref_Bruit_Ambiant_FM_Aux_On_Centre.lvm"
# filenamenoiseAR = "Ref_Bruit_Ambiant_FM_Aux_On_AR.lvm"

# bFieldPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_24\Humidite\\"
# filenameAR = 'Def_Hum30_I50A_AR.lvm'                    ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!
# filenameC = 'Def_Hum30_I50A_Centre.lvm'                 ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!
# filenameAV = 'Def_Hum30_I50A_AV.lvm'                    ###!!!!!!!!-----------> Change here <-----------!!!!!!!!!!!!!!!!
# year = 2020
# scaleBFieldToFollowingCurrent = 50
# investigatedCurrent = 50

# testExperiment = Experiment(2020, "Humidity 30 %", "24.01.2020", 50, 50, noiseBFieldPath, filenamenoiseAV, filenamenoiseCenter,filenamenoiseAR, bFieldPath, filenameAV, filenameC, filenameAR)
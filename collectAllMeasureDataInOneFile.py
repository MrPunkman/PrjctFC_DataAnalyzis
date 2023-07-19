'''This module is created by Leonard Freisem and is used to create diff B-Field for an investigated case.'''
from ctypes import sizeof
from tracemalloc import stop
from turtle import color
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from thesis_general_imports import*
# import seaborn as sns

# import csv and change ',' to '.' . Change df to float df 
def createDF(bFieldPath, filename):
    ## import file and set file path
    df = pd.read_csv(bFieldPath+filename, sep="	",skiprows = [i for i in range(0, 23) ])

    ## change , to . for later calculations. Otherwise, the cell is declared as string and no calculation can be done
    df = df.replace(',','.',regex=True)

    # change type to float
    df = df.astype(float)
    
    return df


# create mean values of the raw data and save in array
def getMeanValueOfDFColumnInVolt(df):                           # this function returns a mean value of the raw data per column of the DataFrame
    # create list with mean value of every sensor column
    meanData = []
    columnMean = []

    for i in range(1,68):
        columnMean = df.iloc[1:,i]
        meanData.append(mean(columnMean))

    # get V values in a list
    vValuesMeanData = meanData[0:len(meanData):1] 
    return vValuesMeanData

# returns B-Field meanvalues as np.array
def getMeanValueBFieldOfDFInVolt(df):                               # returns B-field meanvalues in V as np.array
    meanValuesForEachCol = getMeanValueOfDFColumnInVolt(df)
    # get V values for B-field in a list
    vValuesBFieldData = meanValuesForEachCol[1:61:1]                # selects the meanvalues for the B-Field in the array
    return np.asarray(vValuesBFieldData)

def getMeanValueCurrentAndTensions(df):                               # returns B-field meanvalues in V as np.array
    meanValuesForEachCol = df.iloc[1,1]
    meanValuesCurrent = mean(meanValuesForEachCol)
    # get V values for B-field in a list
    vValuesBFieldData = meanValuesForEachCol[1:61:1]                # selects the meanvalues for the B-Field in the array
    return np.asarray(vValuesBFieldData)

# return measurements as matrix array
def returnAllColumnsOfDFasArray(bFieldPath, filename):              # return measurements as n x m array
    df = np.asarray(createDF(bFieldPath, filename))
    return df

# plot B-Field respecting factors depending on the investigated year and save clean field mean values as txt
def plotFieldMeasurementDataAndSavePlots(rawField, noiseField, cleanField, year, bFieldPath, filename):
    if year == 2020:
        arrayPlotFactor = 1E6
        arrayScaleFactor = 1E6
        arrayDataFactor = 1E6
        ylimBFieldUp = 250
        ylimBFieldDown = -250
    elif year == 2021:
        arrayPlotFactor = 1E2
        arrayScaleFactor = 1E4
        arrayDataFactor = 1E-2
        ylimBFieldUp = 100
        ylimBFieldDown = -100

    # rawFieldArray = np.zeros((len(rawField)))
    # for element in range(0, len(rawFieldArray)-1):
    #     rawFieldArray[element] = np.multiply(np.mean(rawField[element], axis=0),arrayPlotFactor)

    f1 = plt.subplots(1, 1, figsize=set_size(), sharey=True)
    plt.plot(np.multiply(noiseField, arrayPlotFactor), ":" , label = "Noise mean value in $\mu$T", color = specific_colors['G2E_black'])
    plt.plot(np.multiply(rawField, arrayPlotFactor), ':' , label = "B-Field with noise in $\mu$T", color = specific_colors['RawField'])
    plt.plot(np.multiply(cleanField, arrayPlotFactor),   label = "Clean B-Field in $\mu$T", color = specific_colors['MPM_lightblue'])
    plt.xlabel("Sensor number")
    plt.ylabel("Field Strength ($\mu$T)")
    plt.ylim(ylimBFieldDown, ylimBFieldUp)
    plt.xlim(0,len(cleanField)-1)
    plt.legend()
    # plt.show()

    plt.savefig(bFieldPath + filename[0: -11]+"_B_Field_CleanMeasured.pdf")
    measuredField = np.multiply(cleanField, arrayDataFactor)
    # write values to csv
    print("Exported DataFrame to: " + bFieldPath + filename[0: -11]+"_B_Field_CleanMeasured.dat")
    np.savetxt(bFieldPath + filename[0: -11] + "_B_Field_CleanMeasured.dat", 
            measuredField,
            delimiter =", ", 
            fmt ='% s')

def plotDiffField(diffBField, date, name, affectedCurrent, savepath):
    # vizualize both, the faulty B-Field
    print("Visualization of diff Field")
    f3 = plt.subplots(1, 1, figsize=set_size(), sharey=True)
    plt.plot(np.multiply(diffBField,1), label = "Dif B-Field in $\mu$T mapped on Sensors", color = specific_colors['MPM_red'])
    plt.xlim(0,len(diffBField)-1)
    # plt.ylim(-10,10)
    plt.title('Differntial B-Field caused by {faulty} for {amps} A the {date}'.format(date = date, faulty = name, amps = affectedCurrent))
    plt.legend()
    plt.xlabel("Sensor number")
    plt.ylabel("B-Field Strength ($\mu$T)")
    plt.savefig(savepath + name + "_B_diffField_investigated.pdf")

def createViolinPlot(sensorDataFrame, name, savePath):
    pass

# this function is scaling the B-Field values to a certain current respecting linear conditions of the B-Field
def normalizeBFieldsToCurrents(dataframeWithCurrentInfo, BbFieldWithoutNoiseMean, desiredCorruntNormalization, scalevCurrentToAmps):    # normalize B-Fields to current
    ## get mean value of current
    vVlauesOfCurrent = dataframeWithCurrentInfo[:,1]
    currentMeanValue = np.multiply(np.mean(vVlauesOfCurrent),scalevCurrentToAmps)

    ## calc factor for normalization
    normalizationFactor = desiredCorruntNormalization/currentMeanValue
    ## scale with the factor
    scaledBFieldWithoutNoiseMean = np.multiply(BbFieldWithoutNoiseMean, normalizationFactor)
    return scaledBFieldWithoutNoiseMean


# get B-Field Vector 
# def createBFieldVector(noisetPath, noisefile, measurementPath, measurementFile, year, scaleBFieldToFollowingCurrent, investigatedCurrent):
#     # chose scale factors depending on the investigated year
#     if year == 2020 and investigatedCurrent == 50:
#         scaleVCurrentToAmps = 64.86

#     elif year == 2020 and investigatedCurrent == 100:
#         scaleVCurrentToAmps = 60

#     elif year == 2021 and investigatedCurrent == 100:
#         scaleVCurrentToAmps = 100

#     else: 
#         print("Your current is not in the list")
#         stop

#     print('Importing files')
#     readDataNoise = createDF(noisetPath, noisefile)
#     readData = returnAllColumnsOfDFasArray(measurementPath, measurementFile)
#     print('Files were imported')
#     print('Handling noise on data')
#     noiseMeanOnEachSensor = getMeanValueBFieldOfDFInVolt(readDataNoise)

#     # create boxplot for each sensor 
#    # sns.boxplot(data=readDataNoise, x = readDataNoise[2:62], y = readDataNoise[0:-1])

#     vValuesofBbFieldWithNoise = readData[:, 2:62]

#     vValuesofBbFieldWithoutNoise = np.subtract(vValuesofBbFieldWithNoise, noiseMeanOnEachSensor)
#     print('Noise from data deleted') 

#     print('Calculating mean values for each B-Field sensor')
#     vValuesofBbFieldWithoutNoiseMean = np.mean(vValuesofBbFieldWithoutNoise, axis=0)
#     vValuesofBbFieldWithNoiseMean = np.mean(vValuesofBbFieldWithNoise, axis=0)
#     # plot and save data
#     plotFieldMeasurementDataAndSavePlots(vValuesofBbFieldWithNoiseMean, noiseMeanOnEachSensor, vValuesofBbFieldWithoutNoiseMean, year, measurementPath, measurementFile)
#     print('Data plotted and plots saved')

#     bFieldWithoutNoiseMean = vValuesofBbFieldWithoutNoiseMean
#     scaledBFieldWithoutNoiseMean = normalizeBFieldsToCurrents(readData, bFieldWithoutNoiseMean, scaleBFieldToFollowingCurrent, scaleVCurrentToAmps)
#     return scaledBFieldWithoutNoiseMean


# def creatDiffBfieldForMIPSE(sensorcount, noisetPath, noisefile, refMeasurementPath, refMeasurementFile, measurementPath, measurementFile, year, scaleBFieldToFollowingCurrent, investigatedCurrent = 50 or 100, plotIt = False):
#     '''This module is created by Leonard Freisem and is used to create diff B-Field for an investigated case. \n
#     Inputs:\n
#         Noise file of the day ("Path/NoiseFile.lvm") \n
#         Reference Fuel Cell file ("Path/RefMeasurementFile.lvm")\n
#         Investigated Fuel Cell file ("Path/MeasurementFile.lvm")\n
#         Data year (2020 or 2021) --> different factors have to be applied on the measurements\n
#         current scale factor --> by assuming a linear system, we factorize the B-Field\n

#     The function will save the files in the investigated FC-folder
#     '''
#     ## ref fc path and file
#     healthyFCBFieldPath = refMeasurementPath
#     filenameRefFC = refMeasurementFile

#     # get noise path and file
#     noiseBFieldPath = noisetPath
#     filenamenoise = noisefile

#     # get investigated FC
#     bFieldPath = measurementPath
#     filenameC = measurementFile

#     print("Processing data from investigated FC")
#     faultyFC = createBFieldVector(noiseBFieldPath, filenamenoise, bFieldPath, filenameC, year, scaleBFieldToFollowingCurrent, investigatedCurrent)

#     print("Processing data from ref FC")
#     refFC = createBFieldVector(noiseBFieldPath, filenamenoise, healthyFCBFieldPath, filenameRefFC, year, scaleBFieldToFollowingCurrent, investigatedCurrent)
    

#     print('Import of Data from ref FC finished')
#     print("Calculate differential field")

#     # subtract the faulty - healthy field, so faulty, field to get the differential field
#     faultyDiffFCBField = np.subtract(faultyFC, refFC)
#     print("Calculation finished")

#     if year == 2020:
#         arrayPlotFactor = 1E6
#         arrayScaleFactor = 1E6
#         arrayDataFactor = 1E6
#     elif year == 2021:
#         arrayPlotFactor = 1E2
#         arrayScaleFactor = 1E-4
#         arrayDataFactor = 1E-2

#     # vizualize both, the healthy and the faulty B-Field
#     f2 = plt.figure()
#     plt.plot(np.multiply(refFC, arrayPlotFactor), label = "Healthy Fuel Cell B-Field in $\mu$T", color = 'b')
#     plt.plot(np.multiply(faultyFC, arrayPlotFactor), label = "Faulty Fuel Cell B-Field in $\mu$T", color = 'r')
#     plt.plot(np.multiply(faultyDiffFCBField,arrayPlotFactor), label = "Dif B-Field in $\mu$T", color = 'g')
#     plt.xlim(0,len(faultyDiffFCBField)-1)
#     plt.legend()
#     plt.xlabel("Sensor number")
#     plt.ylabel("B-Field Strength ($\mu$T)")
#     plt.savefig(bFieldPath + filenameC[0: -11] + "_B_diffFields.pdf")


#     # vizualize both, the faulty B-Field
#     f3 = plt.figure()
#     plt.plot(np.multiply(faultyDiffFCBField,arrayPlotFactor), label = "Dif B-Field in $\mu$T", color = 'g')
#     plt.xlim(0,len(faultyDiffFCBField)-1)
#     plt.ylim(-10,10)
#     plt.legend()
#     plt.xlabel("Sensor number")
#     plt.ylabel("B-Field Strength ($\mu$T)")
#     plt.savefig(bFieldPath + filenameC[0: -11] + "_B_diffField.pdf")


#     print("Exporting differential field")

#     # save differential field in txt
#     fieldExport = np.multiply(faultyDiffFCBField,arrayScaleFactor)
#     np.savetxt(bFieldPath + filenameC[0: -11] + "_B_diffField.dat", 
#             fieldExport[0:sensorcount],
#             delimiter =", ", 
#             fmt ='% s')

#     print("Exported DataFrame to: " + bFieldPath + filenameC[0: -11] + "_B_diffField.dat")



    # inputs:
    # listOfSensors, bFieldPath, bFieldFile, sensorfile, sensorfilePath
# def appendSensorValuesonSensorMapping(sensorsOfInterest, date, name, affectedCurrent, savepath, bFieldPath):
#     # take list of Sensors
#     print(sensorsOfInterest)
#     # read bField file 
#     bFieldFilename = "SigmaFields.txt"
#     bField = pd.read_csv(bFieldPath + bFieldFilename, sep="	", header = None)
#     print(bField)
#     bField = np.asarray(bField)
#     # read Sensor file
#     sensorPath = r'C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\00-Dataplots\\'
#     sensorFilename = "PYTHON_GENEPAC_Sensors_3_Plan_AV_C_AR.txt"
#     sensorMatrix = pd.read_csv(sensorPath + sensorFilename, sep="	", header = None)
#     print(sensorMatrix)
#     sensorMatrix = np.asarray(sensorMatrix)
#     sensorsOfInterestArray = np.zeros((len(sensorsOfInterest),7))
#     bFieldOfInterestArray = np.zeros(len(sensorsOfInterest))
#     # sensorMatrix = np.append(sensorMatrix, np.zeros(len(sensorMatrix)),1)
#     #print(sensorMatrix)
#     # fill sensormatrix with x y z u v w B-Field

#     for i in range(0,len(sensorsOfInterest)):
#         line = sensorsOfInterest[i]
#         sensorsOfInterestArray [i, 0:6] = sensorMatrix[line, :]
#         sensorsOfInterestArray [i, -1] = bField[line]
#         bFieldOfInterestArray[i] = bField[i]


#     plotDiffField(bFieldOfInterestArray, date, name, affectedCurrent, savepath)
#     print(sensorsOfInterestArray)
#     # Save as .txt
#     np.savetxt(bFieldPath+'SensorPositionsWithFields.txt', sensorsOfInterestArray, delimiter='\t')    


## Test:
# refMeasurementFile = "Pile_saine_Idc100A_Iac_10A_f0Hz_CENTRE.lvm"
# refMeasurementPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesure_2021\2021_07_28\Pile_saine\\"

# refMeasurementFile = "Ref_Pile_I48A_Centre.lvm"
# refMeasurementPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_24\Pile_Saine\\"


# measurementFile = "Ref_Pile_I48A_Centre.lvm"
# measurementPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_22\Pile Saine\Def_PileSaine\\"

# noisefile = "Ref_Bruit_Amb_Aux_ON_Centre.lvm"
# noisetPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_22\Bruit\\"

# # noisefile = "Banc_on_sans_courant_Idc0A_Iac_0A_f0Hz_CENTRE.lvm"
# # noisetPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesure_2021\2021_07_28\Bruitmesure\\"

# year = 2020
# scaleBFieldToFollowingCurrent = 50
# investigatedCurrent = 50
# sensorCount = 60

# # creatDiffBfieldForMIPSE(sensorCount, noisetPath, noisefile, refMeasurementPath, refMeasurementFile, measurementPath, measurementFile, year, scaleBFieldToFollowingCurrent, investigatedCurrent = investigatedCurrent, plotIt = False)
# sensorsOfInterest = np.linspace(60,89,30,dtype=int)
# date = "20200124"
# name = "Humidity 30 %"
# affectedCurrent = 50
# bFieldPath = r"C:\Users\freiseml\Nextcloud\01_France\04_Stage\00-Travail\03-PAC\Mesures 2020\CEA\2020_01_24\Humidite\\"
# # appendSensorValuesonSensorMapping(sensorsOfInterest, date, name, affectedCurrent,bFieldPath)
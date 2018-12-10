# libraries for dealing with matricies, reading files, and machine-learning
import numpy as np
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

## FULL SCAN ##

filename = "chronic_kidney_disease_stripped.arff"

def trainFullScan(filename):
  # import arff file
  data = arff.loadarff(filename)

 # convert data to matrix
  protoData = []
  for row in range(155):
    rowList = []
    for col in range(22):
      rowList.append(data[0][row][col])
    protoData.append(rowList)

  # turn nominals into 1 or 0
  for row in range(155):
    for col in range(22):
      if protoData[row][col] == b'no' or protoData[row][col] == b'notpresent' or protoData[row][col] == b'ckd' or protoData[row][col] == b'poor' or protoData[row][col] == b'abnormal':
        protoData[row][col] = 0
      elif protoData[row][col] == b'normal' or protoData[row][col] == b'good' or protoData[row][col] == b'notckd' or protoData[row][col] == b'present' or protoData[row][col] == b'yes':
        protoData[row][col] = 1
  print(protoData[0][0])
  outcome =  RandomForestClassifier().fit(pd.DataFrame(protoData).drop(21, axis=1), pd.DataFrame(protoData)[21])
  print(outcome)
  return outcome


def runFullScan(fullData, fullModel):
  outcome = fullModel.predict(fullData)
  print(outcome)
  return fullModel.predict(fullData)






















## QUICK SCAN ##
upperRanges = [100,125,80,13,21,300,10,180,100,7.45,0.08,7.5]
lowerRanges = [60,90,40,11,6,30,0,60,91,7.35,0,4.5]
problem = ["heartrate","systolic","diastolic","respiratoryrate","sleep","aerobicactivity","alcohol","bloodglucose","bloodoxygen","bloodacidity","urineglucose","urineacidity"]

def trainQuickScan(upperRanges,lowerRanges):
  # generate matrix of healthy and unhealthy data that models the values set by upper- and lowerRanges
  trainData = []
  for row in range(1000):
    healthyRow, unhealthyRow = [],[]
    for col in range(len(upperRanges)):
      curMean = ((upperRanges[col] + lowerRanges[col])/2)
      if lowerRanges[col] > 0: healthyRow.append(np.random.normal(curMean))
      elif lowerRanges[col] == 0: healthyRow.append(np.random.normal((curMean/4)))
      if np.random.uniform(0,1) < 0.5:
        unhealthyRow.append(np.random.uniform(lowerRanges[col]-curMean,lowerRanges[col]))
      else:
        unhealthyRow.append(np.random.uniform(upperRanges[col],(upperRanges[col])+curMean))
    healthyRow.append(1)
    unhealthyRow.append(0)
    trainData.append(healthyRow)
    trainData.append(unhealthyRow)
  trainData = np.expand_dims((trainData), axis=0)
  trainData.reshape(2000,13)
  X = pd.DataFrame(trainData[0]).drop(12,axis=1)
  y = pd.DataFrame(trainData[0])[12]
  #data_train, data_test, values_train, values_test = train_test_split(pd.DataFrame(trainData[0]).drop(12,axis=1), pd.DataFrame(trainData[0])[12], test_size=0.3, random_state=123)
  data_train, values_train = X, y
  model = RandomForestClassifier()
  model.fit(data_train, values_train)
  return model.fit(data_train, values_train)

def runQuickScan(scanData,model,problem):
  high,low = [],[]
  for col in range(len(upperRanges)):
    curCol = scanData[col]
    if curCol != "na":
      if curCol < lowerRanges[col]: low.append(problem[col])
      elif curCol > upperRanges[col]: high.append(problem[col])
  result = model.predict(np.expand_dims((scanData), axis=0))
  return(high,low,result)
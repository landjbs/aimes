import numpy as np
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import pickle

upperRanges = [100,125,80,13,21,98.9,300,7,180,100,7.45,0.08,7.5]
lowerRanges = [60,90,40,6,12,98.3,30,0,60,91,7.35,0,4.5]
problem = ["heartrate","systolic","diastolic","sleep","respiratoryrate","bodytemp","aerobicactivity","alcohol","bloodglucose","bloodoxygen","bloodacidity","urineglucose","urineacidity"]

def trainQuickScan(upperRanges,lowerRanges):
  # generate matrix of healthy and unhealthy data that models the values set by upper- and lowerRanges
  trainData = []
  for row in range(1000):
    healthyRow, unhealthyRow = [],[]
    for col in range(len(upperRanges)):
      curMean = ((upperRanges[col] + lowerRanges[col])/2)
      if lowerRanges[col] > 0: healthyRow.append(np.random.normal(curMean,(np.std([lowerRanges[col],upperRanges[col]]))*0.38))
      elif lowerRanges[col] == 0: healthyRow.append(np.random.normal(curMean-(curMean/4),(np.std([lowerRanges[col],upperRanges[col]]))*0.38))

      if np.random.uniform(0,1) < 0.5:
        unhealthyRow.append(np.random.uniform(lowerRanges[col]-curMean,lowerRanges[col]))
      else:
        unhealthyRow.append(np.random.uniform(upperRanges[col],(upperRanges[col])+(2*curMean)))
    trainData.append(healthyRow.append(1))
    trainData.append(unhealthyRow.append(0))
  trainData = np.expand_dims((trainData), axis=0)
  trainData.reshape(2000,14)
  model = RandomForestClassifier().fit(pd.DataFrame(trainData[0]).drop(13,axis=1), pd.DataFrame(trainData[0])[13])
  pickle.dump(model, open('quickModel.sav','wb'))
  return 1

def runQuickScan(quickData,quickModel,problem):
  high,low = [],[]
  for col in range(len(upperRanges)):
    curCol = scanData[col]
    if curCol < lowerRanges[col]: low.append(problem[col])
    elif curCol > upperRanges[col]: high.append(problem[col])
  result = model.predict(np.expand_dims((scanData), axis=0))
  return(high,low,result)

trainQuickScan(upperRanges,lowerRanges)

scanData = [100,100,40,6,12,98.3,30,1,60,91,7.35,0,6.5]


loaded_quickModel = pickle.load(open("quickModel.sav","rb"))
result = loaded_quickModel.predict(np.expand_dims(scanData,axis=1).T)
print(result)
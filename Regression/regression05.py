import pandas as pd
import quandl, math, datetime
import numpy as np
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt #plot stuff
from matplotlib import style

style.use('ggplot') #specify style

quandl.ApiConfig.api_key = "9ftK99VkU4KsNiqxvgwt" #quandl API

df = quandl.get('WIKI/GOOGL')
df = df[['Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume',]]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Close']) / df['Adj. Close'] * 100.0
df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) / df['Adj. Open'] * 100.0

df = df[['Adj. Close', 'HL_PCT', 'PCT_change', 'Adj. Volume']]

forecast_col = 'Adj. Close'
df.fillna(-99999, inplace=True)

forecast_out = int(math.ceil(0.01*len(df)))
#print(forecast_out)

df['label'] = df[forecast_col].shift(-forecast_out) #shift prices days into the future

X = np.array(df.drop(['label'], 1)) #discard label column
X = preprocessing.scale(X) #scale
X_lately = X[-forecast_out:]
X = X[:-forecast_out]


df.dropna(inplace=True)
y = np.array(df['label'])
y = np.array(df['label'])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

#define classifier
clf = LinearRegression(n_jobs=10) 
#clf = svm.SVR(kernel='poly')
clf.fit(X_train, y_train) #train

accuracy = clf.score(X_test, y_test) #test
#print(accuracy)

forecast_set = clf.predict(X_lately)
print(forecast_set, accuracy, forecast_out)

df['Forecast'] = np.nan

#specify details of graph
last_date = df.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

#populate dataframe with new dates and forecast values
for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += one_day
    df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]
    #df.loc[next_date] is the index of the df
    #loop will create new indexes, or else replace existing ones
    #sets labels to NaN as we have no info on them, then append forecast

print(df.tail())

df['Adj. Close'].plot()
df['Forecast'].plot()
plt.legend(loc=4)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

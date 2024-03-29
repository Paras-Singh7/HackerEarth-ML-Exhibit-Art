#Importing Libraries
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import sklearn.metrics as metrics
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense,Dropout

#Importing Dataset
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
sub = pd.DataFrame(test['Customer Id'])
sub.head()

#Exploring dataset
df = train
df.head()

df.shape
df.drop(['Customer Id', 'Artist Name'], axis = 1, inplace = True)
df.shape
test.drop(['Customer Id', 'Artist Name'], axis = 1, inplace = True)
test.shape
df.info()

#Explanatory data analysis
num_f = df.select_dtypes(include = [np.number])
cat_f = df.select_dtypes(include = [np.object])

cat_f.head()

fig = plt.figure(figsize=(16,16))
for i in range(len(num_f.columns)):
    fig.add_subplot(3, 4, i+1)
    sns.boxplot(y=num_f.iloc[:,i])
plt.tight_layout()
plt.show()

fig = plt.figure(figsize=(16,30))
for i in range(len(cat_f.columns[:-3])):
    fig.add_subplot(9, 5, i+1)
    cat_f.iloc[:,i].hist()
    plt.xlabel(cat_f.columns[i])
plt.tight_layout()
plt.show()

sns.pairplot(df)
plt.show()

plt.rcParams['figure.figsize'] = (10, 10)
corr = df.corr()
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
sns.heatmap(corr, mask = mask, annot=True)
plt.show()

#Preprocessing Dataset
df.describe()

df.isna().sum()

#Filling missing values
df['Artist Reputation'].fillna(df['Artist Reputation'].median(),inplace = True)
test['Artist Reputation'].fillna(test['Artist Reputation'].median(),inplace = True)
df['Artist Reputation'].isna().any()

df['Height'].fillna(df['Height'].median(), inplace = True)
test['Height'].fillna(test['Height'].median(), inplace = True)
df['Height'].isna().any()

df['Width'].fillna(df['Width'].median(), inplace = True)
test['Width'].fillna(test['Width'].median(), inplace = True)
df['Width'].isna().any()

df['Weight'].fillna(df['Weight'].median(), inplace = True)
test['Weight'].fillna(test['Weight'].median(), inplace = True)
df['Weight'].isna().any()

df['Transport'].fillna(df['Transport'].mode()[0], inplace = True)
test['Transport'].fillna(test['Transport'].mode()[0], inplace = True)
df['Transport'].isna().any()

df['Remote Location'].fillna(df['Remote Location'].mode()[0], inplace = True)
test['Remote Location'].fillna(test['Remote Location'].mode()[0], inplace = True)
df['Remote Location'].isna().any()

df['Material'].fillna(df['Material'].mode()[0], inplace = True)
test['Material'].fillna(test['Material'].mode()[0], inplace = True)
df['Material'].isna().any()

df.isna().any().sum()
test.isna().any().sum()

#Deriving Features
df['state'] = df['Customer Location'].map(lambda x:x.split()[-2])
df.drop('Customer Location', inplace=True, axis=1)

test['state'] = test['Customer Location'].map(lambda x:x.split()[-2])
test.drop('Customer Location', inplace=True, axis=1)
test.head()

df['Scheduled Date'] = pd.to_datetime(df['Scheduled Date'])
df['Delivery Date'] = pd.to_datetime(df['Delivery Date'])
df['scheduleDiff'] = (df['Delivery Date'] - df['Scheduled Date']).map(lambda x:str(x).split()[0])
df['scheduleDiff'] = pd.to_numeric(df['scheduleDiff'])

test['Scheduled Date'] = pd.to_datetime(test['Scheduled Date'])
test['Delivery Date'] = pd.to_datetime(test['Delivery Date'])
test['scheduleDiff'] = (test['Delivery Date'] - test['Scheduled Date']).map(lambda x:str(x).split()[0])
test['scheduleDiff'] = pd.to_numeric(test['scheduleDiff'])

test.head()

df['dday'] = df['Delivery Date'].dt.day
df['dmonth'] = df['Delivery Date'].dt.month
df['dyear'] = df['Delivery Date'].dt.year
df['ddayofweek'] = df['Delivery Date'].dt.dayofweek

test['dday'] = test['Delivery Date'].dt.day
test['dmonth'] = test['Delivery Date'].dt.month
test['dyear'] = test['Delivery Date'].dt.year
test['ddayofweek'] = test['Delivery Date'].dt.dayofweek

test.head()

df.drop(['Delivery Date', 'Scheduled Date'], inplace=True, axis=1)
df.head()

test.drop(['Delivery Date', 'Scheduled Date'], inplace=True, axis=1)
test.head()

#Encoding categorical variable to numeric
num_f = df.select_dtypes(include = [np.number])
cat_f = df.select_dtypes(include = [np.object])
num_f1 = test.select_dtypes(include = [np.number])
cat_f2 = test.select_dtypes(include = [np.object])

enc = LabelEncoder()

for i in cat_f:
  df[i] = enc.fit_transform(cat_f[i])
  test[i] = enc.fit_transform(cat_f2[i])

df.head()

df['Cost1'] = np.log1p(abs(df['Cost']))
df.drop(['Cost'],axis=1,inplace=True)
df.head()

#Modelling
#Splitting our data into train and test
X = df.drop(['Cost1'], axis=1)
y = df['Cost1']

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.20, random_state=42, shuffle=True)
X_train.head()

y_val

#Random Forest
regressor = RandomForestRegressor(criterion='mse', random_state=123, max_depth=10, n_estimators=1000,min_samples_leaf=4, min_samples_split=2)
regressor.fit(X_train,y_train)

y_tr = regressor.predict(X_train)
y_te = regressor.predict(X_val)
rms1 = mean_squared_error(y_train, y_tr, squared=False)
rms2 = mean_squared_error(y_val, y_te, squared=False)
print("RMSE of train:",rms1,"\nRMSE of test:",rms2)

a = plt.axes(aspect='equal')
plt.scatter(y_val, y_te, label='Actual')
plt.xlabel('True Values [MPG]')
plt.ylabel('Predictions [MPG]')
lims = [min(y_val)-1, max(y_val)+1]
plt.xlim(lims)
plt.ylim(lims)
plt.plot(lims, lims, label='Predicted')

actual = np.expm1(y_val)
predicted = np.expm1(y_te)
score = 100*max(0, 1-metrics.mean_squared_log_error(actual, predicted))
score

#XGBoost
xgb1 = xgb.XGBRegressor()
parameters = {'objective':['reg:linear'],
              'learning_rate': [0.01, 0.02], 
              'max_depth': [5, 8],
              'colsample_bytree': [0.3,0.7],
              'n_estimators': [500, 1000],
              'tree_method':['gpu_hist']}
              
xgb_cv = RandomizedSearchCV(xgb1, parameters, cv = 3, verbose=True)
xgb_cv.fit(X_train,y_train)

print(xgb_cv.best_score_)
print(xgb_cv.best_params_)

y_tr = xgb_cv.best_estimator_.predict(X_train)
y_te = xgb_cv.best_estimator_.predict(X_val)

rms1 = mean_squared_error(y_train, y_tr, squared=False)
rms2 = mean_squared_error(y_val, y_te, squared=False)
print("RMSE of train:",rms1,"\nRMSE of test:",rms2)

a = plt.axes(aspect='equal')
plt.scatter(y_val, y_te, label='Actual')
plt.xlabel('True Values [MPG]')
plt.ylabel('Predictions [MPG]')
lims = [min(y_val)-1, max(y_val)+1]
plt.xlim(lims)
plt.ylim(lims)
plt.plot(lims, lims, label='Predicted')

actual = np.expm1(y_val)
predicted = np.expm1(y_te)
score = 100*max(0, 1-metrics.mean_squared_log_error(actual, predicted))
score

#ANN
scaler = MinMaxScaler()
X_train1 = pd.DataFrame(scaler.fit_transform(X_train))
X_val1 = pd.DataFrame(scaler.fit_transform(X_val))
X_train.describe()

model = Sequential()
model.add(Dense(2048, input_dim=20, kernel_initializer='normal', activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1, activation='linear'))
model.summary()

model.compile(loss='mse', optimizer='adam', metrics=['mse','mae'])

history = model.fit(X_train1, y_train, epochs=150, batch_size=50,  verbose=1, validation_split=0.2)

print(history.history.keys())
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

y_tr = model.predict(X_train1)
y_te = model.predict(X_val1)

rms1 = mean_squared_error(y_train, y_tr, squared=False)
rms2 = mean_squared_error(y_val, y_te, squared=False)
print("RMSE of train:",rms1,"\nRMSE of test:",rms2)

a = plt.axes(aspect='equal')
plt.scatter(y_val, y_te, label='Actual')
plt.xlabel('True Values [MPG]')
plt.ylabel('Predictions [MPG]')
lims = [min(y_val)-1, max(y_val)+1]
plt.xlim(lims)
plt.ylim(lims)
plt.plot(lims, lims, label='Predicted')

actual = np.expm1(y_val)
predicted = np.expm1(y_te)
score = 100*max(0, 1-metrics.mean_squared_log_error(actual, predicted))
score

#Working on train and test model
X = train.drop(['Cost1'], axis=1)
X.head()

y = train['Cost1']
y

#XGB
xgb1 = xgb.XGBRegressor()

parameters = {'objective':['reg:linear'],
              'learning_rate': [0.01, 0.02], 
              'max_depth': [5, 8],
              'colsample_bytree': [0.3, 0.7],
              'n_estimators': [500, 1000],
              'tree_method':['gpu_hist']}

xgb_cv = RandomizedSearchCV(xgb1, parameters, cv = 3, verbose=True)
xgb_cv.fit(X,y)

print(xgb_cv.best_score_)
print(xgb_cv.best_params_)

y_pred = xgb_cv.best_estimator_.predict(X)
y_pred

actual = np.expm1(y)
predicted = np.expm1(y_pred)
score = 100*max(0, 1-metrics.mean_squared_log_error(actual, predicted))
score

pred1 = xgb_cv.best_estimator_.predict(test)
pred1 = np.expm1(pred1)
pred1

#Random Forest
regressor = RandomForestRegressor(criterion='mse', random_state=123, max_depth=10, n_estimators=1000,min_samples_leaf=4, min_samples_split=2)
regressor.fit(X,y)

y_pred = regressor.predict(X)

actual = np.expm1(y)
predicted = np.expm1(y_pred)
score = 100*max(0, 1-metrics.mean_squared_log_error(actual, predicted))
score

pred2 = regressor.predict(test)
pred2 = np.expm1(pred2)
pred2

#Creating and writing submission File
sub1 = sub
sub1['Cost'] = pred1
sub1.to_csv("submit4.csv", index = False)
sub1.head()

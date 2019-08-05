# -*- coding: utf-8 -*-
"""FinalMLCode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dk2uJRfkfvVPQ44ZJHCP4FYLvxFa_E3K
"""

# -*- coding: utf-8 -*-
"""MLProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_46P6U6K0P8tQ4lsYxKJIHMWWVONfd1o
"""

import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse 
import sklearn
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_log_error
import pickle
import gc


sales    = pd.read_csv('sales_train.csv')
items           = pd.read_csv('items.csv')
item_categories = pd.read_csv('item_categories.csv')
shops           = pd.read_csv('shops.csv')
test            = pd.read_csv('test.csv')

#print(sales)
sales = sales[sales.item_cnt_day <= 1000] #Removing Outliers
sales = sales[sales.item_price <= 100000]
# print(len(sales))


group = sales.groupby(['date_block_num','shop_id','item_id']).agg({'item_cnt_day': ['sum']}).fillna(0).astype(np.float16)
group.columns = ['item_cnt_month']
group.reset_index(inplace=True)
group.to_csv("groupedData.csv")

plt.plot(sales.date_block_num, sales.item_cnt_day)
plt.show()
plt.scatter(group.date_block_num, group.item_cnt_month)
plt.show()


group.drop(group[group.item_cnt_month > 40].index, inplace=True)
group.drop(group[group.item_cnt_month == 0].index, inplace=True)

month_mean = group[['shop_id', 'item_id', 'item_cnt_month']].groupby(['shop_id', 'item_id'], as_index=False)[['item_cnt_month']].mean()
month_mean = month_mean.rename(columns={'item_cnt_month':'item_cnt_month_mean'})

group = pd.merge(group, month_mean, how='left', on=['shop_id', 'item_id']).clip(0,100)

print(group.columns)
group.head()

plt.scatter(group.date_block_num, group.item_cnt_month_mean)
plt.show()


# group.drop(group[group.item_cnt_month < 3.0].index, inplace=True)
# len(group[group.item_cnt_month < 3.0])
# group.head()
# plt.scatter(group.date_block_num, group.item_cnt_month)
# plt.show()



group.to_pickle('data.pkl')

data = pd.read_pickle('data.pkl')
data = data[[
    'date_block_num',
    'shop_id',
    'item_id',
    'item_cnt_month' , 'item_cnt_month_mean']]

X_train = data[data.date_block_num < 28].drop(['item_cnt_month', 'item_cnt_month_mean'], axis=1)
Y_train = data[data.date_block_num < 28]['item_cnt_month_mean']
X_valid = data[data.date_block_num > 27].drop(['item_cnt_month', 'item_cnt_month_mean'], axis=1)
Y_valid = data[data.date_block_num > 27]['item_cnt_month_mean']


# X_train = data[data.date_block_num < 28].drop(['item_cnt_month'], axis=1)
# Y_train = data[data.date_block_num < 28]['item_cnt_month']
# X_valid = data[data.date_block_num > 27].drop(['item_cnt_month'], axis=1)
# Y_valid = data[data.date_block_num > 27]['item_cnt_month']

print("Y_valid: ", Y_valid.head())

gc.collect();




def XGBRegression(X_train,Y_train,X_valid,Y_valid):
    print("\n\nXGBRegression\n")
    modelXGB = xgb.XGBRegressor(max_depth = 50, subsample = 0.5, colsample_bytree = 0.5, min_child_weight = 30,n_estimators=100)
    ts = time.time()
    model_fit(modelXGB,X_train,Y_train)
    print("training time: ",time.time() - ts)
    ts = time.time()
    Y_pred = model_predict(modelXGB,X_valid)
    print("testing time: ",time.time() - ts)
    Y_pred = pd.Series(Y_pred)
    print(Y_pred.head())
    metrics(Y_valid,Y_pred)
    

def RandomForestRegression(X_train,Y_train,X_valid,Y_valid):
    print("\n\nRandomForestRegression\n")
    modelRFR = RandomForestRegressor(random_state=5, max_depth = None, n_estimators=100, min_samples_split = 10)
    ts = time.time()
    model_fit(modelRFR,X_train,Y_train)
    print("training time: ",time.time() - ts)
    ts = time.time()
    Y_pred = model_predict(modelRFR,X_valid)
    print("testing time: ",time.time() - ts)
    Y_pred = pd.Series(Y_pred)
    print(Y_pred.head())
    metrics(Y_valid,Y_pred)

def AdaBoostRegression(X_train,Y_train,X_valid,Y_valid):
    print("\n\nAdaBoostRegression\n")
    modelABR = AdaBoostRegressor(DecisionTreeRegressor(max_depth=5), learning_rate=0.2, random_state = 20, loss = "linear")
    ts = time.time()
    model_fit(modelABR,X_train,Y_train)
    print("training time: ",time.time() - ts)
    ts = time.time()
    Y_pred = model_predict(modelABR,X_valid)
    print("testing time: ",time.time() - ts)
    Y_pred = pd.Series(Y_pred)
    print(Y_pred.head())
    metrics(Y_valid,Y_pred)

def model_fit(model,X_train,Y_train):
    model.fit(X_train, Y_train)

def model_predict(model,X_valid):
    Y_pred = model.predict(X_valid).clip(0,100)
    pickle.dump(Y_pred, open('xgb_train.pickle', 'wb'))
    return Y_pred

def metrics(Y_valid,Y_pred):
    print(explained_variance_score(Y_valid, Y_pred))
    print(mean_squared_log_error(Y_valid,Y_pred))
    print(r2_score(Y_valid,Y_pred))
    print(np.sqrt(mean_squared_error(Y_valid,Y_pred)))



XGBRegression(X_train,Y_train,X_valid,Y_valid)
RandomForestRegression(X_train,Y_train,X_valid,Y_valid)
AdaBoostRegression(X_train,Y_train,X_valid,Y_valid)
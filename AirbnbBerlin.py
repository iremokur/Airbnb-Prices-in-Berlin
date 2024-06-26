# -*- coding: utf-8 -*-
"""AirbnbBerlin.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FXNVU3Ba_iiK8qYywxpOeXhU63ysh-Gp

# Data Exploration
"""

# Load the packages
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, KFold
import sklearn.compose
import sklearn.preprocessing
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import sklearn.metrics
from sklearn.metrics import r2_score

dataFrame = pd.read_csv('listings.csv')
dataFrame.head(10)

print("Airbnb dataset {} number of rows ".format(dataFrame.shape[0]))
print("Airbnb dataset {} number of columns ".format(dataFrame.shape[1]))

dataFrame.columns.to_list()


bins = [100, 200, 300, 400, np.inf]
labels = ['< 100', '100 < x <= 200', '200 < x <= 300', '> 400']
dataFrame['price_range'] = pd.cut(dataFrame['price'], bins=bins, labels=labels)

dataFrame.drop(['host_id', 'id', 'license', 'name','host_name','price'], axis=1, inplace=True)

dataframe_train, dataframe_test = sklearn.model_selection.train_test_split(dataFrame, test_size=0.20)

print ('dataframe size: ', dataFrame.shape)
print ('dataframe_train size: ', dataframe_train.shape)
print ('dataframe_test size: ', dataframe_test.shape)


# take a look at data types and non null count.
dataframe_train.info()

# visualize numerical features.
dataFrame.hist(figsize=(10, 10))

#Checking for missing data
dataframe_train.isna().any().any()

# Check if columns contain NaN values
dataframe_train.isna().sum()


# fill price_range NaN values with the most frequent value of the column.
most_frequent_price_range = dataframe_train['price_range'].mode()[0]
dataframe_train["price_range"].fillna(most_frequent_price_range, inplace = True)
most_frequent_price_range_test = dataframe_test['price_range'].mode()[0]
dataframe_test["price_range"].fillna(most_frequent_price_range_test, inplace = True)

# reviews_per_month is float64 so filled with 0.0 (means no review)
dataframe_train["reviews_per_month"].fillna(0.0, inplace = True)
dataframe_test["reviews_per_month"].fillna(0.0, inplace = True)

dataframe_train.isna().sum()

dataframe_train.dropna(inplace=True)

dataframe_test.isna().sum()

dataframe_test.dropna(inplace=True)


x_train = dataframe_train.drop(['price_range'], axis=1)
y_train = dataframe_train['price_range']

x_test = dataframe_test.drop(['price_range'], axis=1)
y_test = dataframe_test['price_range']
print('x train set size -> ', x_train.shape)
print('y train set size -> ', y_train.shape)
print('x test set size -> ', x_test.shape)
print('y test set size -> ', y_test.shape)

num_values = x_train.select_dtypes(include = ['int64','float64']).columns.tolist()
cat_values=  x_train.select_dtypes(include = ['object']).columns.tolist()

ct = sklearn.compose.ColumnTransformer([
    ('std_scl', sklearn.preprocessing.StandardScaler(), num_values),
    ('ohe', sklearn.preprocessing.OneHotEncoder(handle_unknown="ignore"), cat_values)
])

ct.fit(x_train)
x_train = ct.transform(x_train)
x_test = ct.transform(x_test)

print ('x train size: ', x_train.shape)
print ('y train size: ', y_train.shape)
print ('x test size: ', x_test.shape)
print ('y test size: ', y_test.shape)

"""# Model Selection
3 different classification model types used.
These are:
1.   Decision Tree Classifier
2.   Random Forest Classifier
3.   Logistic Regressor

To choose the best model between 3 of them, first found the best hyperparameter for each model using **GridSearchCV.**

For the cross validation of the model **K-Fold** is used. K-fold used because it reduces overfitting, helps to compare and select the model.

For the hyperparameter tunning -> chosed 3 important parameters that probably will affect the model performance.
"""

grid_df = pd.DataFrame(columns=["Model", "Best Hyper Parameters","Best Score" ])
# 5-fold cross-validation
kfold = KFold(n_splits=5, shuffle=True)

"""## Decision Tree Classifier

- n_jobs =-1 used  in the grid search cv for all three models, because wanted to use all available CPU cores.

For the hyperparameter tunning:

    {"splitter":["best","random"],
    "max_depth" : [1,3,5],
    "min_samples_leaf":[1,2,3],
    "max_leaf_nodes":[None,10,20]}
 parameters chosed.
"""

parameters_DTR = {"splitter":["best","random"],
                  "max_depth" : [1,3,5],
                  "min_samples_leaf":[1,2,3],
                  "max_leaf_nodes":[None,10,20]}

tuning_model_DTR = GridSearchCV(DecisionTreeClassifier(),parameters_DTR, scoring="accuracy", cv=kfold, n_jobs = -1)
tuning_model_DTR.fit(x_train, y_train)
grid_df = grid_df._append({"Model": "DecisionTreeClassifier", "Best Hyper Parameters": tuning_model_DTR.best_params_, "Best Score":tuning_model_DTR.best_score_}, ignore_index=True)

"""## Random Forest Classifier

For the hyperparameter tunning:

    {"min_samples_split" : [2, 5],
    "min_samples_leaf" : [1, 2],
    "bootstrap" : [True, False]}
 parameters chosed.
"""

parameters_RF = {"min_samples_split" : [2, 5],
                  "min_samples_leaf" : [1, 2],
                  "bootstrap" : [True, False]}

tuning_model_RF = GridSearchCV(RandomForestClassifier(),parameters_RF, scoring="accuracy", cv = kfold, n_jobs = -1)
tuning_model_RF.fit(x_train, y_train)
grid_df = grid_df._append({"Model": "RandomForestClassifier", "Best Hyper Parameters": tuning_model_RF.best_params_, "Best Score":tuning_model_RF.best_score_}, ignore_index=True)

"""## Logistic Regression
For the hyperparameter tunning:

    {'penalty':[ "l2", None],
    'max_iter': [150, 200]}
 parameters chosed.
"""

parameters_LoR = {'penalty':[ "l2", None],
                  'max_iter': [100, 150]}

tuning_model_LoR = GridSearchCV(LogisticRegression(),parameters_LoR, scoring="accuracy", cv = kfold, n_jobs=-1)
tuning_model_LoR.fit(x_train, y_train)
grid_df = grid_df._append({"Model": "LogisticRegression", "Best Hyper Parameters": tuning_model_LoR.best_params_, "Best Score":tuning_model_LoR.best_score_}, ignore_index=True)

display(grid_df)


best_model= tuning_model_RF
y_predicted = best_model.predict(x_test)
prediction_df = pd.DataFrame(y_predicted,columns=['prediction'])
prediction_df.head()

print("Model Accuracy", sklearn.metrics.accuracy_score(y_test, y_predicted))


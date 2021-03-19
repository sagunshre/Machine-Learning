# -*- coding: utf-8 -*-
"""ML Final project 2: Unreliable Sensors

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18Kd4icoTFEo6FzTD9LuXVkI9Pkfsp237
"""

import sys
import numpy as np
from numpy import nan
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_validate
from sklearn.preprocessing import MinMaxScaler, StandardScaler, PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.feature_selection import SelectKBest, RFE, f_regression
from sklearn.linear_model import LinearRegression
np.set_printoptions(threshold=sys.maxsize)
from google.colab import files

DATASET = np.load("data_signals.npz")

def dataset():
  X = np.array(DATASET['X'])
  Y = np.array(DATASET['y'])
  print(X.shape, Y.shape)
  return X,Y

# def replace_missing_value(X):

X, Y = dataset()
X[np.isnan(X)] = np.median(X[~np.isnan(X)])
imputed_X = X

def preprocessor(scaler, x):
  scaler.fit(X)
  return scaler.transform(x)

def feature_selection(selector, x, y):
  return selector.fit_transform(x, y)

def model_cross_validation(model, x, y):
  cv = KFold(n_splits=5, random_state=0, shuffle=True)
  iteration = 0
  mse = {}
  r2 = {}
  y_test_sets = {}
  x_training_sets = {}
  x_test_sets = {}
  y_training_sets = {}
  predictions = {}
  for train_index, test_index in cv.split(x):
    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]
    model.fit(x_train,y_train)
    y_pred = model.predict(x_test)
    x_training_sets[iteration] = x_train
    x_test_sets[iteration] = x_test
    y_training_sets[iteration] = y_train
    y_test_sets[iteration] = y_test
    predictions[iteration] = y_pred
    mse[iteration] = mean_squared_error(y_test, y_pred)
    r2[iteration] = r2_score(y_test, y_pred)
    iteration = iteration + 1
  return(x_training_sets, x_test_sets, y_training_sets, y_test_sets, predictions, mse, r2)

def plot(ax, y, y_pred, title):
  ax.scatter(y, y_pred, color='blue', edgecolors=(0, 0, 0))
  ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', color='red',lw=4)
  ax.set_xlabel('Measured')
  ax.set_ylabel('Predicted')
  ax.set_title(title)
  return ax

model = LinearRegression()
fig, axs = plt.subplots(figsize=(4, 4), constrained_layout=True)
x_training_sets, x_test_sets, y_training_sets, y_test_sets, predictions, mse, r2 = model_cross_validation(model, imputed_X, Y)
plot(axs, np.array(list(y_test_sets.values())[0]), np.array(list(predictions.values())[0]), "Linear Regression")
filename = "base_model.eps"
plt.savefig(filename, format="eps")
files.download(filename)
# plt.show()
print("#################### MSE SCORE ##################")
print(mse)
print(np.mean(np.array(list(mse.values()))))
print("#################### R2 SCORE ##################")
print(r2)
print(np.mean(np.array(list(r2.values()))))

model = LinearRegression()
combination = {"Polynomial Feature Preprocessing": PolynomialFeatures(), "Standardization Preprocessing": StandardScaler() }
fig, axs = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
iteration = 0 
mse = {}
r2 = {}
y_test_sets = {}
x_training_sets = {}
x_test_sets = {}
y_training_sets = {}
predictions = {}
for key, value in combination.items():
  X_scaled = preprocessor(value, imputed_X)
  print(X_scaled.shape)
  x_training_sets[key], x_test_sets[key], y_training_sets[key], y_test_sets[key], predictions[key], mse[key], r2[key] = model_cross_validation(model, X_scaled, Y)
  plot(axs[iteration], np.array(list(y_test_sets[key].values())[0]), np.array(list(predictions[key].values())[0]), key)
  iteration = iteration + 1
filename = "just_preprocessing.eps"
plt.savefig(filename, format="eps")
files.download(filename)
# plt.show()
print("#################### MSE SCORE ##################")
for k, m in mse.items():
  print(m)
  print(np.mean(np.array(list(m.values()))))
print("#################### R2 SCORE ##################")
for k, r in r2.items():
  print(r)
  print(np.mean(np.array(list(r.values()))))

model = LinearRegression()
combination = {"Polynomial Feature & Filter Method": [PolynomialFeatures(), SelectKBest(score_func=f_regression, k=5)], 
               "Polynomial Feature & Wrapper Method ": [PolynomialFeatures(), RFE(model, n_features_to_select=5, step=5)], 
               "standardizing & Wrapper Method": [StandardScaler(), RFE(model, n_features_to_select=5, step=2)],
               "standardizing & Filter Method": [StandardScaler(), SelectKBest(score_func=f_regression, k=5)]}
fig, axs = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
iteration = 0 
mse = {}
r2 = {}
y_test_sets = {}
x_training_sets = {}
x_test_sets = {}
y_training_sets = {}
predictions = {}
for key, value in combination.items():
  X_scaled = preprocessor(value[0], imputed_X)
  features = feature_selection(value[1], X_scaled, Y)
  x_training_sets[key], x_test_sets[key], y_training_sets[key], y_test_sets[key], predictions[key], mse[key], r2[key] = model_cross_validation(model, features, Y)
  if iteration <= 1:
    plot(axs[0, iteration], np.array(list(y_test_sets[key].values())[0]), np.array(list(predictions[key].values())[0]), key)
  else:
    plot(axs[1, iteration - 2],  np.array(list(y_test_sets[key].values())[0]), np.array(list(predictions[key].values())[0]), key)
  iteration = iteration + 1
filename = "preprocessing_and_feature_Selection.eps"
plt.savefig(filename, format="eps")
files.download(filename)
# plt.show()
print("#################### MSE SCORE ##################")
for k, m in mse.items():
  print(m)
  print(np.mean(np.array(list(m.values()))))
print("#################### R2 SCORE ##################")
for k, r in r2.items():
  print(r)
  print(np.mean(np.array(list(r.values()))))

model = LinearRegression()
combination = {"Polynomial Feature & Filter Method": [PolynomialFeatures(), SelectKBest(score_func=f_regression, k="all")], 
               "Polynomial Feature & Wrapper Method ": [PolynomialFeatures(), RFE(model, n_features_to_select=12, step=2)], 
               "standardizing & Wrapper Method": [StandardScaler(), RFE(model, n_features_to_select=12, step=2)],
               "standardizing & Filter Method": [StandardScaler(), SelectKBest(score_func=f_regression, k="all")]}
fig, axs = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
iteration = 0 
mse = {}
r2 = {}
y_test_sets = {}
x_training_sets = {}
x_test_sets = {}
y_training_sets = {}
predictions = {}
for key, value in combination.items():
  X_scaled = preprocessor(value[0], imputed_X)
  features = feature_selection(value[1], X_scaled, Y)
  x_training_sets[key], x_test_sets[key], y_training_sets[key], y_test_sets[key], predictions[key], mse[key], r2[key] = model_cross_validation(model, features, Y)
  if iteration <= 1:
    plot(axs[0, iteration], np.array(list(y_test_sets[key].values())[0]), np.array(list(predictions[key].values())[0]), key)
  else:
    plot(axs[1, iteration - 2],  np.array(list(y_test_sets[key].values())[0]), np.array(list(predictions[key].values())[0]), key)
  iteration = iteration + 1
filename = "preprocessing_and_feature_Selection_2.eps"
plt.savefig(filename, format="eps")
files.download(filename)
# plt.show()

print("#################### MSE SCORE ##################")
for k, m in mse.items():
  print(m)
  print(np.mean(np.array(list(m.values()))))
print("#################### R2 SCORE ##################")
for k, r in r2.items():
  print(r)
  print(np.mean(np.array(list(r.values()))))

from sklearn.model_selection import learning_curve

cv = KFold(n_splits=10, random_state=0, shuffle=True)
X_scaled = preprocessor(PolynomialFeatures(degree=4), imputed_X)
features = feature_selection(SelectKBest(score_func=f_regression, k=20), X_scaled, Y)
train_sizes, train_scores, test_scores = learning_curve(LinearRegression(), features, Y, scoring="neg_mean_squared_error", cv=cv)
plt.plot(train_sizes, -test_scores.mean(1), 'o-', color="r", label="test score")
plt.plot(train_sizes, -train_scores.mean(1), 'o-', color="b", label="train score")
plt.xlabel("Train size")
plt.ylabel("Mean Squared Error")
plt.title('Learning curves')
plt.legend(loc="best")
filename = "preprocessing_and_feature_Selection_2.eps"
plt.savefig(filename, format="eps")
files.download(filename)
plt.show()


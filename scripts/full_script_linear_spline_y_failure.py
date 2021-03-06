python

###########
import numpy as np
import pandas as pd
# from pandas.plotting import scatter_matrix

from regression_tools.dftransformers import (
    ColumnSelector, 
    Identity,
    Intercept,
    FeatureUnion, 
    MapFeature,
    StandardScaler)
from scipy import stats
from plot_univariate import plot_one_univariate
from pandas.tools.plotting import scatter_matrix
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from basis_expansions.basis_expansions import (
    Polynomial, LinearSpline)
from regression_tools.plotting_tools import (
    plot_univariate_smooth,
    bootstrap_train,
    display_coef,
    plot_bootstrap_coefs,
    plot_partial_depenence,
    plot_partial_dependences,
    predicteds_vs_actuals)
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import warnings
warnings.filterwarnings('ignore')
from math import ceil
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score as r2
from r_squared_funcs import (
    r2_for_last_n_cycles,
    r2_generator_last_n_cycles)
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
from basis_expansions.basis_expansions import NaturalCubicSpline
import random

import os
os.getcwd()


np.random.seed(137)

#########################
###### Self made functions######
from r_squared_funcs import (
    r2_for_last_n_cycles,
    r2_generator_last_n_cycles)
from enginedatatransformer import transform_dataframes_add_ys
from plot_pred_vs_act import plot_many_predicteds_vs_actuals
# from export_linear_model import export_linear_model_to_txt
from engine_pipeline import fit_engine_pipeline

##################################


#################################################################################
###               import data 

##### training #############

df1 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_01_fd.csv', sep= " " )
df2 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_02_fd.csv', sep= ' ')
df3 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_03_fd.csv', sep= ' ')
df4 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_04_fd.csv', sep= ' ')

################   This will add a column for the y value which will be the number of cycles until the engine fails.




# It will be a countdown of the total cycles for training set  ######
##  set dataf to dataframe name  ####
#### add column to the end for logistic predictive model   ######
#### 

data_frames_to_transform = [df1, df2, df3 , df4]

def transform_dataframes_add_ys(data_list= [ ] , *args ):
# dataf = df1
    for df in data_list:
        max_cycles = []
        y_failure = []
        for num in range(1, max(df['unit']) + 1):
            #print(num)
            max_cycles.append(max(df['time_cycles'][df['unit']==num] ) )
            # max_cycles
        cycles_to_fail = []
        for total in max_cycles:
            for cycle in range(total, 0, -1):
                y_failure.append( (cycle/total) )
                cycles_to_fail.append(cycle)
        # print(cycles_to_fail)
        len(cycles_to_fail)
        len(df)
        len(y_failure)            
        df['cycles_to_fail'] = cycles_to_fail
        df['y_failure'] = y_failure

# df1.cycles_to_fail

###   Transform all four dataframes   #######

transform_dataframes_add_ys(data_frames_to_transform)
############################






# use column discribe out how remove the columns that do not change #### 

col = df1.columns
col = ['unit', 'time_cycles', 'op_set_1', 'op_set_2', 'op_set_3', 't2_Inlet',
       't24_lpc', 't30_hpc', 't50_lpt', 'p2_fip', 'p15_pby', 'p30_hpc',
       'nf_fan_speed', 'nc_core_speed', 'epr_p50_p2', 'ps_30_sta_press',
       'phi_fp_ps30', 'nrf_cor_fan_sp', 'nrc_core_sp', 'bpr_bypass_rat',
       'far_b_air_rat', 'htbleed_enthalpy', 'nf_dmd_dem_fan_sp', 'pcn_fr_dmd',
       'w31_hpt_cool_bl', 'w32_lpt_cool_bl', 'cycles_to_fail']

#####  End of data import file #######


############  Start of data analysis   #############






## this will plot all columns to check for variation within the feature data
for name in col:
    df1.plot.scatter( 'cycles_to_fail', name, alpha = .3)
    plt.show()
#

######     Several features appear to not be predictive  ######

#   limit the features that are in the model scatter plot #####
small_features_list = ['time_cycles', 't24_lpc', 't30_hpc', 't50_lpt', 
    'p30_hpc', 'nf_fan_speed', 'nc_core_speed', 'ps_30_sta_press', 
    'phi_fp_ps30', 'nrf_cor_fan_sp', 'nrc_core_sp', 'bpr_bypass_rat', 
    'htbleed_enthalpy', 'w31_hpt_cool_bl', 'w32_lpt_cool_bl' ]


#####     Scatter matrix using time cycles            ##### 

scatter_matrix = pd.scatter_matrix(df1[small_features_list], alpha=0.2, figsize=(20, 20), diagonal='kde')

for ax in scatter_matrix.ravel():
    ax.set_xlabel(ax.get_xlabel(), fontsize = 6, rotation = 90)
    ax.set_ylabel(ax.get_ylabel(), fontsize = 6, rotation = 0)
plt.show()



#####         Scatter matrix using cycles to fail        #####
small_features_list = ['cycles_to_fail' , 't24_lpc', 't30_hpc', 't50_lpt', 
    'p30_hpc', 'nf_fan_speed', 'nc_core_speed', 'ps_30_sta_press', 
    'phi_fp_ps30', 'nrf_cor_fan_sp', 'nrc_core_sp', 'bpr_bypass_rat', 
    'htbleed_enthalpy', 'w31_hpt_cool_bl', 'w32_lpt_cool_bl' ]


scatter_matrix = pd.scatter_matrix(df1[small_features_list], alpha=0.2, figsize=(20, 20), diagonal='kde')

for ax in scatter_matrix.ravel():
    ax.set_xlabel(ax.get_xlabel(), fontsize = 6, rotation = 90)
    ax.set_ylabel(ax.get_ylabel(), fontsize = 6, rotation = 0)
plt.show()


#####                                                       ##### 


#    view the description of each column 
col = df1.columns
# col = train_features
for c in col:
  print (df1[c].describe() ) 


### This will print only the standard deviation for each column
col = df1.columns
for c in col:
  print (df1[c].describe()[2] ) 


### This will remove features based the standard deviation for each column
train_features = []
limit = .01
col = df1.columns
for c in col:
  if (df1[c].describe()[2] ) >= .01:
      train_features.append(c)
train_features

####   Created the short list of features to train to ######




#### List of features to train the model to  #######    ### remove 'unit'
train_features = ['time_cycles', 't24_lpc', 't30_hpc', 't50_lpt', 
    'p30_hpc', 'nf_fan_speed', 'nc_core_speed', 'ps_30_sta_press', 
    'phi_fp_ps30', 'nrf_cor_fan_sp', 'nrc_core_sp', 'bpr_bypass_rat', 
    'htbleed_enthalpy', 'w31_hpt_cool_bl', 'w32_lpt_cool_bl']

######    the training features has the columns to train to ### 
#######    the columns time_cycles and time_to_fail have been removed ##


####  The time cycles column may be used as an alternate y value to train to
# y_cycles_to_fail =  df1.cycles_to_fail
# y_time_cycles = df1.time_cycles
####                                                                  #### 

##   view plots for the features that are to be used in df1   ######
for name in train_features:
    df1.plot.scatter( 'cycles_to_fail', name, alpha = .3)
    plt.show()



#### remove features that do not change at all for this dataset
for c in col:
    df1[c].describe()

#####   adjust the data frame to choose 20 % of the engines by unmber and 
#####   train to a sample of 80% by number and 20% saved for test data.
# engines = list(np.random.choice(range(1,101), 20, replace= False))
test_engines = [4, 18, 19, 21, 28, 33, 42, 45, 46, 50, 61, 73, 74, 78, 82, 83, 84, 86, 92, 94]

train_engines = []
for num in range(1,101):
    if num not in test_engines:
        train_engines.append(num)
#        #


train_engines = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 22, 23, 24, 25, 26, 
    27, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 47, 48, 49, 51, 52, 53, 54, 55, 
    56, 57, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 75, 76, 77, 79, 80, 81, 85, 
    87, 88, 89, 90, 91, 93, 95, 96, 97, 98, 99, 100]

train_engines
test_engines
# for eng in train_engines:
#     if eng in test_engines:
#         print(True)
#     else:
#         print(False)


test_idx = df1['unit'].apply(lambda x: x in test_engines)
train_idx = df1['unit'].apply(lambda x: x in train_engines)
test_idx
train_idx


type(test_idx)
type(train_idx)
test_list = list(test_idx)
train_list = list(train_idx)



df_new_test = df1.iloc[test_list].copy()
df_new_train = df1.iloc[train_list].copy()
df_new_test.shape
df_new_train.shape



###### this will make a list of the max number of cycles for the training set of engines
##     

train_eng_max_cycles = []
for e in train_engines:
    train_eng_max_cycles.append(max(df1['time_cycles'][df1['unit']==e]))

train_eng_max_cycles
stats.describe(train_eng_max_cycles)
#  DescribeResult(nobs=80, minmax=(128, 362), 
#  mean=203.4375, variance=2055.6922468354433, 
#  skewness=1.063155863408599, kurtosis=1.5047506637832253)


#######  the max number of cycles for the test set of engines  ########
test_eng_max_cycles = []
for e in test_engines:
    test_eng_max_cycles.append(max(df1['time_cycles'][df1['unit']==e]))

test_eng_max_cycles
    

####   Fit pipeline from engine pipeline script ##################
feature_pipline = fit_engine_pipeline()

##################################################################


###########             Train to Cycles to Fail                ######################
###########@@@@@@@@    Toggle commments to change target   @@@@@########################

## This will make the train test split for this model ####
ytrain = df_new_train['cycles_to_fail']
X_features = df_new_train[train_features]
ytest = df_new_test['cycles_to_fail']
X_test_feaures = df_new_test[train_features]




# ###########                Train to y_failure (0-1)                ######################
# ## This will make the train test split for this model ####
# ytrain = df_new_train['y_failure']
# X_features = df_new_train[train_features]
# ytest = df_new_test['y_failure']
# X_test_features = df_new_test[train_features]




### Hold for future use  #######
# Xtrain, Xtest, ytrain, ytest = train_test_split(X_features, y, test_size = .2, random_state=137)
# Xtrain.shape
# Xtest.shape
# ytrain.shape
# ytest.shape



# L_y_predicted
# ############ 
# ######   Check the coefficients from the model 
# L_model.coef_
# print(list(zip(L_model.coef_, X_features)))


##### Model from old train/test split
# [(0.2098130774662108, 'unit'), (-7.173759447981604, 't24_lpc'), 
# (-0.42305195925658207, 't30_hpc'), (-0.7441639445488603, 't50_lpt'), 
# (7.61219378587503, 'p30_hpc'), (-12.147203483784747, 'nf_fan_speed'), 
# (-0.3844533247091928, 'nc_core_speed'), (-34.641657728829905, 'ps_30_sta_press'),
#  (11.105368284298036, 'phi_fp_ps30'), (-4.474447225499914, 'nrf_cor_fan_sp'), 
#  (-0.20542361139388693, 'nrc_core_sp'), (-126.19522472669553, 'bpr_bypass_rat'), 
#  (-1.9171623154921535, 'htbleed_enthalpy'), (22.12461560626438, 'w31_hpt_cool_bl'),
#  (42.47336192785645, 'w32_lpt_cool_bl')]
#
#  Model from new 80 engine 20 test train/test split
# #print(list(zip(L_model.coef_, X_features)))
# [(-7.9993983227825884, 't24_lpc'), (-0.40343998913641343, 't30_hpc'), 
# (-0.858069141166363, 't50_lpt'), (7.118138412200282, 'p30_hpc'), 
# (-26.53526438485433, 'nf_fan_speed'), (-0.28820253265246504, 'nc_core_speed'), 
# (-38.13957596837547, 'ps_30_sta_press'), (9.984072018801038, 'phi_fp_ps30'), 
# (-21.747334830714323, 'nrf_cor_fan_sp'), (-0.28742611769798204, 'nrc_core_sp'), 
# (-101.5927346354093, 'bpr_bypass_rat'), (-1.6264557877934611, 'htbleed_enthalpy'),
#  (19.17595070701376, 'w31_hpt_cool_bl'), (42.100133123738566, 'w32_lpt_cool_bl')]
#
#
#
#

# #####   Plot the data from the first model and evaluate the residuals

plt.scatter(L_y_predicted, ytrain, alpha = 0.1)
plt.xlabel('y hat from training set')
plt.ylabel( 'y values from training set')
plt.show()
###






### Second plot that will show the difference from actuals vs pred
fig = plt.figure()
fig, ax = plt.subplots(figsize=(15,15) )
ax.plot(list(range(1, len(L_y_predicted) + 1)) , L_y_predicted, '.r', label='predicted')
ax.plot(list(range(1, len(ytrain) + 1 )) , ytrain, '.b' , label='actual')
plt.xlabel('Index of Value')
plt.ylabel( 'Cycles to Fail')
ax.legend()
plt.show()

## First score from basic linear regression model   ####
base_score = r2(ytrain, L_y_predicted)
base_score
linear_model_80_engine = base_score
linear_model_80_engine



#####  score of model no tuning trained to time cycles to go
##  0.5302416225409862

#### score of model with no tuning trained to cycles remaining 
##  0.5302416225409862
##
### There is no difference between the two which makes sense.

####  Linear model 80 engine split 
# linear_model_80_engine
# 0.6004573742141459



# Begin spline analysis of each significant feature


###### plot the full range of each engine against the cycles to fail
fig, axs = plt.subplots(3, 5, figsize=(14, 8))
univariate_plot_names = df1[train_features]                                     #columns[:-1]

for name, ax in zip(univariate_plot_names, axs.flatten()):
    plot_univariate_smooth(ax,
                           df1['cycles_to_fail'],
                           df1[name].values.reshape(-1, 1),
                           bootstrap=100)
    ax.set_title(name, fontsize=7)

plt.show()



#### Plot each feature individually. 
###    (ax, df, y, var_name,
for col in train_features:
    fig, ax = plt.subplots(figsize=(12, 3))
    plot_one_univariate(ax, df1, 'cycles_to_fail', col )
    ax.set_title("Evaluation of: " + str(col))
    plt.xlabel(col)
    plt.ylabel( 'Cycles to Fail')
    plt.show()

### Begining of the linear spline transformation parameters    #######
linear_spline_transformer = LinearSpline(knots=[10, 35, 50, 80, 130, 150, 200, 250, 300])

linear_spline_transformer.transform(df1['cycles_to_fail']).head()

cement_selector = ColumnSelector(name='cycles_to_fail')
cement_column = cement_selector.transform('cycles_to_fail')
linear_spline_transformer.transform(cement_column).head()



train_features

train_features = [
    'time_cycles', 
't24_lpc', 
't30_hpc', 
't50_lpt', 
'p30_hpc', 
'nf_fan_speed', 
'nc_core_speed', 
'ps_30_sta_press', 
'phi_fp_ps30', 
'nrf_cor_fan_sp', 
'nrc_core_sp', 
'bpr_bypass_rat', 
'htbleed_enthalpy', 
'w31_hpt_cool_bl', 
'w32_lpt_cool_bl']




#### Build out the new dataframes with each knot   
#### Must use the 80 engine traing set !!!!!!!   

# feature_pipeline.fit(df_new_train)
# features = feature_pipeline.transform(df_new_test)



###    Fit model to the pipeline   #######

ytest
features

model = LinearRegression(fit_intercept=True)
model.fit(df_new_train[train_features], ytrain)   #np.log(ytrain) # <---- note: the np.log transformation




len(ytest)
len(features)
len(y_hat)

#### View the coefficients
display_coef(model, features.columns)

plt.plot(range(0,len(model.coef_)), model.coef_)
plt.show()

ytest
y_hat

####  Make predictions against the training set
y_hat = model.predict(df_new_test[train_features])
y_hat = y_hat   # np.exp(y_hat)                ## <----- note: the exp to transform back



'''
polynomeal analysis
'''


import numpy as np
from scipy.optimize import curve_fit



from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


poly = PolynomialFeatures(degree=2)
X_ = poly.fit_transform(df_new_train[train_features])
predict_ = poly.fit_transform(df_new_train[train_features])


predict_ = poly.fit_transform(df_new_test[train_features])


clf = linear_model.LinearRegression()
clf.fit(X_, ytrain)


y_hat = clf.predict(predict_)
len(y_hat)
len(ytest)


'''
the above is the alternate quadratic test
'''



####  Plot predictions from data against the actual values ########
x = list(range(0,400))
y = x
plt.scatter(y_hat, ytest, alpha = 0.1, color='blue')
plt.plot(x, y, '-r', label='y=2x+1')
plt.title('Polynomial Regression: Cycles to Fail')
plt.xlabel('$\hat {y}$ from test set')
plt.ylabel( '${y}$ from test set')
plt.ylim(0, 360)
plt.xlim(370, -0.1)
plt.show()
###


clf.coef_
predict_.shape



#### Second plot that will show the difference from actuals vs pred for the pipeline model   ###### 

fig, ax = plt.subplots(figsize=(15,15) )
ax.plot(list(range(1, len(y_hat) + 1)) , y_hat, '.r', label='predicted')
ax.plot(list(range(1, len(ytest) + 1 )) , ytest, '.b' , label='actual')
plt.xlabel('Index of Value')
plt.ylabel( 'Cycles to Fail')
ax.legend()
plt.show()

##########################################


    # #print(num)
    # max_cycles.append(max(df['time_cycles'][df['unit']==num] ) )




    # ax.set_title('Plot number {}'.format(i))


##### this is the plot of all 80 engines on a single chart

fig, axs = plt.subplots(8,10, figsize=(10,4))
ax.set_title("Spline Model of 80 Training Engines")
start_idx = 0
for idx, ax in enumerate(axs.flatten()):
# for idx, e in enumerate(train_engines):
    end_idx = start_idx + train_eng_max_cycles[idx]
    print(start_idx, end_idx, train_eng_max_cycles[idx], end_idx-start_idx)
    # fig, ax = plt.subplots(figsize=(15,15) )
    # ax.plot(y_hat[start_idx : end_idx], list(range(train_eng_max_cycles[idx], 0, -1)), '.r', label='predicted')
    # ax.plot(ytrain[start_idx : end_idx] , list(range(train_eng_max_cycles[idx], 0, -1)) , '-b' , label='actual')
    ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
    ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , ytrain[start_idx : end_idx] , '-b' , label='actual')
    ax.set_title("Engine # " + str(train_engines[idx]), size=6)
    # plt.tick_params(axis='both', which='major', labelsize=8)
    # plt.tick_params(axis='both', which='minor', labelsize=6)
    # plt.xticks(fontsize=8)      #, rotation=90)
    # plt.title('Engine #: ' + str(train_engines[idx]))
    # plt.xlabel('Index')
    # plt.ylabel( 'Cycles to Fail')
    # ax.legend()
    ax.set_ylim(0, 1.1)
    ax.set_xlim(350 ,  0)
    ax.xaxis.set_tick_params(labelsize=5)
    ax.yaxis.set_tick_params(labelsize=5)
    start_idx = end_idx 
        # plt.show()


# plt.tight_layout()
plt.show()



##### Test Set of data    ###############################
##### this is the plot of all 20 test engines on a single chart

fig, axs = plt.subplots(4, 5 , figsize=(10,4))
ax.set_title("Spline Model of 20 Test Engines")
start_idx = 0
for idx, ax in enumerate(axs.flatten()):
# for idx, e in enumerate(train_engines):
    end_idx = start_idx + test_eng_max_cycles[idx]
    print(start_idx, end_idx, test_eng_max_cycles[idx], end_idx-start_idx)
    # fig, ax = plt.subplots(figsize=(15,15) )
    # ax.plot(y_hat[start_idx : end_idx], list(range(train_eng_max_cycles[idx], 0, -1)), '.r', label='predicted')
    # ax.plot(ytrain[start_idx : end_idx] , list(range(train_eng_max_cycles[idx], 0, -1)) , '-b' , label='actual')
    ax.plot(list(range(test_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
    ax.plot(list(range(test_eng_max_cycles[idx], 0, -1)) , ytest[start_idx : end_idx] , '-b' , label='actual')
    ax.set_title("Engine # " + str(test_engines[idx]), size=6)
    # plt.tick_params(axis='both', which='major', labelsize=8)
    # plt.tick_params(axis='both', which='minor', labelsize=6)
    # plt.xticks(fontsize=8)      #, rotation=90)
    # plt.title('Engine #: ' + str(train_engines[idx]))
    # plt.xlabel('Index')
    # plt.ylabel( 'Cycles to Fail')
    # ax.legend()
    ax.set_ylim(0, 1.1)
    ax.set_xlim(350 ,  0)
    ax.xaxis.set_tick_params(labelsize=5)
    ax.yaxis.set_tick_params(labelsize=5)
    start_idx = end_idx 
        # plt.show()


# plt.tight_layout()
plt.show()




#### Third plot that will show the difference from actuals vs pred for
# #   the pipeline model for each engine one by one  ###### 
start_idx = 0
for idx, e in enumerate(train_engines):
    end_idx = start_idx + train_eng_max_cycles[idx]
    print(start_idx, end_idx, train_eng_max_cycles[idx], end_idx-start_idx)
    fig, ax = plt.subplots(figsize=(15,15) )
    ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
    ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , ytrain[start_idx : end_idx] , '.b' , label='actual')
    plt.title('Engine #: ' + str(e))
    plt.xlabel('Index')
    plt.ylabel( 'Cycles to Fail')
    # plt.axvline(stats.describe(train_eng_max_cycles)[1][0], color='r', label='min' )
    # plt.axvline(stats.describe(train_eng_max_cycles)[2], color='g' , label='avg' )
    # plt.axvline(stats.describe(train_eng_max_cycles)[1][1], color='b' , label='max' )
    plt.xlim(350,0)
    plt.ylim(0 , 1.1)
    ax.legend()
    start_idx = end_idx 
    plt.show()






### This will function will create the actual estimations vs predicted values
def plot_many_predicteds_vs_actuals(var_names, y_hat, n_bins=50):
    fig, axs = plt.subplots(len(var_names), figsize=(12, 3*len(var_names)))
    for ax, name in zip(axs, var_names):
        x = df_new_train[name]
        predicteds_vs_actuals(ax, x, df_new_train["cycles_to_fail"], y_hat, n_bins=n_bins)
        # ax.set_title("{} Predicteds vs. Actuals".format(name))
    return fig, axs



### This will plot the final estimations vs the actual data
train_features
# y_hat = model.predict(features.values)
fig, axs = plot_many_predicteds_vs_actuals(train_features, y_hat)
# fig.tight_layout()df1
plt.show()





##########################    Scoreing Section   ###############



#### Score of the first model against the training set.  
## First score from basic linear regression model   ####
log_knot_model = r2(ytrain, y_hat)
log_knot_model
# time_knot_model
# first_knot_model
# 0.64194677350961
# 0.7396060171044228
# log_knot_model
# 0.7272227017732488
#log_knot_model
# 0.7273228097635444
# R- Squared for polynomeal regression of test data is:
#   'The r-squared for the last 500 cycles is: 0.6554345266551393'



##### R-squared for the last n number of observations  #####
#
ytest
y_hat

r2_for_last_n_cycles(y_hat , ytest, last_n=500)
r2_for_last_n_cycles(y_hat , ytrain, last_n=100)
r2_for_last_n_cycles(y_hat , ytrain, last_n=75)
r2_for_last_n_cycles(y_hat , ytrain, last_n=50)
r2_for_last_n_cycles(y_hat , ytrain, last_n=25)
r2_for_last_n_cycles(y_hat , ytrain, last_n=15)
r2_for_last_n_cycles(y_hat , ytrain, last_n=10)
r2_for_last_n_cycles(y_hat , ytrain, last_n=5)

###################   Make a list of r squared values for plotting   ##########

r2_values = r2_generator_last_n_cycles(y_hat , ytrain, 200)

########  Plot the r2 values as the number of cycles remaining approaches the end #######

##### plot the full against the cycles to fail
fig, ax = plt.subplots(1, 1, figsize=(13, 13))
ax.scatter(range(len(r2_values)+1, 1, -1) , r2_values)
plt.ylim(-2, 1)
plt.title('R Squared')
plt.xlabel('Cycles to Fail')
plt.ylabel( 'R Squared Value')
plt.legend()
plt.show()

### Plot of r-squared as the number of observations approaches 1  #########










python

#######
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
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression
)
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
from sklearn.metrics import log_loss, make_scorer
from r_squared_funcs import (
    r2_for_last_n_cycles,
    r2_generator_last_n_cycles)
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
from basis_expansions.basis_expansions import NaturalCubicSpline
import random
from scipy.special import comb
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.ensemble import AdaBoostRegressor, AdaBoostClassifier
from sklearn.datasets import load_boston
from sklearn.model_selection import GridSearchCV



#########################
###### Self made/borrowed functions######
from r_squared_funcs import (
    r2_for_last_n_cycles,
    r2_generator_last_n_cycles)
from enginedatatransformer import transform_dataframes_add_ys
from plot_pred_vs_act import plot_many_predicteds_vs_actuals
from logistic_plots import (
    calculate_threshold_values,
    plot_roc,
    plot_precision_recall,
    decision_boundary_x2,
    plot_decision_boundary
)

##################################

import os
os.getcwd()

np.random.seed(137)

#################################################################################
###               import data 

##### training #############

df1 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_01_fd.csv', sep= " " )
df2 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_02_fd.csv', sep= ' ')
df3 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_03_fd.csv', sep= ' ')
df4 = pd.read_csv('/home/superstinky/Seattle_g89/final_project_data/flight_engineer/enginedata/train_04_fd.csv', sep= ' ')

################   This will add a column for the y value which will be the number of cycles until the engine fails.

#######      List of vaiables and features for model    #######
data_frames_to_transform = [df1, df2, df3 , df4]
transform_dataframes_add_ys(data_frames_to_transform)
# training_set = True
make_plots = False
cols_to_use = small_features_list
df = df1          #<----- #This is the raw dataframe to use for the model
target_variable = 'lower_third_life'  #   or 'y_failure'
n = 75   # <---- set the number of initial cycles to check


##########################################################
# It will be a countdown of the total cycles for training set  ######
##  set dataf to dataframe name  ####
#### add column to the end for logistic predictive model   ######
#### 


#####  End of data import file #######


############  Start of data analysis   #############


#####                                                       ##### 
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
        'w32_lpt_cool_bl' 
]



######    the training features has the columns to train to ### 
#######    the columns time_cycles and time_to_fail have been removed ##


#####   adjust the data frame to choose 20 % of the engines by unmber and 
#####   train to a sample of 80% by number and 20% saved for test data.


# test_engines = list(np.random.choice(range(1,101), 20, replace= False))
test_engines = [4, 18, 19, 21, 28, 33, 42, 45, 46, 50, 61, 73, 74, 78, 82, 83,
 84, 86, 92, 94]


train_engines = []
for num in range(1,101):
    if num not in test_engines:
        train_engines.append(num)


# train_engines = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 22, 23, 24, 25, 26, 
#     27, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 47, 48, 49, 51, 52, 53, 54, 55, 
#     56, 57, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 75, 76, 77, 79, 80, 81, 85, 
#     87, 88, 89, 90, 91, 93, 95, 96, 97, 98, 99, 100]

############  Find index numbers for the training and test sets    ###########   
test_idx = df['unit'].apply(lambda x: x in test_engines)
train_idx = df['unit'].apply(lambda x: x in train_engines)
# test_idx
# train_idx

test_list = list(test_idx)
train_list = list(train_idx)


#### Create new data frames using seperate test and training engines   ##########
df_new_test = df.iloc[test_list].copy()
df_new_train = df.iloc[train_list].copy()

###### this will make a list of the max number of cycles for the training set of engines

train_eng_max_cycles = []
for e in train_engines:
    train_eng_max_cycles.append(max(df['time_cycles'][df['unit']==e]))

# train_eng_max_cycles
# stats.describe(train_eng_max_cycles)
#  DescribeResult(nobs=80, minmax=(128, 362), 
#  mean=203.4375, variance=2055.6922468354433, 
#  skewness=1.063155863408599, kurtosis=1.5047506637832253)



#######  the max number of cycles for the test set of engines  ########
test_eng_max_cycles = []
for e in test_engines:
    test_eng_max_cycles.append(max(df['time_cycles'][df['unit']==e]))


# # test_eng_max_cycles_long = []
# # for e in test_engines:
# #     test_eng_max_cycles_long.append(max(df[df['upper_third_life']][df['unit']==e]))


# test_eng_max_cycles
# stats.describe(test_eng_max_cycles)
# # DescribeResult(nobs=20, minmax=(158, 341), 
# # mean=217.8, variance=2469.326315789474, 
# # skewness=0.8514362921848939, kurtosis=-0.005870492535239968)





########## This will make the train test split for this model ####

# this is the training set split  #######
Xtrain = df_new_train[train_features]
ytrain = df_new_train[target_variable]


### This is the test set split #######
Xtest = df_new_test[train_features]
ytest = df_new_test[target_variable]


#########     Limit the size of the dataframe to first n observations   ###################


def first_n_observations (  df , n):
    num_observations = range(1, n +1 )
    train_idx = df['time_cycles'].apply(lambda x: x in num_observations)
    train_list = list(train_idx)
    return df.iloc[train_list].copy()


######################################################################################
###### Returns the new data frame with required number of cycles for catagorization  ########
#########    Convert the data set and variables to Xtrain /Xtest / ytrain / ytest     #####


df_new_train = first_n_observations(df_new_train,n)
# y = df[target_variable]
Xtrain = df_new_train[train_features]
ytrain = df_new_train[target_variable]



df_new_test = first_n_observations(df_new_test,n)
# y = df[target_variable]
Xtest = df_new_test[train_features]
ytest = df_new_test[target_variable]




##################################################################################################


               ###########             Train               ######################
###########@@@@@@@@    Toggle commments to change target   @@@@@########################


######################################

cols = ['time_cycles', 't2_Inlet',
       't24_lpc', 't30_hpc', 't50_lpt', 'p2_fip', 'p15_pby', 'p30_hpc',
       'nf_fan_speed', 'nc_core_speed', 'epr_p50_p2', 'ps_30_sta_press',
       'phi_fp_ps30', 'nrf_cor_fan_sp', 'nrc_core_sp', 'bpr_bypass_rat',
       'far_b_air_rat', 'htbleed_enthalpy', 'nf_dmd_dem_fan_sp', 'pcn_fr_dmd',
       'w31_hpt_cool_bl', 'w32_lpt_cool_bl']


#####        fit model and use to predict probabilities        #####

# Parameter Search                                     
#  
#
if training_set == True:                                                    
    for num in range(1,5):
        for dep in range(8,13, 4): 
            rf = RandomForestClassifier(n_estimators=2000, 
            max_features='auto', 
            random_state=137 , 
            n_jobs=-1,
            max_depth= dep,
            min_samples_leaf = num,
            verbose= 0)
            rf.fit(Xtrain, ytrain)
            y_hat = rf.predict(Xtest)
            print(f"minimum leaf samples = {num}")
            print(f"max tree depth = {dep}")
            print(f"log loss = {log_loss(ytest, rf.predict_proba(Xtest)[:, 1])}")
            print(f"accuracy = {rf.score(Xtest, ytest)}")


rf.predict_proba(Xtest) #[:, 1]

########################################################################################
########################################################################################
########################################################################################
########################################################################################
                ##### Try Gradiant Boost  ########




gdbr = GradientBoostingRegressor(learning_rate=0.01,
                                  loss='ls',
                                  n_estimators=1000,
                                  random_state=1,
                                max_depth =3 )


gdbr10 = GradientBoostingRegressor(learning_rate=.01,
                                  loss='ls',
                                  n_estimators= 1000,
                                  random_state=1,
                                    max_depth = 10)

gdbr100= GradientBoostingRegressor(learning_rate=.01,
                                  loss='ls',
                                  n_estimators= 1000,
                                  random_state=1,
                                    max_depth = 100)


gdbr.fit(Xtrain, ytrain)
gdbr10.fit(Xtrain, ytrain)
gdbr100.fit(Xtrain, ytrain)



scores_test = []
scores_test_10 = []
scores_test_100 = []


for i in gdbr.staged_predict(Xtest):
    scores_test.append(np.mean((sum( (ytest - i)**2))))
            
for i in gdbr10.staged_predict(Xtest):
    scores_test_10.append(np.mean((sum( (ytest - i)**2))))
     
for i in gdbr100.staged_predict(Xtest):
    scores_test_100.append(np.mean((sum( (ytest - i)**2))))



fig, axs = plt.subplots(1, 1, figsize=(15, 12))
plt.plot(range(len(scores_ada)), scores_ada, color = 'purple')
plt.plot(range(len(scores_test_10)), scores_test_10, color = 'red')
plt.plot(range(len(scores_test_100)), scores_test_100, color = 'b')
plt.plot(range(len(scores_test)), scores_test, color = 'green')
# axs.set_ylim(0,800)
plt.show()







##### Based on the number of cycles in the begining      ##########
        ################# if prob don't work     #############

prob_y = []
total = 0
for idx, est in enumerate(y_hat.tolist()):
    # print(est)
    # print(type(est))
    total += est[0]
    if (idx+1) % n == 0 and idx!= 0:
        prob_y.append( (float(total) / n) )
        print(n, idx, est)
        total = 0
    else:
        continue

    # print(total)
    

prob_y
len(prob_y)

# y_hat = prob_y


y_act = []
total = 0
for idx, est in enumerate(y):
    # print(est)
    # print(type(est))
    # total += est
    if (idx+1) % n == 0 and idx != 0:
        y_act.append( est)
        print(n, idx, est)
        total = 0
    # if (idx+1) == len(y):
    #     y_act.append( total / n )
    #     print(n, idx, est)
    #     total = 0
    else:
        continue

    # print(total)
    

y_act
len(y_act)

### Log Loss func
log_loss(np.array(y_act), np.array(prob_y) ) 
### Log Loss func
# log_loss(np.array(y_act), np.array(prob_y) )
# 0.8683509089053743
# # n = 25 log loss
# log_loss(np.array(y_act), np.array(prob_y) ) 
# 0.8789643598592655
# ### n = 75 Log Loss func
# ... log_loss(np.array(y_act), np.array(prob_y) ) 
# 0.7886718412288982
### Log Loss func
# ... log_loss(np.array(y_act), np.array(prob_y) ) 
# 0.9156950272617351


fig, (ax0, ax1, ax3) = plt.subplots(1,3, figsize=(18,6))
dfp = calculate_threshold_values(model.predict_proba(df[cols])[:,1], y)
plot_roc(ax0, dfp)
plot_precision_recall(ax1, dfp)
plot_decision_boundary(df[cols].values, y, model, ax3)   # ax3
plt.show()


####  Plot predictions from data against the actual values ########
if make_plots==True:
    plt.scatter(range(0,len(y_act)), y_act, alpha = 0.8, color='blue')
    plt.plot(range(0,len(prob_y)), prob_y, '-r', label='Estimated Prob')
    plt.title('Above / Below Mean Probabilities')
    plt.xlabel('$\hat {p}$ from training set')
    plt.ylabel( 'Actuals from training set')
    plt.ylim(-0.1,1.1)
    plt.show()
###
plt.scatter(range(0,len(y_act)), y_act, alpha = 0.8, color='blue')
plt.plot(range(0,len(prob_y)), prob_y, '-r', label='Estimated Prob')
plt.title('Above / Below Mean Probabilities First: ' + str(n) + ' Observations')
plt.xlabel('$\hat {p}$ from training set')
plt.ylabel( 'Actuals from training set')
plt.ylim(-0.1,1.1)
plt.vlines( list(range(1,len(y_act)+1)), 0, 1 ) 
plt.show()




####################################################################





####  Plot predictions from data against the actual values ########
if make_plots==True:
    plt.scatter(y_hat, y, alpha = 0.1, color='blue')
    #plt.plot(x, y, '-r', label='y=2x+1')
    plt.title('Pipline Predictions with log(y)')
    plt.xlabel('$\hat {y}$ from training set')
    plt.ylabel( 'y actuals from training set')
    plt.ylim(0,1)
    plt.show()
###



#### Second plot that will show the difference from actuals vs pred for the pipeline model   ###### 
if make_plots==True:
    fig, ax = plt.subplots(figsize=(15,15) )
    ax.plot(list(range(1, len(y_hat) + 1)) , y_hat, '.r', label='predicted')
    ax.plot(list(range(1, len(y) + 1 )) , y, '.b' , label='actual')
    plt.xlabel('Index of Value')
    plt.ylabel( 'Cycles to Fail')
    ax.legend()
    plt.show()

##########################################



##### this is the plot of all 80 engines on a single chart  #####
#####        Training Set Data Plots        ######### 

if make_plots==True and training_set==True:
    fig, axs = plt.subplots(8,10, figsize=(10,4))
    ax.set_title("Spline Model of 80 Training Engines")
    start_idx = 0
    for idx, ax in enumerate(axs.flatten()):
    # for idx, e in enumerate(train_engines):
        end_idx = start_idx + train_eng_max_cycles[idx]
        print(start_idx, end_idx, train_eng_max_cycles[idx], end_idx-start_idx)
        # fig, ax = plt.subplots(figsize=(15,15) )
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y[start_idx : end_idx] , '-b' , label='actual')
        ax.set_title("Engine # " + str(train_engines[idx]), size=6)
        # plt.tick_params(axis='both', which='major', labelsize=8)
        # plt.tick_params(axis='both', which='minor', labelsize=6)
        # plt.xticks(fontsize=8)      #, rotation=90)
        # plt.title('Engine #: ' + str(train_engines[idx]))
        # plt.xlabel('Index')
        # plt.ylabel( 'Cycles to Fail')
        # ax.legend()
        ax.xaxis.set_tick_params(labelsize=5)
        ax.yaxis.set_tick_params(labelsize=5)
        ax.set_ylim([0,350])
        ax.set_xlim([350, 0])
        start_idx = end_idx 
    plt.show()

              ################################


##### Test Set of data    ###############################
##### this is the plot of all 20 test engines on a single chart

if make_plots==True and training_set==False:
    fig, axs = plt.subplots(4, 5 , figsize=(10,4))
    ax.set_title("Spline Model of 20 Test Engines")
    start_idx = 0
    for idx, ax in enumerate(axs.flatten()):
    # for idx, e in enumerate(train_engines):
        end_idx = start_idx + test_eng_max_cycles[idx]
        print(start_idx, end_idx, test_eng_max_cycles[idx], end_idx-start_idx)
        # fig, ax = plt.subplots(figsize=(15,15) )
        # ax.plot(y_hat[start_idx : end_idx], list(range(train_eng_max_cycles[idx], 0, -1)), '.r', label='predicted')
        # ax.plot(y[start_idx : end_idx] , list(range(train_eng_max_cycles[idx], 0, -1)) , '-b' , label='actual')
        ax.plot(list(range(test_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
        ax.plot(list(range(test_eng_max_cycles[idx], 0, -1)) , y[start_idx : end_idx] , '-b' , label='actual')
        ax.set_title("Engine # " + str(test_engines[idx]), size=6)
        # plt.tick_params(axis='both', which='major', labelsize=8)
        # plt.tick_params(axis='both', which='minor', labelsize=6)
        # plt.xticks(fontsize=8)      #, rotation=90)
        # plt.title('Engine #: ' + str(train_engines[idx]))
        # plt.xlabel('Index')
        # plt.ylabel( 'Cycles to Fail')
        # ax.legend()
        ax.set_ylim( 0  , 350 )
        ax.set_xlim(350 ,  0)
        ax.xaxis.set_tick_params(labelsize=5)
        ax.yaxis.set_tick_params(labelsize=5)
        start_idx = end_idx 
    plt.show()




test_eng_max_cycles
train_eng_max_cycles




np.mean(train_eng_max_cycles)
np.mean(test_eng_max_cycles)


#### Third plot that will show the difference from actuals vs pred for
# #   the pipeline model for each engine one by one  ###### 
if make_plots==True and training_set==True:
    start_idx = 0
    for idx, e in enumerate(train_engines):
        end_idx = start_idx + train_eng_max_cycles[idx]
        print(start_idx, end_idx, train_eng_max_cycles[idx], end_idx-start_idx)
        fig, ax = plt.subplots(figsize=(15,15) )
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y[start_idx : end_idx] , '.b' , label='actual')
        plt.title('Engine #: ' + str(e))
        plt.xlabel('Cycles to Fail')
        plt.ylabel( 'Cycles Used')
        plt.axvline(stats.describe(train_eng_max_cycles)[1][0], color='r', label='min' )
        plt.axvline(stats.describe(train_eng_max_cycles)[2], color='g' , label='avg' )
        plt.axvline(stats.describe(train_eng_max_cycles)[1][1], color='b' , label='max' )
        
        ax.legend()
        start_idx = end_idx 
        plt.show()


# #   the pipeline model for each engine one by one  ###### 
if make_plots==True and training_set==False:
    start_idx = 0
    for idx, e in enumerate(train_engines):
        end_idx = start_idx + train_eng_max_cycles[idx]
        print(start_idx, end_idx, train_eng_max_cycles[idx], end_idx-start_idx)
        fig, ax = plt.subplots(figsize=(15,15) )
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y_hat[start_idx : end_idx], '.r', label='predicted')
        ax.plot(list(range(train_eng_max_cycles[idx], 0, -1)) , y[start_idx : end_idx] , '.b' , label='actual')
        plt.title('Engine #: ' + str(e))
        plt.xlabel('Cycles to Fail')
        plt.ylabel( 'Cycles Used')
        plt.axvline(stats.describe(train_eng_max_cycles)[1][0], color='r', label='min' )
        plt.axvline(stats.describe(train_eng_max_cycles)[2], color='g' , label='avg' )
        plt.axvline(stats.describe(train_eng_max_cycles)[1][1], color='b' , label='max' )
        
        ax.legend()
        start_idx = end_idx 
        plt.show()







### This will plot the final estimations vs the actual data


# y_hat = model.predict(df_new_train.values )




if make_plots==True and training_set==True:
    fig, axs = plot_many_predicteds_vs_actuals(train_features, prob_y)
    # fig.tight_layout()df
    plt.show()

if make_plots==True and training_set==False:
    fig, axs = plot_many_predicteds_vs_actuals(train_features, y_hat)
    # fig.tight_layout()df
    plt.show()


len(y_hat)
len(train_features)
train_features
len(df_new_train)

#########################################################




##########################    Scoreing Section   ###############



#### Score of the first model against the training set.  
## First score from basic linear regression model   ####
log_knot_model = r2(y, y_hat)
log_knot_model
# time_knot_model
# first_knot_model
# 0.64194677350961
# 0.7396060171044228
# log_knot_model
# 0.7272227017732488
#log_knot_model
# 0.7273228097635444




##### R-squared for the last n number of observations  #####
#
y
y_hat

r2_for_last_n_cycles(y_hat , y, last_n=150)
r2_for_last_n_cycles(y_hat , y, last_n=100)
r2_for_last_n_cycles(y_hat , y, last_n=75)
r2_for_last_n_cycles(y_hat , y, last_n=50)
r2_for_last_n_cycles(y_hat , y, last_n=25)
r2_for_last_n_cycles(y_hat , y, last_n=15)
r2_for_last_n_cycles(y_hat , y, last_n=10)
r2_for_last_n_cycles(y_hat , y, last_n=5)

###################   Make a list of r squared values for plotting   ##########

if training_set == True:
    r2_values = r2_generator_last_n_cycles(y_hat , y, 200)


if training_set == False:
    r2_values = r2_generator_last_n_cycles(y_hat , y, 200)

########  Plot the r2 values as the number of cycles remaining approaches the end #######

##### plot the full against the cycles to fail
if make_plots == True:
    fig, ax = plt.subplots(1, 1, figsize=(13, 13))
    ax.scatter(range(len(r2_values)+1, 1, -1) , r2_values)
    plt.ylim(-2, 1)
    plt.xlim(len(r2_values), 0)
    plt.title('R Squared')
    plt.xlabel('Cycles to Fail')
    plt.ylabel( 'R Squared Value')
    plt.show()

### Plot of r-squared as the number of observations approaches 1  #########







####################################################
####   Test for full transformation of data frame  ##########






############################################################################
# This creates a list of models, one for each bootstrap sample.


feature_pipeline.fit(df)
features = feature_pipeline.transform(df)


model = LinearRegression(fit_intercept=True)
model.fit(features.values, df[target_variable] ) 

cols_to_use = [
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


# feature_pipeline.fit(df)
# features = feature_pipeline.transform(df)

models = bootstrap_train(
    LogisticRegression, 
    features.values, 
    df[target_variable].values,
    bootstraps=500,
    fit_intercept=True
)


# fig, axs = plot_bootstrap_coefs(models, features.columns, n_col=4)
# plt.show()


fig, axs = plot_partial_dependences(
     model, 
     X=df,
     var_names=cols_to_use,
     pipeline=feature_pipeline,
     bootstrap_models=models,
     y=None#np.log(df[target_variable]).values  
     )
# fig.tight_layout()


plt.show()



df_new_train.head()
df_new_train.shape




# python
import numpy as np
import pandas as pd
# from pandas.plotting import scatter_matrix

from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
from sklearn.model_selection import train_test_split

from basis_expansions.basis_expansions import NaturalCubicSpline
from regression_tools.dftransformers import (
    ColumnSelector, Identity,
    FeatureUnion, MapFeature,
    StandardScaler)

from regression_tools.plotting_tools import (
    plot_partial_depenence,
    plot_partial_dependences,
    predicteds_vs_actuals)

import matplotlib.pyplot as plt
plt.style.use('ggplot')
import os


np.random.seed(137)


os.getcwd()

df1 = pd.read_csv('/home/superstinky/Seattle_g89/Final Project Data/enginedata/train_01_fd.csv', sep= '\t')


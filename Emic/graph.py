# %%
import re
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# %%
# -*- coding: utf-8 -*-
"""
The function to delete points after rupture is not commented in this version. 
Because there is a lot of tests being plotted in the same graph, there is some customization in the legend. If you are
going to plot less tests change that.
"""


def float_generator(s):
    # Functios that return a float when possible, otherwise return the input
    # inalterated
    try:
        return float(s)
    except ValueError:
        return s


def replace_commas(file):
    # Function to replace the commas by dot in the file
    with open(file, 'r+') as f:
        text = f.read()
        text = re.sub(',', '.', text)
        f.seek(0)
        f.write(text)
        f.truncate()


# Not using for now...
"""
def delet_rows_after_break(data_frame):
    # Analyse the last 100 datapoints of force
    df2 = data_frame['Deformação'].iloc[-1000:].copy()
    # Calculate the absolute percentual change of a row based in their previous value
    df2 = df2.pct_change().abs()
    # Separate the first index in which the diferrence is greater than 20%
    index = df2[lambda x: x >= 0.02].index[0]
    # Delete the rows in the original dataframe
    data_frame.drop(data_frame.index[index:], inplace=True)
    return data_frame
"""

##-- Data aquisition --##


# Directory with txt files
my_directory = os.path.dirname(os.path.realpath(__file__))

# Take all txt filex except 'TODOS.txt'
files = glob.glob('*.txt')
files[:] = [os.path.join(my_directory, x) for x in files]

# Name of the graph file is the same as the folder
graph_name = my_directory.split('\\')[-1]

# %%
# Empty dicitionary to store dataframes with the tests
dfs = {}

for file in files:
    replace_commas(file)

    # Load tests. Take from line 16 onwards.
    df = pd.read_csv(file, delimiter='\t', encoding='latin1')

    # Convert to float the numbers
    df = df.iloc[1:].astype(float)

    # Stay only with deformation and tension
    df = df[['Deformação(mm)', 'Força(N)']]

    # Include in dictionary. Key is the name of the txt
    dfs[os.path.split(file)[-1].split('.')[0]] = df


# %%
##-- Start routine to make graph --##
plt.style.use('ggplot')
fig, axs = plt.subplots()

# Max_value will be to adjust the range of x,y axis later
max_value_y = 0
max_value_x = 0

for i, (key, value) in enumerate(dfs.items()):

    if value['Força(N)'].max() > max_value_y:
        max_value_y = value['Força(N)'].max()

    if (value['Deformação(mm)']).max() > max_value_x:
        max_value_x = (value['Deformação(mm)']).max()

    # Plot deformation by tension. Label is the txt name
    plt.plot(value['Deformação(mm)'], value['Força(N)'],
             linewidth=0.7, label=key)

# Configure the style
plt.grid(True)
plt.xlabel('Deformação [mm]')
plt.ylabel('Força [N]')
plt.ylim(0, max_value_y*1.1)
plt.xlim(0, max_value_x*1.05)

plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.6), ncol=5)
plt.tight_layout()
plt.figure().subplots_adjust(bottom=0.25)
# Save graph as pdf
plt.savefig(graph_name+'.pdf')

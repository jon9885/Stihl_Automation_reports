import re
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# %%
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 09:31:46 2020

@author: jon98
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


def delet_rows_after_break(df):
    # Fucntion to remove lines after the break occour
    # Take the last 100 lines, and when the change in the deformation is
    # above 3%, it remove the lines below that
    df2 = df['Deformação'].iloc[-1000:].copy()
    df2 = df2.pct_change().abs()
    index = df2[lambda x:x >= 0.02].index[0]
    df.drop(df.index[index-1:], inplace=True)

##-- Data aquisition --##


# Directory with txt files
my_directory = os.path.dirname(os.path.realpath(__file__))

# Take all txt filex except 'TODOS.txt'
files = glob.glob('*.txt')
files[:] = [os.path.join(my_directory, x)
            for x in files if 'todos.txt' not in x.lower()]

# Name of the graph file is the same as the folder
graph_name = my_directory.split('\\')[-1]

# Empty dicitionary to store dataframes with the tests
dfs = {}

for file in files:
    replace_commas(file)

    # Load tests. Take from line 16 onwards.
    df = pd.read_csv(file, delimiter='\t', encoding='latin1', skiprows=16)

    # Convert to float the numbers
    df = df.iloc[1:].astype(float)

    delet_rows_after_break(df)

    # Stay only with deformation and tension
    df = df[['Deformação', 'Tensão']]

    # Include in dictionary. Key is the name of the txt
    dfs[os.path.split(file)[-1].split('.')[0]] = df


# Read elastic Modulos from TODOS.txt
replace_commas('todos.txt')
lines_to_read = list(range(12+len(files), 12+2*len(files)))

elastic_modulos = {}
with open('todos.txt', 'r') as f:
    for i, line in enumerate(f):
        if i in lines_to_read:
            # Key will be the name of the test (same used in dfs), and value will be modulus
            # already as float
            elastic_modulos[line.split('\t')[0]] = float(line.split('\t')[1])


##-- Start routine to make graph --##

plt.style.use('ggplot')
fig, axs = plt.subplots()

# Max_value will be to adjust the range of x,y axis later
max_value_y = 0
max_value_x = 0

for i, (key, value) in enumerate(dfs.items()):

    if value['Tensão'].max() > max_value_y:
        max_value_y = value['Tensão'].max()

    if (value['Deformação']+i*0.5).max() > max_value_x:
        # Deformation in the graph will have a offset of .5 in relation to the
        # last plot
        max_value_x = (value['Deformação']+i*0.2).max()

    # Generate line from the elastic modulos. Divide by 100 because deformation is in %
    y = np.polyval([elastic_modulos[key], 0], value['Deformação'])/100

    # Plot deformation by tension, including offset. Label is the txt name
    plt.plot(value['Deformação']+i*0.2,
             value['Tensão'], linewidth=0.7, label=key)

    # Plot modulus line. Also include offset. Same colour as the plot above
    plt.plot(value['Deformação']+i*0.2, y, linewidth=0.4,
             linestyle='dotted', color=plt.gca().lines[-1].get_color())


# Configure the style
plt.grid(True)
plt.xlabel('Deformação [%]')
plt.ylabel('Tensão [N/mm2]')
plt.ylim(0, max_value_y*1.1)
plt.xlim(0, max_value_x*1.05)
plt.legend()

# Save graph as pdf
plt.savefig(graph_name+'.pdf')

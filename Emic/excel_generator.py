# %%
import re
import glob
import os
import pandas as pd
import matplotlib

# %%
color_list = list(matplotlib.colors.cnames.values())


def float_generator(s):
    # Convert to float or return value
    try:
        return float(s)
    except ValueError:
        return s


def replace_commas(file):
    # Replace comma by dot (decimal separator)
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

# Folder with the .txt files
mydirectory = os.path.dirname(os.path.realpath(__file__))

# Identify all the .txt in the folder except todos.txt
files = glob.glob('*.txt')
flag_todos = 'todos.txt' in [file.lower().strip() for file in files]
files[:] = [os.path.join(mydirectory, x) for x in files]

# Name of the Excel table is gonna be the same as the folder
table_name = os.path.split(mydirectory)[-1]

# Initialize objects
writer = pd.ExcelWriter(os.path.join(
    mydirectory, table_name+'.xlsx'), engine='xlsxwriter')
workbook = writer.book
count = 0
for file in files:

    filename = os.path.split(file)[-1]

    replace_commas(file)

    # Load the csv data
    df = pd.read_csv(file, delimiter='\t', encoding='latin1')

    # Convert numéric values from string to float
    df = df.iloc[1:].astype(float)

    # Write in an excel object the dataframe. Start at row 12, with sheet name egual to
    # fileame minus extension
    df.to_excel(writer, index=False, header=True,
                sheet_name=filename.split('.')[0], startrow=11)

    worksheet = writer.sheets[filename.split('.')[0]]

    # --- Build graph
    chart = workbook.add_chart({'type': 'scatter',
                                'subtype': 'straight'})

    chart.add_series({
        'name': filename.split('.')[0],
        'categories': [filename.split('.')[0], 12, 1, len(df)+11, 1],
        'values': [filename.split('.')[0], 12, 2, len(df)+11, 2],
        'line': {'width': 2.0},
    })

    chart.set_x_axis({'name': 'Deformação(mm)', 'min': 0})
    chart.set_y_axis({'name': 'Força(N)'})
    chart.set_style(13)

    # Insert graph in the sheet and export file
    worksheet.insert_chart('J12', chart, {'x_offset': 25, 'y_offset': 10})

# -- Create chartcheet
    if file == files[0]:  # Fisrt loop
        chart_sheet1 = workbook.add_chart({'type': 'scatter',
                                          'subtype': 'straight'})
        chart_sheet1.set_x_axis({'name': 'Deformação(mm)',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12},
                                 'min': 0})
        chart_sheet1.set_y_axis({'name': 'Força(N)',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12}
                                 })
        chart_sheet1.set_style(13)
        chart_sheet1.set_legend({'position': 'bottom',
                                 'font': {'size': 10},
                                 })

    chart_sheet1.add_series({
        'name': filename.split('.')[0],
        'categories': [filename.split('.')[0], 12, 1, len(df)+11, 1],
        'values': [filename.split('.')[0], 12, 2, len(df)+11, 2],
        'line': {'width': 2.0, 'color': color_list[count]},
    })
    count = count+5

# -- Generate excel file
# Gerenate chartsheet1 and activte
chartsheet1 = workbook.add_chartsheet()
chartsheet1.set_chart(chart_sheet1)
chartsheet1.activate()
writer.save()

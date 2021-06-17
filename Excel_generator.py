import re
import glob
import os
import pandas as pd
# %%


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


# Folder with the .txt files
mydirectory = os.path.dirname(os.path.realpath(__file__))

# Identify all the .txt in the folder except todos.txt
files = glob.glob('*.txt')
flag_todos = 'todos.txt' in [file.lower().strip() for file in files]
files[:] = [os.path.join(mydirectory, x)
            for x in files if 'todos.txt' not in x.lower()]


replace_commas('todos.txt')
lines_to_read = list(range(12+len(files), 12+2*len(files)))

if flag_todos:
    elastic_modulos = {}
    YS1 = {}
    with open('todos.txt', 'r') as f:
        for i, line in enumerate(f):
            if i in lines_to_read:
                # Key will be the name of the test (same used in dfs), and value will be modulus
                # already as float
                elastic_modulos[line.split('\t')[0]] = float(
                    line.split('\t')[1])
                YS1[line.split('\t')[0]] = float(line.split('\t')[-1])
            if i == 15:
                elastic_modulos_interval = line.split('\t')[1]

# Name of the Excel table is gonna be the same as the folder
table_name = os.path.split(mydirectory)[-1]

# Initialize objects
writer = pd.ExcelWriter(os.path.join(
    mydirectory, table_name+'.xlsx'), engine='xlsxwriter')
workbook = writer.book

for file in files:

    filename = os.path.split(file)[-1]

    replace_commas(file)

    # Load the csv data
    df = pd.read_csv(file, delimiter='\t', encoding='latin1', skiprows=16)

    # Convert numéric values from string to float
    df = pd.concat([df.iloc[[0]], df.iloc[1:].astype(float)])

    # Delete rows after break of the speciment
    df = delet_rows_after_break(df)

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
        'categories': [filename.split('.')[0], 13, 5, len(df)+11, 5],
        'values': [filename.split('.')[0], 13, 4, len(df)+11, 4],
        'line': {'width': 2.0},
    })

    chart.set_x_axis({'name': 'Deformação', 'min': 0})
    chart.set_y_axis({'name': 'Tensão'})
    chart.set_style(13)

    # Insert graph in the sheet and export file
    worksheet.insert_chart('J12', chart, {'x_offset': 25, 'y_offset': 10})

    # -- Create 2 chartcheet
    if file == files[0]:  # Fisrt loop
        chart_sheet1 = workbook.add_chart({'type': 'scatter',
                                          'subtype': 'straight'})
        chart_sheet1.set_x_axis({'name': 'Deformação',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12},
                                 'min': 0})
        chart_sheet1.set_y_axis({'name': 'Tensão',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12}
                                 })
        chart_sheet1.set_style(13)
        chart_sheet1.set_legend({'position': 'bottom',
                                 'font': {'size': 14},
                                 })

        chart_sheet2 = workbook.add_chart({'type': 'scatter',
                                          'subtype': 'straight'})
        chart_sheet2.set_x_axis({'name': 'Deformação',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12},
                                 'min': 0})
        chart_sheet2.set_y_axis({'name': 'Tensão',
                                 'name_font': {'size': 14},
                                 'num_font': {'size': 12}
                                 })
        chart_sheet2.set_style(13)
        chart_sheet2.set_legend({'position': 'bottom',
                                 'font': {'size': 14},
                                 })

    chart_sheet1.add_series({
        'name': filename.split('.')[0],
        'categories': [filename.split('.')[0], 13, 5, len(df)+11, 5],
        'values': [filename.split('.')[0], 13, 4, len(df)+11, 4],
        'line': {'width': 2.0},
    })

    # Find index of 2% of deformation
    idx_2_pct = pd.to_numeric((df['Deformação'][1:]-2).abs()).idxmin()

    chart_sheet2.add_series({
        'name': filename.split('.')[0],
        'categories': [filename.split('.')[0], 13, 5, idx_2_pct+11, 5],
        'values': [filename.split('.')[0], 13, 4, idx_2_pct+11, 4],
        'line': {'width': 2.0},
    })

    # -- Write the summary of the table

    # Read the sumary (first 16 lines)
    with open(file, 'r') as f:
        summary = [next(f) for x in range(16)]

    # Select lines with important information
    info = [summary[i].split('\t') for i in [6, 7, 8, 10, 11, 12, 13]]

   # Convert numeric information from string to float
    info = [[float_generator(s) for s in line] for line in info]

    if flag_todos:
        info[-1][1] = elastic_modulos[filename.split('.')[0]]
        info[-1][-1] = YS1[filename.split('.')[0]]
        info[4][1:3] = [elastic_modulos_interval]*2

    # Write summary in excel file
    for row_num, row_data in enumerate(info):
        for col_num, col_data in enumerate(row_data):
            worksheet.write(row_num, col_num, col_data)


# -- Generate excel file
# Gerenate chartsheet1 and activte
chartsheet1 = workbook.add_chartsheet()
chartsheet1.set_chart(chart_sheet1)
chartsheet1.activate()

# Generate chartsheet2
chartsheet2 = workbook.add_chartsheet()
chartsheet2.set_chart(chart_sheet2)

# Create consolidation sheet
format_border = workbook.add_format({'border': 1})
format_border2 = workbook.add_format({'border': 1, 'bold': 1})

worksheet = workbook.add_worksheet('Consolidado')

worksheet.write(4, 1, 'Nome', format_border2)
worksheet.write(4, 2, 'Módulo Elástico', format_border2)
worksheet.write(
    5, 2, '=\''+os.path.split(files[0])[-1].split('.')[0]+'\'!B5', format_border2)
worksheet.write(5, 1, 'Parâmetro', format_border2)
worksheet.write(6, 1, 'Unidade', format_border2)
worksheet.write(6, 2, 'N/mm2', format_border2)
worksheet.write(6, 3, 'N/mm2', format_border2)
worksheet.write(6, 4, 'N/mm2', format_border2)
worksheet.write(6, 5, 'N/mm2', format_border2)
worksheet.write(6, 6, 'N/mm2', format_border2)

worksheet.merge_range('D5:D6', 'Tensão máxima', format_border2)
worksheet.merge_range('E5:E6', 'Tensão escoamento', format_border2)
worksheet.merge_range('F5:F6', 'Tensão ruptura', format_border2)
worksheet.write(4, 6, 'YS1_Tensão', format_border2)
worksheet.write(5, 6, '0.20%', format_border2)

worksheet.write(7+len(files), 1, 'Média', format_border2)
worksheet.write(8+len(files), 1, 'Desvio padrão', format_border2)

for count, file in enumerate(files):
    filename = os.path.split(file)[-1].split('.')[0]
    worksheet.write(7+count, 1, filename, format_border)
    worksheet.write(7+count, 2, '=\''+filename+'\'!B7', format_border)
    worksheet.write(7+count, 3, '=\''+filename+'\'!L7', format_border)
    worksheet.write(7+count, 6, '=\''+filename+'\'!M7', format_border)

worksheet.write(7+len(files), 2, '=AVERAGE(C8:C' +
                str(7+len(files))+')', format_border)
worksheet.write(8+len(files), 2, '=STDEV(C8:C' +
                str(7+len(files))+')', format_border)

worksheet.write(7+len(files), 3, '=AVERAGE(D8:D' +
                str(7+len(files))+')', format_border)
worksheet.write(8+len(files), 3, '=STDEV(D8:D' +
                str(7+len(files))+')', format_border)

worksheet.write(7+len(files), 4, '=AVERAGE(E8:E' +
                str(7+len(files))+')', format_border)
worksheet.write(8+len(files), 4, '=STDEV(E8:E' +
                str(7+len(files))+')', format_border)

worksheet.write(7+len(files), 5, '=AVERAGE(F8:F' +
                str(7+len(files))+')', format_border)
worksheet.write(8+len(files), 5, '=STDEV(F8:F' +
                str(7+len(files))+')', format_border)

worksheet.write(7+len(files), 6, '=AVERAGE(G8:G' +
                str(7+len(files))+')', format_border)
worksheet.write(8+len(files), 6, '=STDEV(G8:G' +
                str(7+len(files))+')', format_border)


writer.save()

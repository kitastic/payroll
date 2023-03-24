import re
import pandas as pd
import openpyxl
import csv

filename = 'sample.txt'
rawdata = []
parsed = []
with open(filename) as file:
    # read all lines and remove '\n' at the end of each line
    counter = 0
    temp = []
    for i in file:
        temp.append(i.rstrip())
        counter = counter + 1
        if counter == 26:
            rawdata.append(temp.copy())
            temp.clear()
            counter = 0
sheetname = re.search('\d+/\d+/\d+', rawdata[0][1]).group(0).replace('/','.')

def getDay(row):
    v = re.findall('(?<=\$)\d?,?\d+\.\d+', row)
    # remove comma and convert strings to float for money price
    v = [float(i.replace(',', '')) for i in v]
    d = re.match('\d+-\w+', row)
    # if d is found then return both d and v, else return v
    if d:
        return d.group(0), v
    else:
        return v


def getFloat(row):
    # searching at the end of string for dollar amount
    # remove dollar sign using 'positive lookbehind assertion'
    v = re.search('(?<=\$)\d+,?\d+\.\d+$', row)
    # remove comma and convert strings to float for money price
    v = float(v.group(0).replace(',', ''))
    return v

temp = []
# parse data
for i in rawdata:
    # each i is for each employee ticket for the whole week
    # out of the 26 lines of raw data, we will only extract what we need

    temp.append(['====','====','====','===='])
    temp.append(['Date', '', '', re.search('\d+/\d+/\d+', i[1]).group(0)])
    temp.append(['Name', '', '', re.search('\w+$', i[2]).group(0)])
    temp.append(['Pay:','','',''])
    temp.append(['Total Sale', '', '', getFloat(i[6])])
    temp.append(['','','','',])
    temp.append(['Commission', '', '', getFloat(i[8])])
    temp.append(['Tips', '', '', getFloat(i[9])])
    temp.append(['','','','-------'])
    temp.append(['Total Pay', '', '', getFloat(i[11])])
    temp.append(['Check', '', '', getFloat(i[12])])
    temp.append(['Cash', '', '', getFloat(i[13])])
    temp.append(['Daily:','-------','-------','-------'])
    temp.append(['Day', 'Total', 'Comm', 'Tips'])
    day, values = getDay(i[17])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[18])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[19])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[20])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[21])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[22])
    temp.append([day, values[0], values[1], values[2]])
    day, values = getDay(i[23])
    temp.append([day, values[0], values[1], values[2]])
    temp.append(['     ','-------','-------','-------'])
    values = getDay(i[25])
    temp.append(['', values[0], values[1], values[2]])


with open('sample.csv','w', newline='') as f:
    write = csv.writer(f)
    write.writerows(temp)

read_file = pd.read_csv('sample.csv')

path = 'weeklyPayroll.xlsx'
excelBook = openpyxl.load_workbook(path)
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    writer.book = excelBook
    read_file.to_excel(writer, sheetname, index=False)
    writer.save()

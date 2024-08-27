#!/usr/bin/env python
import PySimpleGUI as sg
import sys
import json

file_name = '../db/nailsSales2024.json'

with open(file_name, 'r') as fp:
    data = json.load(fp)

for date, employees in data.items():
    for employee, sales in employees.items():
        s = sales[0]
        tips = sales[1]
        data[date][employee] = {'sales': s, 'tips': tips}

with open(file_name, 'w+') as fp:
    json.dump(data, fp, indent=4, sort_keys=True)

"""
This will be the main driver file
"""
from webAuto import WebBot
import helper


# list must be alphabetized, so iterating down drop list is easier
poshEmployee = ['Mary', 'Nancy', 'Sophia', 'Tuyen', 'Vu']
upscaleEmployee = []

pBundle = ['kit@posh','Joeblack334$', poshEmployee]

posh = WebBot(pBundle)
# posh.login()
# posh.getPayroll('03/13/2023','03/19/2023')
# posh.exportOrigToTxt('original.txt')
# posh.parseData()
# posh.printOriginalData()

posh.importTxtToOrig('original.txt')
posh.origToRaw()
posh.parseData()
posh.exportParToXlsx('weeklyDB.xlsx')

print('Done')
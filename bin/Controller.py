import datetime
import PySimpleGUI as sg
import Ai
import re

class Controller:
    def __init__(self):
        self.ai = Ai.Ai()
        self.startDate = ''
        self.endDate = ''
        self.guiData = dict()

    def listen(self, command, guiData):
        if command == 'Load Settings':
            self.ai.loadSettings()
        elif command == 'View Settings':
            return self.ai.getSettings()
        elif command == 'view sales':
                self.guiPrint(self.ai.getJson(guiData))
        elif command == 'webscrape sales':
            self.ai.webscrapeSales(guiData[0], guiData[1], guiData[2])
        elif command == 'Payroll':
            self.ai.getPayrollFromSalon(guiData[0], guiData[1], guiData[2])
        elif command == '-eTab_btn_loadEmployees-':
            return self.ai.populateEmpList(guiData)
        elif command == '-eTab_btn_save-':
            self.ai.modEmp(cmd='save', salon=guiData[0], employee=guiData[1])
        elif command == '-eTab_btn_update-':
            self.ai.modEmp(cmd='update', salon=guiData[0], employee=guiData[1])
        elif command == '-eTab_btn_remove-':
            self.ai.modEmp(cmd='remove', salon=guiData[0], employee=guiData[1])

        elif command == 'savedb':
            self.ai.saveNewSettings()
        else:
            sg.easy_print('Command not found')

    def guiPrint(self, guiData):
        tmp = ''
        if isinstance(guiData, dict):
            for salon,bundle in guiData.items():
                tmp += '{}: {}\n'.format(salon,bundle)
            sg.Print(tmp)
        elif isinstance(guiData, str):
            sg.Print(guiData)
        else:
            sg.Print('Error: Controller.guiPrint cannot parse guiData to print')

    def determineSalon(self, guiData):
        """
        *** IMPORTANT *** If adding or removing salon, modify this method accordingly.
        If processing anything, we need to know which salon do we want to access if not all.
        During development, sometimes only one salon needs to be tested to make sure the
        workflow and functions are proper. After that we can expand to multiple salon tests.
        Args:
            guiData:

        Returns:

        """
        try:
            return [guiData['-salon-'].lower()]
        except TypeError:
            print('TypeError: Cannot determine which salon ')

    def validDates(self, sdate, edate):
        try:
            sd = datetime.datetime.strptime(sdate, '%m/%d/%Y')
            ed = datetime.datetime.strptime(edate, '%m/%d/%Y')
            if sd <= ed:
                return True
            else:
                return False
        except ValueError:
            sg.easy_print('ValueError: unable to parse time')



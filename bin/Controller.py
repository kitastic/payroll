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

    def listen(self, command, guiData=None, addOn=None):
        salons = addOn
        if command == 'loadSettings':
            self.ai.loadSettings()
        elif command == 'viewSettings':
            self.guiPrint(self.ai.getSettings())
        elif command == 'viewSalonBundles':
            self.guiPrint(self.ai.getSalonBundles())
        elif command == 'Get Sales':
            if self.validDates(guiData=guiData):
                self.ai.webscrapeSales(addOn, self.startDate, self.endDate)
        elif command == 'Json::view':
            salons = self.determineSalon(guiData=guiData)
            if self.validDates(guiData=guiData):
                self.guiPrint(self.ai.getJson(salons, self.startDate, self.endDate))
        elif command == 'Payroll':
            if self.validDates(guiData=guiData):
                self.ai.getPayrollFromSalon(salons, self.startDate, self.endDate)
        elif command == 'save employee':
            self.ai.modEmp(cmd='save', employee=guiData, salon=addOn)
        elif command == 'Update Employee':
            self.ai.modEmp(cmd='update', employee=guiData, salon=addOn)
        elif command == 'Remove Employee':
            self.ai.modEmp(cmd='remove', employee=guiData, salon=addOn)
        elif command == 'populateEmpListSettings':
            return self.ai.populateEmpList(addOn)
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

    def validDates(self, guiData, gui=None):
        self.startDate = guiData['-startDateInput-']
        self.endDate = guiData['-endDateInput-']
        try:
            sd = datetime.datetime.strptime(self.startDate, '%m/%d/%Y')
            ed = datetime.datetime.strptime(self.endDate, '%m/%d/%Y')
            if sd <= ed:
                return True
            else:
                return False
        except ValueError:
            sg.easy_print('ValueError: unable to parse time')



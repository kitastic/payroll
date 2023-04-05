import datetime
import PySimpleGUI as sg
import Ai
import re

class Controller:
    def __init__(self):
        self.ai = Ai.Ai()
        self.startDate = ''
        self.endDate = ''
        self.data = dict()

    def listen(self, command,data=None):
        salons = self.determineSalon(data)
        if command == 'loadSettings':
            self.ai.loadSettings()
        elif command == 'viewSettings':
            self.guiPrint(self.ai.getSettings())
        elif command == 'viewSalonBundles':
            self.guiPrint(self.ai.getSalonBundles())
        elif command == 'Get Sales':
            if self.validDates(data):
                self.ai.webscrapeSales(salons, self.startDate, self.endDate)
        elif command == 'Json::view':
            salons = self.determineSalon(data)
            if self.validDates(data):
                self.guiPrint(self.ai.getJson(salons, self.startDate, self.endDate))
        elif command == 'Payroll':
            if self.validDates(data):
                self.ai.getPayrollFromSalon(salons, self.startDate, self.endDate)
        elif command == 'save employee':
            if salons:
                self.ai.modEmp(salons, data, 'update')
            else:
                sg.Print('Error: no salon was selected')
        elif command == 'populateEmpListSettings':
            # force to perform for all because it does not matter
            # TODO this bypass still hasnt worked, gui still crashes if no salon selected
            # data['salonAll'] = True
            # salons = self.determineSalon(data)
            if salons:
                return self.ai.populateEmpList(salons)
            else:
                sg.Print('Please choose 1 salon at a time')

        elif command == 'savedb':
            self.ai.saveNewSettings()
        else:
            sg.easy_print('Command not found')

    def guiPrint(self, data):
        tmp = ''
        if isinstance(data, dict):
            for salon,bundle in data.items():
                tmp += '{}: {}\n'.format(salon,bundle)
            sg.Print(tmp)
        elif isinstance(data, str):
            sg.Print(data)
        else:
            sg.Print('Error: Controller.guiPrint cannot parse data to print')

    def determineSalon(self, data):
        """
        *** IMPORTANT *** If adding or removing salon, modify this method accordingly.
        If processing anything, we need to know which salon do we want to access if not all.
        During development, sometimes only one salon needs to be tested to make sure the
        workflow and functions are proper. After that we can expand to multiple salon tests.
        Args:
            data:

        Returns:

        """
        try:
            if data['salonUpscale']:
                return ['upscale']
            elif data['salonPosh']:
                return ['posh']
            elif data['salonAll']:
                return ['posh', 'upscale']
        except TypeError:
            print('TypeError: Cannot determine which salon ')

    def validDates(self, data, gui=None):
        self.startDate = data['-startDateInput-']
        self.endDate = data['-endDateInput-']
        try:
            sd = datetime.datetime.strptime(self.startDate, '%m/%d/%Y')
            ed = datetime.datetime.strptime(self.endDate, '%m/%d/%Y')
            if sd <= ed:
                return True
            else:
                return False
        except ValueError:
            sg.easy_print('ValueError: unable to parse time')



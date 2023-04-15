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
            return self.ai.webscrapeSales(guiData[0], guiData[1], guiData[2])
        elif command in ('Txt Files', '-mTab_btn_exporttxt-'):
            self.ai.exportPayroll(guiData[0], guiData[1], guiData[2])
        elif command == '-mTab_btn_payroll-':
            return self.ai.getPayrollFromSalon(guiData)
        elif command == '-mTab_btn_status-':
            return self.ai.getEmpStatus(guiData)
        elif command == '-eTab_btn_loadEmployees-':
            return self.ai.populateEmpList(guiData)
        elif command == '-eTab_btn_save-':
            self.ai.modEmp(cmd='save', salon=guiData[0], employee=guiData[1])
        elif command == '-eTab_btn_update-':
            self.ai.modEmp(cmd='update', salon=guiData[0], employee=guiData[1])
        elif command == '-eTab_btn_remove-':
            self.ai.modEmp(cmd='remove', salon=guiData[0], employee=guiData[1])
        elif command == 'getSalonNames':
            return self.ai.getAllSalonNames()
        elif command == '-sTab_btn_save-':
            self.ai.createSalon(guiData)
        elif command == '-sTab_btn_remove-':
            self.ai.removeSalon(guiData)
        elif command == 'importJson':
            self.ai.importJson(guiData[0], guiData[1])
        elif command == 'savedb':
            self.ai.saveNewSettings()
        else:
            print('WARNING:(Controller.listen): Command not found')







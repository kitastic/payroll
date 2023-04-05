import glob
import os
import time
import openpyxl
import re
import datetime
import xlHelper
import json
import Salon
import PySimpleGUI as sg

class Ai:

    def __init__(self,):
        '''
            settings = {'upscale': {'name': 'upscale',
                                    'login': {'username': 'upscalemanager', 'password': 'Joeblack334$'},
                                    'salesJson': 'uSales.json',
                                    'salesXl': 'uSales.xlsx',
                                    'payments': 'uPayments.xlsx',
                                    'employees': {'Anna': { 'pay': 0, 'rent': 0........},
                                                  'Cindy': {'pay': 900, 'rent': 60......},
                                                 }
                                    },
                        'posh': {'name': 'posh',
                                 'login': {'username': 'kit@posh', 'password': 'Joeblack334$'},
                                 'salesJson': 'pSales.json',
                                 'salesXl': 'pSales.xlsx',
                                 'payments': 'pPayments.xlsx',
                                 'employees': {}
                        }}
        '''
        self.loadedSettings = dict()

        '''
            for each salon:
            { 'salon name': { 'obj': Salon instance
                              'settings': {'name': 'posh',
                                             'login': {'username': 'kit@posh', 'password': 'Joeblack334$'},
                                             'salesJson': 'pSales.json',
                                             'salesXl': 'pSales.xlsx',
                                             'payments': 'pPayments.xlsx'
                                             'employees': {'empNames': {'pay': '',
                                                                        'fees': '',
                                                                        'rent': '',
                                                                        'paygrade': {'regular': '',
                                                                                        'commission': '',
                                                                                        'check': '',
                                                                                        'commissionspecial': '',
                                                                                        'checkdeal': '',
                                                                                        'checkreport': ''
                                                                                        }
                                             }
                            }
        '''
        self.salons = dict()            # keys are salon names and values are salon class objects
        self.employees = dict()
        self.loadSettings()

    def loadSettings(self):
        '''
        This function will get information from one big dictionary in the form
         of json and parse that information and divide them into separate salon dictionaries,
        salonsBundle. Key is salon name and values are settings
        Returns:
            None
        '''
        with open('../db/master.json','r') as reader:
            self.loadedSettings = json.load(reader)

        for name in self.loadedSettings.keys():     # dict keys are iterable BUT NOT subscriptable ie [0]
            self.salons[name] = dict()
            self.salons[name]['obj'] = Salon.Salon(self.loadedSettings[name])       # create salon objects
            self.salons[name]['settings'] = self.loadedSettings[name]

    def webscrapeSales(self, salons, sDate, eDate):
        """
        this function will grab each salon object required from
        list of salons and send to threads to process each salon one at a time
        Args:
            salons: list of salon names
            sDate: string format mm/dd/yyyy
            eDate: string format mm/dd/yyyy

        Returns:

        """
        for s in salons:
            # get salon object from dictionary
            salon = self.salons[s]['obj']
            path, fname = salon.dlEmpSales(s, salon.zotaUname, salon.zotaPass,
                                           startDate=sDate,endDate=eDate
                                           )
            salon.readSalesXltoJson(path+fname)
            salon.updateJsonFileDelXl(path)
            time.sleep(5)

    def getJson(self, salons, sDate, eDate):
        """
        Gets json with specific dates from salon constructor. Called by controller
        and information received from ai will be printed out in viewer
        Args:
            salons: [str] list of strings of salon names
            sDate: str
            eDate: str

        Returns:
            dictionary with salon names as keys and values is dictionary
        """
        tmp = dict()
        for s in self.salons.keys():
            salon = self.salons[s]['obj']
            tmp[s] = salon.getJsonRange(sDate, eDate)
        return tmp

    def modEmp(self, salons, data, cmd):
        # newEmp = dict()
        newEmp = {data['-empName-']: {'id': data['-empId-'],
                                      'salonName': data[''],
                                      'pay': data['-basePay-'] if data['-basePay-'] else '0',
                                      'fees': data['-fees-'] if data['-fees-'] else '0',
                                      'rent': data['-rent-'] if data['-rent-'] else '0',
                                      'paygrade': { 'regular': data['-regular-'],
                                                    'commission': data['-commission-'] if data['-commission-'] else '0',
                                                    'check': data['-check-'] if data['-check-'] else '0',
                                                    'commissionspecial': data['-commissionspecial-'] if data[
                                                        '-commissionspecial-'] else '0',
                                                    'checkdeal': data['-checkdeal-'] if data['-checkdeal-'] else '0',
                                                    'checkreport': data['-checkreport-'] if data['-checkreport-'] else
                                                    '0'
                                                    }
                                      } }

        # now newEmp will be added to corresponding salon's 'employees' dictionary
        for s in salons:
            if cmd == 'create':
                self.salons[s]['settings']['employees'] = newEmp.copy()
                self.loadedSettings[s]['employees'] = newEmp.copy()
            elif cmd == 'update':
                self.salons[s]['settings']['employees'] = newEmp.copy()
                self.loadedSettings[s]['employees'] = newEmp.copy()
            elif cmd == 'remove':
                deletedValue = self.salons[s]['settings']['employees'].pop(data['-empName-'])
                deletedValue = self.loadedSettings[s]['employees'].pop(data['-empName-'])
            elif cmd == 'view':
                return self.salons[s]['settings']['employees'][data['-empName-']]


    def getPayrollFromSalon(self, salons, sDate, eDate):
        for s in self.salons:
            salon = self.salons[s]

    def saveNewSettings(self):
        with open('../db/master.json','+w') as writer:
            # '|' means combine both dict but crops empty values, best is newDict = {**dict1, **dict2}
            json.dump(self.loadedSettings, writer, indent=4, sort_keys=True)

    def populateEmpList(self, salons):
        """

        Args:
            salons: [str]

        Returns:
            list of employee dictionaries
        """
        emps = {}
        for s in salons:
            emps[s] = self.salons[s]['settings']['employees'].copy()
        return emps

    def discardNewSettings(self):
        self.newSettings = self.loadedSettings

    def getSalonInfo(self, salonName):
        """
        this will be called by Salon class in order to construct Salon

        Returns:
            (list of lists): salon's list of settings
        """
        salonNames = list(self.salons.keys())
        if salonName not in salonNames:
            print('Salon name not found in settings: check name or update settings with new salon')
        else:
            return self.salons[salonName]['settings']

    def renameFile(self,newName,downloadPath,time_to_wait=60):
        '''
        mean to rename recently downloaded file from website
        Args:
            newName:
            downloadPath:
            time_to_wait:

        Returns:

        '''
        time_counter = 0
        filename = max([f for f in os.listdir(downloadPath)],
                       key=lambda xa: os.path.getctime(os.path.join(downloadPath,xa)))

        # check if chrome still attached incomplete suffix
        while '.crdownload' in filename:
            time.sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:
                raise Exception('Waited too long for file to download')
        # check if file exists: glob will return a list with any match or empty list
        while not (glob.glob('../tmp/Employee_Sales*.xlsx')):
            time.sleep(1)

        filename = max([f for f in os.listdir(downloadPath)],
                       key=lambda xa: os.path.getctime(os.path.join(downloadPath,xa)))
        os.rename(os.path.join(downloadPath,filename),os.path.join(downloadPath,newName))

    def getSettings(self):
        sg.Print(self.loadedSettings)
        return self.loadedSettings

    def getSalonBundles(self):
        '''
        Called by ai to print salon bundles into gui output text
        Returns:
            (dict): keys are salon names, values are salon obj and settings in nested dict
        '''
        sg.Print(self.salons)
        return self.salons

import datetime
import glob
import json
import os
import PySimpleGUI as sg

import re
import Salon
import time


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
            salons dict:  {'salon name': salon obj
                              'salon name2: salon obj }
        '''
        self.salons = dict()  # keys are salon names and values are salon class objects
        self.employees = dict()
        self.loadSettings(pfname=None)

    def createSalon(self,salonPkt):
        self.salons[salonPkt['name']] = Salon.Salon(salonPkt)

    def exportPayroll(self, sName, sDate, format):
        if format == 'html':
            self.salons[sName].exportPayroll(sDate, format)
        else:
            self.salons[sName].exportPayroll(sDate,format)

    def getAllSalonNames(self):
        names = []
        for s in self.salons:
            names.append(s)
        return names

    def getEmpStatus(self, sname):
        return self.salons[sname].getEmpStatus()

    def getJsonRange(self, salon, sDate, eDate):
        """
            Gets json with specific dates from salon obj.
        Args:
            salons: [str] list of strings of salon names
            sDate: str
            eDate: str

        Returns:
            list with first element indicating how many nestic dict layers and
            dictionary with salon names as keys and values is dictionary
        """
        return [2, {salon: {self.salons[salon].getJsonRange(sDate, eDate)}}]


    def getJsonLatestDates(self, cmd):
        salon = [s for s in self.salons]
        result = []
        displayResult = ''
        currentYr = datetime.datetime.now().year
        for i in salon:
            with open(f'../db/{i}Sales{currentYr}.json','r') as read:
                for line in reversed(list(read)):
                    line.rstrip()
                    l = re.search('\d+/\d+/\d+',line)
                    if l:
                        result.append(l.group(0))
                        displayResult += f'{i}: {l.group(0)}\n'
                        break
        if cmd == 'display':
            return displayResult
        elif cmd == 'webscrape':
            return result

    def getPayrollFromSalon(self, sname, sdate, edate):
        """
            Retrieves sales from json for given date range and salon name
        Args:

        Returns:
            dictionary of employee key and their payroll values
        """
        return self.salons[sname].getPayroll(sdate, edate)

    def getSalonInfo(self,salonName):
        """
        this will be called by Salon class in order to construct Salon

        Returns:
            (list of lists): salon's list of settings
        """
        salonNames = list(self.salons.keys())
        if salonName not in salonNames:
            print('Salon name not found in settings: check name or update settings with new salon')
        else:
            return self.salons[salonName].getSalonInfo()

    def getSettings(self):
        return self.loadedSettings

    def importJson(self,sname,pfname):
        self.salons[sname].readSalesXltoJson(pfname)
        self.salons[sname].updateJsonFileDelXl(path=None)

    def loadSettings(self, pfname):
        '''
        This function will get information from one big dictionary in the form
         of json and parse that information and divide them into separate salon dictionaries,
        salonsBundle. Key is salon name and values are settings
        Returns:
            None
        '''
        if pfname:
            with open(pfname,'r') as reader:
                self.loadedSettings = json.load(reader)
        else:
            with open('../db/master.json','r') as reader:
                self.loadedSettings = json.load(reader)
        for name in self.loadedSettings.keys():  # dict keys are iterable BUT NOT subscriptable ie [0]
            self.salons[name] = Salon.Salon(self.loadedSettings[name])  # create salon objects

    def modEmp(self,cmd,salon,employee):
        # employee has its name as the key so we get it from list(dict.keys()) and get the only value in the list
        if cmd == 'save':
            self.salons[salon].createEmpFromGui(name=list(employee.keys())[0],empData=employee)
        elif cmd == 'update':
            self.salons[salon].updateEmpFromGui(name=list(employee.keys())[0],empData=employee)
        elif cmd == 'remove':
            # if remove cmd was sent, employee is a string name
            self.salons[salon].deleteEmp(name=employee)
        else:
            sg.Print('Warning: did not do anything because dont know command regarding Ai.modEmp()')

    def populateEmpList(self,salon):
        """
        Args:
            salons: [str]
        Returns:
            list of employee dictionaries
        """
        return self.salons[salon].getEmps()

    def removeSalon(self,name):
        if name in self.salons.keys():
            self.salons.pop(name)
            print(f'[Ai]: {name} removed successfully')
        else:
            print(f'[Ai]: {name} not found to remove')

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
                       key=lambda xa:os.path.getctime(os.path.join(downloadPath,xa)))

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
                       key=lambda xa:os.path.getctime(os.path.join(downloadPath,xa)))
        os.rename(os.path.join(downloadPath,filename),os.path.join(downloadPath,newName))

    def saveNewSettings(self):
        data = {}
        for name,salonObj in self.salons.items():
            data[name] = salonObj.getDataToSave()
        with open('../db/master.json','+w') as writer:
            # '|' means combine both dict but crops empty values, best is newDict = {**dict1, **dict2}
            json.dump(data,writer,indent=4,sort_keys=True)

    def webscrapeSales(self,salon,sDate,eDate):
        """
        this function will grab each salon object required from
        list of salons and send to threads to process each salon one at a time
        Args:
            salon: (string) salon name
            sDate: string format mm/dd/yyyy
            eDate: string format mm/dd/yyyy
        Returns:
        """
        salonObj = self.salons[salon]
        # salon is using inherited method dlEmpSales from WebBot
        try:
            print(f'[Ai.webscrapeSales]: beginning to retrieve sales for {salon} date range {sDate} - {eDate}')
            path,fname = salonObj.dlEmpSales(salon,salonObj.zotaUname,salonObj.zotaPass,
                                             startDate=sDate,endDate=eDate)
            if not path:
                print(f'[Ai.webscrapeSales]{salon} unable to download file range {sDate} - {eDate}')
                return False
            salonObj.readSalesXltoJson(path + fname)
            time.sleep(2)
            salonObj.updateJsonFileDelXl(path)
            return True
        except Exception:
            print('[Ai.webscrapeSales]ERROR: Failed to get sales.\nPossible problems:\n-date range too long and '
                  'browser took too long to load\n-maybe there is no sales data for the salon within'
                  'date range (erased data by zota?)\n-or zota connection is slow and retry')
            return False

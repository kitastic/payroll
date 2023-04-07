import os
import glob
import openpyxl
import datetime
import re
import xlHelper
import json
import Bot
import time
import PySimpleGUI as sg
import random
import Employee

import helper


class Salon(Bot.Bot):
    def __init__(self,bundle):
        """

        Args:
            bundle: (dictionary) layout:
                    bundle =  { 'name': 'upscale',
                                'login': {'username': 'upscalemanager', 'password': 'Joeblack334$'},
                                'salesJson': '../db/uSales.json',
                                'salesXl': '../db/uSales.xlsx',      # might not need yet
                                'payments': 'uPayments.xlsx',
                                'employees': {'Name': { 'pay': 0, 'rent': 0, 'fees': 0,'active':bool, 'id': int, 'salonName': str, 'name': empname,
                                                        'paygrade':{'regType': True for regular False for special
                                                                    'regular': {'commission':, 'check':, }
                                                                    'special': {'commissionspecial', 'checkdeal':, 'checkoriginal':,}}},
                                              'Name2': { ... }
                                             }},
        """
        super().__init__()
        # at this point, the keys in bundle have been alphabetized by json
        self.employees = bundle['employees']
        self.zotaUname = bundle['login']['username']
        self.zotaPass = bundle['login']['password']
        self.salonName = bundle['name']
        self.jsonPfname = bundle['salesJson']   # path and filename to json file stored
        self.salesXl = bundle['salesXl']
        self.paymentsXl = ''

        # variables stored during program runtime
        self.salesJson = dict()     # keys are datetime, values are employee dict()
        self.Emps = dict()          # holds employee objects
        self.setupSalon()

    def setupSalon(self):
        """
            Retrieves all sales data from json and creates employee objects
        Returns:
            None
        """
        try:
            if os.path.getsize(self.jsonPfname) > 10:
                with open(self.jsonPfname,'r') as reader:
                    self.salesJson = json.load(reader)
        except FileNotFoundError:
            pass

        for emp, info in self.employees.items():
            self.Emps[emp] = Employee.Employee(info)

    def createEmpFromGui(self, name, empData):
        """

        Args:
            name:
            empData:

        Returns:

        """
        self.Emps[name] = Employee.Employee(empData[name])

    def updateEmpFromGui(self, name, empData):
        # easiest way is to remove existing dictionary and set new one
        self.Emps.pop(name)
        self.Emps[name] = Employee.Employee(empData[name])

    def loadEmp(self, name, data):
        """
            mainly for setting up salon and parsing information from json da
        Args:
            name: (str) employee name
            data: (dict) key is emp name

        Returns:

        """
        usedId = []
        # for emp in self.Emps:
        #     usedId.append(emp.getId())
        for e in self.Emps.keys():
            usedId.append(self.Emps[e].getId())

        pay,fees,rent,commission,check,comspec,checkdeal,checkoriginal = (0 for i in range(1,9))
        idNum = 0
        active = True
        searching = True
        while searching:
            if self.salonName == 'upscale':
                idNum = random.randint(100,299)
            elif self.salonName == 'posh':
                idNum = random.randint(300,599)
            if idNum not in usedId:
                searching = False

        paygradetype = True

        try:
            idNum = data['empId']
        except KeyError:
            pass
        try:
            active = data['active']
        except KeyError:
            pass
        try:
            pay = data['pay']
        except KeyError:
            pass
        try:
            fees = data['fees']
        except KeyError:
            pass
        try:
            rent = data['rent']
        except KeyError:
            pass
        try:
            paygradetype = data['paygrade']['regType']
        except KeyError:
            pass
        try:
            commission = data['paygrade']['regular']['commission']
        except KeyError:
            pass
        try:
            check = data['paygrade']['regular']['check']
        except KeyError:
            pass
        try:
            comspec = data['paygrade']['special']['commissionspecial']
        except KeyError:
            pass
        try:
            checkdeal = data['paygrade']['special']['checkdeal']
        except KeyError:
            pass
        try:
            checkoriginal = data['paygrade']['special']['checkoriginal']
        except KeyError:
            pass

        # make sure id is unique
        searching = True
        while searching:
            if self.salonName == 'upscale':
                idNum = random.randint(100,299)
            elif self.salonName == 'posh':
                idNum = random.randint(300,599)
            if idNum not in usedId:
                searching = False

        objBundle = {'paygrade':{'regType':paygradetype,
                                 'regular':{'commission':commission,'check':check},
                                 'special':{'commissionspecial':comspec,'checkdeal':checkdeal,
                                            'checkoriginal':checkoriginal}},
                     'id':idNum,'name':name,'salonName':self.salonName,
                     'active': active, 'rent':rent,'fees':fees,'pay':pay}
        self.Emps[name] = Employee.Employee(objBundle)

    def deleteEmp(self, name):
        deletedValue = self.Emps.pop(name)
        print(deletedValue)

    def readSalesXltoJson(self, pfName):
        workBook = openpyxl.load_workbook(pfName)
        workSheet = workBook.active

        # keys are employee names, values are their totals for the day
        empDict = dict()
        day = ''
        for row in workSheet.iter_rows(values_only=True):
            if isinstance(row[0],datetime.datetime):
                # if employees dictionary has data, copy it to sales dictionary
                # before setting new day and getting new day data
                if empDict and day != 0:  # if not False
                    self.salesJson[day] = empDict.copy()
                    empDict.clear()
                # day is going to be dictionary key, but needs to be
                # converted to string because datetime is not serializable
                # by json
                day = datetime.datetime.strftime(row[0], '%m/%d/%Y')
            elif not row[0]:
                continue
            else:
                try:
                    if row[1] == 'S':
                        tech = row[0]
                        totalSale = row[4]
                        commission = row[11]
                        tips = row[10]
                        empDict[tech] = [totalSale,commission,tips]
                except Exception as e:
                    print('Cannot iterate to find tech')
        # pack any employee data that still in storage because iterater
        # has not reached a row with datetime
        self.salesJson[day] = empDict.copy()
        empDict.clear()

    def updateJsonFileDelXl(self, path):
        if os.path.isfile(self.jsonPfname):
            size = os.path.getsize(self.jsonPfname)
            if size < 10:
                # sometimes empty json can have {} and thats 2 bytes
                # this is an empty file so we can just dump the whole json
                with open(self.jsonPfname,'w+') as writer:
                    json.dump(self.salesJson,writer,indent=4,sort_keys=True)
                sg.easy_print('Status: Salon.updateJsonFile > is file but considered empty; overwrite')
            else:
                with open(self.jsonPfname,'r') as reader:
                    data = json.load(reader)

                # find what day ended in file and append dates greater than that
                # or another way, just jump and do a '|' (straight line up not slash)
                # to add or up update with the right side taking priority to replace left side
                self.salesJson = data | self.salesJson

                with open(self.jsonPfname,'w+') as writer:
                    json.dump(self.salesJson,writer, indent=4,sort_keys=True)
                print('Status: Salon.updateJsonFile > json exists, merging data')
        else:
            with open(self.jsonPfname,'w+') as writer:
                json.dump(self.salesJson, writer, indent=4, sort_keys=True)
                print('Status: Salon.updateJsonFile > no json exists, creating new one')

        # now delete recently downloaded excel from website in tmp folder
        filename = max([f for f in os.listdir(path)],
                       key=lambda xa: os.path.getctime(os.path.join(path,xa)))
        os.remove(path + filename)

    def getJsonRange(self, sDate, eDate):
        """
        With the given date range, returns a dictionary of days with their
        respective income for all employees
        Args:
            sDate: (string)
            eDate: (string)

        Returns:
            Dictionary where keys are datetime and values are dictionaries of
            employees and their income
        """
        # have to load json file, sometimes current and previous commands
        # have not populated the internal json
        with open(self.jsonPfname,'r') as reader:
            self.salesJson = json.load(reader)

        # list of keys formatted to datetime objects
        keys = [datetime.datetime.strptime(i,'%m/%d/%Y') for i in self.salesJson]
        wantedRange = dict()
        sdate = datetime.datetime.strptime(sDate,'%m/%d/%Y')
        edate = datetime.datetime.strptime(eDate,'%m/%d/%Y')
        for k in keys:
            if k >= sdate and k <= edate:
                # convert key back to string to match json
                kstr = datetime.datetime.strftime(k,'%m/%d/%Y')
                wantedRange[k] = self.salesJson[kstr]
        print(wantedRange)
        return wantedRange

    def getPayroll(self):
        # TODO start here
        pass

    def getEmps(self, name=None):
        emps = {}
        for name, empObj in self.Emps.items():
            emps[name] = empObj.getInfo()
        return emps

    def getDataToSave(self):
        emps = {}
        for empObjKeys, obj in self.Emps.items():
            emps[empObjKeys] = obj.getInfo()
        data = {'name': self.salonName,
                'login': {'username': self.zotaUname, 'password': self.zotaPass},
                'salesJson': self.jsonPfname,
                'salesXl': self.salesXl,
                'payments': self.paymentsXl,
                'employees': emps
                }

        return data

    def mergeSheetToBook(self,fname,path,book):
        '''
        copy sheet from new downloaded book and merge it with a book that keeps track of weekly amounts
        sheet name is the first day of the week
        Args:
            fname:
            path:
            book:

        Returns:

        '''
        tempPathAndFname = path + fname
        sheetName = fname.replace('.xlsx','')

        # import new workbook sheet to existing book and delete new book
        wb_target = openpyxl.load_workbook(book)

        # before copying new temp sheet into weeklyDB, delete existing match
        if sheetName in wb_target.sheetnames:  # remove default sheet
            wb_target.remove(wb_target[sheetName])

        target_sheet = wb_target.create_sheet(sheetName)
        wb_source = openpyxl.load_workbook(tempPathAndFname)
        source_sheet = wb_source['Sales Summary']
        xlHelper.copy_sheet(source_sheet,target_sheet)
        wb_target.save(book)
        # remove temporary downloaded file from zota after extracting info
        os.remove(tempPathAndFname)

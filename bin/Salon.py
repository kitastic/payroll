import os
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
from pprint import PrettyPrinter
import string
from pathlib import Path

pp = PrettyPrinter(
    indent=2,
    width=100,
    compact=True,
    sort_dicts=False,
)


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
                                'employees': {'Name': { 'pay': 0, 'rent': 0, 'fees': 0,'active':bool, 'id': int,
                                'salonName': str, 'name': empname,
                                                        'paygrade':{'regType': True for regular False for special
                                                                    'regular': {'commission':, 'check':, }
                                                                    'special': {'commissionspecial', 'checkdeal':,
                                                                    'checkoriginal':,}}},
                                              'Name2': { ... }
                                             }},
        """
        super().__init__()
        # at this point, the keys in bundle have been alphabetized by json
        self.employees = bundle['employees']
        self.zotaUname = bundle['login']['username']
        self.zotaPass = bundle['login']['password']
        self.salonName = bundle['name']
        self.paymentsFnames = bundle['paymentsFnames']
        self.path = bundle['path']
        self.salesFnames = bundle['salesFnames']    # dict of json files names, key=year

        # variables stored during program runtime
        self.salesDict = dict()  # {year: {datetime: {empName: [total, comm, tips]}}
        self.Emps = dict()  # holds employee objects
        self.setupSalon()

    def setupSalon(self):
        """
            Retrieves all sales data from json and creates employee objects
        Returns:
            None
        """
        if self.salesFnames:
            for year, fname in self.salesFnames.items():
                try:
                    if os.path.getsize(self.path+fname) > 10:
                        with open(self.path+fname,'r') as reader:
                            self.salesDict = json.load(reader)
                except FileNotFoundError:
                    print(f'[Salon.setupSalon] {self.salonName} did not find any json')

        for emp,info in self.employees.items():
            if not info['paygrade']['regType']:
                if info['paygrade']['special']['checkdeal'] == 0:
                    self.Emps[string.capwords(emp)] = Employee.EmployeeCash(info)
                else:
                    self.Emps[string.capwords(emp)] = Employee.EmployeeSpecial(info)
            else:
                self.Emps[string.capwords(emp)] = Employee.Employee(info)

    def createEmpFromGui(self,name,empData):
        self.Emps[string.capwords(name)] = Employee.Employee(empData[string.capwords(name)])

    def createEmpReg(self,name):
        newEmp = {
            name:{'active':True,
                  'id':0,'name':name,'salonName':self.salonName,'pay':0,'fees':0,'rent':0,
                  'paygrade':{'regType':True,
                              'regular':{'commission':6,'check':6},
                              'special':{'commissionspecial':0,'checkdeal':0,
                                         'checkoriginal':0}
                              }}}
        self.Emps[name] = Employee.Employee(newEmp[name])

    def updateEmpFromGui(self,name,empData):
        # easiest way is to remove existing dictionary and set new one
        self.Emps.pop(name)
        self.Emps[name] = Employee.Employee(empData[name])

    def deleteEmp(self,name):
        deletedValue = self.Emps.pop(name)
        print(deletedValue)

    def readSalesXltoJson(self, pfName):
        if not os.path.isfile(pfName):
            print(f'[Salon.readSalesXltoJson]: {self.salonName} cannot read {pfName}')
            return

        workBook = openpyxl.load_workbook(pfName)
        workSheet = workBook.active

        # keys are employee names, values are their totals for the day
        empDict = dict()
        tmpSales = dict()   # daily sales to be inserted in to sales json which is yearly keyed
        day = ''
        currentYr = False

        for row in workSheet.iter_rows(values_only=True):
            if isinstance(row[0],datetime.datetime):
                # if employees dictionary has data, copy it to sales dictionary
                # before setting new day and getting new day data
                if empDict and day != 0:  # if not False
                    tmpSales[day] = empDict.copy()
                    empDict.clear()
                # day is going to be dictionary key, but needs to be
                # converted to string because datetime is not serializable
                # by json
                day = datetime.datetime.strftime(row[0],'%m/%d/%Y')
                year = row[0].year
                if not currentYr:
                    currentYr = year
                else:
                    if year != currentYr:
                        self.salesDict[year] = tmpSales.copy()
                        tmpSales.clear()
                        currentYr = year
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
        tmpSales[day] = empDict.copy()
        self.salesDict[currentYr] = tmpSales.copy()
        empDict.clear()
        tmpSales.clear()

    def updateJsonFileDelXl(self,path):
        for year, days in self.salesDict.items():
            fname = f'{self.salonName}Sales{year}.json'
            if os.path.isfile(self.path+fname):
                size = os.path.getsize(self.path+fname)
                if size < 10:
                    # sometimes empty json can have {} and thats 2 bytes
                    # this is an empty file so we can just dump the whole json
                    with open(self.path+fname,'w+') as writer:
                        json.dump(self.salesDict[year],writer,indent=4,sort_keys=True)
                    sg.easy_print('Status: Salon.updateJsonFile > is file but considered empty; overwrite')
                else:
                    with open(self.path+fname,'r') as reader:
                        data = json.load(reader)

                    # find what day ended in file and append dates greater than that
                    # or another way, just jump and do a '|' (straight line up not slash)
                    # to add or up update with the right side taking priority to replace left side
                    self.salesDict[year] = data | self.salesDict[year]

                    with open(self.path+fname,'w+') as writer:
                        json.dump(self.salesDict[year],writer,indent=4,sort_keys=True)
                    print('Status: Salon.updateJsonFile > json exists, merging data')
            else:
                with open(self.path+fname,'w+') as writer:
                    json.dump(self.salesDict[year],writer,indent=4,sort_keys=True)
                    print('Status: Salon.updateJsonFile > no json exists, creating new one')
        if path:
            # now delete recently downloaded excel from website in tmp folder
            filename = max([f for f in os.listdir(path)],
                           key=lambda xa:os.path.getctime(os.path.join(path,xa)))
            os.remove(path + filename)

    def getJsonRange(self,sDate,eDate):
        """
            With the given date range, returns a dictionary of days with their
            respective income for all employees.
            have to load json file, sometimes current and previous commands
            have not populated the internal json; ie this is the first command
            when starting up the gui window. When the range spans two years,
            just gather data from 2 jsons into one temp dict and then iterate
            for given range
        Args:
            sDate: (string)
            eDate: (string)
        Returns:
            Dictionary where keys are datetime and values are dictionaries of
            employees and their income
        """
        sdate = datetime.datetime.strptime(sDate,'%m/%d/%Y')
        edate = datetime.datetime.strptime(eDate,'%m/%d/%Y')

        if not os.path.isfile(f'{self.path}{self.salonName}Sales{sdate.year}.json'):
            print(f'[Salon.getJsonRange] {self.salonName} file not found')
            return False


        range = []
        if sdate.year != edate.year:
            range = [sdate.year, edate.year]
        else:
            range = [sdate.year]
        tmpSales = dict()
        # grab all dates from, maybe both years into tmpSales
        for year in range:
            with open(f'{self.path}{self.salonName}Sales{year}.json', 'r') as reader:
                tmpSales = tmpSales | json.load(reader)

        keys = [datetime.datetime.strptime(i,'%m/%d/%Y') for i in tmpSales]
        wantedRange = dict()
        for k in keys:
            if k >= sdate and k <= edate:
                # convert key back to string to match json
                kstr = datetime.datetime.strftime(k,'%m/%d/%Y')
                wantedRange[k] = tmpSales[kstr]
        return wantedRange

    def getPayroll(self,request):
        """
            given startdate and enddate, salon will tell each employee to calculate
            their own payroll and return their report back
        Args:
            request: (list) [startDate, endDate]

        Returns:

        """
        sDate = request[0]
        eDate = request[1]
        # TODO start debugging here
        week = self.getJsonRange(sDate,eDate)
        if not week:
            return False

        sorted = {}
        # rearrange dictionary keys from days to employees
        for dates,value in week.items():
            for e in value:
                sorted[e.lower()] = {}
        for dates,value in week.items():
            for e,total in value.items():
                sorted[e.lower()][dates] = total
        # pp.pprint(sorted)
        # compare for extra employees , ie 'anybody*', not currently in settings DB and create new regular ones
        salesEmployees = [string.capwords(n) for n in sorted]
        currentEmployees = []
        for key,obj in self.Emps.items():
            currentEmployees.append(string.capwords(key))
        # create Employees for any extra in sales so they can calculate their sales
        for e in salesEmployees:
            if e not in currentEmployees:
                agree = sg.popup_ok_cancel(
                    f'{e} not found in current employees list.\n\nWould you like to add employee to database?')
                if agree == 'OK':
                    self.createEmpReg(e)
                else:
                    print(f'INFO: skipping payroll calculations for {e}.')
        # now tell all employees to calculate
        payrollPkt = {}
        for eName,eObj in self.Emps.items():
            for e,val in sorted.items():
                if eName in string.capwords(e):
                    eObj.calculatePayroll(val)
                    payrollPkt[eName] = eObj.getPrintOut()
        return payrollPkt

    def getEmpStatus(self):
        status = {}
        for name,obj in self.Emps.items():
            status[name] = obj.getStatus()
        return status

    def getEmps(self,name=None):
        emps = {}
        for name,empObj in self.Emps.items():
            emps[name] = empObj.getInfo()
        return emps

    def exportTxtPayroll(self,sDate,eDate):
        for name,obj in self.Emps.items():
            printableData = ''
            try:
                printableData = obj.getPrintOut()
            except Exception:
                sg.popup_ok('ERROR: Salon.exportTxtPayroll: employee data is empty\n'
                            'Try to calculate payroll first')
            if len(printableData) > 5:
                pfname = f'../payroll/{self.salonName}/{self.salonName[0]}.{sDate.replace("/",".")}.{name}.txt'
                Path(pfname.replace(f'{self.salonName[0]}.{sDate.replace("/",".")}.{name}.txt','')).mkdir(parents=True,
                                                                                                          exist_ok=True)
                with open(pfname,'w') as f:
                    f.writelines(printableData)
                print(f'INFO: ({self.salonName}) finished exporting text files')

    def getDataToSave(self):
        emps = {}
        for empObjKeys,obj in self.Emps.items():
            emps[empObjKeys] = obj.getInfo()
        data = {'name':self.salonName,
                'login':{'username':self.zotaUname,'password':self.zotaPass},
                'salesFnames': self.salesFnames,
                'path': self.path,
                'employees':emps
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

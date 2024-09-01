import os
import math
import openpyxl
import datetime
import pandas as pd
import re
import json
import PySimpleGUI as sg
from pprint import PrettyPrinter
import string

import Bot
import Employee
import xlHelper

pp = PrettyPrinter(
    indent=2,
    width=100,
    compact=True,
    sort_dicts=False,
)


class Salon(Bot.Bot):
    def __init__(self, bundle):
        """

        Args:
            bundle: (dictionary) layout:
                    bundle =  { 'name': 'upscale',
                                'login': {'username': 'upscalemanager', 'password': 'Joeblack334$'},
                                'salesJson':
                                'active': bool   # might not need yet
                                'payments': 'uPayments.xlsx',
                                'employees': {
                                name:{'active':True,
                                      'id': idNum, 'name': nameCapitalized, 'salonName':salon,
                                      'pay6': pay6, 'pay7': pay7
                                      'fees':fees, 'rent':rent, 'printchecks': printchecks,
                                      'type':{'role': 'role'
                                                 'regular':{'commission': commission, 'check': check},
                                                 'special':{'commissionspecial': comspec, 'checkdeal': checkdeal,
                                                 'checkoriginal': checkoriginal, 'cashrate': cashrate}
                                      }}}
        """
        super().__init__()
        # at this point, the keys in bundle have been alphabetized by json
        self.employees = bundle['employees']
        self.zotaUname = bundle['login']['username']
        self.zotaPass = bundle['login']['password']
        self.salonName = bundle['name']
        self.paymentsFnames = bundle['paymentsFnames']
        self.path = bundle['path']
        # self.salesFnames = bundle['salesFnames']  # dict of json files names, key=year
        self.active = bundle['active']
        # variables stored during program runtime
        self.salesDict = dict()  # {year: {datetime: {empName: [total, comm, tips]}}
        self.modifiedSalesDict = dict()
        self.Emps = dict()  # holds employee objects
        self.modFlag = False # to know whether working with regular sales or modified sales
        self.setupSalon()

    def setupSalon(self):
        """
            Retrieves all sales data from json and creates employee objects
        Returns:
            None
        """
        # if self.salesFnames:
        #     for year, fname in self.salesFnames.items():
        #         try:
        #             if os.path.getsize(self.path + fname) > 10:
        #                 with open(self.path + fname, 'r') as reader:
        #                     self.salesDict = json.load(reader)
        #         except FileNotFoundError:
        #             print(f'[Salon.setupSalon] {self.salonName} did not find any json')

        for emp, info in self.employees.items():
            if info['type']['role'].lower() in ['checkdeal', 'cash']:
                self.Emps[string.capwords(emp)] = Employee.EmployeeSpecial(info)
            elif info['type']['role'] == 'Janitor':
                self.Emps[string.capwords(emp)] = Employee.EmployeeJanitor(info)
            else:
                self.Emps[string.capwords(emp)] = Employee.Employee(info)

    def createEmpFromGui(self, name, empData):
        self.Emps[name] = Employee.Employee(empData[name])

    def createEmpReg(self, name):
        newEmp = {
            name: {'active': True,
                   'name': name, 'checkName': '', 'salonName': self.salonName,
                   'pay6': 0, 'pay7': 0, 'fees': 0, 'rent': 0,
                   'boothcustom': 0, 'boothcustomflag': False, 'printchecks': True,
                   'type': {'role': 'Regular',
                            'regular': {'commission': 0.6, 'check': 0.6, 'boothrent': 0},
                            'special': {'commissionspecial': 0, 'checkdeal': 0,
                                        'checkoriginal': 0, 'cashrate': 0}
                            },
                   "workdays": {"fri": False,
                                "mon": False,
                                "sat": False,
                                "sun": False,
                                "thu": False,
                                "tue": False,
                                "wed": False
                                },
                   }}
        self.Emps[name] = Employee.Employee(newEmp[name])

    def deleteEmp(self, name):
        deletedValue = self.Emps.pop(name)
        print(deletedValue)

    def exportPayroll(self, sDate, eDate, format):
        empdata = {}
        xldict = dict()
        for name, obj in self.Emps.items():
            printableData = ''
            try:
                printableData = obj.getPrintOut()
            except Exception:
                sg.popup_ok('ERROR: Salon.exportPayroll: employee data is empty\n'
                            'Try to calculate payroll first')
            if len(printableData) > 5:
                if obj.role not in ['Janitor', 'Owner']:
                    empdata[name] = printableData

        htmlheader = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    @media print {
                        .pagebreak {
                            clear: both;
                            page-break-before: always;
                        }
                    }
                    </style>
                    </head>
                    <pre>
                    <body>"""
        htmllogo = False
        if self.salonName.lower() == 'upscale' and os.path.isfile('images/ulogo.png'):
            htmllogo = """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <img src="ulogo.png" style="width:100px"><br>"""
        elif self.salonName.lower() == 'nails' and os.path.isfile('images/nlogo.png'):
            htmllogo = """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <img src="G:/My Drive/payrollAutomation/bin/images/nlogo.png" style="width:100px"><br>"""
        htmlpagebreak = """<div class="pagebreak"></div>"""
        htmlfooter = """
        </body>
        <pre>
        </html>
        """
        pfname = f'../payroll/{sDate.replace("/", ".")}.{self.salonName}.html'
        with open(pfname, 'w+') as write:
            write.writelines(htmlheader)
            write.write('\n')
            lastValue = list(empdata.values())[-1]
            for values in empdata.values():
                if htmllogo:
                    write.writelines(htmllogo)
                write.writelines(values)
                if values != lastValue:
                    write.writelines(htmlpagebreak)
            write.writelines(htmlfooter)

        # now update yearly excel book for 1099
        # pass path, salon prefix for sheetname, data
        path = f'../payroll/{sDate[-4:]}.xlsx'
        sheet = f'{self.salonName[0].lower()}.salary'
        data = []
        for emp, obj in self.Emps.items():
            if obj.printchecks or obj.role == 'Cash':
                # cash employee must be explicitly included because there is no check to print
                xldict = xldict | {emp: {}}
                xldict[emp] = obj.getXlReport()
                sdate = datetime.datetime.strptime(sDate, '%m/%d/%Y')
                # edate = sdate + datetime.timedelta(days=6)
                # eDate = datetime.datetime.strftime(eDate, '%m/%d/%Y')
                # remove nickname in parentheses
                xldict[emp]['name'] = re.search('^[^(]+', emp).group(0)
                xldict[emp]['date'] = eDate
                # when exporting to excel, data list order and excel sheet column numbers align.
                # column names and dictionary keys do not matter
                if len(obj.checkName) > 1:
                    data.append([sDate, eDate, obj.checkName,
                                 math.ceil(xldict[emp]['bcash']), math.ceil(xldict[emp]['bcheck']),
                                 math.ceil(xldict[emp]['checkdeal']), xldict[emp]['booth']])
                else:
                    data.append([sDate, eDate, emp.upper(),
                                 math.ceil(xldict[emp]['bcash']), math.ceil(xldict[emp]['bcheck']),
                                 math.ceil(xldict[emp]['checkdeal']), xldict[emp]['booth']])
        df = pd.DataFrame(data, )
        reader = pd.read_excel(path, sheet_name=sheet, index_col=False)
        startRow = len(reader.index) + 1
        try:
            with pd.ExcelWriter(path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name=sheet, header=False, index=False, startrow=startRow)
        except Exception as e:
            return False, f'[Salon.exportPayroll.197] error: {e}'
        return True, f'[Salon.exportPayroll]: {self.salonName} finished exporting {pfname}'

    def getDataToSave(self):
        emps = {}
        for empObjKeys, obj in self.Emps.items():
            emps[empObjKeys] = obj.getInfo()
        data = {'name': self.salonName,
                'login': {'username': self.zotaUname, 'password': self.zotaPass},
                'active': self.active,
                'path': self.path,
                'employees': emps,
                'paymentsFnames': self.paymentsFnames,
                }
        return data

    def getEmps(self, name=None):
        emps = {}
        for name, empObj in self.Emps.items():
            emps[name] = empObj.getInfo()
        return emps

    def getActiveOnlyEmps(self, name=None):
        emps = {}
        for name, empObj in self.Emps.items():
            if empObj.get_active_status():
                emps[name] = empObj.getInfo()
        return emps

    def getEmpStatus(self):
        status = {}
        for name, obj in self.Emps.items():
            result = obj.getStatus()
            if result:
                status[name] = result
        return status

    def getJsonRange(self, sDate, eDate, type):
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
            type: (string) 'regular' or 'modified'
        Returns:
            bool, data: boolean to signal operation status, and either error msg or Dictionary where keys are
            datetime and values are dictionaries of employees and their income
        """
        sdate = datetime.datetime.strptime(sDate, '%m/%d/%Y')
        edate = datetime.datetime.strptime(eDate, '%m/%d/%Y')
        date_range = []
        if sdate.year != edate.year:
            start = sdate.year
            while start <= edate.year:
                date_range.append(start)
                start += 1
        else:
            date_range = [sdate.year]

        tmpSales = dict()
        file_name = f'{self.path}{self.salonName}'
        file_name += 'Sales' if type == 'regular' else 'ModifiedSales'

        # grab all dates from, maybe both years into tmpSales
        for year in date_range:
            tmp_file_name = f'{file_name}{str(year)}.json'
            if not os.path.isfile(tmp_file_name):
                return False, f'[Salon.getJsonRange] {self.salonName} file not found'
            else:
                try:
                    with open(tmp_file_name, 'r') as reader:
                        tmpSales = tmpSales | json.load(reader)
                except Exception as e:
                    return False, f'[Salon.getJsonRange] {self.salonName} {type} > {e}'

        keys = [datetime.datetime.strptime(i, '%m/%d/%Y') for i in tmpSales]
        wantedRange = dict()
        for k in keys:
            if k >= sdate and k <= edate:
                # convert key back to string to match json
                kstr = datetime.datetime.strftime(k, '%m/%d/%Y')
                wantedRange[k] = tmpSales[kstr]

        if not wantedRange and type == 'regular':
            # must at least have original sales data to continue
            return False, f'[Salon.getJsonRange] {self.salonName} {type} > No data within date range'

        return True, wantedRange

    def getPayroll(self, sDate, eDate, guarantee, booth):
        """
            given startdate and enddate, salon will tell each employee to calculate
            their own payroll and return their report back
        Args:

        Returns:
            dictionary of employee key and their payroll values
        """
        status, week = self.getJsonRange(sDate, eDate, 'regular')
        if not status:
            return False, week  # week is now error msg

        status_mod, modifiedWeek = self.getJsonRange(sDate, eDate, 'modified')
        '''
        At this point, modifiedWeek may be an empty dictionary because there is no available 
        modified sales yet. But that's okay, we can still continue.
        Week is dictionary of days as keys and values is all employees income working that day,
        sorted rearranges it to  where keys are employees and values are their daily income
        '''
        # sorted rearranges it to  where keys are employees and values are their daily income
        sorted = {}
        sortedModified = {}
        # rearrange dictionary keys from days to employees
        for dates, value in week.items():
            for emp in value:
                # string.capwords() was added because sometimes names from zota can have extra spaces at end
                # we validate the name to make sure it matches with what we have saved already
                name = string.capwords(emp)
                sorted[name.lower()] = {}
        for dates, value in week.items():
            for emp, total in value.items():
                name = string.capwords(emp)
                sorted[name.lower()][dates] = total

        if status_mod:
            for dates, value in modifiedWeek.items():
                for e in value:
                    sortedModified[e.lower()] = {}
            for dates, value in modifiedWeek.items():
                for e, total in value.items():
                    sortedModified[e.lower()][dates] = total

        # pp.pprint(sorted)
        # compare for extra employees , ie 'anybody*', not currently in settings DB and create new regular ones
        salesEmployees = [string.capwords(n) for n in sorted]
        currentEmployees = [key for key, obj in self.Emps.items()]
        # create Employees for any extra in sales so they can calculate their sales
        for employee in salesEmployees:
            if employee not in currentEmployees:
                agree = sg.popup_ok_cancel(
                    f'{employee} not found in current employees list.\n\nWould you like to add employee to database?')
                if agree == 'OK':
                    employee.replace('  ', ' ')
                    self.createEmpReg(employee)
                else:
                    print(f'INFO: skipping payroll calculations for {employee}.')
        # now tell all employees to calculate
        payrollPkt = {}
        salon_fee_days = {
            'mon': False,
            'tue': False,
            'wed': False,
            'thu': False,
            'fri': False,
            'sat': False,
            'sun': False
        }
        # we Must find janitor's work days first to calculate which day to have fees
        for eName, eObj in self.Emps.items():
            if eObj.role == 'Janitor':
                salon_fee_days.update(eObj.workdays)
                eObj.calculatePayroll(sales=None)
                payrollPkt[eObj.name] = eObj.getPrintOut()
        # iterate again after calculating fee days from janitor
        for empSorted, valSorted in sorted.items():
            for emp, empObj in self.Emps.items():
                if empObj.role == 'Janitor':
                    continue    # continues to next item in this loop
                if emp.lower() == empSorted:
                    if status_mod:
                        msales = sortedModified[empSorted]
                    else:
                        msales = None
                    status_pay, msg = empObj.calculatePayroll(sales=valSorted, modified_sales=msales,
                                            fee_days=salon_fee_days, guarantee=guarantee, booth=booth)
                    if not status_pay:
                        return False, msg
                    payrollPkt[emp] = empObj.getPrintOut()
                    break   # breaks out of this loop
        return True, payrollPkt

    def getSalonInfo(self):
        """
            Used for displaying salon info in the salon tab when clicking the load salon button
        Returns:
            list of dictionary login and formatted additional text dislay to go into the output in salon tab
        """
        login = {
            'username': self.zotaUname,
            'password': self.zotaPass,
            'active': self.active
        }
        niceprint = f'path: {self.path},\nactive: {self.active}' \
                    f'\npymentsFnames: {self.paymentsFnames}\n' \
                    f'employees:\n'
        for names in self.Emps:
            niceprint += f'  {names}\n'
        return login, niceprint

    def mergeSheetToBook(self, fname, path, book):
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
        sheetName = fname.replace('.xlsx', '')

        # import new workbook sheet to existing book and delete new book
        wb_target = openpyxl.load_workbook(book)

        # before copying new temp sheet into weeklyDB, delete existing match
        if sheetName in wb_target.sheetnames:  # remove default sheet
            wb_target.remove(wb_target[sheetName])

        target_sheet = wb_target.create_sheet(sheetName)
        wb_source = openpyxl.load_workbook(tempPathAndFname)
        source_sheet = wb_source['Sales Summary']
        xlHelper.copy_sheet(source_sheet, target_sheet)
        wb_target.save(book)
        # remove temporary downloaded file from zota after extracting info
        os.remove(tempPathAndFname)

    def readSalesXltoJson(self, pfName, type):
        """
        Read downloaded sales from webscraping and parse it into a local variable sales dictionary
        Args:
            pfName: path and filename
            type:   'regular' or 'modified' to signal working with original sales or modified sales

        Returns:

        """
        self.toggleStatus(type)
        if not os.path.isfile(pfName):
            return False, f'[Salon.readSalesXltoJson]: {self.salonName} cannot read {pfName}'

        workBook = openpyxl.load_workbook(pfName)
        workSheet = workBook.active
        # keys are employee names, values are their totals for the day
        empDict = dict()
        tmpSales = dict()  # daily sales to be inserted in to sales json which is yearly keyed
        day = ''
        currentYr = False

        for row in workSheet.iter_rows(values_only=True):
            if isinstance(row[0], datetime.datetime):
                # if employees dictionary has data, copy it to sales dictionary
                # before setting new day and getting new day data
                if empDict and day != 0:  # if not False
                    tmpSales[day] = empDict.copy()
                    empDict.clear()
                # day is going to be dictionary key, but needs to be
                # converted to string because datetime is not serializable
                # by json
                day = datetime.datetime.strftime(row[0], '%m/%d/%Y')
                year = row[0].year
                if not currentYr:
                    currentYr = year
                else:
                    if year != currentYr:
                        if self.modFlag:
                            self.modifiedSalesDict[currentYr] = tmpSales.copy()
                        else:
                            self.salesDict[currentYr] = tmpSales.copy()
                        tmpSales.clear()
                        currentYr = year
            elif not row[0]:
                continue
            else:
                try:
                    if row[1] == 'S':
                        if self.modFlag:
                            empDict[row[0]] = {'sales': row[4],
                                               'tips': row[10],
                                               'commission': row[11]}
                        else:
                            empDict[row[0]] = {'sales': row[4],
                                               'tips': row[10]}
                except Exception as e:
                    print('[Salon.readSalesXltoJson] Cannot iterate to find tech')

        # pack any employee data that still in storage because iterator
        # has not reached a row with datetime
        tmpSales[day] = empDict.copy()
        if self.modFlag:
            self.modifiedSalesDict[currentYr] = self.modifiedSalesDict.get(currentYr, {}) | tmpSales
        else:
            self.salesDict[currentYr] = self.salesDict.get(currentYr, {}) | tmpSales
        empDict.clear()
        tmpSales.clear()
        return True, False

    def toggleStatus(self, stat):
        self.modFlag = 'Modified' if stat == 'modified' else False

    def updateEmpFromGui(self, name, empData):
        # easiest way is to remove existing dictionary and set new one
        self.Emps.pop(name)
        if empData[name]['type']['role'] in ['checkdeal', 'cash']:
            self.Emps[name] = Employee.EmployeeSpecial(empData[name])
        elif empData[name]['type']['role'] == 'Janitor':
            self.Emps[name] = Employee.EmployeeJanitor(empData[name])
        else:
            self.Emps[name] = Employee.Employee(empData[name])

    def updateJsonFileDelXl(self, path, type):
        self.toggleStatus(type)
        currentDict = self.modifiedSalesDict if self.modFlag else self.salesDict
        for year, days in currentDict.items():
            fname = f'{self.salonName}ModifiedSales{str(year)}.json' if self.modFlag \
                    else f'{self.salonName}Sales{str(year)}.json'
            if os.path.isfile(self.path + fname):
                size = os.path.getsize(self.path + fname)
                if size > 10:
                    with open(self.path + fname, 'r') as reader:
                        new_data = json.load(reader)

                    # find what day ended in file and append dates greater than that
                    # or another way, just jump and do a '|' (straight line up not slash)
                    # to add or up update with the right side taking priority to replace left side
                    if self.modFlag:
                        self.modifiedSalesDict[year] = self.modifiedSalesDict[year] | new_data
                    else:
                        self.salesDict[year] = self.salesDict[year] | new_data
            with open(self.path + fname, 'w+') as writer:
                if self.modFlag:
                    json.dump(self.modifiedSalesDict[year], writer, indent=4, sort_keys=True)
                else:
                    json.dump(self.salesDict[year], writer, indent=4, sort_keys=True)
        if path is None:
            return  # if no path given, this command was called by Ai to import and no need to delete file

        # now delete recently downloaded excel from website in tmp folder
        if path:
            self.delete_files_in_directory(path)

    def updateSalon(self, salonPkt):
        self.salonName = salonPkt['sname']
        self.zotaUname = salonPkt['login']['username']
        self.zotaPass = salonPkt['login']['password']
        self.active = salonPkt['active']

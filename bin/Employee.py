"""
Steps to perform when changing employee info:
- View.__setup__(): gui design and assigning key
- View.openApp():  put keys into designated tabs to listen for command
- View.togglePaygrade()
- View.parseEmp(): remember key
- View.empToGui(): remember key
- View.clearBtn()
- Employee.__init__() (include updating function documentation)
- Employee.getInfo()

"""

import math
import datetime
import string
import PySimpleGUI as sg


class Employee:
    def __init__(self, data):
        """
        Args:
            data layout: {'active':True,
                      'name': nameCapitalized, 'salonName':salon, 'pay':pay,
                      'fees':fees, 'rent':rent,
                      'pay6': pay6, 'pay7': pay7
                      'printchecks': printchecks,
                      'type':{'role': role,
                              'regular':{'commission': commission, 'check': check},
                              'special':{'commissionspecial': comspec, 'checkdeal': checkdeal,
                                         'checkoriginal': checkoriginal, 'cashrate': cashrate
                              }
                      'workdays': { 'mon': bool,
                                    'tue': bool,
                                    'wed': bool,
                                    'thur': bool,
                                    'fri': bool,
                                    'sat': bool,
                                    'sun': bool
                                 }
                      }}}
        """
        # dict.get(key, valueifkeyerror) If dict is nested attach additional .get() for each level
        self.name = data.get('name', '')
        self.checkName = data.get('checkName', '')
        self.salonName = data.get('salonName', '')
        self.pay6 = data.get('pay6', 0)
        self.pay7 = data.get('pay7', 0)
        self.rent = data.get('rent', 0)
        self.fees = data.get('fees', 0)
        self.checkbonus = data.get('checkbonus', 0)
        self.checkfee = data.get('checkfee', 0)
        self.cashbonus = data.get('cashbonus', 0)
        self.cashfee = data.get('cashfee', 0)
        self.active = data.get('active', True)
        self.role = data.get('type', {}).get('role', 'regular')
        self.commission = data.get('type', {}).get('regular', {}).get('commission', 0)
        self.commissionspecial = data.get('type', {}).get('special', {}).get('commissionspecial', 0)
        self.check = data.get('type', {}).get('regular', {}).get('check', 0.6)
        self.checkdeal = data.get('type', {}).get('special', {}).get('checkdeal', 0)
        self.checkoriginal = data.get('type', {}).get('special', {}).get('checkoriginal', 0.6)
        self.cashrate = data.get('type', {}).get('special', {}).get('cashrate', 0)
        self.printchecks = data.get('printchecks', True)
        self.boothcustom = data.get('boothcustom', 0)
        self.boothcustomflag = data.get('boothcustomflag', False)
        self.workdays = data.get('workdays', {"fri": False,
                                              "mon": False,
                                              "sat": False,
                                              "sun": False,
                                              "thu": False,
                                              "tue": False,
                                              "wed": False
                                              })
        self.sales = {}
        self.modifiedSales = {}
        self.sDate = ''                             # m.d.y for saving text purpose
        self.boothrent = 0                          # universal booth rent, whether salon set, custom personal, etc
        self.boothSummary = {                       # all values are copied from zota especially commission
                             'total': 0,
                             'tips': 0,
                             'commission': 0,
                             'check': 0,
                            }
        self.paySummary = {
                            'total': 0,
                            'commission': 0,        # actual commission set in program
                            'check': 0,             # raw check amount before bao luong
                            'cash': 0,              # raw cash amount before bao luong
                            'basepaycheck': 0,      # check amt if bao luong
                            'basepaycash': 0,       # check amt if bao luong
                            'paycheck': 0,          # actual check to be paid before adding tips
                            'paycash': 0,           # actual cash to be paid before subtracting fees
                            'tips': 0,
                            'fees': 0,              # clean up fees for whole week, based on janitor worked days
                            'daysworked': 0,
                            'metGoal': False,       # checks if enough luong bao
                            }
        self.xlreport = {                           # amounts in here are actual write out amounts
                         'check': 0,                # based off of regular sales
                         'checkdeal': 0,           # based off of regular sales
                         'cash': 0,                 # based off of regular sales
                         'booth': 0,                # difference between regular check and booth check
                         'bcheck': 0,               # based off of modified sales
                         'bcash': 0                 # based off of modified sales
                         }
        self.payPrint = ''

    def calculatePayroll(self, sales, modified_sales, fee_days, guarantee, booth):
        """
        Args:
            sales: dictionary of daily sales, keys are datetime
            modified_sales: same as sales but modified data
            fee_days: days that janitor work
            guarantee: [bool] will guarantee base pay regardless of days worked
            booth: integer of how much booth rent is set manually
        Returns:
            bool and either error msg or just a True value
        """
        if self.role != 'janitor':
            self.sales = sales.copy()
            if modified_sales:
                self.modifiedSales = modified_sales.copy()
            status, msg = self.genericCalculate(fee_days, guarantee, booth)
            if not status:
                return False, msg
            else:
                return True, True

    def genericCalculate(self, fee_days, guarantee, booth):
        """
        Generic calculation of payroll and generates a payroll printout saved locally in self.payrollPrint.
        Args:
            fee_days: days that janitor work
            guarantee: [bool] will guarantee base pay regardless of days worked
            booth: [bool] will signal manual booth rent
        Returns:
        """
        tips, commissionSales, totalSales, daysWorked, personal_fees = [0 for i in range(1, 6)]
        boothSales = 0
        boothTips = 0
        boothCommission = 0
        tmpCommissionForOutput = 0
        if self.role.capitalize() in ['Regular', 'Owner']:
            tmpCommissionForOutput = self.commission
        else:
            tmpCommissionForOutput = self.commissionspecial

        # this part is the text of the daily summaries based off of regular ticket printout
        out = f'{"  " + string.capwords(self.salonName) + "  ":=^48}\n'
        out += f'{self.name:<48}\n'
        out += f'{" Daily ":-^48}\n'
        out += f'{"Day":<17}{"Tips":>10}{"Sales":>10}\n'

        for day, amt in self.sales.items():
            dayName = day.isoweekday()  # monday = 1
            # this is the part where we compare janitor and employee work days to know if there is a fee
            if dayName == 1 and fee_days['mon']:
                personal_fees += self.fees
            elif dayName == 2 and fee_days['tue']:
                personal_fees += self.fees
            elif dayName == 3 and fee_days['wed']:
                personal_fees += self.fees
            elif dayName == 4 and fee_days['thu']:
                personal_fees += self.fees
            elif dayName == 5 and fee_days['fri']:
                personal_fees += self.fees
            elif dayName == 6 and fee_days['sat']:
                personal_fees += self.fees
            elif dayName == 7 and fee_days['sun']:
                personal_fees += self.fees

            bDailySales = 0
            bDailyTip = 0
            # instead of multiplying by self.commissionbooth, get value directly from zota because of
            # percentage rounding discrepancies
            bDailyCommission = 0
            if self.modifiedSales:
                bDailySales = self.modifiedSales.get(day, {}).get('sales', 0)
                bDailyTip = self.modifiedSales.get(day, {}).get('tips', 0)
                bDailyCommission = self.modifiedSales.get(day, {}).get('commission', 0)

            tipForDay = amt['tips']
            tips += amt['tips']
            commissionSales += (amt['sales'] * tmpCommissionForOutput)  # no need
            boothCommission += bDailyCommission
            totalSales += amt['sales']
            boothSales += bDailySales
            boothTips += bDailyTip
            if amt['sales'] > 0:
                daysWorked += 1
            d = datetime.datetime.strftime(day, '%m/%d:%a')
            out += f'{d:<17}{tipForDay:>10.2f}{amt["sales"]:>10.2f}\n'

        out += f'{" ":17}{"-":->20}\n'
        out += f'{" ":17}{tips:>10.2f}{totalSales:>10.2f}\n\n\n'
        out += f'{"":*^48}\n'
        out += f'{" Summary ":-^48}\n'
        out += f'{"Total Sale":<10}{" ":5}{totalSales:>10.2f}\n'
        out += f'{"Commission":<10}{" ":5}{commissionSales:>10.2f}\n'
        out += f'{"Tips":<10}{" ":5}{tips:>10.2f}\n'
        out += f'{" ":15}{"-":->10}\n'
        out += f'{"Sales Pay":<10}{" ":5}{commissionSales + tips:>10.2f}\n'
        out += f'{"=":=^48}\n\n\n'
        self.payPrint = out
        if self.role.capitalize() in ['Regular', 'Owner']:
            check = (commissionSales * self.check)
            cash = commissionSales - check
        else:
            check = commissionSales * self.checkoriginal
            cash = commissionSales - check

        # this is to keep track daily performance if metgoal
        basePayPerDay = self.pay6 / 6
        basePayPerRange = basePayPerDay * daysWorked

        basepaycheck = 0
        basepaycash = 0
        if daysWorked == 6:
            if self.role.capitalize() in ['Regular', 'Owner']:
                basepaycheck = (self.pay6 * self.check)
                basepaycash = self.pay6 - basepaycheck
            else:
                basepaycheck = (self.pay6 * self.checkoriginal)
                basepaycash = self.pay6 - basepaycheck
        elif daysWorked == 7:
            basePayPerDay = (self.pay6 + self.pay7) / 7
            basePayPerRange = basePayPerDay * daysWorked
            if self.role.capitalize() in ['Regular', 'Owner']:
                basepaycheck = (self.pay6 + self.pay7) * self.check
                basepaycash = (self.pay6 + self.pay7) - basepaycheck
            else:
                basepaycheck = (self.pay6 + self.pay7) * self.checkoriginal
                basepaycash = (self.pay6 + self.pay7) - basepaycheck
        elif guarantee:
            if self.role.capitalize() in ['Regular', 'Owner']:
                basepaycheck = basePayPerRange * self.check
                basepaycash = basePayPerRange - basepaycheck
            else:
                basepaycheck = basePayPerRange * self.checkoriginal
                basepaycash = basePayPerRange - basepaycheck

        metgoal = False if commissionSales < basePayPerRange else True

        self.paySummary['total'] = totalSales
        self.paySummary['commission'] = commissionSales
        self.paySummary['check'] = check
        self.paySummary['cash'] = cash
        self.paySummary['basepaycheck'] = basepaycheck
        self.paySummary['basepaycash'] = basepaycash
        self.paySummary['tips'] = tips
        self.paySummary['fees'] = personal_fees
        self.paySummary['daysworked'] = daysWorked
        self.paySummary['metGoal'] = metgoal
        self.boothSummary['total'] = boothSales
        self.boothSummary['tips'] = boothTips
        self.boothSummary['commission'] = boothCommission
        self.boothSummary['check'] = boothCommission + boothTips

        # neu lam du ngay thi check coi can bao luong hay ko
        if (self.paySummary['daysworked'] >= 6) | guarantee:
            self.paySummary['paycheck'] = self.paySummary['check'] if self.paySummary['metGoal'] else \
                self.paySummary['basepaycheck']
            self.paySummary['paycash'] = self.paySummary['cash'] if self.paySummary['metGoal'] else \
                self.paySummary['basepaycash']
        else:
            self.paySummary['paycheck'] = self.paySummary['check']
            self.paySummary['paycash'] = self.paySummary['cash']

        # we need to figure out exact amount of check pay out based on regular sales first
        # then we use it to deduct from modified sale's data to find booth rent amount
        self.xlreport['check'] = (self.paySummary['paycheck'] + self.paySummary['tips']
                                  + self.checkbonus - self.checkfee)
        self.xlreport['cash'] = (self.paySummary['cash'] - self.paySummary['fees']
                                 - self.rent + self.cashbonus - self.cashfee)

        if self.boothcustomflag:
            # personal custom booth rent specified takes priority
            try:
                self.boothrent = float(self.boothcustom)
            except Exception:
                sg.easy_print(f'Custom booth rent value for {self.name} in {self.salonName} is incorrect.\n'
                              f'Must be a number without spaces. Now setting value to 0.')
                self.boothrent = 0
        elif booth:
            # next priority is salon set manually on main tab
            try:
                self.boothrent = float(booth)
            except ValueError:
                self.boothrent = 0
        elif self.modifiedSales:
            # if not manual booth rent was set but there is available modified sales
            self.boothrent = self.boothSummary['check'] - self.xlreport['check']
        # else self.manualBooth is still = 0
        self.xlreport['booth'] = self.boothrent
        self.xlreport['bcheck'] = self.boothSummary['check']
        self.xlreport['bcash'] = self.xlreport['cash'] - self.boothrent

        out = ''
        out += f'{"Opt1":<15}    {self.paySummary["paycheck"]:>10.2f}\n'
        out += f'{"Tips":<15}  + {self.paySummary["tips"]:>10.2f}\n'
        if self.checkbonus:
            out += f'{"Bonus":<15}  + {self.checkbonus:>10.2f}\n'
        if self.checkfee:
            out += f'{"Fee":<15}  - {self.checkfee:>10.2f}\n'
        out += f'{" ":<15}  {"":-^12}\n'
        out += f'{" ":<15}    {self.xlreport["check"]:>10.2f}\n'
        out += f'{"MS":<15}  + {self.boothrent:>10.2f}\n'
        out += f'{" ":<15}  {"":=^12}\n'
        out += f'{"Opt1 Total":<15}    {math.ceil(self.xlreport["check"] + self.boothrent):>10.2f}\n\n'
        out += f'{"Opt2":<15}    {self.paySummary["paycash"]:>10.2f}\n'
        out += f'{"Fees":<15}  - {self.paySummary["fees"] + self.rent:>10.2f}\n'
        if self.cashbonus:
            out += f'{"Bonus":<15}  + {self.cashbonus:>10.2f}\n'
        if self.cashfee:
            out += f'{"Fee2":<15}  - {self.cashfee:>10.2f}\n'
        out += f'{" ":<15}  {"":-^12}\n'
        out += f'{" ":<15}    {self.xlreport["cash"]:>10.2f}\n'
        out += f'{"MS":<15}  - {self.boothrent:>10.2f}\n'
        out += f'{" ":<15}  {"":=^12}\n'
        out += f'{"Opt2 Total":<15}    {math.ceil(self.xlreport["bcash"]):>10.2f}\n\n'
        self.payPrint += out
        return True, True

    def getPayrollSummary(self):
        return self.paySummary

    def getPrintOut(self):
        return self.payPrint

    def getStatus(self):
        """
        This checks progress of employees during the week.
        """
        if self.commission == 0:
            return False
        try:
            result = {
                'total': math.ceil(self.paySummary['totalsale']),
                'comm': math.ceil(self.paySummary['commission']),
                'tips': math.ceil(self.paySummary['tips']),
                'daysWorked': math.ceil(self.paySummary['daysworked']),
                'metGoal': self.paySummary['metGoal']
            }
            return result
        except Exception:
            print('cannot get from emp {}'.format(self.name))

    def exportPayroll(self):
        sdate = ''
        counter = 0
        while counter < 1:
            for keys in self.sales:
                sdate = datetime.datetime.strftime(keys, '%m.%d.%Y')
            counter += 1

        fname = f'{self.salonName[0]}.{sdate}.{self.name}.txt'
        path = '../tmp/'
        with open(path + fname, 'w+') as file:
            file.writelines(self.payPrint)
        return path + fname

    def getInfo(self):
        return {'active': self.active, 'salonName': self.salonName, 'name': self.name, 'checkName': self.checkName,
                'rent': self.rent, 'fees': self.fees, 'pay6': self.pay6, 'pay7': self.pay7,
                'checkbonus': self.checkbonus, 'checkfee': self.checkfee,
                'cashbonus': self.cashbonus, 'cashfee': self.cashfee,
                'boothcustom': self.boothcustom, 'boothcustomflag': self.boothcustomflag,
                'printchecks': self.printchecks,
                'type': {'role': self.role,
                         'regular': {'commission': self.commission, 'check': self.check},
                         'special': {'commissionspecial': self.commissionspecial, 'checkdeal': self.checkdeal,
                                     'checkoriginal': self.checkoriginal, 'cashrate': self.cashrate}
                         },
                'workdays': self.workdays
                }

    def get_active_status(self):
        return self.active

    def getXlReport(self):
        return self.xlreport


class EmployeeSpecial(Employee):
    """
        Nguoi nay can phai khai income thap cho nen ky check it ma khai so thiet
    """

    def __init__(self, data):
        super().__init__(data)
        self.payrollSummaryEtc = dict()

    def calculatePayroll(self, sales, modified_sales, fee_days, guarantee, booth):
        '''
            so tien check ky ra va so tien check deal se co khac biet.
            check deal la so ky ra va check binh thuong la ho phai khai cuoi nam
        '''

        self.sales = sales.copy()
        boothFlag = False
        if booth:
            try:
                self.manualBooth = int(booth)
                boothFlag = True
            except ValueError:
                self.manualBooth = 0
        if modified_sales:
            self.modifiedSales = modified_sales.copy()
        self.genericCalculate(fee_days, guarantee, booth)
        out = f'{"*":*^40}\n'
        if self.role.lower() == 'checkdeal':
            totalpay = self.paySummary['paycheck'] + self.paySummary['paycash']
            paycheckdeal = totalpay * self.checkdeal
            paycashdeal = totalpay - paycheckdeal
            self.xlreport['checkdeal'] = (paycheckdeal + self.paySummary['tips']
                                          + self.checkbonus - self.checkfee)
            self.xlreport['bcheck'] = self.xlreport['checkdeal'] + self.xlreport['booth']
            self.xlreport['bcash'] = (paycashdeal - self.paySummary['fees'] - self.rent
                                     + self.cashbonus - self.cashfee - self.boothrent)
            out += f'{"Check Deal":<15}    {paycheckdeal:>10.2f}\n'
            out += f'{"Tips":<15}  + {self.paySummary["tips"]:>10.2f}\n'
            if self.checkbonus:
                out += f'{"Bonus":<15}  + {self.checkbonus:>10.2f}\n'
            if self.checkfee:
                out += f'{"Fee":<15}  - {self.checkfee:>10.2f}\n'
            out += f'{" ":<15}  {"":-^12}\n'
            out += f'{" ":<15}    {self.xlreport["checkdeal"]:>10.2f}\n'
            out += f'{"MS":<15}  + {self.boothrent:>10.2f}\n'
            out += f'{" ":<15}  {"":=^12}\n'
            out += f'{"Opt1 Total":<15}    {math.ceil(self.xlreport["bcheck"]):>10.2f}\n\n'
            out += f'{"Opt2":<15}    {paycashdeal:>10.2f}\n'
            out += f'{"Fees":<15}  - {self.paySummary["fees"] + self.rent:>10.2f}\n'
            if self.cashbonus:
                out += f'{"Bonus":<15}  + {self.cashbonus:>10.2f}\n'
            if self.cashfee:
                out += f'{"Fee2":<15}  - {self.cashfee:>10.2f}\n'
            out += f'{" ":<15}  {"":-^12}\n'
            out += f'{" ":<15}    {self.xlreport["bcash"] - self.boothrent:>10.2f}\n'
            out += f'{"MS":<15}  - {self.boothrent:>10.2f}\n'
            out += f'{" ":<15}  {"":=^12}\n'
            out += f'{"Opt2 Total":<15}    {math.ceil(self.xlreport["bcash"]):>10.2f}\n\n'
            self.payPrint += out

        elif self.role.lower() == 'cash':
            cashdeal = float(self.xlreport["check"] * self.cashrate)
            out += f'{"Check Qua Tien Mat:":<25}{cashdeal:<10.2f}\n'
            out += f'{"Tien Mat:":<25}{self.xlreport["cash"]:<10.2f}\n'
            self.xlreport["cash"] = math.ceil(self.xlreport["cash"] + cashdeal)
            out += f'{"Ca hai cong loi:":<25}{self.xlreport["cash"]:<10}\n\n'
            self.xlreport["check"] = 0
            self.payPrint += out
        return True, True


class EmployeeJanitor(Employee):
    def __init__(self, data):
        super().__init__(data)

    def calculatePayroll(self, sales=None, modified_sales=None, fee_days=None, guarantee=None, booth=None):
        pay_per_day = self.pay6 / 6
        days_worked = 0
        for day, work in self.workdays.items():
            if work:
                days_worked += 1
        current_week_pay = pay_per_day * days_worked

        self.xlreport['check'] = math.ceil(current_week_pay * self.check)
        self.xlreport['cash'] = math.ceil(current_week_pay - self.xlreport['check'])

        if self.xlreport['cash'] == 0:
            self.xlreport['check'] = self.xlreport['check'] - self.rent
        self.payPrint = f'Check: {self.xlreport["check"]}    Cash: {self.xlreport["cash"]}'


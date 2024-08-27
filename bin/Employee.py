import math
import datetime
import string


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
                              'regular':{'commission': commission, 'check': check, 'commissionbooth': commissionbooth},
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
        self.active = data.get('active', True)
        self.role = data.get('type', {}).get('role', 'regular')
        self.commission = data.get('type', {}).get('regular', {}).get('commission', 0)
        self.commissionspecial = data.get('type', {}).get('special', {}).get('commissionspecial', 0)
        self.boothrent = data.get('type', {}).get('regular', {}).get('boothrent', 0)
        self.check = data.get('type', {}).get('regular', {}).get('check', 0.6)

        self.checkdeal = data.get('type', {}).get('special', {}).get('checkdeal', 0)
        self.checkoriginal = data.get('type', {}).get('special', {}).get('checkoriginal', 0.6)
        self.cashrate = data.get('type', {}).get('special', {}).get('cashrate', 0)

        self.printchecks = data.get('printchecks', True)
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
        self.sDate = ''  # m.d.y for saving text purpose
        self.manualBooth = 0
        self.payrollSummary = dict()
        self.modifiedPayrollSummary = dict()
        self.xlreport = {'check': 0, 'checkdeal': '', 'cash': 0, 'booth': 0, 'bcheck': 0, 'bcash': 0}
        self.payrollPrint = ''

    def calculatePayroll(self, sales, modified_sales, fee_days, guarantee, booth):
        """
        Args:
            sales: dictionary of daily sales, keys are datetime
            modified_sales: same as sales but modified data
            fee_days: days that janitor work
            guarantee: [bool] will guarantee base pay regardless of days worked
            booth: integer of how much booth rent is set manually
        Returns:
        """
        if self.role != 'janitor':
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
            self.genericCalculate(fee_days, guarantee, boothFlag)

    def genericCalculate(self, fee_days, guarantee, boothFlag):
        """
        Generic calculation of payroll and generates a payroll printout saved locally in self.payrollPrint.
        Args:
            fee_days: days that janitor work
            guarantee: [bool] will guarantee base pay regardless of days worked
            boothFlag: [bool] will signal manual booth rent
        Returns:
        """
        tips, commissionSales, totalSales, daysWorked, personal_fees = [0 for i in range(1, 6)]
        boothSales = 0
        boothTips = 0
        commissionBoothSales = 0
        tmpCommissionForOutput = 0
        if self.role.capitalize() in ['Regular', 'Owner']:
            tmpCommissionForOutput = self.commission
        else:
            tmpCommissionForOutput = self.commissionspecial

        # this part is the text of the daily summaries based off of regular ticket printout
        output = f'{"  " + string.capwords(self.salonName) + "  ":=^60}\n'
        output += f'{self.name:<60}\n'
        output += f'{" Daily ":-^60}\n'
        output += f'{"Day":<17}{"Tips":>10}{"Sales":>10}{" | "}{"B Tips":>10}{"B Sales":>10}\n'

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
            commissionBoothSales += bDailyCommission
            totalSales += amt['sales']
            boothSales += bDailySales
            boothTips += bDailyTip
            if amt['sales'] > 0:
                daysWorked += 1
            d = datetime.datetime.strftime(day, '%m/%d:%a')
            output += (f'{d:<17}{tipForDay:>10.2f}{amt["sales"]:>10.2f}{" | "}{bDailyTip:>10.2f}{bDailySales:>10.2f}\n')

        output += f'{" ":17}{"-":->20}{" | "}{"-":->20}\n'
        output += f'{" ":17}{tips:>10.2f}{totalSales:>10.2f}{" | "}{boothTips:>10.2f}{boothSales:>10.2f}\n\n\n'
        output += f'{"":*^60}\n'
        output += f'{" Summary ":-^60}\n'
        output += f'{"Total Sale":<10}{" ":5}{totalSales:>10.2f}{" ":10}{"Booth Sale":10}{" ":5}{boothSales:>10.2f}\n'
        output += f'{"Commission":<10}{" ":5}{commissionSales:>10.2f}{" ":10}{"Booth Comm":10}{" ":5}{commissionBoothSales:>10.2f}\n'
        output += f'{"Tips":<10}{" ":5}{tips:>10.2f}{" ":10}{"Tips":<10}{" ":5}{boothTips:>10.2f}\n'
        output += f'{" ":15}{"-":->10}{" ":25}{"-":->10}\n'
        output += (f'{"Sales Pay":<10}{" ":5}{commissionSales + tips:>10.2f}{" ":10}'
                   f'{"Booth Pay":10}{" ":5}{commissionBoothSales + boothTips:>10.2f}\n')
        output += f'{"=":=^60}\n\n\n'
        self.payrollPrint = output

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

        self.payrollSummary = {
            'totalsale': totalSales,
            'commission': commissionSales,
            'check': check,  # raw check amount
            'cash': cash,  # raw cash amount
            'basepaycheck': basepaycheck,  #
            'basepaycash': basepaycash,
            'paycheck': 0,  # actual check to be paid before adding tips
            'paycash': 0,  # actual cash to be paid before subtracting fees
            'tips': tips,
            'personalfees': personal_fees,  # clean up fees
            'daysworked': daysWorked,
            'metGoal': metgoal,
            'boothrent': self.manualBooth if boothFlag else 0,
            'boothcheck': commissionBoothSales + boothTips
        }

        # neu lam du ngay thi check coi can bao luong hay ko
        if (self.payrollSummary['daysworked'] >= 6) | guarantee:
            self.payrollSummary['paycheck'] = self.payrollSummary['check'] if self.payrollSummary['metGoal'] else \
                self.payrollSummary['basepaycheck']
            self.payrollSummary['paycash'] = self.payrollSummary['cash'] if self.payrollSummary['metGoal'] else \
                self.payrollSummary['basepaycash']
        else:
            self.payrollSummary['paycheck'] = self.payrollSummary['check']
            self.payrollSummary['paycash'] = self.payrollSummary['cash']

        outputExtra = ''
        if self.rent < 0:  # when we want to help employee pay rent or give bonus
            if not boothFlag:
                # when there is no manual setting for booth rent
                self.payrollSummary['boothrent'] = 0 if not self.modifiedSales else (
                                                math.ceil(self.payrollSummary["paycheck"]
                                                          + self.payrollSummary["tips"]
                                                          + abs(self.rent)
                                                          - self.payrollSummary["boothcheck"]))
            self.xlreport['booth'] = abs(self.payrollSummary['boothrent'])
            self.xlreport['check'] = math.ceil(self.payrollSummary['paycheck']
                                               + self.payrollSummary['tips']
                                               + abs(self.rent))
            self.xlreport['bcheck'] = math.ceil(self.payrollSummary["boothcheck"])
            self.xlreport['cash'] = math.ceil(self.payrollSummary["paycash"]
                                              - self.payrollSummary["personalfees"])
            self.xlreport['bcash'] = math.ceil(self.payrollSummary["paycash"]
                                               - self.payrollSummary["personalfees"]
                                               - abs(self.payrollSummary["boothrent"]))
            outputExtra += f'{"Option 1":<10} + {"Tip":<10} + {"Bonus":<5} = {"Opt1 Total":<10} + {"Booth Rent":<10} = {"Booth Pay":<10}\n'
            outputExtra += f'{self.payrollSummary["paycheck"]:<10.2f} + {self.payrollSummary["tips"]:<10.2f} + '
            outputExtra += f'{abs(self.rent):<5d} = {self.xlreport["check"]:<10.2f} + {self.xlreport["booth"]:<10.2f} = ${self.xlreport["bcheck"]:<10}\n\n'
            outputExtra += f'{"Option 2":<10} - {"Le Phi":<10} - {"Booth Rent":<10} = {"Opt2 Total":<10}\n'
            outputExtra += f'{self.payrollSummary["paycash"]:<10.2f} - {self.payrollSummary["personalfees"]:<10.2f}'
            outputExtra += f' - {self.xlreport["booth"]:<10} = ${self.xlreport["bcash"]:<10}\n\n'
        else:
            if not boothFlag:
                self.payrollSummary['boothrent'] = 0 if not self.modifiedSales else (
                                                math.ceil(self.payrollSummary["paycheck"]
                                                          + self.payrollSummary["tips"]
                                                          - self.payrollSummary["boothcheck"]))
            self.xlreport['booth'] = abs(self.payrollSummary['boothrent'])
            self.xlreport['check'] = math.ceil(self.payrollSummary["paycheck"] + self.payrollSummary["tips"])
            self.xlreport['bcheck'] = math.ceil(self.payrollSummary["boothcheck"])
            self.xlreport['cash'] = math.ceil(self.payrollSummary["paycash"]
                                              - self.payrollSummary["personalfees"]
                                              - self.rent)
            self.xlreport['bcash'] = math.ceil(self.payrollSummary["paycash"]
                                               - self.payrollSummary["personalfees"]
                                               - self.rent
                                               - abs(self.payrollSummary["boothrent"]))

            outputExtra += f'{"Option 1":<10} + {"Tip":<10} = {"Opt1 Total":<10} + {"Booth Rent":<10} = {"Booth Pay":<10}\n'
            outputExtra += f'{self.payrollSummary["paycheck"]:<10.2f} + {self.payrollSummary["tips"]:<10.2f} '
            outputExtra += f'= {self.xlreport["check"]:<10.2f} + {self.xlreport["booth"]:<10.2f} = ${self.xlreport["bcheck"]:<10}\n\n'
            outputExtra += f'{"Option 2":<10} - {"Le Phi":<10} = {"Opt2 Total":<10} - {"Booth Rent":<10} = {"Opt2 Pay"}\n'
            outputExtra += f'{self.payrollSummary["paycash"]:<10.2f} - {self.payrollSummary["personalfees"] + self.rent:<10.2f} '
            outputExtra += (f'= {self.xlreport["cash"]:<10} - {self.xlreport["booth"]:<10} = '
                            f'{self.xlreport["bcash"]}\n\n')
        self.payrollPrint += outputExtra

    def getPayrollSummary(self):
        return self.payrollSummary

    def getPrintOut(self):
        return self.payrollPrint

    def getStatus(self):
        """
        This checks progress of employees during the week.
        """
        if self.commission == 0:
            return False
        try:
            result = {
                'total': math.ceil(self.payrollSummary['totalsale']),
                'comm': math.ceil(self.payrollSummary['commission']),
                'tips': math.ceil(self.payrollSummary['tips']),
                'daysWorked': math.ceil(self.payrollSummary['daysworked']),
                'metGoal': self.payrollSummary['metGoal']
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
            file.writelines(self.payrollPrint)
        return path + fname

    def getInfo(self):
        return {'active': self.active, 'salonName': self.salonName, 'name': self.name, 'checkName': self.checkName,
                'rent': self.rent, 'fees': self.fees, 'pay6': self.pay6, 'pay7': self.pay7,
                'printchecks': self.printchecks,
                'type': {'role': self.role,
                         'regular': {'commission': self.commission, 'check': self.check,
                                     'boothrent': self.boothrent},
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
        self.genericCalculate(fee_days, guarantee, boothFlag)
        output = f'{"*":*^40}\n'

        if self.role.lower() == 'checkdeal':
            totalpay = self.payrollSummary['paycheck'] + self.payrollSummary['paycash']
            paycheckdeal = totalpay * self.checkdeal
            paycashdeal = totalpay - paycheckdeal
            output = ''
            if self.rent < 0:  # if there was a bonus or rent help
                self.xlreport['checkdeal'] = math.ceil(paycheckdeal + self.payrollSummary["tips"] - self.rent)
                output += f'{"Check Deal":<10} + {"Tip":<10} + {"Bonus":<10}\n '
                output += f'{paycheckdeal:<10.2f} + {self.payrollSummary["tips"]:<10.2f} '
                output += f'+ {abs(self.rent):<10.2f} = {self.xlreport["checkdeal"]:<10}\n'
                self.xlreport['cash'] = math.ceil(paycashdeal - self.payrollSummary["personalfees"])
                output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
                output += f'{paycashdeal:<10.2f} - {self.payrollSummary["personalfees"]:<10} = '
                output += f'{self.xlreport["cash"]}\n\n'
            else:
                self.xlreport['checkdeal'] = math.ceil(paycheckdeal + self.payrollSummary["tips"])
                output += f'{"Option 1":<10} + {"Tip"}\n'
                output += f'{paycheckdeal:<10.2f} + {self.payrollSummary["tips"]:<10.2f} = '
                output += f'{self.xlreport["checkdeal"]}\n'
                self.xlreport['cash'] = math.ceil(paycashdeal - self.payrollSummary["personalfees"] - self.rent)
                output += f'{"Option 2":<10} - {"Le Phi":<8}\n'
                output += f'{paycashdeal:<10.2f} - {self.payrollSummary["personalfees"] + self.rent:<10} = '
                output += f'{self.xlreport["cash"]}\n\n'
            self.payrollPrint += output

        elif self.role.lower() == 'cash':
            cashdeal = float(self.xlreport["check"] * self.cashrate)
            output += f'{"Check Qua Tien Mat:":<25}{cashdeal:<10.2f}\n'
            output += f'{"Tien Mat:":<25}{self.xlreport["cash"]:<10.2f}\n'
            self.xlreport["cash"] = math.ceil(self.xlreport["cash"] + cashdeal)
            output += f'{"Ca hai cong loi:":<25}{self.xlreport["cash"]:<10}\n\n'
            self.xlreport["check"] = 0
            self.payrollPrint += output


class EmployeeJanitor(Employee):
    def __init__(self, data):
        super().__init__(data)

    def calculatePayroll(self, sales=None, modified_sales=None, fee_days=None, guarantee=None):
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
        self.payrollPrint = f'Check: {self.xlreport["check"]}    Cash: {self.xlreport["cash"]}'

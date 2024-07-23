import math
import datetime
import string


class Employee:
    def __init__(self, data):
        """
        Args:
            data layout: {'active':True,
                      'id': idNum, 'name': nameCapitalized, 'salonName':salon, 'pay':pay,
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
        self.id = data['id']
        self.name = data['name']
        self.salonName = data['salonName']
        self.pay6 = float(data['pay6'])
        self.pay7 = float(data['pay7'])
        self.rent = data['rent']
        self.fees = data['fees']
        self.active = data['active']
        self.role = data['type']['role']
        self.commission = float(data['type']['regular']['commission'])
        self.check = float(data['type']['regular']['check'])
        self.commissionspecial = float(data['type']['special']['commissionspecial'])
        self.checkdeal = float(data['type']['special']['checkdeal'])
        self.checkoriginal = float(data['type']['special']['checkoriginal'])
        self.cashrate = float(data['type']['special']['cashrate'])
        self.printchecks = data['printchecks']
        self.workdays = {}
        self.workdays.update(data['workdays'])

        self.sales = {}
        self.sDate = ''         # m.d.y for saving text purpose
        self.payrollSummary = dict()
        self.xlreport = {'check': 0, 'checkdeal': 0, 'cash': 0}
        self.payrollPrint = ''

    def calculatePayroll(self, sales, fee_days, guarantee):
        """
        Args:
            sales: dictionary of daily sales, keys are datetime
            fee_days: days that janitor work
            guarantee: [bool] will guarantee base pay regardless of days worked
        Returns:
        """
        if self.role != 'janitor':
            self.sales = sales.copy()
            self.genericCalculate(fee_days, guarantee)

    def genericCalculate(self, salon_fee_days, guarantee):
        tips, commissionSales, totalSales, daysWorked, personal_fees = [0 for i in range(1, 6)]

        tmpCommissionForOutput = 0
        if self.role.capitalize() in ['Regular','Owner']:
            tmpCommissionForOutput = self.commission
        else:
            tmpCommissionForOutput = self.commissionspecial

        for days, amt in self.sales.items():
            dayName = days.isoweekday()        # monday = 1
            # this is the part where we compare janitor and employee work days to know if there is a fee
            if dayName == 1 and salon_fee_days['mon']:
                personal_fees += self.fees
            elif dayName == 2 and salon_fee_days['tue']:
                personal_fees += self.fees
            elif dayName == 3 and salon_fee_days['wed']:
                personal_fees += self.fees
            elif dayName == 4 and salon_fee_days['thu']:
                personal_fees += self.fees
            elif dayName == 5 and salon_fee_days['fri']:
                personal_fees += self.fees
            elif dayName == 6 and salon_fee_days['sat']:
                personal_fees += self.fees
            elif dayName == 7 and salon_fee_days['sun']:
                personal_fees += self.fees

            tips += amt[2]
            commissionSales += (amt[0] * tmpCommissionForOutput)
            totalSales += amt[0]
            if amt[0] > 0:
                daysWorked += 1


        # this part is the text of the daily summaries based off of regular ticket printout
        output = f'{"  " + string.capwords(self.salonName) + "  ":=^40}\n'
        output += f'{"Name":<10}{" ":10}{self.name:>20}\n'
        output += f'{" Summary ":-^40}\n'
        output += f'{"Total Sale":<10}{" ":20}{totalSales:>10.2f}\n'
        output += f'{"Commission":<10}{" ":20}{commissionSales:>10.2f}\n'
        output += f'{"Tips":<10}{" ":20}{tips:>10.2f}\n'
        output += f'{" ":30}{"-":->10}\n'
        output += f'{"Total Pay":<10}{" ":20}{commissionSales + tips:>10.2f}\n'
        output += f'{" Daily ":-^40}\n'
        output += f'{"Day":<10}{"Total":>10}{"Comm":>10}{"Tips":>10}\n'
        for day, amt in self.sales.items():
            d = datetime.datetime.strftime(day, '%m/%d:%a')
            output += f'{d:<10}{amt[0]:>10.2f}{amt[0] * tmpCommissionForOutput:>10.2f}{amt[2]:>10.2f}\n'
        output += f'{" ":12}{"-":->8}{" ":2}{"-":->8}{" ":2}{"-":->8}\n'
        output += f'{" ":10}{totalSales:>10.2f}{commissionSales:>10.2f}{tips:>10.2f}\n'
        output += f'{"=":=^40}\n'
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
            'check': check,                 # raw check amount
            'cash': cash,                   # raw cash amount
            'basepaycheck': basepaycheck,   #
            'basepaycash': basepaycash,
            'paycheck': 0,                  # actual check to be paid before adding tips
            'paycash': 0,                   # actual cash to be paid before subtracting fees
            'tips': tips,
            'personalfees': personal_fees,  # clean up fees
            'daysworked': daysWorked,
            'metGoal': metgoal,
        }

        # neu lam du ngay thi check coi can bao luong hay ko
        if (self.payrollSummary['daysworked'] >= 6) | guarantee:
            self.payrollSummary['paycheck'] = self.payrollSummary['check'] if self.payrollSummary['metGoal'] else self.payrollSummary['basepaycheck']
            self.payrollSummary['paycash'] = self.payrollSummary['cash'] if self.payrollSummary['metGoal'] else self.payrollSummary['basepaycash']
        else:
            self.payrollSummary['paycheck'] = self.payrollSummary['check']
            self.payrollSummary['paycash'] = self.payrollSummary['cash']

        outputExtra = ''
        if self.rent < 0:   # when we want to help employee pay rent or give bonus
            self.xlreport['check'] = math.ceil(self.payrollSummary['paycheck'] + self.payrollSummary['tips'] - self.rent)
            outputExtra += f'{"Option 1":<10} + {"Tip":<10} + {"Bonus"}\n'
            outputExtra += f'{self.payrollSummary["paycheck"]:<10.2f} + {self.payrollSummary["tips"]:<10.2f} + '
            outputExtra += f'{abs(self.rent):<5.0f} = ${self.xlreport["check"]:<10}\n'
            self.xlreport['cash'] = math.ceil(self.payrollSummary["paycash"] - self.payrollSummary["personalfees"])
            outputExtra += f'{"Option 2":<10} - {"Le Phi":<8}\n'
            outputExtra += f'{self.payrollSummary["paycash"]:<10.2f} - {self.payrollSummary["personalfees"]:<10.2f}'
            outputExtra += f' = ${self.xlreport["cash"]:<10}\n\n'
        else:
            self.xlreport['check'] = math.ceil(self.payrollSummary["paycheck"] + self.payrollSummary["tips"])
            outputExtra += f'{"Option 1":<10} + {"Tip":<10}\n'
            outputExtra += f'{self.payrollSummary["paycheck"]:<10.2f} + {self.payrollSummary["tips"]:<10.2f} = '
            outputExtra += f'${self.xlreport["check"]:<10}\n'
            self.xlreport['cash'] = math.ceil(self.payrollSummary["paycash"] - self.payrollSummary["personalfees"] - self.rent)
            outputExtra += f'{"Option 2":<10} - {"Le Phi":<8}\n{self.payrollSummary["paycash"]:<10.2f} - '
            outputExtra += f'{self.payrollSummary["personalfees"] + self.rent:<10.2f} = ${self.xlreport["cash"]:<10}\n\n'
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
        return {'id': self.id, 'active': self.active, 'salonName': self.salonName, 'name': self.name,
                'rent': self.rent, 'fees': self.fees, 'pay6': self.pay6, 'pay7': self.pay7,
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

    def calculatePayroll(self, sales, salon_fee_days, guarantee):
        '''
            so tien check ky ra va so tien check deal se co khac biet.
            check deal la so ky ra va check binh thuong la ho phai khai cuoi nam
        '''
        self.sales = sales.copy()
        self.genericCalculate(salon_fee_days, guarantee)
        output = f'{"*":*^40}\n'

        if self.role.lower() == 'checkdeal':
            totalpay = self.payrollSummary['paycheck'] + self.payrollSummary['paycash']
            paycheckdeal = totalpay * self.checkdeal
            paycashdeal = totalpay - paycheckdeal
            output = ''
            if self.rent < 0:   # if there was a bonus or rent help
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

    def calculatePayroll(self, sales=None, fee_days=None, guarantee=None):
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

import math
import datetime
import string


class Employee:
    def __init__(self, data):
        """

        Args:
            data layout: {'paygrade': {'type': boolean,  True if regular, False if special
                                        'regular': {'commission': commission, 'check': check}
                                        'special': {'commissionspecial': comspec, 'checkdeal': checkdeal, 'checkoriginal': checkoriginal}}
                            'id': idNum, 'salonName': sname, 'name': name, 'rent': rent, 'fees': fees, 'pay': pay, 'active': bool}
        """
        self.id = data['id']
        self.name = data['name']
        self.salonName = data['salonName']
        self.basePay = data['pay']
        self.rent = data['rent']
        self.fees = data['fees']
        self.active = data['active']
        self.regtype = data['paygrade']['regType']
        self.commission = data['paygrade']['regular']['commission']
        self.check = data['paygrade']['regular']['check']
        self.commissionspecial = data['paygrade']['special']['commissionspecial']
        self.checkdeal = data['paygrade']['special']['checkdeal']
        self.checkoriginal = data['paygrade']['special']['checkoriginal']

        self.sales = {}
        self.sDate = ''         # m.d.y for saving text purpose
        self.payrollSummary = dict()
        self.xlreport= {'check': 0, 'checkdeal': 0, 'cash': 0}

        self.payrollPrint = ''

    def calculatePayroll(self, sales):
        """

        Args:
            sales: dictionary of daily sales, keys are datetime

        Returns:

        """
        self.sales = sales.copy()
        self.genericCalculate()


    def genericCalculate(self):
        tips,commissionSales,totalSales,cleaningFees,daysWorked = [0 for i in range(1,6)]
        for days,amt in self.sales.items():
            tips += amt[2]
            commissionSales += amt[1]
            totalSales += amt[0]
            if amt[0] > 0:
                daysWorked += 1

        # self.commission is an integer 1-10 convert it to decimal percent
        check = (commissionSales * (self.check / 10))
        cash = commissionSales * ((10 - self.check) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * daysWorked
        basePayCheck = (basePayPerRange * (self.check / 10))
        basePayCash = basePayPerRange * ((10 - self.check) / 10)
        fees = (daysWorked * self.fees) + self.rent
        self.payrollSummary = {
            'totalsale':totalSales,
            'commission':commissionSales,
            'check':check,
            'cash':cash,
            'basepaycheck':basePayCheck,
            'basepaycash':basePayCash,
            'tips':tips,
            'fees':fees,
            'daysworked': daysWorked,
            'metGoal':True if commissionSales > basePayPerRange else False
        }

        output = f'{"  "+string.capwords(self.salonName)+"  ":=^40}\n'
        output += f'{"Name":<10}{" ":10}{self.name:>20}\n'
        output += f'{" Summary ":-^40}\n'
        output += f'{"Total Sale":<10}{" ":20}{totalSales:>10.2f}\n'
        output += f'{"Commission":<10}{" ":20}{commissionSales:>10.2f}\n'
        output += f'{"Tips":<10}{" ":20}{tips:>10.2f}\n'
        output += f'{" ":30}{"-":->10}\n'
        output += f'{"Total Pay":<10}{" ":20}{commissionSales + tips:>10.2f}\n'
        output += f'{" Daily ":-^40}\n'
        output += f'{"Day":<10}{"Total":>10}{"Comm":>10}{"Tips":>10}\n'
        for day,amt in self.sales.items():
            d = datetime.datetime.strftime(day,'%m/%d:%a')
            output += f'{d:<10}{amt[0]:>10.2f}{amt[1]:>10.2f}{amt[2]:>10.2f}\n'
        output += f'{" ":12}{"-":->8}{" ":2}{"-":->8}{" ":2}{"-":->8}\n'
        output += f'{" ":10}{totalSales:>10.2f}{commissionSales:>10.2f}{tips:>10.2f}\n'
        output += f'{"=":=^40}\n'
        self.payrollPrint = output
        if self.regtype:
            self.regTypeSummaryAddOn()

    def regTypeSummaryAddOn(self):
        check = self.payrollSummary['check'] if self.payrollSummary['metGoal'] else self.payrollSummary['basepaycheck']
        cash = self.payrollSummary['cash'] if self.payrollSummary['metGoal'] else self.payrollSummary['basepaycash']
        self.xlreport['check'] = check + self.payrollSummary["tips"]
        self.xlreport['cash'] = cash - self.payrollSummary["fees"]
        output = f'{"Check":<10} + {"Tip"}\n'
        output += f'{check:<10.2f} + {self.payrollSummary["tips"]:<8.2f} = ' \
                  f'${math.ceil(check + self.payrollSummary["tips"]):<10}\n'
        output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
        output += f'{cash:<10.2f} - {self.payrollSummary["fees"]:<8.2f} = ' \
                  f'${math.ceil(cash - self.payrollSummary["fees"]):<10}\n\n'
        self.payrollPrint += output

    def getPayrollSummary(self):
        return self.payrollSummary

    def getPrintOut(self):
        return self.payrollPrint

    def getStatus(self):
        try:
            result = {
                'total': math.ceil(self.payrollSummary['totalsale']),
                'comm': math.ceil(self.payrollSummary['commission']),
                'tips': math.ceil(self.payrollSummary['tips']),
                'daysWorked': math.ceil(self.payrollSummary['daysworked']),
                'metGoal': math.ceil(self.payrollSummary['metGoal'])
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

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getInfo(self):
        return {'paygrade': {'regType': self.regtype,
                            'regular': {'commission': self.commission, 'check': self.check},
                            'special': {'commissionspecial': self.commissionspecial, 'checkdeal': self.checkdeal, 'checkoriginal': self.checkoriginal}},
                'id': self.id, 'active': self.active,'salonName': self.salonName, 'name': self.name,
                'rent': self.rent, 'fees': self.fees, 'pay': self.basePay}

    def getXlReport(self):
        return self.xlreport

class EmployeeSpecial(Employee):
    """
        Nguoi nay can phai khai income thap cho nen ky check it ma khai so thiet
    """
    def __init__(self, data):
        super().__init__(data)
        self.payrollSummaryEtc = dict()

    def calculatePayroll(self,sales):

        self.sales = sales.copy()
        self.genericCalculate()

        '''
            so tien check ky ra va so tien check deal se co khac biet. 
            check deal la so ky ra va check binh thuong la ho phai khai cuoi nam
        '''

        # self.commission is an integer 1-10 convert it to decimal percent
        check = self.payrollSummary['commission'] * (self.checkoriginal / 10)
        cash = self.payrollSummary['commission'] * ((10 - self.checkoriginal) / 10)

        checkdeal = self.payrollSummary['commission'] * (self.checkdeal / 10)
        cashdeal = self.payrollSummary['commission'] * ((10 - self.checkdeal) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * self.payrollSummary['daysworked']

        basePayCheck = basePayPerRange * (self.checkoriginal / 10)
        basePayCash = basePayPerRange * ((10 - self.checkoriginal) / 10)

        basePayCheckDeal = basePayPerRange * (self.checkdeal / 10)
        basePayCashDeal = basePayPerRange * ((10 - self.checkdeal) / 10)

        self.payrollSummaryEtc = {
            'check':check,
            'cash':cash,
            'basepaycheck': basePayCheck,
            'basepaycash': basePayCash,
            'metGoal':True if self.payrollSummary['commission'] > basePayPerRange else False,
            'checkdeal':checkdeal,
            'cashdeal':cashdeal,
            'basepaycheckdeal':basePayCashDeal,
            'basepaycashdeal':basePayCashDeal
        }
        check = self.payrollSummaryEtc['check'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycheck']
        cash = self.payrollSummaryEtc['cash'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycash']
        output = f'{"Check":<10} + {"Tip"}\n'
        output += f'{check:<10.2f} + {self.payrollSummary["tips"]:<8.2f} = ' \
                  f'${math.ceil(check + self.payrollSummary["tips"]):<10}\n'
        output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
        output += f'{cash:<10.2f} - {self.payrollSummary["fees"]:<8.2f} = ' \
                  f'${math.ceil(cash - self.payrollSummary["fees"]):<10}\n\n'

        # add additional info to payroll for special case
        checkdeal = self.payrollSummaryEtc['checkdeal'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycheckdeal']
        cashdeal = self.payrollSummaryEtc['cashdeal'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycashdeal']
        self.xlreport['check'] = check + self.payrollSummary["tips"]
        self.xlreport['checkdeal'] = checkdeal + self.payrollSummary["tips"]
        self.xlreport['cashdeal'] = cashdeal - self.payrollSummary["fees"]
        output += f'{"*":*^40}\n'
        output += f'{"Check":<10} + {"Tip"}\n'
        output += f'{checkdeal:<10.2f} + {self.payrollSummary["tips"]:<10.2f} = ' \
                             f'{math.ceil(checkdeal + self.payrollSummary["tips"]):<10}\n'
        output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
        output += f'{cashdeal:<10.2f} - {self.payrollSummary["fees"]:<8} = ' \
                             f'{math.ceil(cashdeal - self.payrollSummary["fees"])}\n\n'
        self.payrollPrint += output

class EmployeeCash(Employee):
    def __init__(self, data):
        super().__init__(data)
        self.payrollSummaryEtc = {}

    def calculatePayroll(self,sales):
        self.sales = sales.copy()
        self.genericCalculate()

        # self.commission is an integer 1-10 convert it to decimal percent
        '''
            the next three lines are what makes the difference because check is 
            deducted 17% and converted to cash 
        '''
        check = self.payrollSummary['commission'] * (self.checkoriginal / 10)
        cash = self.payrollSummary['commission'] * ((10 - self.checkoriginal) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * self.payrollSummary['daysworked']
        basePayCheck = basePayPerRange * (self.checkoriginal / 10)
        basePayCash = basePayPerRange * ((10 - self.checkoriginal) / 10)
        self.payrollSummaryEtc = {
            'cash': cash,
            'check': check,
            'basepaycash': basePayCash,
            'basepaycheck': basePayCheck,
            'rate': 0.83,
            'metGoal': True if cash > basePayCash else False
        }

        # add additional info to payroll for special case
        cash = self.payrollSummaryEtc['cash'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycash']
        check = self.payrollSummaryEtc['check'] if self.payrollSummaryEtc['metGoal'] else self.payrollSummaryEtc['basepaycheck']
        cashdeal = (check + self.payrollSummary['tips']) * self.payrollSummaryEtc['rate']
        self.xlreport['cash'] = cash + cashdeal - self.payrollSummary["fees"]
        output = f'{"Check":<10} + {"Tip"}\n'
        output += f'{check:<10.2f} + {self.payrollSummary["tips"]:<8.2f} = ' \
                  f'${math.ceil(check + self.payrollSummary["tips"]):<10}\n'
        output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
        output += f'{cash:<10.2f} - {self.payrollSummary["fees"]:<8.2f} = ' \
                  f'${math.ceil(cash - self.payrollSummary["fees"]):<10}\n\n'

        output += f'{"*":*^40}\n'
        output += f'{"Check Qua Tien Mat":<30}:{cashdeal:>10.2f}\n'
        output += f'{"Tien Mat":<10} - {"Le Phi":<8}\n'
        output += f'{cash:<8.2f} - {self.payrollSummary["fees"]:<6} = ' \
                             f'{cash - self.payrollSummary["fees"]:>8.2f}\n'
        subTotal = cash + cashdeal - self.payrollSummary["fees"]
        output += f'{"Ca hai cong loi:":<30}{math.ceil(subTotal):>10}\n\n'
        self.payrollPrint += output




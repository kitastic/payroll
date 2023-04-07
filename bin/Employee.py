import math


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
        self.paygrade = data['paygrade']['regType']
        self.commission = data['paygrade']['regular']['commission']
        self.check = data['paygrade']['regular']['check']
        self.commissionspecial = data['paygrade']['special']['commissionspecial']
        self.checkdeal = data['paygrade']['special']['checkdeal']
        self.checkoriginal = data['paygrade']['special']['checkoriginal']

        self.payroll = dict()
    def calculatePayroll(self, sales):
        tips, commissionSales, totalSales, cleaningFees, daysWorked = [0 for i in range(1,6)]
        for days, amt in sales.items():
            tips += amt[2]
            commissionSales += amt[1]
            totalSales += amt[0]
            if amt[0] > 0:
                daysWorked += 1

        # self.commission is an integer 1-10 convert it to decimal percent
        check = (commissionSales * (self.check / 10)) + tips
        cash = commissionSales * ((10 - self.check) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * daysWorked
        basePayCheck = (basePayPerRange * (self.check / 10) ) + tips
        basePayCash = basePayPerRange * ((10 - self.check) / 10)

        if commissionSales < basePayPerRange :
            self.payroll = {
                'check': basePayCheck,
                'cash': basePayCash,
                'tips': tips,
                'fees': (daysWorked * self.fees) + self.rent
            }
        else:
            self.payroll = {
                'check': check,
                'cash': cash,
                'tips': tips,
                'fees': (daysWorked * self.fees) + self.rent
            }

    def getPayroll(self):
        return self.payroll

    def exportPayroll(self):
        output = ''

        def calAnna():
            # use variable globally within exportPayroll method
            nonlocal output
            commission = self.parsedData[6][3]
            tips = self.parsedData[7][3]
            check = (commission * .5)               # check 50/50 instead of 60/40 like everyone else
            cash = (commission * .5)
            self.falseCheckPaid = check + tips      # check amount paid out, but will file actual more amount
            output += '\n' + '*' * 40 + '\n'
            output += 'Check + Tip: ' + "{:.2f}".format(check) + ' + ' \
                      + "{:.2f}".format(tips) + ' = ' + "{:.2f}".format(math.ceil(check + tips)) + '\n'
            fees = self.rent + self.cleanUp
            output += 'Tien Mat - (nha/don dep): ' + "{:.2f}".format(cash) + ' - ' \
                      + "{:.2f}".format(fees) + ' = ' + '{:.2f}'.format(math.ceil(cash - fees)) + '\n'

        def calCindy():
            # use variable globally within exportPayroll method
            nonlocal output
            commission = self.parsedData[6][3]
            tips = self.parsedData[7][3]
            check = (commission * .6) + tips
            cashFromCheck = math.ceil(check * 0.83)
            cash = (commission * .4)
            output += '\n' + '*' * 40 + '\n'
            output += 'Check Qua Tien Mat: ' + '{:.0f}'.format(cashFromCheck)+ '\n'
            fees = self.rent + self.cleanUp
            output += 'Tien Mat - (nha/don dep): ' + "{:.2f}".format(cash) + ' - ' \
                      + "{:.2f}".format(fees) + ' = ' + '{:.2f}'.format(cash - fees) + '\n'
            totalCash = cashFromCheck + cash - fees
            self.totalCash = totalCash
            output += 'Ca Hai Cong Loi: ' + '{:.2f}'.format(math.ceil(totalCash))

        # format each line to have each item padded 10 chars with alignment
        for line in self.parsedData:
            temp = [line[0], line[1], line[2], line[3]]
            formatted = []
            for i in temp:
                # TODO: add a condition where the first line of '=====' is included.
                # can be fixed at webBot class > exportEmployee method
                if isinstance(i, str):
                    formatted.append(i)
                else:
                    formatted.append("{:.2f}".format(i))

            output += formatted[0].ljust(10) + formatted[1].center(10) \
                      + formatted[2].center(10) + formatted[3].rjust(10) + '\n'

        output += '\n' + '=' * 40 + '\n'
        output += 'Check + Tip: ' + "{:.2f}".format(self.payroll[0]) + ' + ' + "{:.2f}".format(self.payroll[1]) + ' = ' + "{:.2f}".format(math.ceil(self.payroll[2])) + '\n'
        fees = self.rent + self.cleanUp
        output += 'Tien Mat - (nha/don dep): ' + "{:.2f}".format(self.payroll[3]) + ' - ' \
                  + "{:.2f}".format(fees) + ' = ' + '{:.2f}'.format(math.ceil(self.payroll[3] - fees)) + '\n'

        if self.name == 'Anna':
            calAnna()
        if self.name == 'Cindy':
            calCindy()
        print(output)

        fname = self.salonName[0] + '.' + self.parsedData[0][2].replace('/', '.') + self.name + '.txt'
        path = '../tmp/'
        with open(path + fname, 'w+') as file:
            file.writelines(output)
        return path + fname

    def printAll(self):
        print('name: ' + self.name)
        print('basepay: ' + str(self.basePay))
        print('rent: ' + str(self.rent))
        print('days worked: ' + str(self.daysWorked))
        print('clean up: ' + str(self.cleanUp))
        for i in self.parsedData: print(i)
        for i in self.income: print(i)

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getInfo(self):
        return {'paygrade': {'regType': self.paygrade,
                            'regular': {'commission': self.commission, 'check': self.check},
                            'special': {'commissionspecial': self.commissionspecial, 'checkdeal': self.checkdeal, 'checkoriginal': self.checkoriginal}},
                'id': self.id, 'active': self.active,'salonName': self.salonName, 'name': self.name,
                'rent': self.rent, 'fees': self.fees, 'pay': self.basePay}


class EmployeeSpecial(Employee):
    """
        Nguoi nay can phai khai income thap cho nen ky check it ma khai so thiet
    """
    def __init__(self, data):
        super().__init__( data)

    def calculatePayroll(self,sales):
        tips,commissionSales,totalSales,cleaningFees,daysWorked = [0 for i in range(1,6)]
        for days,amt in sales.items():
            tips += amt[2]
            commissionSales += amt[1]
            totalSales += amt[0]
            if amt[0] > 0:
                daysWorked += 1

        # self.commission is an integer 1-10 convert it to decimal percent
        '''
            the next three lines are what makes the difference because check is 
            deducted 17% and converted to cash 
        '''
        check = commissionSales * (self.checkoriginal / 10) + tips
        checkdeal = commissionSales * (self.checkdeal / 10) + tips
        cash = commissionSales * ((10 - self.checkoriginal) / 10)
        cashdeal = commissionSales * ((10 - self.checkdeal) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * daysWorked
        basePayCheck = basePayPerRange * (self.checkoriginal / 10) + tips
        basePayCheckDeal = basePayPerRange * (self.checkdeal / 10) + tips
        basePayCash = basePayPerRange * ((10 - self.checkoriginal) / 10)
        basePayCashDeal = basePayPerRange * ((10 - self.checkdeal) / 10)

        if commissionSales < basePayPerRange:
            self.payroll = {
                'check':basePayCheck,
                'checkdeal': basePayCheckDeal,
                'cash':basePayCash,
                'cashdeal':basePayCashDeal,
                'tips':tips,
                'fees':(daysWorked * self.fees) + self.rent
            }
        else:
            self.payroll = {
                'check':check,
                'checkdeal': checkdeal,
                'cashdeal': cashdeal,
                'cash':cash,
                'tips':tips,
                'fees':(daysWorked * self.fees) + self.rent
            }


class EmployeeCash(Employee):
    def __init__(self, data):
        super().__init__(data)

    def calculatePayroll(self,sales):
        tips,commissionSales,totalSales,cleaningFees,daysWorked = [0 for i in range(1,6)]
        for days,amt in sales.items():
            tips += amt[2]
            commissionSales += amt[1]
            totalSales += amt[0]
            if amt[0] > 0:
                daysWorked += 1

        # self.commission is an integer 1-10 convert it to decimal percent
        '''
            the next three lines are what makes the difference because check is 
            deducted 17% and converted to cash 
        '''
        check = commissionSales * (self.checkoriginal / 10) + tips
        convertedCheck = check * 0.83
        cash = commissionSales * ((10 - self.checkoriginal) / 10)
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerRange = basePayPerDay * daysWorked
        basePayCheck = basePayPerRange * (self.checkoriginal / 10) + tips
        basePayConvertedCheck = basePayCheck * 0.83
        basePayCash = basePayPerRange * ((10 - self.checkoriginal) / 10)

        if commissionSales < basePayPerRange:
            self.payroll = {
                'check':basePayCheck,
                'checkdeal': basePayConvertedCheck,
                'cash':basePayCash,
                'tips':tips,
                'fees':(daysWorked * self.fees) + self.rent
            }
        else:
            self.payroll = {
                'check':check,
                'checkdeal': convertedCheck,
                'cash':cash,
                'tips':tips,
                'fees':(daysWorked * self.fees) + self.rent
            }


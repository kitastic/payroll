import math


class Employee:
    def __init__(self, data):
        """

        Args:
            data layout: {'paygrade': {'type': paygradetype,
                                        'regular': {'commission': commission, 'check': check}
                                        'special': {'commissionspecial': comspec, 'checkdeal': checkdeal, 'checkreport': checkreport}}
                            'id': idNum, 'salonName': sname, 'name': name, 'rent': rent, 'fees': fees, 'pay': pay}
        """
        self.id = data['id']
        self.name = data['name']
        self.salonName = data['salonName']
        # self.parsedData = data[0]
        # self.income = data[1]
        self.basePay = data['pay']
        self.rent = data['rent']
        self.fees = data['fees']
        self.paygrade = data['paygrade']['type']
        self.commission = data['paygrade']['regular']['commission']
        self.check = data['paygrade']['regular']['check']
        self.commissionspecial = data['paygrade']['special']['commissionspecial']
        self.checkdeal = data['paygrade']['special']['checkdeal']
        self.checkreport = data['paygrade']['special']['checkreport']


        self.daysWorked = 0
        self.cleanUp = 0
        self.payroll = []
        self.falseCheckPaid = 0        # for people who want to claim less income, but will file actual with irs
        self.totalCash = 0              # for people who will deduct tax from check and convert to cash also


    def calcFees(self):
        # this function is the main salon differentiation
        for i in self.income:
            if i[2] > 0:
                self.daysWorked = self.daysWorked + 1

            if self.salonName == 'upscale' and i[2] >= 170:
                # deduct $5 for every day that made total sale >= &170
                self.cleanUp = self.cleanUp + 5

    def addCalculation(self):
        tips = self.parsedData[7][3]            #6, 9, 10
        check = self.parsedData[10][3] - tips
        cash = self.parsedData[11][3]
        # check if made enough
        basePayPerDay = self.basePay / 6
        basePayPerWeek = basePayPerDay * self.daysWorked
        basePayCheck = basePayPerWeek * 0.6
        basePayCash = basePayPerWeek * 0.4

        if cash < basePayCash:
            updatedCash = basePayCash
            updatedCheck = basePayCheck
            self.payroll.append(basePayCheck)
            self.payroll.append(tips)
            self.payroll.append(updatedCheck + tips)
            self.payroll.append(updatedCash)
        else:
            self.payroll.append(check)
            self.payroll.append(tips)
            self.payroll.append(check + tips)
            self.payroll.append(cash)

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


class EmployeeCash(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)
        self.salary = []


class Employee50(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)


class Employee60(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)


class EmployeeManager(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)


class EmployeeNoFees(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)


class CashEmployee(Employee):
    def __init__(self, id, name, salon, data, base, rent):
        super().__init__(id,  name, salon, data, base, rent)

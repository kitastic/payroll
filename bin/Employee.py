
class Employee():

    def __init__(self, name, salon, data, pbase, rent):
        self.name = name
        self.salon = salon
        self.parsedData = data[0]
        self.income = data[1]
        self.basePay = pbase
        self.rent = rent
        self.daysWorked = 0
        self.cleanUp = 0
        self.payroll = []
        self.calcFees()
        self.addCalculation()

    def calcFees(self):
        # this function is the main salon differentiation
        for i in self.income:
            if i[2] > 0:
                self.daysWorked = self.daysWorked + 1

            if self.salon == 'upscale' and i[2] >= 170:
                # deduct $5 for every day that made total sale >= &170
                self.cleanUp = self.cleanUp + 5

    def addCalculation(self):
        tips = self.parsedData[6][3]
        check = self.parsedData[9][3] - tips
        cash = self.parsedData[10][3]
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
            self.payroll.append(updatedCheck+tips)
            self.payroll.append(updatedCash)
        else:
            self.payroll.append(check)
            self.payroll.append(tips)
            self.payroll.append(check+tips)
            self.payroll.append(cash)

    def exportPayroll(self):
        # format each line to have each item padded 10 chars with alignment
        output = ''
        for line in self.parsedData:
            temp = [line[0], line[1], line[2], line[3]]
            formatted = []
            for i in temp:
                if isinstance(i, str):
                    formatted.append(i)
                else:
                    formatted.append(str("{:.2f}".format(i)))

            output += formatted[0].ljust(10) + formatted[1].center(10) \
                    + formatted[2].center(10) + formatted[3].rjust(10) + '\n'

        output += '-'*40 + '\n'
        output += 'Check + Tip: ' + str(self.payroll[0]) + ' + ' \
                  + str("{:.2f}".format(self.payroll[1])) + ' = ' + str(self.payroll[2]) + '\n'
        fees = self.rent + self.cleanUp
        output += 'Tien Mat - (nha/don dep): ' + str(self.payroll[3]) + ' - ' \
                + str(fees) + ' = ' + str(self.payroll[3] - fees) + '\n'

        print(output)
        fname = self.parsedData[0][2].replace('/','.') + self.name + '.txt'
        path = '../tmp/'
        with open(path+fname, 'w+') as file:
            file.writelines(output)
        return path+fname

    def printAll(self):
        print('name: ' + self.name)
        print('basepay: ' + str(self.basePay))
        print('rent: ' + str(self.rent))
        print('days worked: ' + str(self.daysWorked))
        print('clean up: ' + str(self.cleanUp))
        for i in self.parsedData: print(i)
        for i in self.income: print(i)
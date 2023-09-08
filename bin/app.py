"""
This will be the main driver file. First, the WebBot will be constructed
to login to website and retrieve various data and format the information
into different forms such as txt, and excel. There is a method to convert
to csv but it is not needed. Next, Employees will be constructed to
process their individual payrol from a range of dates. Mostly the range is
a week to week bases with Monday is the first day.
Order of operation:
    1. Construct webBot (per salon) and call login method
            method used: WebBot.login()
    2. Create thread to download employee sales so that there is no file
        conflict with multiple salon bots trying to race for it.
            method used: WebBot.dlEmpSales()
    3. Create another thread, after the previous one finishes, to extract
        information from the excel downloaded file.
            method used: WebBot.parseXlToData()
    4.Construct each employee and call the Employee.exportPayroll() method

During debugging stage and if logging into website is not needed, there
are also import/export methods for working with locally stored files in WebBot.py
"""
from WebBot import WebBot
from Employee import Employee
import datetime
import threading
import logging


def payrollAutomateThread(botBundle, startDate, endDate, threadBundle):
    bot = WebBot(botBundle)
    bot.login()

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating dlEmpSales thread")
    # daemon threads will terminate immediately when program exits
    # with regular threads, program will wait for thread to finish before exiting
    threadDlEmpSales = threading.Thread(target=bot.dlEmpSales,
                                        args=(startDate, endDate, threadBundle[0]),
                                        daemon=True,
                                        )
    logging.info("Main    : before running dlEmpSales thread")
    threadDlEmpSales.start()
    logging.info("Main    : waiting for dlEmpSales thread to finish")
    threadDlEmpSales.join()
    logging.info("Main    : downloading dlEmpSales thread joined")

    logging.info("Main    : before creating parseXlToDa thread")
    threadParseXlToData = threading.Thread(target=bot.parseXlToData,
                                           args=(threadBundle[0][0] + '.' + startDate.replace('/','.'),),
                                           daemon=True,
                                           )
    logging.info("Main    : before running threadParseXlToData")
    threadParseXlToData.start()
    logging.info("Main    : waiting for threadParseXlToData to finish")
    threadParseXlToData.join()
    logging.info("Main    : downloading threadParseXlToData joined")

    for emp in botBundle[2]:
        emp = Employee(emp,
                       threadBundle[0],
                       bot.exportEmployee(emp),
                       threadBundle[1][botBundle[2].index(emp)],
                       threadBundle[2][botBundle[2].index(emp)],
                       )
        emp.exportPayroll()


# list must be alphabetized, so iterating down drop list is easier
poshEmployee = ['Mary', 'Nancy', 'Sophia', 'Tuyen', 'Vu']
pBase = [900, 900, 1300, 900, 1500]
pRent = [0, 0, 0, 0, 0]
pBotBundle = ['kit@posh', 'Joeblack334$', poshEmployee, 'pWeeklyDB.xlsx']
pThreadBundle = ['posh', pBase, pRent, ]

upscaleEmployee = ['Anna', 'Cindy', 'Kayla', 'Chau', 'Lisa',
                   'Sumo', 'Kelly', 'Sammy', 'Leo', 'Ethan',
                   'Judy']
uBase = [0, 900, 1300, 1100, 900,
         1400, 1300, 1200, 1200, 0,
         1000]
uRent = [0, 60, 70, 60, 60,
         60, 0, 60, 70, 0,
         187]
uBotBundle = ['upscalemanager', 'Joeblack334$', upscaleEmployee, 'uWeeklyDB.xlsx']
uThreadBundle = ['upscale', uBase, uRent, ]
# startDate, endDate = helper.getDateGui()
startDate = '3/20/2023'
startObj = datetime.datetime.strptime(startDate, '%m/%d/%Y')
endObj = startObj + datetime.timedelta(days=6)
endDate = endObj.strftime('%m/%d/%Y')

# posh bot automate payroll
payrollAutomateThread(pBotBundle, startDate, endDate, pThreadBundle)

# upscale bot automate payroll
payrollAutomateThread(uBotBundle, startDate, endDate, uThreadBundle)


print('Done')

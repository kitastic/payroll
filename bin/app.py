"""
This will be the main driver file
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
                                        args=(startDate, endDate, threadBundle[0], 'dlEmpSales'),
                                        daemon=True,
                                        )
    logging.info("Main    : before running dlEmpSales thread")
    threadDlEmpSales.start()
    logging.info("Main    : waiting for dlEmpSales thread to finish")
    threadDlEmpSales.join()
    logging.info("Main    : downloading dlEmpSales thread joined")

    logging.info("Main    : before creating parseXlToDa thread")
    threadParseXlToData = threading.Thread(target=bot.parseXlToData,
                                           args=(threadBundle[0][0] + '.' + startDate.replace('/','.'),'parseXlToData'),
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
# posh = WebBot(pBotBundle)
# posh.login()
# posh.dlEmpSales(startDate, endDate, 'p', 'pWeeklyDB.xlsx')
# posh.parseXlToData('p.' + startDate.replace('/','.'))
# time.sleep(3)
#
# for emp in poshEmployee:
#     emp = Employee(emp,
#                    'posh',
#                    posh.exportEmployee(emp),
#                    pBase[poshEmployee.index(emp)],
#                    pRent[poshEmployee.index(emp)],
#                    )
#     emp.exportPayroll()
#
# upscale = WebBot(uBotBundle)
# upscale.login()
# upscale.dlEmpSales(startDate, endDate, 'u', 'uWeeklyDB.xlsx')
# upscale.parseXlToData('u.' + startDate.replace('/','.'))
#
# for emp in upscaleEmployee:
#     emp = Employee(emp,
#                    'upscale',
#                    upscale.exportEmployee(emp),
#                    uBase[upscaleEmployee.index(emp)],
#                    uRent[upscaleEmployee.index(emp)],
#                    )
#     emp.exportPayroll()


print('Done')

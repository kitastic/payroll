from datetime import datetime
import pandas as pd
import PySimpleGUI as sg
import os
from PyPDF2 import PdfReader
import re

officeExpenses = ("samsclub", "sams club", "walmart",
                  'walmart.com', "wal-mart", "amzn",
                  'amazon', "best buy", "big lots",
                  "liquor", "hobby-lobby", "bath & body",
                  "staples", "joann", "sally beauty",
                  'wal sam', 'locked up', 'bestbuy', 'hobbylobby'
                  )
description = dict({"Rent": "robson",
                    "Merchant Fees": ("mthly direct payment", 'direct dps', 'hs group'),
                    "Bank Fees": "service charge",
                    "Cable": ("optimum", "suddenlink"),
                    "Utilities": ("ok natural gas", "city of stillwater"),
                    "Insurance": "insurance",
                    "Marketing": ("facebk", "google", "college coupon", 'metaplatfor'),
                    "Office Expenses": officeExpenses,
                    "License fees": ("secretary of state", "osbcb"),
                    "Supplies": {'supply', 'nailsjobs', 'nails plus'},
                    "Wages": 'check',
                    "Taxes": ("irs", "tax", 'oklahomataxpmts'),
                    "Remodel/Maintenance": ("lowe", "heating", 'frontier fire'),
                    "Miscellaneous": {},
                    "Depreciation": {},
                    "Amortization": {},
                    "Sales": "merch dep",
                    "Deposit": 'deposit',
                    "Non Deductible": {}
                    })


def makeWindow(theme):
    sg.theme(theme)
    layout = [
        [sg.Text('Year End Reporting', size=(35, 1), justification='center', relief=sg.RELIEF_RIDGE)],
        [sg.HorizontalSeparator()],
        [sg.Radio('Exchange', 'bank', default=True, k='-exchange-'),
         sg.Radio('Chase', 'bank', default=False, k='-chase-')],
        [sg.Radio('Transaction downloads', 'type', k='-transactions-'),
         sg.Radio('Bank statements', 'type', k='-statements-', default=True)],
        [sg.Button('Bank transactions', k='-bank-')],
        [sg.Button('Excel bookkeeper', k='-book-'), sg.Column([[]], expand_x=True),
         sg.Button('Process', k='-process-'), sg.Button('Exit', k='exit')],
        [sg.StatusBar('', size=60, k='-status-')]
    ]
    window = sg.Window('Reports', layout, grab_anywhere=True, finalize=True)
    return window


def chaseParseTransactions(transactions, dfBank):
    for index, row in transactions.iterrows():
        identified = False
        details = row["Details"]
        date = datetime.strptime(row["Posting Date"], "%m/%d/%Y")
        desc = row["Description"]
        amt = row["Amount"]
        checkNum = row["Check or Slip #"]
        # break out of loop when no more row in transactions
        if isinstance(details, float):
            break
        # create new row template
        newRow = {'Category': {},
                  'type': details,
                  'date': date,
                  'description': desc,
                  'amount': amt,
                  'check#': checkNum
                  }

        if details.lower() in "credit" and description["Sales"] in desc.lower():
            newRow['Category'] = 'Sales'
            # add newRow to the bottom of dfBank, no need to convert row to dataframe
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if details.lower() in "debit":
            breakOutFlag = False
            # now we figure out what Category expense
            for category in description.keys():
                values = description[category]
                if isinstance(values, str):
                    if values in desc.lower():
                        newRow['Category'] = category
                        dfBank.loc[len(dfBank.index)] = newRow
                        identified = True
                        breakOutFlag = True
                        break
                else:
                    for value in values:
                        if value in desc.lower():
                            newRow['Category'] = category
                            dfBank.loc[len(dfBank.index)] = newRow
                            identified = True
                            breakOutFlag = True
                            break

        if details.lower() in "check":
            newRow['Category'] = 'Wages'
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if details.lower() in 'dslip':
            newRow['Category'] = 'Deposits'
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if not identified:
            newRow['Category'] = 'Miscellaneous'
            dfBank.loc[len(dfBank.index)] = newRow

    return dfBank


def exchangeParseTransactions(transactions, dfBank):
    for index, row in transactions.iterrows():
        identified = False
        date = datetime.strptime(row[3], "%m/%d/%Y")
        desc = row[5]
        # break out of loop when no more row in transactions
        if isinstance(desc, float):
            break
        # create new row template
        newRow = {'Category': '',
                  'type': desc,
                  'date': date,
                  'description': desc,
                  'amount': '',
                  'check#': ''
                  }

        if 'credit' and description["Sales"] in desc.lower():
            newRow['Category'] = 'Sales'
            newRow['type'] = 'Credit'
            newRow['amount'] = row[8]
            # add newRow to the bottom of dfBank, no need to convert row to dataframe
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if 'debit' in desc.lower():
            # now we figure out what category expense
            for category in description.keys():
                values = description[category]
                if isinstance(values, str):  # if only one category
                    if values in desc.lower():
                        newRow['Category'] = category
                        newRow['amount'] = -abs(row[7])
                        dfBank.loc[len(dfBank.index)] = newRow
                        if -abs(row[7]) == -1170:
                            print('hi')
                        identified = True
                else:
                    for value in values:
                        if value in desc.lower():
                            newRow['Category'] = category
                            newRow['amount'] = -abs(row[7])
                            dfBank.loc[len(dfBank.index)] = newRow
                            if -abs(row[7]) == -1170:
                                print('hi')
                            identified = True
                            break

        if "check" in desc.lower():
            newRow['Category'] = 'Wages'
            newRow['check#'] = row[10]
            newRow['amount'] = -abs(row[7])
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if 'deposit' in desc.lower():
            newRow['Category'] = 'Deposits'
            newRow['amount'] = row[8]
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if not identified:
            newRow['Category'] = 'Miscellaneous'
            if row[7]:
                newRow['amount'] = -abs(row[7])
            else:
                newRow['amount'] = row[8]
            dfBank.loc[len(dfBank.index)] = newRow
    return dfBank


def exchangeParseStatements(statement, dfBank):
    # creating a pdf reader object
    reader = PdfReader(statement)
    parsed = []
    for num in range(len(reader.pages)):
        page = reader.pages[num]
        # extracting text from page
        text = page.extract_text()
        lines = text.translate({ord(i): None for i in ' ,'})
        lines2 = re.split('\n', lines)

        filtered = []
        for l1 in lines2:
            find = re.match('\d+/\d\d\s[A-Z0-9(/)]+\d+\.\d+(-?)\d+\.\d+', l1)
            if find:
                filtered.append(find.group(0))

        for l2 in filtered:
            if not isinstance(l2, str):
                continue
            check = None
            l3 = ''
            if 'check' in l2.lower():
                # check to see if check number provided
                l3 = re.match('(?P<date>\d+/\d+)(?P<desc>\D+)(?P<check>\d\d\d\d)(?P<amt>\d+\.\d\d-?)', l2)
                if l3:
                    check = l3.group('check')
                else:
                    l3 = re.match('(?P<date>\d+/\d+)(?P<desc>\D+)(?P<amt>\d+\.\d\d-?)', l2)
            elif 'cable' in l2.lower():
                l3 = re.match('(?P<date>\d+/\d+)(?P<desc>\D+)(?P<amt>\d+\.\d\d-?)', l2)
            else:
                l3 = re.match('(?P<date>\d+/\d+)(?P<desc>\D+)(?P<amt>\d+\.\d\d-?)', l2)

            # check if amt is negative
            negative = re.search('-$', l3.group('amt'))
            # convert amount to float from string
            amt = -float(l3.group('amt').replace('-', '')) if negative else float(l3.group('amt').replace('-', ''))
            date = l3.group('date')
            desc = l3.group('desc').lower()

            # create new row template
            newRow = {'Category': '',
                      'type': '',
                      'date': date,
                      'description': desc,
                      'amount': amt,
                      'check#': check
                      }
            # now we figure out what category expense
            if amt < 0:
                newRow['type'] = 'Debit'
            else:
                newRow['type'] = 'Credit'
            identified = False
            for category in description.keys():
                values = description[category]
                if isinstance(values, str):  # if only one value
                    if values.replace(' ', '') in desc.lower():
                        newRow['Category'] = category
                        dfBank.loc[len(dfBank.index)] = newRow
                        parsed.append(newRow)
                        identified = True
                        break
                else:  # has a list of values
                    for value in values:
                        if value.replace(' ', '') in desc:
                            newRow['Category'] = category
                            dfBank.loc[len(dfBank.index)] = newRow
                            parsed.append(newRow)
                            identified = True
                            break
            if not identified:
                newRow['Category'] = 'Miscellaneous'
                dfBank.loc[len(dfBank.index)] = newRow
                parsed.append(newRow)
                identified = True
    return dfBank


def exportToExcel(outputExcel, dfBank, initial):
    with pd.ExcelWriter(outputExcel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        dfBank.to_excel(writer, sheet_name=initial + '.bank', header=None, index=False,
                        startrow=writer.sheets[initial + '.bank'].max_row)


def main():
    window = makeWindow(sg.theme())
    bank = '01.pdf'
    book = '2024taxCat - Copy.xlsx'
    transactions = ''
    dfBank = pd.DataFrame(columns=['Category', 'type', 'date', 'description', 'amount', 'check#'])
    while True:
        event, values = window.read()
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED, 'exit'):
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key=value) --------')
            for key in values:
                print(key, ' = ', values[key])
        if event == '-bank-':
            bank = sg.popup_get_file('Bank transactions/statements', 'Choose bank info', initial_folder=os.getcwd())
        elif event == '-book-':
            book = sg.popup_get_file('Excel book', 'Choose excel book', initial_folder=os.getcwd())
        elif event == '-process-':
            bankInitial = 't' if values['-exchange-'] else 'e'
            result = ''
            if values['-transactions-']:
                transactions = pd.read_csv(bank, index_col=False)
                if values['-exchange-']:
                    result = exchangeParseTransactions(transactions, dfBank)
                else:
                    result = chaseParseTransactions(transactions, dfBank)
            elif values['-statements-']:
                if values['-exchange-']:
                    result = exchangeParseStatements(bank, dfBank)
                else:
                    # result = chaseParseStatements(bank, dfBank)
                    continue

            exportToExcel(book, result, bankInitial)
            window['-status-'].update('Process complete')
        else:
            window.close()
            exit(0)


if __name__ == '__main__':
    sg.theme('dark grey 14')
    main()

# # bank statement
# bank = "Chase7668_Activity_20240324.csv"
# # excel bookkeeper
# book = "book2024 - Copy.xlsx"
#
# # load bank sheet
# loadedBank = pd.read_excel(book, sheet_name="y.bank", )
# dfBank = pd.DataFrame(columns=loadedBank.columns)
# transactions = pd.read_csv(bank, index_col=False)
#
# bank = {'chase': False, 'exchange': False}
# bankNum = input("press 1 for chase or 2 for exchange bank\n")
# statement = False
# if bankNum == '1':
#     bank['chase'] = True
# else:
#     bank['exchange'] = True
#     ask = input('press 1 for statement or 2 for downloaded transactions:')
#     statement = True if ask == '1' else False
#
# result = ''
# if bank['chase']:
#     result = chaseParseTransactions(transactions, dfBank)
#     exportToExcel(book, result, 'y')
# else:
#     if statement:
#         exchangeParseStatements()
#     else:
#         exchangeParseTransactions(transactions)

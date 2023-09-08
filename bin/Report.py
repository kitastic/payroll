from datetime import datetime
import pandas as pd


# bank statement
bank = "thrivegen082423.csv"
# excel bookkeeper
book = "bookThrivegen2023.xlsx"

# load bank sheet
loadedBank = pd.read_excel(book, sheet_name="t.bank", )

dfBank = loadedBank.copy()

statement = pd.read_csv(bank, index_col=False)

officeExpenses = ("samsclub",
                  "sams club",
                  "walmart",
                  'walmart.com',
                  "wal-mart",
                  "amzn",
                  'amazon',
                  "best buy",
                  "big lots",
                  "liquor",
                  "hobby-lobby",
                  "bath & body",
                  "staples",
                  "joann",
                  "sally beauty",
                  'wal sam',
                  'locked up',
                  'bestbuy'
                  )

transactions = dict({"Rent": "robson",
                     "Merchant Fees": ("direct payment", 'direct dps', 'hs group'),
                     "Bank Fees": "service charge",
                     "Cable": ("optimum", "suddenlink"),
                     "Utilities": ("ok natural gas", "city of stillwater"),
                     "Insurance": "insurance",
                     "Marketing": ("facebk", "google", "college coupon", 'metaplatfor'),
                     "Office Expenses": officeExpenses,
                     "License fees": ("secretary of state", "osbcb"),
                     "Supplies": {'supply', 'nailsjobs', 'nails plus'},
                     "Wages": {},
                     "Taxes": ("irs", "tax", 'oklahomataxpmts'),
                     "Remodel/Maintenance": ("lowe", "heating", 'frontier fire'),
                     "Miscellaneous": {},
                     "Depreciation": {},
                     "Amortization": {},
                     "Sales": "direct payment",
                     "Deposits": {},
                     "Non Deductible": {}
                     })

bank = {'chase': False, 'exchange': False}
bankNum = input("1: chase\n2: exchange\nenter bank:\n")
if bankNum == 1:
    bank['chase'] = True
else:
    bank['exchange'] = True

if bank['chase']:
    for index, row in statement.iterrows():
        identified = False
        details = row["Details"]
        date = datetime.strptime(row["Posting Date"], "%m/%d/%Y")
        desc = row["Description"]
        amt = row["Amount"]
        checkNum = row["Check or Slip #"]
        # break out of loop when no more row in statement
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

        if details.lower() in "credit" and transactions["Sales"] in desc.lower():
            newRow['Category'] = 'Sales'
            # add newRow to the bottom of dfBank, no need to convert row to dataframe
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if details.lower() in "debit":
            breakOutFlag = False
            # now we figure out what category expense
            for category in transactions.keys():
                values = transactions[category]
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
else:
    for index, row in statement.iterrows():
        identified = False
        date = datetime.strptime(row[3], "%m/%d/%Y")
        desc = row[5]
        # break out of loop when no more row in statement
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

        if 'credit' and transactions["Sales"] in desc.lower():
            newRow['Category'] = 'Sales'
            newRow['type'] = 'Credit'
            newRow['amount'] = row[8]
            # add newRow to the bottom of dfBank, no need to convert row to dataframe
            dfBank.loc[len(dfBank.index)] = newRow
            identified = True

        if 'debit' in desc.lower():
            # now we figure out what category expense
            for category in transactions.keys():
                values = transactions[category]
                if isinstance(values, str):
                    if values in desc.lower():
                        newRow['Category'] = category
                        newRow['amount'] = -abs(row[7])
                        dfBank.loc[len(dfBank.index)] = newRow
                        identified = True
                else:
                    for value in values:
                        if value in desc.lower():
                            newRow['Category'] = category
                            newRow['amount'] = -abs(row[7])
                            dfBank.loc[len(dfBank.index)] = newRow

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

with pd.ExcelWriter(book, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    dfBank.to_excel(writer, sheet_name='t.bank', header=None, index=False, startrow=writer.sheets['t.bank'].max_row)
    
# with pd.ExcelWriter(book, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
#     dfBank.to_excel(writer, sheet_name='t.bank', header=None, index=False, startrow=writer.sheets['t.bank'].max_row)
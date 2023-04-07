# Python program showing
# use of json package
import glob
import json
import pprint


path = '../db/'
data = {'upscale': {'name': 'upscale',
                    'login': {'username': 'upscalemanager', 'password': 'Joeblack334$'},
                    'salesJson': '../db/uSales.json',
                    'salesXl': 'uSales.xlsx',
                    'payments': 'uPayments.xlsx',
                    'employees': {'Anna': { 'paygrade': {'regType': False,
                                                         'regular': {'commission': 0, 'check': 0},
                                                         'special': {'commissionspecial': 6, 'checkdeal': 5, 'checkoriginal':6}},
                                            'name': 'Anna', 'salonName': 'upscale', 'pay': 0, 'rent': 0, 'fees': 5, 'active': True, 'id': 103},
                                  'Cindy': { 'paygrade': {'regType': False,
                                                          'regular': {'commission': 0, 'check': 0},
                                                          'special': {'commissionspecial': 6, 'checkdeal': 0, 'checkoriginal':0}},
                                            'name': 'Cindy', 'salonName': 'upscale', 'pay': 900, 'rent': 60, 'fees': 5, 'active': True, 'id': 104},
                                  'Kayla': { 'paygrade': {'regType': True,
                                                          'regular': {'commission': 6, 'check': 6},
                                                          'special': {'commissionspecial': 0, 'checkdeal': 0, 'checkoriginal':0}},
                                            'name': 'Kayla', 'salonName': 'upscale','pay': 1300, 'rent': 70, 'fees': 5, 'active': True, 'id': 102},
                                  'Kelly': { 'paygrade': {'regType': True,
                                                          'regular': {'commission': 7, 'check': 5},
                                                          'special': {'commissionspecial': 0, 'checkdeal': 0, 'checkoriginal':0}},
                                            'name': 'Kelly', 'salonName': 'upscale','pay': 1300, 'rent': 0, 'fees': 0, 'active': True, 'id': 100},
                                 'Kit': { 'paygrade': {'regType': True,
                                                          'regular': {'commission': 7, 'check': 5},
                                                          'special': {'commissionspecial': 0, 'checkdeal': 0, 'checkoriginal':0}},
                                            'name': 'Kelly', 'salonName': 'upscale','pay': 2000, 'rent': 0, 'fees': 0, 'active': False, 'id': 188},
                                 }
                    },
        'posh': {'name': 'posh',
                'login': {'username': 'kit@posh', 'password': 'Joeblack334$'},
                 'salesJson': '../db/pSales.json',
                 'salesXl': 'pSales.xlsx',
                 'payments': 'pPayments.xlsx',
                 'employees': {}
        }}

with open('../db/master.json', '+w') as writer:
    json.dump(data, writer, indent=4, sort_keys=True)

pp = pprint.PrettyPrinter(indent=4, compact=False, width=100)

with open('../db/master.json', 'r') as reader:
    b = json.load(reader)

# pp.pprint(b)

salon = list(b.keys())
s = b[salon[0]]
print(s)

# with open('../db/poshMaster.json', '+w') as writer:
#     writer.write(json.dumps(data2, indent=4))


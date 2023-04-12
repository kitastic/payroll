import string
import PySimpleGUI as sg
import json
import random
import re
import datetime
import os
from pprint import PrettyPrinter

import Ai

class View:
    def __init__(self):
        self.gui = None
        self.values = dict()
        self.event = ''
        self.salonNames = ['upscale', 'posh', 'nails']
        self.currentSalon = ''  # all, upscale, or posh
        self.startDate = ''
        self.endDate = ''
        self.dates = False
        self.btnColor = '#40444b'
        self.sbColor = '#91C0F6'

        self.tabFlags = dict()
        self.eTab_lb_Emps = dict()
        self.mTab_lb_Emps = dict()
        self.mTab_empStatus = dict()
        self.ai = Ai.Ai()
        self.j = PrettyPrinter(
            indent=2,
            width=100,
            compact=True,
            sort_dicts=False,
        )
        self.__setup__()
        self.openApp()

    def __setup__(self):
        # GUI element designs --------------------------------------
        sg.theme('darkgrey9')
        menu_def = [['File', ['Load Settings','Retrieve Payments','-------------',
                              'Get Sales', ['All::sales', 'Upscale::sales', 'Posh::sales'],
                              'Exit']],
                        ['View',['View Settings', 'Json Sales', ['Nails::viewjsonsales', 'Upscale::viewjsonsales', 'Posh::viewjsonsales']]],
                        ['Payroll',['All::payroll','Salon',['Upscale::payroll','Posh::payroll']]],
                        ['Export', ['Txt Files']],
                        ['Import', ['Excel Sales::importExcel']]
                        ]
        logTab = [[sg.Text("Anything printed will display here!")],
                  [sg.Multiline(font='Courier 10',expand_x=True,expand_y=True,write_only=True,
                                reroute_stdout=True,reroute_stderr=True,echo_stdout_stderr=True,autoscroll=True,
                                auto_refresh=True)]]

        sTabLeftFrame = sg.Frame('', [
            [sg.T('Current Salons:'), sg.Combo(values=(self.salonNames), key='-sTab_c_salon-', expand_x=True),
             sg.Button(image_filename='../images/refresh24.png', key='-sTab_btn_load-')],
            [sg.T('')],
            [sg.HorizontalSeparator()],
            [sg.Image(filename='../images/password-40.png',)],
            [sg.T('Salon Name:'), sg.Input('', key='-sTab_in_name-')],
            [sg.T('Username:'), sg.Input('', key='-sTab_in_uname-')],
            [sg.T('Password:'), sg.Input('', key='-sTab_in_pass-')],
            [sg.T('')],
            [sg.HorizontalSeparator()],
            [sg.Image(filename='../images/add-file-40.png')],
            [sg.T('Import Json Sales: ')],
            [sg.Input('',size=20, key='-sTab_in_jsonFile-'), sg.FileBrowse(target='-sTab_in_jsonFile-', initial_folder=os.getcwd(),)],
            [sg.Frame('',[
                [sg.Column([
                    [sg.T('Save')],
                    [sg.Button(image_filename='../images/add-fingerprint-40.png',tooltip='Save salon',key='-sTab_btn_save-')]
                ]),
                    sg.Column([
                        [sg.T('Clear')],
                        [sg.Button(image_filename='../images/erase-40.png', key='-sTab_btn_clear-',tooltip='Clear form')]
                    ]),
                    sg.Column([
                        [sg.T('Remove')],
                        [sg.Button(image_filename='../images/remove-fingerprint-40.png', key='-sTab_btn_remove-',tooltip='Remove salon')],
                    ])
                ]
            ],expand_x=True, vertical_alignment='bottom', element_justification='c')]

        ], expand_y=True, size=(250))
        sTab = [
            [sg.Image(filename='../images/shop-94.png',pad=(2,2),expand_x=True)],
            [sTabLeftFrame,
             sg.Frame('', [
                 [sg.Image(filename='../images/settings-40.png', expand_x=True)],
                 [sg.Multiline('', key='-sTab_in_display-', horizontal_scroll=True, autoscroll=True, auto_refresh=True, expand_x=True, expand_y=True)]], expand_x=True, expand_y=True)]
        ]
        paygradeFrame = [[sg.Radio('Regular',group_id='-paygrade-',key='-eTab_r_regular-',default=True,
                                   enable_events=True),
                          sg.Radio('Special',group_id='-paygrade-',key='-eTab_r_special-',default=False,enable_events=True),],
                         [sg.HorizontalSeparator()],
                         [sg.T("")],
                         [sg.Text('Commission:'),
                          sg.Combo((5,6,7),default_value=6,key='-eTab_c_commission-',size=(5,1),disabled=True),
                          sg.Text('Check:'),
                          sg.Combo((0,5,6,7),default_value=6,key='-eTab_c_check-',size=(5,1),disabled=True)],
                         [sg.T("")],
                         [sg.Text('Commission:',justification='left',expand_x=True),
                          sg.Combo((5,6,7),default_value=6,key='-eTab_c_commissionspecial-',size=(5,1),
                                   disabled=True)],
                         [sg.T('Check Deal:',justification='l',expand_x=True),
                          sg.Combo((0,5,6,7),default_value=6,key='-eTab_c_checkdeal-',size=(5,1),disabled=True)],
                         [sg.T('Check Original:', justification='l', expand_x=True),
                          sg.Combo((5,6,7),default_value=6,key='-eTab_c_checkoriginal-',size=(5,1),disabled=True,)]
                         ]
        empTabLeftCol = sg.Frame('', [
            [sg.Text('Salon: '), sg.Input('',key='-eTab_in_salon-', size=(15,None)),
             sg.Text('ID: ', tooltip='Upscale: 100-299\nPosh: 300-599'),
             sg.Input(key='-eTab_in_empId-', size=(6,None)),
             sg.Button(image_filename='../images/help-30.png', key='eTab_btn_empid',)],
            [sg.T('Status'), sg.Button(image_data=toggle_btn_on, key='-eTab_btn_status-', image_subsample=2,border_width=0,
                                       button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                       metadata=BtnInfo())],
            [sg.Text('Name (Last name optional):')],
            [sg.Input(key='-eTab_in_empName-',)],
            [sg.Text('Base Pay Per Wk:')],
            [sg.Input(key='-eTab_in_basePay-')],
            [sg.Text('Fees Per Day:')],
            [sg.Input(key='-eTab_in_fees-')],
            [sg.Text('Rent Per Week:')],[sg.Input(key='-eTab_in_rent-')],
            [sg.Frame('Pay Grade',paygradeFrame, expand_x=True)],
            [sg.Frame('',[
                [sg.Column([
                        [sg.T('Save New')],
                        [sg.Button(image_filename='../images/add-40.png', tooltip='Save New Employee',key='-eTab_btn_save-')]
                    ]),
                    sg.Column([
                        [sg.T('Clear Form')],
                        [sg.Button(image_filename='../images/erase-40.png', key='-eTab_btn_clear-',tooltip='Clear Form')]
                    ]),
                    sg.Column([
                        [sg.T('Update Existing')],
                        [sg.Button(image_filename='../images/save-as-40.png',
                                   key='-eTab_btn_update-',tooltip='Update Employee')],
                    ])
                ]
            ], expand_x=True)]
        ], expand_x=True, expand_y=True)

        empTabRightCol = sg.Frame('',[
            [sg.T('Choose Salon '),
             sg.OptionMenu(values=(self.salonNames),key='-eTab_om_salon-'),
             sg.Button(image_filename='../images/refresh24.png',  key='-eTab_btn_load-')],
            [sg.Image('../images/staff50.png', expand_x=True,)],
            [sg.Listbox(values=[],select_mode='extended',size=(50,22),key='-eTab_lb-', enable_events=True,expand_y=True)],
            [sg.Column([[sg.Button(key='-eTab_btn_remove-', image_filename='../images/trash-40.png',  tooltip='Delete employee')]],justification='r')]
        ], expand_x=True, expand_y=True)

        empTab = [[sg.Column([[empTabLeftCol]],expand_y=True,),sg.Column([[empTabRightCol]], expand_y=True,)]]

        mTab_r1c1 = sg.Frame('Date Range',
                             [[sg.Input('Enter Start Date',key='-mTab_in_sDate-',size=15),
                               sg.Button('',image_filename='../images/calendar20.png',button_color='#40444b',
                                         key='-mTab_cal_sDate-')],
                              [sg.Input('Enter End Date',key='-mTab_in_eDate-',size=15),
                               sg.Button('',image_filename='../images/calendar20.png',button_color='#40444b',
                                         key='-mTab_cal_eDate-')],
                              ], size=(150,90))
        mTab_r1c2 = sg.Frame('Salon',[
                        [sg.Image('../images/shop-30.png',expand_x=True)],
                        [sg.Combo(values=(self.salonNames), size=(12), key='-mTab_c_salon-')],
                        [sg.Button(image_filename='../images/refresh24.png', key='-mTab_btn_load-')]
                    ], size=(130, 90), element_justification='c')
        mTab_r1c3 = sg.Column([[sg.Checkbox('This\nWeek', default=False, key='-mTab_cb_thisweek-', enable_events=True)]])
        mTab_r1c4 = sg.Column([
            [sg.T('Sales')],[sg.Button('', image_filename='../images/chart-45.png', key='-mTab_btn_sales-', tooltip='Download salse reports')]
        ])
        mTab_r1c5 = sg.Column([[sg.T('Payroll')],
                        [sg.Button('', image_filename='../images/money-transfer-45.png',
                                    key='-mTab_btn_payroll-')],
                    ])
        mTab_r1c6 = sg.Column([
            [sg.T("Export")], [sg.Button(image_filename='../images/document-45.png', key='-mTab_btn_exporttxt-',  tooltip='Export txt files to hard drive')]
        ])
        mTab_r1c7 = sg.Column([
            [sg.T('Status')],[sg.Button(image_filename='../images/in-progress-45.png', key='-mTab_btn_status-',  tooltip='Export txt files to hard drive')]
        ])

        mainTab = [[mTab_r1c1,  mTab_r1c3, mTab_r1c4, mTab_r1c5, mTab_r1c6, mTab_r1c7],
                   [sg.Frame('', [[sg.Image('../images/shop-30.png',expand_x=True)],
                        [sg.Combo(values=(self.salonNames), size=(12), key='-mTab_c_salon-', enable_events=True),
                         sg.Button(image_filename='../images/refresh24.png', key='-mTab_btn_load-')],
                                    [sg.T('Employees')],
                                  [sg.Listbox(values=[],select_mode='extended',key='-mTab_lb-', expand_y=True,expand_x=True, enable_events=True)]],expand_y=True, size=(150,None)),
                    sg.Frame('',[[sg.Multiline('',key='-mTab_in_display-',expand_x=True,expand_y=True,autoscroll=True,horizontal_scroll=True)]], expand_y=True, expand_x=True, size=(550,None))],
                   ]

        self.layout = [[sg.Menubar(menu_def)],
                       [sg.Column([[sg.Image('../images/kp_w40.png', expand_x=True)]]),
                        sg.Column([[sg.Button(image_filename='../images/save-50.png',button_color='#40444b', expand_x=True,key='-Save-')]]),
                        sg.Column([[sg.ButtonMenu('', [['a','u','p'],['All','Upscale','Posh']], tooltip='Update sales database',
                                                  image_filename='../images/cloud-sync-50.png', key='updateJson', button_color=self.btnColor),
                                    sg.T('', key='jsonInfo'),
                                    sg.Button(image_filename='../images/shutdown-50.png',button_color='#40444b', key='Exit')]],justification='right',)],]
        self.layout += [[sg.TabGroup([[sg.Tab('Main', mainTab),
                                       sg.Tab('Employees', empTab),
                                       sg.Tab('Salon',sTab),
                                       sg.Tab('Log', logTab),
                                       sg.Tab('Output',[[sg.Multiline('', key='-OUT-', expand_x=True,expand_y=True, autoscroll=True, horizontal_scroll=True, auto_refresh=True)]],),
                                       ]])
                         ],
                        # key '-noticeBuffer-' is a MUST HAVE in order to make status bar show because
                        # it expands (assigned after starting window) and make sure there is space for the bar
                        [sg.T(key='-noticeBuffer-', font='ANY 1', pad=(0,0))],
                        [sg.StatusBar('hi',key='-notice-', expand_x=True, size=(200,None))]
                        ]
        # self.layout[-1].append(sg.Sizegrip())

    def openApp(self):
        self.salonNames = self.ai.listen('getSalonNames', None)

        # sg.show_debugger_window(location=(10,10))
        self.gui = sg.Window('', self.layout,
                             size=(700,735),
                             resizable=True,
                             finalize=True,
                             grab_anywhere=True,
                             sbar_background_color=self.sbColor,
                             button_color=self.btnColor
                             )
        self.gui['-noticeBuffer-'].expand(True, True, True)
        self.gui.set_min_size(self.gui.size)
        # self.getJsonLatestDates('display')
        self.salonNames = self.ai.listen('getSalonNames', guiData=False)
        salonLists = ['-mTab_c_salon-', '-eTab_om_salon-', '-sTab_c_salon-',]
        for l in salonLists:
            self.gui[l].update(value=self.salonNames[0])

        for s in self.salonNames:
            self.eTab_lb_Emps[s] = self.ai.listen('-eTab_btn_load-',s)
        # setup commands to cleanup gui while True loop
        mBar = ['Load Settings','Retrieve Payments', 'Get Sales', 'All::sales', 'Upscale::sales', 'Posh::sales',
                'View Settings','Salon Bundles','Json::view', '::viewjsonsales', 'Txt Files', 'Excel Sales::importExcel']

        mTab = ['-mTab_cal_sDate-', '-mTab_in_sDate-', '-mTab_cal_eDate-', '-mTab_in_eDate-', '-mTab_c_salon-',
                '-mTab_btn_load-', '-mTab_cb_thisweek-', '-mTab_btn_sales-',
                '-mTab_btn_payroll-', '-mTab_c_salon-', '-mTab_btn_exporttxt-', '-mTab_btn_status-', '-mTab_lb-']

        eTab = ['-eTab_r_regular-', '-eTab_r_special-', '-eTab_in_rent-', '-eTab_in_fees-', '-eTab_in_basePay-',
                '-eTab_in_empName-', '-eTab_in_empId-', 'eTab_btn_empid', '-eTab_in_salon-', '-eTab_btn_save-',
                '-eTab_btn_clear-', '-eTab_btn_update-', '-eTab_btn_remove-', '-eTab_btn_load-',
                '-eTab_lb-', '-eTab_om_salon-', ]

        sTab = ['-sTab_c_salon-', '-sTab_btn_load-', '-sTab_in_name-', '-sTab_in_uname-', '-sTab_in_pass-',
                '-sTab_in_jsonFile-', '-sTab_btn_save-', '-sTab_btn_clear-', '-sTab_btn_remove-',
                '-sTab_in_display-',]

        while True:
            event, values = self.gui.read()
            if event not in (sg.TIMEOUT_EVENT,sg.WIN_CLOSED):
                self.gui['-notice-'].update(event)
                print('============ Event = ',event,' ==============')
                print('-------- Values Dictionary (key=value) --------')
                for key in values:
                    print(key,' = ',values[key])
            if event == "Exit" or event == sg.WIN_CLOSED:
               break

            self.values = self.values | values
            self.event = event
            if event in mTab:
                self.listenMTab()
            elif event in mBar:
                self.listenMBar()
            elif event in eTab:
                self.listenETab()
            elif event in sTab:
                self.listenSTab()
            elif event == 'updateJson':
                recentSalonDates = self.ai.listen('updateJson', 'webscrape')
                today = datetime.datetime.today().strftime('%m/%d/%Y')
                '''
                    Webscrape start date should be inclusive of recent json date in case
                    last information pull was mid-day and not a full day of record
                '''
                if self.values['updateJson'] == 'Posh':
                    self.ai.listen('webscrape sales',['posh',recentSalonDates[0],today])
                elif self.values['updateJson'] == 'Upscale':
                    salons = ['upscale']
                    self.ai.listen('webscrape sales',['upscale',recentSalonDates[1],today])
                else:
                    salons = self.salonNames
                    # have to send webscrape command for each salon separately
                    # if the recent dates were the same then we could just send it in one go
                    for s, d in zip(salons, recentSalonDates):
                        self.ai.listen('webscrape sales',[s,d,today])
                self.ai.listen('updateJson', 'display')
            elif event == '-Save-':
                print('INFO: saving to database')
                self.ai.listen('savedb', guiData=self.values)

            else:
                print('INFO: command not found')

        self.exitProgram()

    def listenMBar(self):
        if self.event == 'Load Settings':
            self.ai.listen(self.event, guiData=None)
        elif self.event == 'View Settings':
            result = self.ai.listen(self.event, guiData=None)
            nicerResult = ''
            for key, value in result.items():
                if isinstance(value, dict):
                    for subkey, subval in value.items():
                        if isinstance(subval, dict):
                            for sskey, ssval in subval.items():
                                nicerResult += '    {}: {}\n'.format(sskey, ssval)
                        else:
                            nicerResult += '  {}: {}\n'.format(subkey, subval)
                else:
                    nicerResult += '{}: {}\n'.format(key, value)
            self.gui['-OUT-'].update(nicerResult)
        elif '::viewjsonsales' in self.event:
            # extract name and lower case salon name
            self.ai.listen('view sales', re.search('^\w+', self.event).group(0).lower())
        elif '::sales' in self.event:
            sName = re.search('^\w+', self.event).group(0).lower()
            if sName == 'all':
                sname = self.salonNames
            else:
                sname = [sName]

            try:
                sDate = sg.popup_get_date(title='Choose start date')
                sdate = '{}/{}/{}'.format(sDate[0],sDate[1],sDate[2])
                eDate = sg.popup_get_date(title='Choose end date')
                edate = '{}/{}/{}'.format(eDate[0],eDate[1],eDate[2])
                self.verifyDates(sdate, edate)
                if self.dates:
                    # package for each salon webscrape: name and dates, even if the dates are the same
                    for s in sname:
                        self.ai.listen('webscrape sales', [s,sdate,edate])
            except Exception:
                print('ERROR:(View.listenMBar) failed to validate dates to webscrape sales')

            self.getJsonLatestDates('display')

        elif self.event == 'Payroll':
            print('[LOG] payroll clicked')
            self.ai.listen('Payroll',guiData=self.values)
        elif self.event == 'Txt Files':
            try:
                sDate = sg.popup_get_date(title='Choose start date')
                sdate = '{}/{}/{}'.format(sDate[0],sDate[1],sDate[2])
                eDate = sg.popup_get_date(title='Choose end date')
                edate = '{}/{}/{}'.format(eDate[0],eDate[1],eDate[2])
                if self.verifyDates(sdate,edate):
                    # package for each salon webscrape: name and dates, even if the dates are the same
                    for s in self.salonNames:
                        self.ai.listen(self.event, [s,sDate,eDate])
            except Exception:
                print('ERROR:(View.listenMBar) failed to validate dates to export files')
        elif self.event == 'Excel Sales::importExcel':
            lo = [[sg.T('Salon'), sg.Combo(values=self.salonNames, key='sname')],
                  [sg.Input('',key='-salespfname-'), sg.FileBrowse(target='-salespfname-', initial_folder=os.getcwd())],
                  [sg.Button('Submit'), sg.Button('Cancel')]]
            win = sg.Window('Choose excel sales file to import', lo, finalize=True)
            win.read()
            pfname = ''
            sname = ''
            while True:
                event, values = win.read()
                if event == sg.WIN_CLOSED or event == 'Cancel':
                    break
                elif event == 'Submit':
                    pfname = values['-salespfname-']
                    sname = values['sname']
                    break
            win.close()
            if pfname and sname:
                self.ai.listen('Excel Sales::importExcel', [sname, pfname])

    def listenMTab(self):
        performedPayroll = False
        sDate = self.values['-mTab_in_sDate-']
        eDate = self.values['-mTab_in_eDate-']
        self.verifyDates(sDate,eDate)
        if self.event == '-mTab_cal_sDate-':
            try:
                sDate = sg.popup_get_date(title='Choose start date')
                sdate = '{}/{}/{}'.format(sDate[0],sDate[1],sDate[2])
                # tried simply adding 6 to day element and instead of going next month, day was 33
                # time delta is smarter and know when to increment month
                edate = datetime.datetime.strptime(sdate, '%m/%d/%Y') + datetime.timedelta(6)
                e = datetime.datetime.strftime(edate, '%m/%d/%Y')
                self.gui['-mTab_in_sDate-'].update(sdate)
                self.gui['-mTab_in_eDate-'].update(e)
            except Exception:
                print('ERROR:(View.listenMTab) failed to get valid date')
        elif self.event == '-mTab_cal_eDate-':
            eDate = sg.popup_get_date(title='Choose start date')
            try:
                edate = '{}/{}/{}'.format(eDate[0],eDate[1],eDate[2])
                if edate:
                    self.gui['-mTab_in_eDate-'].update(edate)
            except TypeError:
                pass
        elif self.event == '-mTab_cb_thisweek-':
            self.verifyDates()
        elif self.event == '-mTab_btn_sales-':
            if self.dates:
                sname = self.values['-mTab_c_salon-'].lower()
                ranges = self.splitRange(self.startDate, self.endDate)
                for r in ranges:
                    # each r is [sdate, edate]
                    self.ai.listen('webscrape sales', [sname, r[0], r[1]])
        elif self.event in ('-mTab_btn_payroll-', '-mTab_btn_exporttxt-', '-mTab_btn_status-', '-mTab_btn_load-'):
            sname = self.values['-mTab_c_salon-'].lower()
            if not self.dates and self.event != '-mTab_c_salon-':
                print("[View] Dates are not valid")
                return
            # if list box doesn't have existing salon's dictionary of employees
            if sname not in self.mTab_lb_Emps:
                self.mTab_lb_Emps[sname] = self.ai.listen('-mTab_btn_payroll-', [sname, self.startDate, self.endDate])
                self.gui['-mTab_lb-'].update(self.mTab_lb_Emps[sname].keys())
            else:
                print("WARNING(View.listenMTab): invalid dates")

            if self.event == '-mTab_btn_exporttxt-':
                try:
                    for s in self.salonNames:
                        self.ai.listen(self.event, [s, self.startDate, self.endDate])
                except Exception:
                    print('ERROR:(View.listenMTab): dates are valid, performed payroll,\n'
                          'but error after sending cmd to controller')

            elif self.event == '-mTab_btn_status-':
                self.mTab_empStatus = self.ai.listen('-mTab_btn_status-', sname)
                tmp = ''
                for name,bundle in self.mTab_empStatus.items():
                    tmp += '{}:\n {}\n'.format(name,bundle)
                self.gui['-mTab_in_display-'].update(tmp)

            elif self.event == '-mTab_btn_load-':
                self.gui['-mTab_lb-'].update(self.mTab_lb_Emps[sname].keys())

        elif self.event == '-mTab_lb-':
            try:
                # make sure something is selected, will catch and error if nothing is selected
                salon = self.values['-mTab_c_salon-'].lower()
                n = self.values['-mTab_lb-'][0]
                e = self.mTab_lb_Emps[salon][n]
                self.gui['-mTab_in_display-'].update(e)
            except KeyError:
                pass


    def listenETab(self):
        salonName = self.values['-eTab_om_salon-'].lower()
        if self.event == '-eTab_btn_load-':
            # send this command first to have a list to compare ids when adding new one
            self.eTab_lb_Emps = self.ai.listen('-eTab_btn_load-', salonName)
            self.refreshETabList(salonName)
        elif self.event == 'eTab_btn_empid':
            salon = self.test(self.values['-eTab_in_salon-'], 'str')
            if salon and salon in self.salonNames:
                salon = salon.lower()
                usedId = []
                # gather ids already in use
                for emp,values in self.eTab_lb_Emps[salon].items():
                    usedId.append(int(values['id']))

                while True:
                    id = random.randint(100,599)
                    if salon == 'upscale' and (100 <= id <= 299):
                        break
                    if salon == 'posh' and (300 <= id <= 599):
                        break
                self.gui['-eTab_in_empId-'].update(id)
            else:
                print('INFO (View.listenETab): choose salon first because id is based on that')
        elif self.event == '-eTab_btn_save-':
            # grab employees and gather into dictionary to validate id and etc
            # this step is needed incase the first thing someone does is add employee without
            # populating list first. if not, the first thing throwing error is gathering all
            # ids to make avoid duplicates
            result = self.parseEmp()
            if result:
                salonName = self.values['-eTab_in_salon-']      # specified when creating employee, not from listbox
                self.ai.listen(self.event, guiData=[salonName, result])
            self.refreshETabList(salonName)
        elif self.event == '-eTab_btn_update-':
            result = self.parseEmp()
            if result:
                salonName = self.values['-eTab_in_salon-']
                self.ai.listen(self.event, guiData=[salonName, result])
                self.refreshETabList(salonName)
        elif self.event == '-eTab_btn_remove-':
            try:
                eName = self.values['-eTab_lb-'][0]
                if eName:
                    if len(self.values['-eTab_lb-']) > 1:
                        for n in self.values['-eTab_lb-']:
                            self.ai.listen(self.event,guiData=[salonName,n])
                    else:
                        self.ai.listen(self.event,guiData=[salonName, eName])
                    self.refreshETabList(salonName)
            except Exception:
                print('ERROR: View.listenETab cannot remove employee > no name')
        elif '-eTab_btn_status-' in self.event:
            self.gui[self.event].metadata.state = not self.gui[self.event].metadata.state
            self.gui[self.event].update(image_data=toggle_btn_on if self.gui[self.event].metadata.state else toggle_btn_off,
                                   image_subsample=2)
        elif self.event == '-eTab_r_special-':
            self.togglePaygrade('special')
        elif self.event == '-eTab_r_regular-':
            self.togglePaygrade('regular')
        elif self.event == '-eTab_lb-':
            try:
                # make sure something is selected, will catch and error if nothing is selected
                salon = self.values['-eTab_om_salon-'].lower()
                n = self.values['-eTab_lb-'][0]
                e = self.eTab_lb_Emps[salon][n]
                self.empToGui(e)
            except KeyError:
                pass
        elif self.event == '-eTab_btn_clear-':
            self.clearBtn()
        else:
            print('INFO: Command not found in employee tab')

    def listenSTab(self):
        if self.event == '-sTab_btn_save-':
            sname = self.values['-sTab_in_name-']
            uname = self.values['-sTab_in_uname-']
            password = self.values['-sTab_in_pass-']
            json = False
            try:
                json = self.values['Browse']
            except Exception:
                pass
            # create salon first and then import json so that the default
            # pfname of json is still default
            salon = {'name': sname,
                     'login': {'username': uname, 'password': password},
                     'salesFnames':{},   # default path and filename of json
                     'path': '../db/',     # might not need yet
                     'payments': '',
                     'employees': {}}
            self.ai.listen('-sTab_btn_save-', salon)
            self.salonNames.append(sname)
            self.refreshSalonLists()
            if json:
                self.ai.listen('importJson', [salon, salon['salesJson']])
        elif self.event == '-sTab_btn_remove-':
            sname = self.values['-sTab_c_salon-']
            if sname in self.salonNames:
                self.ai.listen(self.event, sname)
                self.salonNames.remove(sname)
                self.refreshSalonLists()
        elif self.event == '-sTab_btn_clear-':
            self.gui['-sTab_in_name-'].update('')
            self.gui['-sTab_in_uname-'].update('')
            self.gui['-sTab_in_pass-'].update('')
            self.gui['-sTab_in_jsonFile-'].update('')




    def parseEmp(self):
        """
            instead of deciphering values everytime data passes between classes, this method
            will format it so that when employees object is passed around, it is easier to know
            what to do with it without having to catch all types of errors
        Returns:

        """
        checkpoint = {'salonname':False,'id':False,'name':False, 'paygrade':False}
        usedId = []
        currentSalon = self.values['-eTab_in_salon-']
        if self.eTab_lb_Emps[currentSalon]:
            for emp, values in self.eTab_lb_Emps[currentSalon].items():
                usedId.append(int(values['id']))

        # validating each field of information before sending to ai
        salon = self.test(self.values['-eTab_in_salon-'],'str')
        if salon in self.salonNames:
            checkpoint['salonname'] = True
        idNum = self.test(self.values['-eTab_in_empId-'], 'int')
        if (100 <= idNum <= 999)  and (idNum not in usedId):
            checkpoint['id'] = True
        if 'Update' in self.event:
            checkpoint['id'] = True

        # dont need to test status its a given
        name = self.test(self.values['-eTab_in_empName-'], 'str')
        if len(name) >= 1:
            checkpoint['name'] = True
        string.capwords(name)
        pay = self.test(self.values['-eTab_in_basePay-'], 'int')
        fees = self.test(self.values['-eTab_in_fees-'], 'int')
        rent = self.test(self.values['-eTab_in_rent-'], 'int')
        regType = self.test(self.values['-eTab_r_regular-'],'bool')
        commission,check,comspec,checkdeal,checkoriginal = (0 for i in range(1,6))
        if regType:
            self.togglePaygrade('regular')
            commission = self.test(self.values['-eTab_c_commission-'], 'int')
            check = self.test(self.values['-eTab_c_check-'], 'int')
        else:
            self.togglePaygrade('special')
            comspec = self.test(self.values['-eTab_c_commissionspecial-'], 'int')
            checkdeal = self.test(self.values['-eTab_c_checkdeal-'], 'int')
            checkoriginal = self.test(self.values['-eTab_c_checkoriginal-'], 'int')
        # validating paygrades and amounts correspond
        if regType and commission > 0 and check > 0:
            checkpoint['paygrade'] = True
        if not regType and comspec > 0  and checkoriginal > 0:
            checkpoint['paygrade'] = True

        if all(checkpoint.values()):        # if all data entries are valid or 'True'
            newEmp = {
                name:{'active':True,
                      'id': idNum, 'name': name, 'salonName':salon, 'pay':pay, 'fees':fees, 'rent':rent, 'paygrade':{'regType':regType,
                      'regular':{'commission': commission, 'check': check},
                      'special':{'commissionspecial': comspec, 'checkdeal': checkdeal, 'checkoriginal': checkoriginal}
                      }}}
            return newEmp
        elif not checkpoint['id']:
            sg.popup_ok('Invalid ID number:\nUpscale employees should be 100 - 299\n'
                        'Posh employees should be 300 - 599\nOr ID exists already')
        else:
            failed = []
            for point, val in checkpoint.items():
                if not val:
                    failed.append('Entry: {}'.format(point))
            sg.popup_ok('Invalid Entry\n{}'.format(failed))

    def empToGui(self, emp):
        """
            Updates the gui with information of employee retrieved from ai and fills
            the form on emloyees tab
        Args:
            emp:

        Returns:

        """
        if emp['active']:
            self.gui['-eTab_btn_status-'].metadata.setState(True)
            self.gui['-eTab_btn_status-'].update(image_data=toggle_btn_on,image_subsample=2)
        else:
            self.gui['-eTab_btn_status-'].metadata.setState(False)
            self.gui['-eTab_btn_status-'].update(image_data=toggle_btn_off,image_subsample=2)
        self.gui['-eTab_in_empId-'].update(emp['id'])
        self.gui['-eTab_in_salon-'].update(emp['salonName'])
        self.gui['-eTab_in_empName-'].update(emp['name'])
        self.gui['-eTab_in_basePay-'].update(emp['pay'])
        self.gui['-eTab_in_fees-'].update(emp['fees'])
        self.gui['-eTab_in_rent-'].update(emp['rent'])

        if emp['paygrade']['regType']:
            self.gui['-eTab_r_regular-'].update(value=True)
            self.gui['-eTab_r_special-'].update(value=False)
            self.togglePaygrade('regular')
            self.gui['-eTab_c_commission-'].update(emp['paygrade']['regular']['commission'])
            self.gui['-eTab_c_check-'].update(emp['paygrade']['regular']['check'])
        else:
            self.gui['-eTab_r_regular-'].update(value=False)
            self.gui['-eTab_r_special-'].update(value=True)
            self.togglePaygrade('special')
            self.gui['-eTab_c_commissionspecial-'].update(emp['paygrade']['special']['commissionspecial'])
            self.gui['-eTab_c_checkdeal-'].update(emp['paygrade']['special']['checkdeal'])
            self.gui['-eTab_c_checkoriginal-'].update(emp['paygrade']['special']['checkoriginal'])

    def determineSalon(self):
        """
        *** IMPORTANT *** If adding or removing salon, modify this method accordingly.
        If processing anything, we need to know which salon do we want to access if not all.
        During development, sometimes only one salon needs to be tested to make sure the
        workflow and functions are proper. After that we can expand to multiple salon tests.
        Args:

        Returns:
                list with salon name or False if can't find salon
        """
        try:
            if self.values['salonUpscale']:
                return ['upscale']
            elif self.values['salonPosh']:
                return ['posh']
        except TypeError:
            print('TypeError: Cannot determine which salon ')
            return False

    def togglePaygrade(self, paytype):
        rkeys = ['-eTab_c_commission-', '-eTab_c_check-']
        skeys = ['-eTab_c_commissionspecial-', '-eTab_c_checkdeal-', '-eTab_c_checkoriginal-']
        if paytype == 'regular':
            [self.gui[i].update(disabled=False) for i in rkeys]
            [self.gui[i].update(disabled=True) for i in skeys]
            self.gui['-eTab_r_regular-'].update(True)
            self.gui['-eTab_r_special-'].update(False)
        else:
            [self.gui[i].update(disabled=True) for i in rkeys]
            [self.gui[i].update(disabled=False) for i in skeys]
            self.gui['-eTab_r_regular-'].update(False)
            self.gui['-eTab_r_special-'].update(True)

    def refreshETabList(self, salonName):
        # refresh list with employee removed
        self.eTab_lb_Emps = self.ai.listen('-eTab_btn_load-', salonName)
        self.gui['-eTab_lb-'].update(values=self.eTab_lb_Emps[salonName].keys())

    def refreshMTabList(self, salonName):
        if self.eTab_lb_Emps:
            self.gui['-mTab_lb-'].update(self.mTab_lb_Emps[salonName].keys())

    def refreshSalonLists(self):
        salonLists = ['-mTab_c_salon-','-eTab_om_salon-','-sTab_c_salon-',]
        for l in salonLists:
            self.gui[l].update(values=(self.salonNames))

    def clearBtn(self):
        inputs = ['-eTab_in_empId-', '-eTab_in_salon-', '-eTab_in_empName-', '-eTab_in_basePay-', '-eTab_in_fees-', '-eTab_in_rent-',
                  '-eTab_c_commission-', '-eTab_c_check-', '-eTab_c_commissionspecial-', '-eTab_c_checkdeal-', '-eTab_c_checkoriginal-']
        self.gui['-eTab_btn_status-'].metadata.setState(False)
        self.gui['-eTab_btn_status-'].update(image_data=toggle_btn_off, image_subsample=2)
        for i in inputs:
            self.gui[i].update('')
        self.togglePaygrade('regular')

    def getDateRange(self):
        layout = [
            [sg.Frame('Date Range',
                     [[sg.Input('Enter Start Date',key='-mTab_in_sDate-',size=15),
                       sg.Button('',image_filename='../images/calendar20.png',button_color='#40444b',
                                 key='-mTab_cal_sDate-')],
                      [sg.Input('Enter End Date',key='-mTab_in_eDate-',size=15),
                       sg.Button('',image_filename='../images/calendar20.png',button_color='#40444b',
                                 key='-mTab_cal_eDate-')]
                      ],size=(150,90)),],
        ]

    def test(self, expression, dataType):
        try:
            if dataType == 'int':
                return int(expression)
            else:
                return expression

        except Exception:
            if dataType == 'str':
                return ''
            if dataType == 'int':
                return 0
            if dataType == 'bool':
                return False

    def verifyDates(self, sdate=None, edate=None):
        """
            takes two dates and make sure it is sdate is before edate.
            and if the "this week" checkbox is marked, figure out the monday
            and sunday dates automatically if current day is mid-week. This
            method sets global variables instead of returning any value.
            The other part of the test will convert text to datetime and compare
            dates.
        Args:
            sdate: string mm/dd/yyyy
            edate:

        Returns:

        """
        if self.values['-mTab_cb_thisweek-']:
            cday = datetime.date.today()
            daynum = cday.weekday()
            startday = cday - datetime.timedelta(daynum)
            endday = startday + datetime.timedelta(6)
            self.startDate = startday.strftime('%m/%d/%Y')
            self.endDate = endday.strftime('%m/%d/%Y')
            self.gui['-mTab_in_sDate-'].update(self.startDate)
            self.gui['-mTab_in_eDate-'].update(self.endDate)
            self.dates = True
        else:
            try:
                sd = datetime.datetime.strptime(sdate, '%m/%d/%Y')
                ed = datetime.datetime.strptime(edate, '%m/%d/%Y')
                if sd <= ed:
                    self.dates = True
                    self.startDate = sdate
                    self.endDate = edate
                else:
                    self.dates = False
            except ValueError:
                pass

    def splitRange(self, sDate, eDate):
        """
            When using the webscrape sales function, we use this helper function to split the
            date range request if it wants a range of over 6 months. The reason for that is because
            if the range is to spread out, zota website might either take way too long to load the request
            or not at all (sometimes). So to avoid time out, we can request multiple parts to be more
            efficient
        Args:
            sDate: (string) mm/dd/yyyy
            eDate:

        Returns:
            (list) list of date ranges, that are converted back to string format
        """
        sday = datetime.datetime.strptime(sDate, '%m/%d/%Y')
        eday = datetime.datetime.strptime(eDate, '%m/%d/%Y')
        dif = eday - sday
        if dif > datetime.timedelta(days=180):
            firsthalf = sday + (dif / 2)
            secondhalf = firsthalf + datetime.timedelta(days=1)
            firsthalf = datetime.datetime.strftime(firsthalf, '%m/%d/%Y')
            secondhalf = datetime.datetime.strftime(secondhalf, '%m/%d/%Y')
            return [[sDate, firsthalf], [secondhalf, eDate]]
        else:
            return [[sDate, eDate]]

    def exitProgram(self):
        self.gui.close()

    def updateValues(self, values):
        self.values = self.values | values


class BtnInfo:
    def __init__(self, state=True):
        self.state = state      # can be True, False, or None (disabled)

    def setState(self, state):
        self.state = state


if __name__ == '__main__':
    toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAAPpElEQVRoge1b63MUVRY' \
                     b'//Zo3eQHyMBEU5LVYpbxdKosQIbAqoFBraclatZ922Q9bW5b/gvpBa10' \
                     b'+6K6WftFyxSpfaAmCEUIEFRTRAkQFFQkkJJghmcm8uqd763e6b+dOZyYJktoiskeb9OP2ne7zu' \
                     b'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'
    toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAARfUlEQVRoge1bCZRVxZn+qure' \
                    b'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'
    start = View()

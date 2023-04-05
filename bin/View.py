import PySimpleGUI as sg
from Controller import Controller
import json
import helper
import cal


class View:
    def __init__(self):
        self.gui = None
        self.values = dict()
        self.salonName = ''  # all, upscale, or posh
        self.startDate = ''
        self.endDate = ''
        self.empsTabListEmps = dict()
        self.mainTabListEmps = dict()

        self.__setup__()
        self.openApp()

    def __setup__(self):
        # GUI element designs --------------------------------------
        sg.theme('darkteal4')
        menu_def = [['File', ['Load Settings','Retrieve Payments','-------------','Get Sales','Exit']],
                    ['View',['View Settings','Salon Bundles', 'Json::view']],
                    ['Payroll',['All','Salon',['Upscale','Posh::payroll']]],
                    ['Tools',['Create Employee','Edit Employee', 'Modify Employee']],
                    ]
        salonOM = sg.OptionMenu(values=('Upscale', 'Posh'), default_value='Upscale',)
        dateRange = sg.Frame('Date Range',
                             [[sg.Input('Enter Start Date',key='-startDateInput-',size=15),
                               sg.Button('', image_filename='../images/calendar20.png',key='-calsdate-')],
                              [sg.Input('Enter End Date',key='-endDateInput-',size=15),
                               sg.Button('',image_filename='../images/calendar20.png',key='-caledate-')]]
                             )

        empTabPaygradeRadio = [[sg.Radio('Regular',group_id='-paygrade-',key='-regular-',default=True,
                                        enable_events=True),
                                sg.Radio('Special',group_id='-paygrade-',key='-special-',default=False,enable_events=True),]]
        empTabRegPayFrame = [[sg.Text('Commission:'),sg.Combo((5,5.5,6,6.5,7,7.5), default_value=6,key='-commission-',size=(5,1)),
                                sg.Text('Check:'),sg.Combo((5,5.5,6,6.5,7,7.5), default_value=6,key='-check-',size=(5,1)),]]
        empTabSpecialPayFrame = [[sg.Text('Commission:',justification='left',expand_x=True),
                                 sg.Combo((5,5.5,6,6.5,7,7.5), default_value=6,key='-commissionspecial-',size=(5,1))],
                                [sg.T('Check Deal:',justification='l',expand_x=True),
                                 sg.Combo((5,5.5,6,6.5,7,7.5),default_value=5,key='-checkdeal-',size=(5,1)),],
                                [sg.T('Check Reporting to IRS:'),
                                 sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-checkreport-',size=(5,1)),]]

        logTab = [[sg.Text("Anything printed will display here!")],
                  [sg.Multiline(size=(60,15),font='Courier 8',expand_x=True,expand_y=True,write_only=True,
                                reroute_stdout=True,reroute_stderr=True,echo_stdout_stderr=True,autoscroll=True,
                                auto_refresh=True)]
                  # [sg.Output(size=(60,15), font='Courier 8', expand_x=True, expand_y=True)]
                  ]
        empTabLeftCol = [[sg.Text('Name (Last name optional):')],
                          [sg.Input(key='-empName-',)],
                          [sg.Text('Base Pay:')],
                          [sg.Input(key='-basePay-')],
                          [sg.Text('Fees Per Day:')],
                          [sg.Input(key='-fees-')],
                          [sg.Text('Rent:')],[sg.Input(key='-rent-')],
                          [sg.Frame('Pay Grade',empTabPaygradeRadio)],
                          [sg.Frame('Regular Pay',empTabRegPayFrame,k='-regularpayframe-')],
                          [sg.Frame('Special Pay',empTabSpecialPayFrame,k='-specialpayframe-',visible=False)],
                          [sg.Text(size=(25,1),k='-OUTPUT-')],
                          [sg.Column([[sg.Button('Clear')]], justification='right')],
                          [sg.Column([[sg.Button('Save Employee')]], element_justification='l'), sg.Column([[sg.Button('Remove Employee')]],
                                                                                  element_justification='r')],
                         ]
        empTabRightCol = [[salonOM],
                          [sg.Button('Populate Employees Settings')],
                          [sg.T('', key='salonoutput'), sg.T('Employees')],
                          [sg.Listbox(values=[], select_mode='extended',size=(30,20), key='-empTabListbox-',
                                      enable_events=True)]]

        empTab = [[sg.Column(empTabLeftCol,expand_y=True, expand_x=True),sg.Column(empTabRightCol, expand_y=True,
                                                                                   expand_x=True)],
                  ]

        mainTab = [[dateRange, sg.Button('Get Sales',), sg.Button('Payroll',), sg.Button('Populate Employees')],
                   [sg.T('Employees')], [sg.Listbox(values=[], select_mode='extended',size=(30,20),
                                                    key='-mainTabListbox-'),],
                   [sg.HSeparator()],
                   [sg.Text('',key='-EVENT-',)]]

        self.layout = [[sg.Menubar(menu_def,), ],
                        [sg.Column([[sg.Image('../images/kp_w.png', subsample=(4), expand_x=True)]],
                                   element_justification='left',),
                         sg.Column([[sg.Button(image_filename='../images/save40.png',image_subsample=(2), expand_x=True,key='-Save-' )]],
                                   justification='left',),
                         sg.Column([[sg.Button("Exit")]],justification='right',)],
                        ]

        self.layout += [[sg.TabGroup([[sg.Tab('Main', mainTab),
                                        sg.Tab('Employees', empTab),
                                       sg.Tab('Log', logTab),
                                       sg.Tab('Output', [[sg.Multiline('',key='-OUT-',horizontal_scroll=True,expand_x=True,expand_y=True, autoscroll=True, size=(100,3))]],)
                                       ]])
                         ]]
        self.layout[-1].append(sg.Sizegrip())

    def openApp(self):
        controller = Controller()
        self.gui = sg.Window('', self.layout,
                             size=(700,700),
                             resizable=True,
                             finalize=True,
                             grab_anywhere=True,

                             )
        self.gui.set_min_size(self.gui.size)
        while True:
            event, values = self.gui.read()
            if event not in (sg.TIMEOUT_EVENT,sg.WIN_CLOSED):
                print('============ Event = ',event,' ==============')
                print('-------- Values Dictionary (key=value) --------')
                for key in values:
                    print(key,' = ',values[key])
            if event == "Exit" or event == sg.WIN_CLOSED:
               break
            else:
                self.gui['-EVENT-'].update(str(values) + ' ...')

            self.values = self.values | values
            if event == 'Load Settings':
                print('[LOG] clicked load settings')
                controller.listen('loadSettings')
            elif event == 'View Settings':
                print('[LOG] clicked View Settings')
                controller.listen('viewSettings')
            elif event == 'Salon Bundles':
                print('[LOG] clicked salon bundles')
                controller.listen('viewSalonBundles')
            elif event == 'Get Sales':
                print('[LOG] getting sales, this may take a few minutes')
                self.updateValues(values)
                controller.listen('Get Sales', data=self.values)
            elif event == 'Json::view':
                print('[LOG] retrieving json for viewing')
                controller.listen('Json::view', data=self.values)
            elif event == 'Payroll':
                print('[LOG] payroll clicked')
                controller.listen('Payroll', data=self.values)
            elif event == 'Create Employee' :
                print('[LOG] attempting to create employee')
                pass
            elif event == '-calsdate-':
                self.gui['-startDateInput-'].update(cal.popup_get_date())
            elif event == '-caledate-':
                self.gui['-endDateInput-'].update(cal.popup_get_date())
            elif event == '-special-':
                    self.gui['-specialpayframe-'].update(visible=True)
                    self.gui['-regularpayframe-'].update(visible=False)
            elif event == '-regular-':
                    self.gui['-specialpayframe-'].update(visible=False)
                    self.gui['-regularpayframe-'].update(visible=True)
            elif event == 'Save Employee':
                print('[LOG] saving employee')
                controller.listen('save employee', data=self.values)
            elif event == 'Populate Employees Settings':
                salon = self.determineSalon()
                if not salon:
                    sg.popup('Please choose salon')
                else:
                    print('INFO: rounding up employees!')
                    self.empsTabListEmps = controller.listen('populateEmpListSettings',data=self.values)
                    names = []
                    for salon in self.empsTabListEmps.keys():
                        for e in self.empsTabListEmps[salon]:
                            names.append(e)
                    self.gui['-empTabListbox-'].update(values=names)

            elif event == '-empTabListbox-':
                salon = self.determineSalon()
                if salon:
                    name = values['-empTabListbox-'][0]
                    # TODO remove these tries once employes are normalized
                    try: pay = self.empsTabListEmps[salon[0]][name]['pay']
                    except Exception: pay = '0'

                    try: fees = self.empsTabListEmps[salon[0]][name]['fees']
                    except Exception: fees = '0'

                    try: rent = self.empsTabListEmps[salon[0]][name]['rent']
                    except Exception: rent = '0'

                    try: commission = self.empsTabListEmps[salon[0]][name]['commission']
                    except KeyError: commission = '0'

                    try: check = self.empsTabListEmps[salon[0]][name]['check']
                    except KeyError: check = '0'

                    try: comspec = self.empsTabListEmps[salon[0]][name]['commissionspecial']
                    except KeyError: comspec = '0'

                    try: checkdeal = self.empsTabListEmps[salon[0]][name]['checkdeal']
                    except KeyError: checkdeal = '0'

                    try: checkreport = self.empsTabListEmps[salon[0]][name]['checkreport']
                    except KeyError: checkreport = '0'

                    self.gui['-empName-'].update(value=name)
                    self.gui['-basePay-'].update(pay)
                    self.gui['-fees-'].update(fees)
                    self.gui['-rent-'].update(rent)
                    if self.gui['-regular-']:
                        self.gui['-commission-'].update(commission)
                        self.gui['-check-'].update(check)
                    else:
                        self.gui['-commissionspecial-'].update(comspec)
                        self.gui['-checkdeal-'].update(checkdeal)
                        self.gui['-checkreport-'].update(checkreport
                                                         )
            elif event == '-Save-':
                print('INFO: saving to database')
                controller.listen('savedb', data=self.values)
            else:
                self.gui['-EVENT-'].update('Command not found')

        self.exitProgram()

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

    def exitProgram(self):
        self.gui.close()

    def updateValues(self, values):
        self.values = self.values | values


start = View()

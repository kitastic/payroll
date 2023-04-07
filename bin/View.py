import PySimpleGUI as sg
from Controller import Controller
import json
import helper
import cal
import random

class View:
    def __init__(self):
        self.gui = None
        self.values = dict()
        self.event = ''
        self.salonNames = ['upscale', 'posh']
        self.currentSalon = ''  # all, upscale, or posh
        self.startDate = ''
        self.endDate = ''
        self.eTab_lb_Emps = dict()
        self.mTab_lb_Emps = dict()

        self.__setup__()
        self.openApp()

    def __setup__(self):
        # GUI element designs --------------------------------------
        sg.theme('darkgrey9')
        menu_def = [['File', ['Load Settings','Retrieve Payments','-------------',
                              'Get Sales', ['All::sales', 'Upscale::sales', 'Posh::sales'],
                              'Exit']],
                    ['View',['View Settings','Salon Bundles', 'Json::view']],
                    ['Payroll',['All','Salon',['Upscale','Posh::payroll']]],
                    ['Tools',['Create Employee','Edit Employee', 'Modify Employee']],
                    ]
        salonOM = sg.OptionMenu(values=('Upscale', 'Posh'), default_value='Upscale',key='-salon-')
        dateRange = sg.Frame('Date Range',
                             [[sg.Input('Enter Start Date',key='-startDateInput-',size=15),
                               sg.Button('', image_filename='../images/calendar20.png',key='-calsdate-')],
                              [sg.Input('Enter End Date',key='-endDateInput-',size=15),
                               sg.Button('',image_filename='../images/calendar20.png',key='-caledate-')]]
                             )

        paygradeFrame = [[sg.Radio('Regular',group_id='-paygrade-',key='-regular-',default=True,
                                   enable_events=True),
                          sg.Radio('Special',group_id='-paygrade-',key='-special-',default=False,enable_events=True),],
                         [sg.HorizontalSeparator()],
                         [sg.T("")],
                         [sg.Text('Commission:'),
                          sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-commission-',size=(5,1),disabled=True),
                          sg.Text('Check:'),
                          sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-check-',size=(5,1),disabled=True)],
                         [sg.T("")],
                         [sg.Text('Commission:',justification='left',expand_x=True),
                          sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-commissionspecial-',size=(5,1),
                                   disabled=True)],
                         [sg.T('Check Deal:',justification='l',expand_x=True),
                          sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-checkdeal-',size=(5,1),disabled=True)],
                         [sg.T('Check Original:', justification='l', expand_x=True),
                          sg.Combo((5,5.5,6,6.5,7,7.5),default_value=6,key='-checkoriginal-',size=(5,1),disabled=True,)]
                         ]

        logTab = [[sg.Text("Anything printed will display here!")],
                  [sg.Multiline(size=(60,15),font='Courier 8',expand_x=True,expand_y=True,write_only=True,
                                reroute_stdout=True,reroute_stderr=True,echo_stdout_stderr=True,autoscroll=True,
                                auto_refresh=True)]
                  ]
        empTabLeftCol = sg.Frame('', [
            [sg.Text('Salon: '), sg.Input(key='-salonName-', size=(15,None)), sg.Text('ID: '),sg.Input(key='-empId-', size=(6,None))],
            [sg.T('Status'), sg.Button(image_data=toggle_btn_on, key='statusToggle', image_subsample=2,border_width=0,
                                       button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                       metadata=BtnInfo())],
            [sg.Text('Name (Last name optional):')],
            [sg.Input(key='-empName-',)],
            [sg.Text('Base Pay Per Wk:')],
            [sg.Input(key='-basePay-')],
            [sg.Text('Fees Per Day:')],
            [sg.Input(key='-fees-')],
            [sg.Text('Rent Per Week:')],[sg.Input(key='-rent-')],
            [sg.Frame('Pay Grade',paygradeFrame)],
            [sg.Column([[sg.Button('Clear')]],justification='right', expand_y=True, vertical_alignment='bottom')],
            [sg.Button('Save Employee'), sg.T('         '), sg.Button('Update Employee')]
        ])

        empTabRightCol = sg.Frame('',[
            [sg.T('Choose Salon '), salonOM],
            [sg.Button('Populate Employees Settings')],
            [sg.Listbox(values=[],select_mode='extended',size=(50,23),key='-eTab_lb-', enable_events=True,expand_y=True)],

            [sg.Column([[sg.Button('Remove Employee')]],justification='r')]
        ])

        empTab = [[sg.Column([[empTabLeftCol]],expand_y=True,),sg.Column([[empTabRightCol]], expand_y=True,
                                                                                      )]]

        mainTab = [[dateRange, sg.Button('Get Sales',), sg.Button('Payroll',), sg.Button('Populate Employees')],
                   [sg.T('Employees')], [sg.Listbox(values=[], select_mode='extended',size=(30,20),
                                                    key='-mainTabListbox-')],
                   ]

        self.layout = [[sg.Menubar(menu_def,), ],
                       [sg.Column([[sg.Image('../images/kp_w.png', subsample=(4), expand_x=True)]],
                                  element_justification='left',),
                        sg.Column([[sg.Button(image_filename='../images/save40.png',image_size=(30,30), expand_x=True,key='-Save-' )]],
                                  justification='left',),
                        sg.Column([[sg.Button("Exit")]],justification='right',)],
                       ]

        self.layout += [[sg.TabGroup([[sg.Tab('Main', mainTab),
                                       sg.Tab('Employees', empTab),
                                       sg.Tab('Log', logTab),
                                       sg.Tab('Output',[[sg.Multiline('',key='-OUT-',horizontal_scroll=True,
                                                                      expand_x=True,expand_y=True,autoscroll=True,
                                                                      size=(100,100))]],)
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

            self.values = self.values | values
            self.event = event
            self.eTab_lb_Emps = controller.listen('populateEmpListSettings',guiData=self.values,addOn=self.salonNames)
            if event == 'Load Settings':
                print('[LOG] clicked load settings')
                controller.listen('loadSettings')
            elif event == 'View Settings':
                print('[LOG] clicked View Settings')
                controller.listen('viewSettings')
            elif event == 'Salon Bundles':
                print('[LOG] clicked salon bundles')
                controller.listen('viewSalonBundles')
            elif 'sales' in event:
                print('[LOG] getting sales, this may take a few minutes')
                salons = []
                if 'All' in event:
                    salons = self.salonNames.copy()
                else:
                    salons.append(event.replace('::sales','').lower())
                controller.listen('Get Sales', guiData=self.values, addOn=salons)
            elif event == 'Json::view':
                print('[LOG] retrieving json for viewing')
                controller.listen('Json::view', guiData=self.values)
            elif event == 'Payroll':
                print('[LOG] payroll clicked')
                controller.listen('Payroll', guiData=self.values)
            elif event == '-calsdate-':
                d = cal.popup_get_date()
                if d:
                    self.gui['-startDateInput-'].update(d)
            elif event == '-caledate-':
                d = cal.popup_get_date()
                if d:
                    self.gui['-startDateInput-'].update(d)
            elif 'statusToggle' in event:
                self.gui[event].metadata.state = not self.gui[event].metadata.state
                self.gui[event].update(image_data=toggle_btn_on if self.gui[event].metadata.state else toggle_btn_off, image_subsample=2)
            elif event == '-special-':
                self.togglePaygrade('special')
            elif event == '-regular-':
                self.togglePaygrade('regular')
            elif event == 'Save Employee':
                print('[LOG] saving employee')
                # grab employees and gather into dictionary to validate id and etc
                # this step is needed incase the first thing someone does is add employee without
                # populating list first. if not, the first thing throwing error is gathering all
                # ids to make avoid duplicates
                self.refreshETabList(controller)
                result = self.parseEmp()
                if result:
                    controller.listen('save employee', guiData=result, addOn=self.values['-salonName-'])
                self.refreshETabList(controller)
            elif event == 'Update Employee':
                self.refreshETabList(controller)
                result = self.parseEmp()
                if result:
                    controller.listen(event ,guiData=result,addOn=self.values['-salonName-'])
            elif event == 'Populate Employees Settings':
                print('INFO: rounding up employees!')
                self.refreshETabList(controller)
            elif event == '-eTab_lb-':
                try:
                    # make sure something is selected in, will catch and error if nothing is selected
                    salon = self.values['-salon-'].lower()
                    n = self.values['-eTab_lb-'][0]
                    e = self.eTab_lb_Emps[salon][n]
                    self.empToGui(e)
                except KeyError:
                    pass
            elif event == 'Clear':
                self.clearBtn()
            elif event == '-Save-':
                print('INFO: saving to database')
                controller.listen('savedb', guiData=self.values)
            elif event == 'Remove Employee':
                controller.listen(event, guiData=self.values, addOn=self.values['-salonName-'])
                # refresh list with employee removed
                self.refreshETabList(controller)
            else:
                print('INFO: command not found')

        self.exitProgram()

    def parseEmp(self):
        """
            instead of deciphering values everytime data passes between classes, this method
            will format it so that when employees object is passed around, it is easier to know
            what to do with it without having to catch all types of errors
        Returns:

        """
        checkpoint = {'salonname':False,'id':False,'name':False, 'paygrade':False}
        usedId = []
        currentSalon = self.values['-salonName-']
        if self.eTab_lb_Emps[currentSalon]:
            for emp, values in self.eTab_lb_Emps[currentSalon].items():
                usedId.append(int(values['id']))

        # validating each field of information before sending to ai
        salon = self.test(self.values['-salonName-'],'str')
        if salon in self.salonNames:
            checkpoint['salonname'] = True
        idNum = self.test(self.values['-empId-'], 'int')
        if (currentSalon == 'upscale' and (100 <= idNum <= 299) and (idNum not in usedId)) or \
                (currentSalon == 'posh' and (300 <= idNum <= 599) and (idNum not in usedId)):
            checkpoint['id'] = True
        if 'Update' in self.event:
            checkpoint['id'] = True

        # dont need to test status its a given
        name = self.test(self.values['-empName-'], 'str')
        if len(name) >= 1:
            checkpoint['name'] = True
        pay = self.test(self.values['-basePay-'], 'int')
        fees = self.test(self.values['-fees-'], 'int')
        rent = self.test(self.values['-rent-'], 'int')
        regType = self.test(self.values['-regular-'],'bool')
        commission,check,comspec,checkdeal,checkoriginal = (0 for i in range(1,6))
        if regType:
            self.togglePaygrade('regular')
            commission = self.test(self.values['-commission-'], 'int')
            check = self.test(self.values['-check-'], 'int')
        else:
            self.togglePaygrade('special')
            comspec = self.test(self.values['-commissionspecial-'], 'int')
            checkdeal = self.test(self.values['-checkdeal-'], 'int')
            checkoriginal = self.test(self.values['-checkoriginal-'], 'int')
        # validating paygrades and amounts correspond
        if regType and commission > 0 and check > 0:
            checkpoint['paygrade'] = True
        if not regType and comspec > 0 and checkdeal > 0 and checkoriginal > 0:
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
        if emp['active']:
            self.gui['statusToggle'].metadata.setState(True)
            self.gui['statusToggle'].update(image_data=toggle_btn_on,image_subsample=2)
        else:
            self.gui['statusToggle'].metadata.setState(False)
            self.gui['statusToggle'].update(image_data=toggle_btn_off,image_subsample=2)
        self.gui['-empId-'].update(emp['id'])
        self.gui['-salonName-'].update(emp['salonName'])
        self.gui['-empName-'].update(emp['name'])
        self.gui['-basePay-'].update(emp['pay'])
        self.gui['-fees-'].update(emp['fees'])
        self.gui['-rent-'].update(emp['rent'])

        if emp['paygrade']['regType']:
            self.gui['-regular-'].update(value=True)
            self.gui['-special-'].update(value=False)
            self.togglePaygrade('regular')
            self.gui['-commission-'].update(emp['paygrade']['regular']['commission'])
            self.gui['-check-'].update(emp['paygrade']['regular']['check'])
        else:
            self.gui['-regular-'].update(value=False)
            self.gui['-special-'].update(value=True)
            self.togglePaygrade('special')
            self.gui['-commissionspecial-'].update(emp['paygrade']['special']['commissionspecial'])
            self.gui['-checkdeal-'].update(emp['paygrade']['special']['checkdeal'])
            self.gui['-checkoriginal-'].update(emp['paygrade']['special']['checkoriginal'])
        print('============ Event = ','Updated employee info',' ==============')
        print('-------- Values Dictionary (key=value) --------')
        for key in self.values:
            print(key,' = ',self.values[key])

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
        rkeys = ['-commission-', '-check-']
        skeys = ['-commissionspecial-', '-checkdeal-', '-checkoriginal-']
        if paytype == 'regular':
            [self.gui[i].update(disabled=False) for i in rkeys]
            [self.gui[i].update(disabled=True) for i in skeys]
            self.gui['-regular-'].update(True)
            self.gui['-special-'].update(False)
        else:
            [self.gui[i].update(disabled=True) for i in rkeys]
            [self.gui[i].update(disabled=False) for i in skeys]
            self.gui['-regular-'].update(False)
            self.gui['-special-'].update(True)

    def refreshETabList(self, controller):
        # refresh list with employee removed
        self.eTab_lb_Emps = controller.listen('populateEmpListSettings',guiData=self.values,
                                              addOn=self.salonNames)
        salon = self.values['-salon-'].lower()
        self.gui['-eTab_lb-'].update(values=self.eTab_lb_Emps[salon].keys())

    def clearBtn(self):
        inputs = ['-empId-', '-salonName-', '-empName-', '-basePay-', '-fees-', '-rent-',
                  '-commission-', '-check-', '-commissionspecial-', '-checkdeal-', '-checkoriginal-']
        self.gui['statusToggle'].metadata.setState(False)
        self.gui['statusToggle'].update(image_data=toggle_btn_off, image_subsample=2)
        for i in inputs:
            self.gui[i].update('')
        self.togglePaygrade('regular')

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
                     b'+d3Hve2smvXLhqpKIpCmqaRruu1hmGsCoVCdxiGMc8wjNmapiUURalGm2tQeh3HSTuO802xWDxhmmaraZotpmkmC4UCWZZFxWKRHMcZVjMjAkQAEQqFmiORyJ+j0ei6UCgUNgyDz6uqym3Edi0KlC0227YBQN40zV2FQuHZbDa7O5fLOQBnOGCGBQTKNgzj9lgs9s9EIrE4EomQAOJaVf5IBYoHAKZpHs7lcn9rbm7+OAjGCy+8UHKsD9W3ruuRSCTyVCKR+Es8HlfC4bAPRF9fHx0/fpx+/PFH6unp4WOYJkbHtWApwhowYHVdp6qqKqqrq6Pp06fTvHnzqLq6mnWAa5qmLTYM48DevXuf7e/vf+Suu+7KVep3kIWsXbuW/7a0tDREo9Ed1dXVt8bjcbYK/MB3331HbW1t1N7eTgAIFoMfxSZTF3lU92sUMcplisJgxJbL5Sifz1N9fT01NjbSzTffXAKiaZpH+/v7169Zs+Yszr344oslFFbWQlpaWubGYrH3a2pqGmKxGCv74sWL9Pbbb1NnZyclEgmaNGmST13kUVsJ0h4wOB8EaixLkHIEKKAmAQx8BRhj+/btNHnyZNqwYQNNnDiR398wjFsTicSBDz74oPnOO+/8Gro1TbOyhWiaVh+Pxz+ura3FXwbj8OHDtHv3bgI448aNYyCg5Ouvv55mzJjBf2traykajXIf2WyWaQxWdOrUKTp//rww3V+N75GtRBaA4lkCA5NKpSiTydDq1atpyZIlfkvLstr7+/tvTyaT+MuAUhAQVVUjsVgMYABFVvzOnTvp888/Z34EIDgHjly6dCmfc3vBk4leFPd/jBwo3nHo559/pgMfHaATX59ApFZCb2NJKkVH5cARwAAUKBwDdOHChbRu3Tq/DegrnU4DlBxAwz3aQw895KpRUaCsp6urq9fDQUHxsIojR47QhAkTCNYCAO677z5acNttFI3FyCGHilaRUqk0myi2/nSaRwRMV9c1UhWFYrEozZo9mx3eyW9OMscGqexq3IJS7hlJOk+S3xTnvLyNB+L333/P4MycOVMYwGRN02pt234PwHFAJCxE1/Vl48aNO1hXV6fAEj777DPCteuuu44d9w033EDr16/3aQlKv3TpEv8tHS6exXiCvmpqaigWj5NCDqXT/bT9tdfoYnc39yWs5WqXcr6j0rHwK/I+KAy66u7upubmZlq8eLG47mQymeU9PT0fg95UD00lFAptSyQSHNrCgcM6xo8fz2DceOONtHnTJt4v2kXq7LxAHR0d7CvYccujRlNIwchX3WO06ejopM6ODrKsIgP0xy1bGGhhSRgZV7sELaNcRBnclzcwDt4dLAPdAhih+3A4/A8wEKyIAdE0bU0kEuGkDyaGaAo3YwMod999NyvZtCx20JlMf8lDkaK6ICgq8X/sRrxj1QUMwJw/D1BMvu8P99/PYTPCRAHI1Uxf5aLESvQ1FChQPPQKHQvRNG1pNBpdDf2rHl2hHMI3nD592g9tcdy8ppl03eCR3N3VxT5D5n9331U6/2XLUEv2Fe9vsWjRha5uKloWhUMGbdiwnjkVPkVEGWPNUoLnKJB/BdvACqBb6Bg5nbhmGMZWpnBVVWpDodDvw+EQO+H9+/fzDbhx9uzZTC2OU6Te3l5Wms/3AV9R8tCOe9FRSps4pJBdtCh56RKHyfX1DTRnzhx2dgAf/mQ0Iy9ky0jMFi1aVHL+k08+YWWAs4WibrnlFlq+fPmQ/bW2ttJPP/1EW7ZsGbLdiRMn2P/KdT74EfFbYAboGAn2rFlu4qjrGjCoVVVVawqFQiHDCHG0hNwBSKGjhYsWckf5XJ5yHBkJK3AtwPcVgq48y1A0lVRN8Y5Vv72GB1I1DgXzuRw5tsPZLHwJnJ5cdrnSbdq0afTAAw8MAgOybNkyVuqUKVN8yxxJJRa0i204wful0+lBVEwD1sA6hq77+lI8eBVFBQZNqqZpvxMZ97Fjxxg9HONhq6uq2IlnsjkXaU/xLlVppLHCNRck35m759FO0zyHrwpwNB8kvJjt2DS+bjxn/fAloMWRKGY4gWXI8X4luffee5kJ8LsjEQyakVArgEBbYRWyyNQFXUPnQoCFrmnafFwEICgUohEU1tDQQLbtlQXsImmqihyPFMWjI4bbIdUBFam8r5CbCJLi0pU79AjunRzVvU/1ruPFsOHhkO0fOnRoIFu9QtpasGCBv//DDz/Qu+++S2fOnOF3RMSIeh1yIggS3D179pQMhMcee4yTWVEWEgI9wfKEwDHv27dvUPUBx3DecjgvrguQ0Aa6xvMJqgQWuqqqMwXP4SHA4xCMWlGbwYh3exXde0onDwQSICnAhc+riuIn74yh15oR5HMqjyIEDPUN9cynIgS+0rxEKBuOc9u2bczXSG5h+QgiXn31VXrwwQc5t4KffOutt0pCb7QTpaCgUhEJyccoJUH5QfBEqUi0C1q+qBIjg5f6m6Fjlk84H/AekjgcV1VXk+Ol/6Cjih5ciOfkub2iuqA4A5Yi4GMsaaCtYxdpwvgJPh1cKWWBrjCSIaADhJg4J49YKB/hOwCBgnFdBuTRRx8d1O/JkyfZksSAhSBRxiYLAoXnn3/eD1AqvY+okCeTSd96VFWtASBVgtegFNFJyNDdhwTlqKXoO/6oH8BpiKDLvY5+yjSwHcdNOD0KG80kEX5KTBHIIxj7YAMhSNaG+12E5hiwsJyhBP0gIsXAFgOjkgidCwEWuhzNyOk+/Af8BUdRnqpLaojSUen5YSTQGC8gttFw6HIfsI5KRUxQspCuri6aOnXqkP1isCB6Gu4ZOSq9zLxKfj7dcZw+x3Gq0BG4U/wgRhfMXCR//s3Sv25hl52GDw1T0zAIKS5zMSUWbZsLkqMlGJ1QCCwD1dUDBw6UHf1w7hBEdwBEVsrjjz8+yKmDXuCL5HZw6shNhFMXDhu+J+hTyonQuRBgoXsrJqpwDlVesUIC3BaJRlh7hqaxB/B8OXk+2hvtiqi4+2gzpqoHkIi6PJ5TvAQRlFfwKOpCV9eoluORaM6dO5dp4+GHH+aKNWpvUBIsA5EVSkLkRWHBAieOca/s1EVkFHTyACno1L11CEM+o5hhRFAgRWCXdNu2TxWLxQaghYdEZIJ9/J00eTKRbZIaCZPDilcGrMJz0H6465kEY6EKvDwa5PkRhfy4S3HbF7MWJ4ciJA2+8C8RvBzmbwAIBGGqHKoGZceOHX6oLysa5wTlyRIsi4iioezsg/Mj5WhORLCYUZTuO606jnNMOFPkAzB37KNE4BRdSsEmlKX5SR6SQdU77yaFqtfGTQA1r6blZvAaZ/AaX1M4D7FdJ+7Y9O2335aMUnlJzS/ZEOm8+eabw8KJFR9ggmB4e7kSLL3L7yCfl6/h3aHrm266yffhtm0fV23b3i8mR+bPn8+NgBx4NZnsYZ7PZtxMHQBwJq55ZRKpNKJ5inYVrvrZO498v42bteNcNpsjx7G5DI0QFCNytOZG8Bznzp2j5557jvbu3TvoOsrfTzzxBE8vI+TFCB8pXVZSMlUAo9IcPJeP8nmuoQmxbbsVlNViWVbBsqwQHg4ZOhwjlHPkiy9oxR13kJ3P880iKWKK4mxcJHkeiSkDeYbrLRQ/ifTDAcWhXD5Hhby7EqZ1XyuHh6JaUO4lfomgLzwz1gOgYArnLSIfXMO7iOQPx0ePHuUAALOeGBTwIeWeBZNyTz75pF9shd8dDozgOYS6CJqga+l3gEELoiwsd3wvn89vxMOtXLmSXn75ZR6xKKXM6ezkim9vX68/Hy78uVISbXl+Y8C1uDgEEhVMUvVe6iWbHDrXfo6OHT/GeYBY8zVagJBUwkDfcp1M8dZLydVlgCCmIMjL1is9B/oT+YjwfZXAKAeMyGk2btzotykWi8Agyfxgmua/gBiQmzVrFq8iwTFuRljHcTXTWDfPaah+kVHMhahSAdGt6mr+vIjq+ReVR1R3dxf3hQryG2+84U+EyRYyWiJCdvSN3wA4YoKIZ+ekyE6uwoqp5XI0JqItWJhYxXk5YIhKMPIelG1owGqegc4ZENu2d+fz+cNi9m7Tpk0MiEASnGuaFs/2dXRcoGwmw5EUNkVUc0maPfRnEL3pTkXhEjumcTHraBaLXE/CbyBslOP2K3Xo/4tNVra8lQNA3jDgUUuDLjZv3iw780PZbHYP9K0hTvc6OKYoyp9CoZDCixJiMfrqq694FKATOF6Ej7AAHMMpozDII01xfUq5OQwoHY4bnIsySSFf4AVkyAvgs8DBQ43Iq0VGa5EDEk5MiUvW4eTz+ft7e3vP4roMSLvjOBN1XV8CM4TyoUxM6YIzAQJm2VA1TcQTbDHpVIp9S8Es8LFYHIb7+nr7qKu7i3r7+tgqIOfOtdMrr/yHHaMMxtW6eC44+iu1Ce4PBQYWyzU1NfnXsTo+lUr9G8EE1xI//PBDv0NVVaPxePwgFsqJFYrvvPMOT3lCeeBcOEdUSRcvXkS1NdJCOZIrjAOFeeyjxNzW9hFXTGF5oClBVWNlGRCNwkI5VAjuuecevw0WyqVSqd8mk8ks2vCMqQwIuWUDfykplAaFARAAA/qCtXhL7KmurpamT5tOU6ZiKalbagAUuWyOkj1JOtt+1l80IRxr0ImPFTCCUinPKLeUFMoGTWHqWAiWknqrFnkpqZi1HATIqlWrMFk0Nx6P82Jrsb4XieLrr7/O88CinO0MfP8wqGKrDHzk409Xim2sLiWly1hsDdoW0RSCJFFdRlvLss729/c3NzY2fo3gRi7Bl139joZtbW3LHcfZYds2f46AXGTr1q1MO8h+kaNAsZVWi/gZvLeUUvGmbRFJ4IHHsgR9RPBzBGzwwcgzsKpGBq9QKOBzhI0rVqw4Q16RUZaKH+w0Njae3b9//+22bT9lWZb/wQ6iA/wIoqYvv/ySK6siivLXp5aJtsYqNVUSAYao7MLHYmEIyvooQckTWZ4F4ZO2Z9Pp9CNNTU05+ZosZSkrKAcPHsQnbU/H4/ElYgX8/z9pG14kSj+UyWT+vnLlyoNBAF566aWS4xEBIuTTTz/Fcse/RqPRteFwOCy+ExHglFtuea2IHCJ7/qRgmubOfD7/jPfRpz+TOFQYPQiQoUQ4asMw8Fk0FtitCIVCv9F1nT+LVlW16hoFJOU4Tsq2bXwWfdyyrNZCodBSKBSScNgjXsBBRP8FGptkKVwR+ZoAAAAASUVORK5CYII='
    toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAARfUlEQVRoge1bCZRVxZn+qure' \
                    b'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'
    start = View()

import os.path
import PySimpleGUI as sg
from selenium import webdriver
# no longer need to download browser drivers
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import glob                     # check if file exists with wildcard
import datetime
from pathlib import Path

# local files
import helper


class Bot:
    def __init__(self):
        self.driver = None

    def dlEmpSales(self, salonName, uname, password, startDate, endDate):
        """
        Goes directly to employee sales reports on website and downloads excel file version.
        Automatic downloaded path was specified when creating chromedriver using
        linux (or windows, not sure but for sure tricky) syntax.
        After download finishes, the file gets renamed
        Args:
            startDate: (str) 'mm/dd/yyyy'
            endDate: (str) 'mm/dd/yyyy'

        Returns:
            (str): path+filename of downloaded file relative to main project's bin folder
        """
        dlDir = r'{}\{}\\'.format(os.getcwd(),salonName)
        # make sure path exists
        Path(dlDir).mkdir(parents=True, exist_ok=True)
        self.connect(dlDir, uname, password)
        startDate = startDate
        # saveAsName = salonName[0] + '.' + startDate.replace('/', '.') + '.xlsx'
        self.driver.get('https://pos2.zota.us/#/reports/employee-reports')
        sDateXpath = '//div/div/div[2]/div/main/div/div/div[3]/div[2]/span/span/span/span/input'
        helper.waitLoadingClick(sDateXpath, 10, 'By.XPATH: startDate', self.driver)

        sDateElement = self.driver.find_element(By.NAME, 'startDate')
        defaultStart = helper.parseDate(sDateElement.get_attribute('value'))
        sDateFormatted = helper.parseDate(startDate)
        helper.enterDate(sDateFormatted, defaultStart, sDateElement)
        time.sleep(.5)

        eDateElement = self.driver.find_element(By.NAME, 'endDate')
        defaultEnd = helper.parseDate(eDateElement.get_attribute('value'))
        eDateFormatted = helper.parseDate(endDate)
        helper.enterDate(eDateFormatted, defaultEnd, eDateElement)
        time.sleep(.5)

        runReportBtn = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/main/div/div/div[2]/div[5]/button')
        runReportBtn.click()

        # wait to locate and click the excel download button
        excelxpath = '//div/div/div[2]/div/main/div/div/div[4]/div/div/div/div/div/div/div/div[2]/span[2]'
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            helper.waitLoadingClick(excelxpath, 10, 'By.XPATH: excel link', self.driver)
            try:
                self.driver.find_element(By.XPATH, excelxpath).click()
                print('INFO: {}s out of 10s - Successfuly clicked download link'.format(counter))
                linkFound = True
                break
            except Exception as e:
                print('WARNING: {}s out of 10s - Failed to click excel link: '.format(counter))

            if counter == 30 :
                print('WARNING: refreshing page')
                self.driver.refresh()
            if counter == 60:
                print('WARNING: {}s out of 10s - Cannot find link even after refreshing'.format(counter))
                self.driver.quit()
                return False
        time_counter = 0
        time_to_wait = 8
        downloadedFileName = ''
        while True:
            time.sleep(1)
            time_counter += 1
            if time_counter % 2 == 0:
                try:
                    # max() called on empty (in this case folder) will return error
                    downloadedFileName = max([f for f in os.listdir(dlDir)],
                                   key=lambda xa: os.path.getctime(os.path.join(dlDir,xa)))
                    break
                except ValueError as e:
                    print('{}: waiting {} sec more'.format(e, time_counter))
            if time_counter == time_to_wait:
                sg.Print('ERROR: file never found')
                self.driver.quit()
                return False

        self.driver.quit()
        time.sleep(2)
        # rename file
        time_counter = 0
        time_to_wait = 20
        while '.crdownload' in downloadedFileName:
            time.sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:
                print('Waited too long for file to download')
                return False

        downloadedFileName = max([f for f in os.listdir(dlDir)],
                       key=lambda xa: os.path.getctime(os.path.join(dlDir,xa)))
        newDownloadedFname = f'{salonName[0]}Sales{endDate[-4:]}.xlsx'
        try:
            os.rename(os.path.join(dlDir,downloadedFileName),os.path.join(dlDir, newDownloadedFname))
        except FileExistsError:
            os.remove(dlDir + salonName[0] + 'Sales.xlsx')
            os.rename(os.path.join(dlDir,downloadedFileName),os.path.join(dlDir,newDownloadedFname))
        return dlDir, newDownloadedFname  # returns path and filename

    def connect(self, dlDir, uName, password):
        """
        Salon inherits this method
        Args:
            login: (list) first element is username and second is password

        Returns:
            None
        """
        chromedriver_autoinstaller.install()
        opts = webdriver.ChromeOptions()
        # dlDir = "D:\\pradagy\\projects\\payrollAutomation\\tmp\\"
        prefs = {'download.default_directory': dlDir,
                 'directory_upgrade': True,
                 }
        opts.add_experimental_option('prefs',prefs)
        self.driver = webdriver.Chrome(options=opts)

        self.driver.get("https://pos2.zota.us/#/login")
        # self.driver.maximize_window()
        usernameInput = self.driver.find_element(By.NAME,"username")
        usernameInput.clear()
        usernameInput.send_keys(uName)
        passInput = self.driver.find_element(By.NAME,"password")
        passInput.clear()
        passInput.send_keys(password)
        loginBtn = self.driver.find_element(By.CLASS_NAME,"btn-login")
        loginBtn.click()
        # once logged in, wait for page to load (when avatar is located)
        helper.waitLoadingPresence('avatar', 10, self.driver)

    def printHtml(self, pfname):
        chromedriver_autoinstaller.install()
        opts = webdriver.ChromeOptions()
        # dlDir = "D:\\pradagy\\projects\\payrollAutomation\\tmp\\"
        prefs = {
                'directory_upgrade':True,
                'detach': True,
                # "services.sync.prefs.sync.browser.download.manager.showWhenStarting":False,
                # "pdfjs.disabled":True,
                # "print.always_print_silent":True,
                # "print.show_print_progress":False,
                # "browser.download.show_plugins_in_list":False,
        }
        opts.add_experimental_option('prefs',prefs)
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get(os.getcwd()+ '/' + pfname)
        time.sleep(2)
        # self.driver.execute_script("window.print();")
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).send_keys('P').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        actions.send_keys(Keys.ENTER).perform()

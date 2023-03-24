from selenium import webdriver
# no longer need to download browser drivers
import chromedriver_autoinstaller

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

username = "kit@posh"
password = "Joeblack334$"
startDay = "03/13/2023"
endDay = "03/19/2023"

# list must be alphabetized, so iterating down drop list is easier
activeEmp = ['Nancy','Sophia']


def parseDate(date):
    # this function will extract the month, day, and year into three 
    # 
    month = int(date[0:2])
    day = int(date[3:5])
    year = int(date[8:10])  # two digit format of year

    return [month, day, year]


def enterDate(date, default, element):
    # default date tends to be more recent. that means default will subtract
    # date to find the difference to move back to

    # check if month the same or different
    monDif = date[0] - default[0]
    dayDif = date[1] - default[1]

    # =============================================================================
    #     if required date is a previous month than of default month, then we will
    #     have to press up monDif amount of times.
    #     ie: wanted month was 02 and default was 03,
    #     then monDif will be a negative int, and we have to press down 1 time to
    #     change default of '03' to '02'
    #     if the months are the same we will leave it alone
    # =============================================================================
    element.click()
    # The following two left arrows are meant to make sure the highlighted
    # area for editing is in the far left (sometimes year is selected when clicked)
    element.send_keys(Keys.ARROW_LEFT * 2)
    if monDif <= -1:
        for i in range(0, abs(monDif)):  # use absolute of negative int
            element.send_keys(Keys.ARROW_DOWN)

    if monDif >= 1:
        for i in range(0, monDif):
            element.send_keys(Keys.ARROW_UP)

    # now we press right to change the date criteria within the element
    element.send_keys(Keys.ARROW_RIGHT)

    # we just match up the days (easy because month is already specified)

    if dayDif <= -1:
        for i in range(0, abs(dayDif)):
            element.send_keys(Keys.ARROW_DOWN)

    if dayDif >= 1:
        for i in range(0, dayDif):
            element.send_keys(Keys.ARROW_UP)


def waitLoadingClick(xpath, time, element):
    try:
        element = WebDriverWait(driver, time).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutError:
        print('time out waiting for' + element + ' to be clickable')


def waitLoadingPresence(className, time, element):
    try:
        element = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, className)))
    except TimeoutError:
        print('time out waiting for' + element + ' to be located')


# start web auto
# ------------------------------------------------------------------------------
chromedriver_autoinstaller.install()
driver = webdriver.Chrome(service=Service())
driver.get("https://pos2.zota.us/#/login")
# driver.maximize_window()

# login
# -------------------------------------------------------
usernameInput = driver.find_element(By.NAME, "username")
usernameInput.clear()
usernameInput.send_keys(username)
passInput = driver.find_element(By.NAME, "password")
passInput.clear()
passInput.send_keys(password)
loginBtn = driver.find_element(By.CLASS_NAME, "btn-login")
loginBtn.click()

# once logged in
# ------------------------------------------------------
# wait for page to load (when avatar is located within page)
waitLoadingPresence('avatar', 5, 'avatar')

# load payroll page
driver.get("https://pos2.zota.us/#/payroll")

# wait for startdate element to be clickable
s = '//div/div/div[2]/div/main/div/div/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/span/span/span/span/input'
waitLoadingClick(s, 5, 'startDate input')

# select start date
startDate = driver.find_element(By.NAME, 'startDate')
defaultstart = parseDate(startDate.get_attribute('value'))
start = parseDate(startDay)
enterDate(start, defaultstart, startDate)
time.sleep(.5)

# select and change end date
endDate = driver.find_element(By.NAME, 'endDate')
defaultend = parseDate(endDate.get_attribute('value'))
end = parseDate(endDay)
enterDate(end, defaultend, endDate)
time.sleep(1)

# select employee from list

# manually clicking menu
e = driver.find_element(By.CLASS_NAME, 'k-dropdown-wrap')

for a in activeEmp:
    e.click()
    end = False
    eZota = ""
    while (not end):
        # while zota employee list not ended and not matched
        e.send_keys(Keys.ARROW_DOWN)
        etemp = e.text
        if eZota == etemp or a in e.text:
            end = True
        eZota = etemp

    print('found match: ' + eZota)
    load = driver.find_element(By.XPATH,
                               '//*[@id="root"]/div/div[2]/div/main/div/div/div/div[3]/div[1]/div/div[4]/button')
    load.click()
    reportBtn = '//div/div/div[2]/div/main/div/div/div/div[3]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/button'
    waitLoadingClick(reportBtn, 5, "Report Button")
    reportBtn = driver.find_element(By.XPATH, reportBtn)
    reportBtn.click()
    r = driver.find_element(By.XPATH,
                            '//div/div/div[2]/div/main/div/div/div/div[3]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/pre')
    print(r.text)


# e.send_keys(activeEmp[0])
# time.sleep(1)
# e.send_keys(Keys.ARROW_DOWN*2)
# e.send_keys(Keys.ENTER)
# print(e.text)

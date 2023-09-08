from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
import pandas as pd
import re
import tkinter as tk
from tkinter import simpledialog
import time
import os




def parseDate(date):
    """
    This function will splice the given string and extract the month,
    day, and year into a list of integers.
    Args:
        date (str): "month/day/year" format

    Returns:
        list[int]: a list with three elements for each month, day, and yer
    """
    # this function will extract the month, day, and year into three 
    # 
    month = int(re.search('^\d+', date).group(0))
    day = int(re.search('/\d+/', date).group(0).replace('/',''))
    year = int(re.search('\d+$', date).group(0))  # two digit format of year
    return [month, day, year]

def enterDate(date, default, element):
    """
    This function is meant to figure out the difference between the 'date'
    and 'default' dates. Then navigate the text input element (a tricky one)
    using arrow keys to change the value from 'default' to 'date'. The
    element is prefilled with default date and cannot be simply clearing
    and pasting new values. Doing so will make the webpage to turn completely blank.
    Args:
        date (list): a list with three int elements for month, day, and yer
        default (list): a list with three int elements for month, day, and year
        element (webelement): text input webelement

    Returns:
        None
    """
    # Find the difference between the list elements
    # check if month the same or different
    monDif = date[0] - default[0]
    dayDif = date[1] - default[1]
    yearDif = date[2] - default[2]

    element.click()
    '''
    The following two left arrows are meant to make sure the highlighted
    area for editing is in the far left (sometimes year is selected when clicked)
    '''
    element.send_keys(Keys.ARROW_LEFT)
    element.send_keys(Keys.ARROW_LEFT)
    element.send_keys(Keys.ARROW_LEFT)

    # if wanted month is 01 and default month is 12, monDif = -11
    if monDif <= -1:
        # use absolute of negative int
        for i in range(0, abs(monDif)):
            # from 12 press down 11 times to get to 01
            element.send_keys(Keys.ARROW_DOWN)
    # if wanted month is 12 and default is 1, monDif = 11
    if monDif >= 1:
        for i in range(0, monDif):
            # from 1 press up 11 times to get to 12
            element.send_keys(Keys.ARROW_UP)
    '''
    0 is left out of the two if tests because if there is no difference,
    we just move to the next area by pressing right
    '''

    # now we press right to change the date criteria within the element
    element.send_keys(Keys.ARROW_RIGHT)
    if dayDif <= -1:
        for i in range(0, abs(dayDif)):
            element.send_keys(Keys.ARROW_DOWN)
    if dayDif >= 1:
        for i in range(0, dayDif):
            element.send_keys(Keys.ARROW_UP)

    element.send_keys(Keys.ARROW_RIGHT)
    if yearDif <= -1:
        for i in range(0, abs(yearDif)):
            element.send_keys(Keys.ARROW_DOWN)
    if yearDif >= 1:
        for i in range(0, yearDif):
            element.send_keys(Keys.ARROW_UP)

def waitLoadingClick(xpath, sec, elementName, driver):
    """
    Waits for a specified time for a certain element to be clickable.
    This is to wait for the page to completely load.
    Args:
        xpath(str): html xpath of web element
        sec(int): number of seconds to wait
        elementName(str): name of web element
        driver(web element): browser driver

    Returns:
        None
    """
    try:
        element = WebDriverWait(driver, sec).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutError:
        print('time out waiting for' + elementName + ' to be clickable')

def waitLoadingPresence(class_name, sec, driver):
    """
    Waits for a specified time for a certain element to be found or located.
    This is to wait for the page to completely load.
    Args:
        class_name(str): class name of web element
        sec(int): number of seconds to wait
        driver(web element): browser driver

    Returns:
        None
    """
    try:
        element = WebDriverWait(driver, sec).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    except TimeoutError:
        print('time out waiting for' + class_name + ' to be located')

def getDay(row):
    '''
    converts any number to floats and captures day if present
    Args:
        row(str): row of data

    Returns:
        [d(str), v(float)]: list of day and value or just value only
    '''
    v = re.findall('(?<=\$)\d?,?\d+\.\d+', row)
    # remove comma and convert strings to float for money price
    v = [float(i.replace(',', '')) for i in v]
    d = re.match('\d+-\w+', row)
    # if d is found then return both d and v, else return v
    if d:
        return d.group(0), v
    else:
        return v

def dayToDate(rawDay, rawDate):
    year = re.search('\d+$', rawDate).group(0)
    month = re.search('^\d+', rawDate).group(0)
    dayNum = re.search('^\d+', rawDay).group(0)
    dayWord = re.search('\w+$', rawDay).group(0)
    dateString = ''.join([month, '/', dayNum, '/', year])
    dateObj = datetime.datetime.strptime(dateString, '%m/%d/%Y')
    return [dateObj, dayWord]  # can also return date obj

def getDateGui():
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    startStr = simpledialog.askstring(title="Dates",
                                      prompt="Enter start day of week (mm/dd/yyyy): ")
    startObj = datetime.datetime.strptime(startStr, '%m/%d/%Y')
    endObj = startObj + datetime.timedelta(days=6)
    endStr = endObj.strftime('%m/%d/%Y')
    return [startStr, endStr]

def getFloat(row):
    # searching at the end of string for dollar amount
    v = re.search('\d+?,?\d+.\d+$',row)
    if not v:
        # remove dollar sign using 'positive lookbehind assertion'
        zero = re.search('(?<=[^\d])0\.0', row)
        return(float(zero.group(0)))
    else:
        return(float(v.group(0).replace(',','')))

def renameFile(newName, downloadPath, time_to_wait=60):
    time_counter = 0
    filename = max([f for f in os.listdir(downloadPath)], key=lambda xa :   os.path.getctime(os.path.join(downloadPath,xa)))
    while '.crdownload' in filename:
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise Exception('Waited too long for file to download')
    filename = max([f for f in os.listdir(downloadPath)], key=lambda xa :   os.path.getctime(os.path.join(downloadPath,xa)))
    os.rename(os.path.join(downloadPath, filename), os.path.join(downloadPath, newName))

def update1099Xl():
    # pass path, salon prefix for sheetname, data
    path = '2023 - Copy.xlsx'
    sheet = 'p.salary'
    data = [[datetime.now(), '', 'Kit', 2000, '', '', 3000],
            [datetime.now(), '', 'kelly', 2300, '', '', 4300]]
    df = pd.DataFrame(data, )
    reader = pd.read_excel(path, sheet_name=sheet, index_col=False)
    startRow = len(reader.index)
    with pd.ExcelWriter(path, mode='a', engine='openpyxl',
                        if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name='p.salary',
                    header=False, index=False, startrow=startRow
                    )

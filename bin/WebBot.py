import requests
from bs4 import BeautifulSoup

login_url = "https://pos2.zota.us/#/login"  # Replace with the actual login URL
data = {
    'username': 'upscalemanager',
    'password': 'Joeblack334$'
}

with requests.Session() as s:
    response = s.post(login_url, data=data)
    # Check if login was successful (e.g., by checking the response status code or content)

    # Now, make requests to authenticated pages within the same session
    protected_page_url = 'https://pos2.zota.us/#/reports/employee-reports'
    protected_page_response = s.get(protected_page_url)

    sDate = '8/11/2025'
    eDate = '8/17/2025'

    payload = {'startDate': sDate, 'endDate': eDate}

    r = requests.post(protected_page_url, data=payload)

    # Parse the HTML content of the protected page
    soup = BeautifulSoup(protected_page_response.text, 'html.parser')
    print()
    # Extract desired information from 'soup'
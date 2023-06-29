from bs4 import BeautifulSoup
import requests
import re
import time
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

def scrapingResults():
    url = "http://exam.dtu.ac.in/result.htm"  # Replace with the actual URL of the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    td_element = soup.find('td', class_='back')
    if td_element:
        table_element = td_element.find('table')
        table_rows = table_element.find_all('tr')
        third_row = table_rows[2]
        row_contents = []
        for td_element in third_row.find_all('td'):
            content = td_element.text.strip()
            # Remove redundant spaces using regular expression
            content = re.sub('\s+', ' ', content)
            row_contents.append(content)
        return row_contents
    else:
        print("Table with class 'back' not found.")
        return None


def send_email(sender, recipient, subject, message):
    ses_client = boto3.client('ses', region_name=os.environ['REGION'])

    response = ses_client.send_email(
        Source=sender,
        Destination={
            'ToAddresses': [recipient]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )
    print(f"Email sent. MessageId: {response['MessageId']}")

sender_email= os.environ['SENDMAIL']

recipient_email = os.environ['RECEIVEMAIL']

previous_content = None

while True:
    current_content = scrapingResults()

    if current_content is not None:
        if current_content != previous_content:
            message = '\n'.join(current_content)

            # Send the email via Amazon SES
            send_email(sender_email, recipient_email, 'Scraped Results', message)

            previous_content = current_content

    # Wait for 1 minute before the next scraping
    time.sleep(60)

from bs4 import BeautifulSoup
import requests
import time
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def scrapingResults():
    url = "http://exam.dtu.ac.in/result.htm"  
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    td_element = soup.find('td', class_='back')
    if td_element:
        table_element = td_element.find('table')
        table_rows = table_element.find_all('tr')
        third_row = table_rows[2]
        results = []
        resultFinal = f"<b>New Results Announced, Check <a href='http://exam.dtu.ac.in/' style='text-decoration: none; font-weight: bold; color: black;'>DTU Results</a></b><br>"
        for td_element in third_row.find_all('td'):
            font_tag = td_element.find('font')
            main_text = None  
            for item in font_tag.find_all('a'):
                if item.previous_sibling:  
                    main_text = item.previous_sibling.strip(':').strip()  
                link = item.get('href')
                results.append((main_text, item.text.strip(), link))
        for result in results:
            resultFinal += f"<a href='http://exam.dtu.ac.in/{result[2]}' style='text-decoration: none; font-weight: bold; color: #0070C0;'><b>{result[0]} {result[1]}</b>\n</a><br>"
        return resultFinal
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
                'Html': {
                    'Data': message
                }
            }
        }
    )
    print(f"Email sent. MessageId: {response['MessageId']}")


sender_email = os.environ['SENDMAIL']
recipient_email = os.environ['RECEIVEMAIL']

previous_content = None

while True:
    current_content = scrapingResults()

    if current_content is not None:
        if current_content != previous_content:
            message = current_content

            # Send the email via Amazon SES
            send_email(sender_email, recipient_email, 'DTU Results', message)

            previous_content = current_content

    # Wait for 1 minute before the next scraping
    time.sleep(60)

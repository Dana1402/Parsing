import gspread
import csv
from oauth2client.service_account import ServiceAccountCredentials

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/anastasiya/PycharmProjects/Selenium/nimble-climber-432115-r6-f9c5fc5e77d1.json', scopes = scopes)

file = gspread.authorize(creds)
workbook = file.open("Indeed.com")
sheet = workbook.sheet1

csv_file = '/Users/anastasiya/PycharmProjects/Selenium/indeed_data.csv'
with open(csv_file, "r") as f:
    values = [r for r in csv.reader(f, delimiter=';')]
    sheet.update(values)


# Run some simple reports against the database with 
# IBM Cloud access management data
#
# Written by 2023 Henrik Loeser, IBM, hloeser@de.ibm.com

import json, sys
from sqlalchemy import create_engine, text
from utils import reports

def printColumnHeaders(keys):
    for key in keys:
        print(key, end=" ")
    print('\n================')

def runReport(connection, query):
    print('-----------------------------------------------')
    print('-----------------------------------------------')
    print()
    print(query['name'], ':', query['desc'])
    print()
    result = connection.execute(text(query['stmt']))
    printColumnHeaders(result.keys())
    for row in result:
        print(row)
        
        
    


if __name__== "__main__":

    engine = create_engine("sqlite:///iaminsights.sqlite3")

    with engine.begin() as connection:
        for report in reports.ACCOUNT_REPORTS:
            runReport(connection, report)
        
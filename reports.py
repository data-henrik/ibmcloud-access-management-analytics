import json, sys
from sqlalchemy import MetaData, create_engine, insert, text
from sqlalchemy import Table, Column, Integer, String, ForeignKey
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
        
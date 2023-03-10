import requests, json, sys
from sqlalchemy import MetaData, create_engine, insert
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from utils import CloudTables, insert, retrieve
from urllib.parse import urljoin


def readApiKey(filename):
    with open(filename) as data_file:
        credentials = json.load(data_file)
    api_key = credentials.get('apikey')
    return api_key



if __name__== "__main__":

    credfile=sys.argv[1]

    print ("Reading credentials")
    apiKey=readApiKey(credfile)
    print ("generating auth tokens")
    authTokens=retrieve.getAuthTokens(api_key=apiKey)
    iam_token=authTokens["access_token"]   

    # create database tables
    engine = create_engine("sqlite:///iaminsights.sqlite3")
    tables=CloudTables.CloudTables()
    tables.createTables(engine)

    print ("Getting account details")
    accDetails=retrieve.getIAMDetails(api_key=apiKey, iam_token=iam_token)
    account_id=accDetails['account_id']

    accounts_data=retrieve.getAccounts(iam_token)
        
    print ("Getting data")
    user_data=retrieve.getUsers(iam_token, account_id)
    serviceid_data=retrieve.getServiceIDs(iam_token, account_id)
    group_data=retrieve.getResourceGroups(iam_token)
    instance_data=retrieve.getResourceInstances(iam_token)
    access_group_data=retrieve.getAccessGroups(iam_token, account_id)

    with engine.begin() as connection:
        print ("inserting")
        insert.insertAccounts(accounts_data['resources'][0], connection, tables.accounts)
        insert.insertUsers(user_data['resources'], connection, tables.users)
        insert.insertServiceIDs(serviceid_data['serviceids'], connection, tables.serviceids)
        insert.insertAccessGroups(access_group_data['groups'], connection, tables.access_groups, account_id)
        insert.insertResourceGroups(group_data['resources'], connection, tables.resource_groups)
        insert.insertResourceInstances(instance_data['resources'], connection, tables.resource_service_instances)


    tp_data=retrieve.getTrustedProfiles(iam_token, account_id)
    with engine.begin() as connection:
        print ("inserting TPs")
        insert.insertTrustedProfiles(tp_data['profiles'], connection, tables.trustedprofiles)
        for profile in tp_data['profiles']:
            tp_links=retrieve.getTrustedProfileLinks(iam_token, profile['id'])
            insert.insertTPLinks(tp_links['links'], connection, tables.trustedprofile_links, profile['id'])


    with engine.begin() as connection:
        print ("inserting batch 2")
        for group in access_group_data['groups']:
            agmembers=retrieve.getAccessGroupMembers(iam_token, account_id, group['id'])
            insert.insertAccessGroupMembers(agmembers['members'], connection, tables.access_group_members, group['id'])

    policy_data=retrieve.getAccessPolicies(iam_token, account_id)
    with engine.begin() as connection:
        print ("inserting policies")
        insert.insertAccessPolicies(policy_data, connection, tables, account_id)

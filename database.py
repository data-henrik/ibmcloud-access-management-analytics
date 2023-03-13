# Build a database with IBM Cloud access management data
# for the account identified by its API key
#
# Written by 2023 Henrik Loeser, IBM, hloeser@de.ibm.com

import requests, json, sys, os, base64
from sqlalchemy import create_engine
from utils import CloudTables, insert, retrieve


def readApiKey(filename):
    with open(filename) as data_file:
        credentials = json.load(data_file)
    api_key = credentials.get('apikey')
    return api_key

# use split and base64 to get to the content of the IAM token
def extractAccount(iam_token):
    data = iam_token.split('.')
    padded = data[1] + "="*divmod(len(data[1]),4)[1]
    jsondata = json.loads(base64.urlsafe_b64decode(padded))
    return jsondata

if __name__== "__main__":

    iam_token=os.getenv("IBMCLOUD_TOKEN", None)
    if iam_token is None:
        print("Need IBM Cloud access token passed as environment variable IBMCLOUD_TOKEN.")
        exit

    # credfile=sys.argv[1]

    # print ("Reading credentials")
    # apiKey=readApiKey(credfile)
    # print ("generating auth tokens")
    # authTokens=retrieve.getAuthTokens(api_key=apiKey)
    # iam_token=authTokens["access_token"]   

    # create database tables
    engine = create_engine("sqlite:///iaminsights.sqlite3")
    tables=CloudTables.CloudTables()
    tables.createTables(engine)

    print ("Getting account details")
    token_data=extractAccount(iam_token)
    account_id=token_data["account"]["bss"]
    #accDetails=retrieve.getIAMDetails(api_key=apiKey, iam_token=iam_token)
    #account_id=accDetails['account_id']

    accounts_data=retrieve.getAccounts(iam_token)
        
    print ("Fetching access data")
    user_data=retrieve.getUsers(iam_token, account_id)
    serviceid_data=retrieve.getServiceIDs(iam_token, account_id)
    group_data=retrieve.getResourceGroups(iam_token)
    instance_data=retrieve.getResourceInstances(iam_token)
    access_group_data=retrieve.getAccessGroups(iam_token, account_id)

    with engine.begin() as connection:
        print ("inserting")
        print(json.dumps(accounts_data))
        insert.insertAccounts(accounts_data['resources'], connection, tables.accounts)
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
        print ("inserting AG members")
        for group in access_group_data['groups']:
            agmembers=retrieve.getAccessGroupMembers(iam_token, account_id, group['id'])
            insert.insertAccessGroupMembers(agmembers['members'], connection, tables.access_group_members, group['id'])

    print ("processing policies")
    policy_data=retrieve.getAccessPolicies(iam_token, account_id)
    with engine.begin() as connection:
        insert.insertAccessPolicies(policy_data, connection, tables, account_id)

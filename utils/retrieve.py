# Helper function to retrieve data from the IBM Cloud APIs
#
# Written by 2023 Henrik Loeser, IBM, hloeser@de.ibm.com
import requests
from urllib.parse import urljoin


# fetch from API and perform necessary paging
def handleAPIAccess(url, headers, payload, next_field, result_field):
    # fetch data from API function, passing headers and parameters
    response = requests.get(url, headers=headers, params=payload)
    data=response.json()
    curr_response=response.json()
    # check for paging field and, if necessary, page through all results sets
    # we need to make sure to only move ahead if the next field is present and non-empty
    while (str(next_field) in curr_response and curr_response[str(next_field)] is not None):

        if curr_response[str(next_field)].startswith("https"):
            # fetch next result page if full URL present
            response = requests.get(curr_response[str(next_field)], headers=headers)
        else:
            # only a partial URL present, construct it from the base and the new path
            newurl = urljoin(url, curr_response[str(next_field)])
            response = requests.get(newurl, headers=headers)
        curr_response=response.json()
        # extend the set of retrieved objects
        data[str(result_field)].extend(curr_response[str(result_field)])
    return data


# see https://cloud.ibm.com/apidocs/iam-identity-token-api#gettoken-apikey
def getAuthTokens(api_key):
    url     = "https://iam.cloud.ibm.com/identity/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + api_key + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    response  = requests.post( url, headers=headers, data=data )
    return response.json()

# see https://cloud.ibm.com/apidocs/iam-identity-token-api#get-api-keys-details
def getIAMDetails(api_key, iam_token):
    url     = "https://iam.cloud.ibm.com/v1/apikeys/details"
    headers = { "Authorization" : iam_token, "IAM-Apikey" : api_key, "Content-Type" : "application/json" }
    response  = requests.get( url, headers=headers )
    return response.json()

# retrieve account information
def getAccounts(iam_token):
    url     = "https://accounts.cloud.ibm.com/v1/accounts"
    headers = { "Authorization" : iam_token }
    response  = requests.get( url, headers=headers )
    return response.json()

# retrieve all users in the account, https://cloud.ibm.com/apidocs/user-management#list-users
def getUsers(iam_token, account_id):
    url = f'https://user-management.cloud.ibm.com/v2/accounts/{account_id}/users'
    headers = { "Authorization" : iam_token }
    payload = {"pagesize": 100}
    return handleAPIAccess(url, headers, payload, "next_url", "resources")

# retrieve all service IDs in the account, https://cloud.ibm.com/apidocs/iam-identity-token-api#list-service-ids
def getServiceIDs(iam_token, account_id):
    url = 'https://iam.cloud.ibm.com/v1/serviceids'
    headers = { "Authorization" : iam_token }
    payload = {"account_id": account_id, "pagesize": 100}
    return handleAPIAccess(url, headers, payload, "next", "serviceids")

# retrieve Trusted Profiles, https://cloud.ibm.com/apidocs/iam-identity-token-api#list-profiles
def getTrustedProfiles(iam_token, account_id):
    url = f"https://iam.cloud.ibm.com/v1/profiles"
    headers = { "Authorization" : iam_token }
    payload = {"account_id": account_id, "pagesize": 100}
    response = requests.get(url, headers=headers, params=payload)
    return handleAPIAccess(url, headers, payload, "next", "profiles")

# retrieve links between TPs and compute resources, https://cloud.ibm.com/apidocs/iam-identity-token-api#list-links
def getTrustedProfileLinks(iam_token, tp_id):
    url = f"https://iam.cloud.ibm.com/v1/profiles/{tp_id}/links"
    headers = { "Authorization" : iam_token }
    response = requests.get(url, headers=headers)
    return response.json()

# see https://cloud.ibm.com/apidocs/resource-controller/resource-manager#list-resource-groups
def getResourceGroups(iam_token):
    url = f'https://resource-controller.cloud.ibm.com/v2/resource_groups'
    headers = { "Authorization" : iam_token }
    response = requests.get(url, headers=headers)
    return response.json()

# see https://cloud.ibm.com/apidocs/resource-controller/resource-controller#list-resource-instances
def getResourceInstances(iam_token):
    url = f'https://resource-controller.cloud.ibm.com/v2/resource_instances'
    headers = { "Authorization" : iam_token }
    payload = { "limit": 100}
    return handleAPIAccess(url, headers, payload, "next_url", "resources")


# Obtain access groups and handle paging, https://cloud.ibm.com/apidocs/iam-access-groups#list-access-groups
def getAccessGroups(iam_token, account_id):
    url = 'https://iam.cloud.ibm.com/v2/groups'
    # Empty transaction ID here in the code, but you could set it for better tracking
    headers = { "Authorization" : iam_token, "accept": "application/json", "Transaction-Id":"" }
    payload = {"account_id": account_id, "hide_public_access": "true", "limit": 100}
    response = requests.get(url, headers=headers, params=payload)
    groups=response.json()
    curr_response=response.json()
    while ("next" in curr_response):
        response = requests.get(curr_response["next"]["href"], headers=headers)
        curr_response=response.json()
        groups["groups"].extend(curr_response["groups"])
    return groups   

# see https://cloud.ibm.com/apidocs/iam-access-groups#list-access-group-members
def getAccessGroupMembers(iam_token, account_id, groupID):
    url = f"https://iam.cloud.ibm.com/v2/groups/{groupID}/members"
    # Empty transaction ID here in the code, but you could set it for better tracking
    headers = { "Authorization" : iam_token, "accept": "application/json", "Transaction-Id":"" }
    payload = { "membership_type": "all", "limit": 100}
    response = requests.get(url, headers=headers, params=payload)
    agusers=response.json()
    curr_response=response.json()
    while ("next" in curr_response):
        response = requests.get(curr_response["next"]["href"], headers=headers)
        curr_response=response.json()
        agusers["members"].extend(curr_response["members"])
    return agusers


# Obtain the policies, either for an access group or related to an IAM ID (user, service ID)
# see https://cloud.ibm.com/apidocs/iam-policy-management#list-policies
# Note that v1 is used
def getAccessPolicies(iam_token, account_id, access_group_id=None, user_iam_id=None):
    url = 'https://iam.cloud.ibm.com/v1/policies'
    headers = { "Authorization" : iam_token, "accept": "application/json" }
    payload = {"account_id": account_id, "access_group_id": access_group_id, "iam_id": user_iam_id, "format": "include_last_permit"}
    response = requests.get(url, headers=headers, params=payload)
    return response.json()    


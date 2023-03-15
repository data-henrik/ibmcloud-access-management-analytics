# functions to insert data into the database tables
#
# Written by 2023 Henrik Loeser, IBM, hloeser@de.ibm.com
from sqlalchemy import create_engine, insert

def insertAccounts(accDetails, connection, tablename):
    for item in accDetails:
        connection.execute(insert(tablename).values(account_id=item['metadata']['guid'],
                                 name=item['entity']['name'],
                                 owner=item['entity']['primary_owner']['ibmid'],
        ))

def insertUsers(user_data, connection, tablename):
    for item in user_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                iam_id=item['iam_id'],
                                user_id=item['user_id'],
                                account_id=item['account_id'],
                                state=item['state'],
        ))

def insertServiceIDs(serviceid_data, connection, tablename):
    for item in serviceid_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                iam_id=item['iam_id'],
                                name=item['name'],
                                account_id=item['account_id'],
        ))

def insertTrustedProfiles(tp_data, connection, tablename):
    for item in tp_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                iam_id=item['iam_id'],
                                name=item['name'],
                                account_id=item['account_id'],
        ))


def insertTPLinks(tp_link_data, connection, tablename, tp_id):
    for item in tp_link_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                cr_type=item['cr_type'],
                                tp_id=tp_id,
                                link_crn=item['link'].get('crn'),
                                link_namespace=item['link'].get('namespace'),
                                link_name=item['link'].get('name'),
        ))

def insertResourceGroups(group_data, connection, tablename):
    for item in group_data:
        connection.execute(insert(tablename).values(
                                resource_group_id=item['id'],
                                crn=item['crn'],
                                account_id=item['account_id'],
                                name=item['name'],
        ))


def insertResourceInstances(instance_data, connection, tablename):
    for item in instance_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                guid=item['guid'],
                                crn=item['crn'],
                                resource_group_id=item['resource_group_id'],
                                account_id=item['account_id'],
                                created_by=item['created_by'],
                                updated_by=item['updated_by'],
                                name=item['name'],
                                region_id=item['region_id'],
        ))


def insertAccessGroups(group_data, connection, tablename, account_id):
    for item in group_data:
        connection.execute(insert(tablename).values(
                                id=item['id'],
                                name=item['name'],
                                description=item.get('description'),
                                account_id=account_id,
                                created_by_id=item['created_by_id'],
        ))

def insertAccessGroupMembers(member_data, connection, tablename, group_id):
    for item in member_data:
        connection.execute(insert(tablename).values(
                                iam_id=item['iam_id'],
                                group_id=group_id,
                                type=item['type'],
                                membership_type=item['membership_type'],
        ))

def insertAccessPolicies(policy_data, connection, tables, account_id):
    # iterate over all policies
    for item in policy_data['policies']:
        connection.execute(insert(tables.policies).values(
                                id=item['id'],
                                type=item['type'],
                                state=item['state'],
                                created_by_id=item['created_by_id'],
                                description=item.get('description'),
                                last_permit_at=item.get('last_permit_at'),
                                last_permit_frequency=item.get('last_permit_frequency'),
                                account_id=account_id,
        ))
        policy_id=item['id']
        # go over roles
        for role in item['roles']:
            connection.execute(insert(tables.policy_roles).values(
                                policy_id=policy_id,
                                role_id=role['role_id'],
                                display_name=role.get('display_name')
            ))
        # go over resource attributes
        for res in item['resources']:
            for attr in res['attributes']:
                connection.execute(insert(tables.policy_resource_attributes).values(
                                policy_id=policy_id,
                                name=attr['name'],
                                value=attr['value'],
                                operator=attr.get('operator')
                ))

        # go over subject attributes
        for sub in item['subjects']:
            for attr in sub['attributes']:
                connection.execute(insert(tables.policy_subjects).values(
                                policy_id=policy_id,
                                name=attr['name'],
                                value=attr['value'],
                ))

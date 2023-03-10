ACCOUNT_REPORTS=[{'name':'sql_reportUnreferencedServiceInstances',
            'stmt':"""
---which resources are not used in access policies
select rsiall.name, rsiall.region_id, rsiall.crn
from resource_service_instances rsiall
where rsiall.crn not in (
    select distinct rsi.crn
    from resource_groups rg, resource_service_instances rsi, policies p 
    inner join policy_roles pr on p.id=pr.policy_id
    inner join policy_resource_attributes pra on p.id=pra.policy_id
    inner join policy_subjects ps on p.id=ps.policy_id, 
    access_groups ag inner join access_group_members agm on ag.id=agm.group_id
    where pra.value=rsi.guid)
""",
'desc':'which resources are not used in access policies'},

{'name':'sql_reportServiceAccessByIAMID','stmt':"""
-- which resources are accessible by whom through some Access Group policy
select distinct rsi.name, agm.iam_id, rsi.crn, p.id, ag.id 
from resource_groups rg, resource_service_instances rsi, policies p 
inner join policy_roles pr on p.id=pr.policy_id
inner join policy_resource_attributes pra on p.id=pra.policy_id
inner join policy_subjects ps on p.id=ps.policy_id, 
access_groups ag inner join access_group_members agm on ag.id=agm.group_id
where pra.value=rsi.guid
""",
'desc':'which resources are accessible by whom through some Access Group policy'},

{'name':'sql_reportUsersNotInAccessGroup','stmt':"""
---users which are not in an Access Group
select * from users
where iam_id not in (
select agm.iam_id
from access_group_members agm)
""",
'desc':'users which are not in an Access Group'},

{'name':'sql_reportAccessGroupsWithoutServicePolicy','stmt':"""
-- which Access Groups have policies not defined on a service name or type
select distinct ag.*
from access_groups ag, policy_subjects ps
where ps.name='access_group_id' and ag.id=ps.value
and ag.id not in
( select ps.value
 from policies p
inner join policy_resource_attributes pra on p.id=pra.policy_id
inner join policy_subjects ps on p.id=ps.policy_id
where  ((pra.policy_id, pra.resource_id)  in
(select pra2.policy_id, pra2.resource_id
from policy_resource_attributes pra2
where  pra2.name in ('serviceName', 'serviceType')))
and 
ps.name='access_group_id')
""",
'desc':'which Access Groups have policies not defined on a service name or type'},

{'name':'sql_reportAccessGroupsWithoutRegionRGroupPolicy','stmt':"""
-- Access Groups with no policies defined on a region or specific resource group
select distinct ag.*
from access_groups ag, policy_subjects ps
where ps.name='access_group_id' and ag.id=ps.value
and ag.id not in

( select ps.value
 from policies p
inner join policy_resource_attributes pra on p.id=pra.policy_id
inner join policy_subjects ps on p.id=ps.policy_id
where  ((pra.policy_id, pra.resource_id)  in
(select pra2.policy_id, pra2.resource_id
from policy_resource_attributes pra2
where  pra2.name in ('region','resourceGroupId')))
and 
ps.name='access_group_id')
""",
'desc':'Access Groups with no policies defined on a region or specific resource group'},

{'name':'sql_reportAccessGroupsNoReaderViewerRoles','stmt':"""
-- which Access Groups have no policies with Reader or Viewer roles and what are the roles
select distinct ag.*, pr.*
from access_groups ag, policy_subjects ps, policy_roles pr
where ps.name='access_group_id' and ag.id=ps.value
and ps.policy_id=pr.policy_id
and ag.id not in

( select ps.value
 from policies p
inner join policy_roles pr on p.id=pr.policy_id
inner join policy_subjects ps on p.id=ps.policy_id
where  
ps.name='access_group_id'
 and pr.policy_id  in
(select pr2.policy_id
from policy_roles pr2
where  pr2.role_id in ('crn:v1:bluemix:public:iam::::serviceRole:Reader','crn:v1:bluemix:public:iam::::role:Viewer')
))
""",
'desc':'which Access Groups have no policies with Reader or Viewer roles and what are the roles'},


{'name':'sql_reportServicesReferencedNotExisting','stmt':"""
-- which services are referenced but do not exist
select p.*, pra.value, pra.name
from policy_resource_attributes pra
inner join policies p on p.id=pra.policy_id
where pra.name='serviceInstance'
and pra.value not in
(
select rsi.guid
from resource_service_instances rsi
)
""",
'desc':'which services are referenced but do not exist'},

{'name':'sql_reportPoliciesOrderedByLastPermit','stmt':"""
--- policies with those not used or not used for a long time shown first
select * from policies
order by last_permit_frequency asc
LIMIT 30
""",
'desc':'policies with those not used or not used for a long time shown first'},

]
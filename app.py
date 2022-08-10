import config
import os
import json
import sys
import requests
import getpass
import pprint
import urllib3

#disable https warnings
urllib3.disable_warnings()

#bi server and header info
BIServer = "zhj3z7is.ps.beyondtrustcloud.com"
BaseURL="https://zhj3z7is.ps.beyondtrustcloud.com/BeyondTrust/api/public/v3"
auth_head='PS-Auth key={}; runas={};'.format(config.APIKey,config.biUsername)
header = {'Authorization': auth_head}
DataType={'Content-type':'application/json'}
session = requests.Session()
session.headers.update(header)

#Sign into BeyondInsight with URL and header information
url=BaseURL + '/Auth/SignAppin'
session.post(url=url,verify=False)

#get hostname and instance name from managed system list
urlMansys = BaseURL + '/ManagedSystems'
mansyslist = session.get(urlMansys,verify=False)
mansysjson = mansyslist.json()


# - system and account information to check-out
systemname = "DC112"
instanceName = "default"
manacct = "sa"

#loop managed system list by asset name to find assetID and system ID
for asset in mansysjson:
	if asset['HostName'] == systemname:
		assetID = asset['HostName']
		instance01 = asset['InstanceName']
		dbname = '{}/{}'.format(assetID,instance01)
		mansysID = asset['ManagedSystemID']
		#print(mansysID)

		#get managed account list
		urlManAcct = BaseURL + '/ManagedAccounts'
		manacctlist = session.get(urlManAcct,verify=False)
		manacctjson = manacctlist.json()
		
		#loop managed accounts list by account name to find assetID
		for account in manacctjson:
			if account['AccountName'] == manacct:
				accountID = account['AccountId']
				if account['SystemId'] == mansysID:
					acctID = account['AccountId']
					acctname = account['AccountName']
					print('The account ID is: {}'.format(acctID))					
					#print(acctname)

					#build password check out request in json
					urlreq = BaseURL + '/Requests'
					req = { 
						"SystemID": mansysID,
						"AccountID": acctID,
						"DurationMinutes": 1,
						"Reason": "API-Example"
					}
					#submit request to get request number
					reqnum = session.post(urlreq, data=req)
					reqID = reqnum.text
					print('The request ID is: {}'.format(reqID))

					#get creds
					urlcreds = BaseURL + '/Credentials/{}'.format(reqID)
					creds = session.get(urlcreds,verify=False)
					pwd = creds.text
					print(pwd)
					pwd01 = pwd.replace('"', '')
					print(pwd01)
					#print(dbname)					
						
					#checkin request and provide reason
					urlchkin = BaseURL + '/Requests/{}/Checkin'.format(reqID)
					#print(urlchkin)
					reason= { 
							"Reason": "Demo Complete"
							}
					chkin = session.put(urlchkin, data=reason)
					
					#URL that is sent to checkin the request after use
					print(chkin)

					#if statement to return status code 204 for success
					if chkin.status_code == 204:
						print("Success! The password was viewed, then the password is checked back in, and rotated at the specified time")
					else:
						print("Error: Existing Request still open")
					break

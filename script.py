#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 02:02:27 2020
@author: sachin
"""
import os
import json
import time
import numpy as np 
from boto import ec2
from boto.exception import EC2ResponseError

start_time = time.time() 

# Logic to get list of AMIs which are being used by EC2 instances
def ami_from_ec2_instances():
    resp = "aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId, InstanceType, ImageId, State.Name, LaunchTime, Placement.AvailabilityZone, InstanceLifecycle, Platform, VirtualizationType, PrivateIpAddress, PublicIpAddress, [Tags[?Key==`Name`].Value][0][0], [Tags[?Key==`purpose`].Value][0][0], [Tags[?Key==`team`].Value][0][0], [Tags[?Key==`habitat`].Value][0][0], [Tags[?Key==`Project`].Value][0][0], [Tags[?Key==`provisioner`].Value][0][0]]' --region us-east-1 --output json"
    ec2_data = os.popen(resp)
    output = ec2_data.read()
    ec2_data_json = json.loads(output)
    ami_from_ec2 = []

    for i in ec2_data_json:
        for j in i:
            for k in j:
                res = [str(k or 'NA') for k in j]
                sac = ",".join(res)
                val = tuple(sac.split(','))
                instance_id = val[0]
                ami = val[2]
                state = val[3]
                private_ip = val[9]
                name = val[11]
                value = (instance_id, ami, state, private_ip, name)
                if state == "running":
                    ami_from_ec2.append(ami)
                else:
                    pass

    return ami_from_ec2

# Logic to get list of AMIs which exist in AWS account
def ami_from_ami_list():
    ami_from_amilist = []
    resp1 = "aws ec2 describe-images --region us-east-1 --filters --owners self --output json"
    config_data1 = os.popen(resp1)
    output1 = config_data1.read()
    config_data_json1 = json.loads(output1)

    for num in config_data_json1['Images']:
        image_id = num['ImageId']
        state = num['State']
        if state == "available":
            ami_from_amilist.append(image_id)

    return ami_from_amilist

# Function which returns a list of AMIs that are not in use
def ami_not_in_use():
    ami_from_ec2 = ami_from_ec2_instances()
    ami_from_amilist = ami_from_ami_list()
    ami_not_inuse = np.setdiff1d(ami_from_amilist, ami_from_ec2)
    print("AMI which are not in use")
    print(ami_not_inuse)
    print("\n")
    return ami_not_inuse

# Function to deregister AMIs that are not in use
def deregister_ami():
    connection = ec2.connect_to_region("us-east-1")
    ami_to_deregister = ami_not_in_use()
    print("Deregistering AMIs")
    print("-----------------")
    print("\n")
    for ami in ami_to_deregister:
        try:
            connection.deregister_image(ami)
            print("Deregistering AMI %s" % ami)
        except EC2ResponseError as e:
            print("Exception in AMI: %s" % ami)
        else:
            pass

# Calling function    
deregister_ami()
total_execution_time = (time.time() - start_time)
print("\n")
print("Total Execution Time", total_execution_time, "seconds")

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import os

from license_tracker.logger import logger

def read_altair_output(lines):
    
    server_info ={}
    server_info["lic_file"] = ""
    lic_info ={}
    version = ""
    feature = ""
    feature_list =  []
    frsttime_flag = False
    site_code_dict = get_redmine_sitecode()
    for line in lines:
        try:
            line = line.strip()
            if "License Server on" in line:
                server_info["hostname"] = line.strip().split(" ")[-1][0:-1]
            
            if "Feature:" in line:
                info = line.split(" ")
                if frsttime_flag:
                    # feature_list.append(lic_info)
                    break
                    lic_info = {}
                else: 
                    frsttime_flag = True
                
                feature = info[1].strip()
                version = info[3].strip()
                lic_info["NAME"] = info[1].strip()
                lic_info["VERSION"] = info[3].strip()
                
            if  "license(s) used:" in line:
                info = line.split(" ")
                lic_info["TOTAL_LICENSES"] = info[2].strip()
                lic_info["USED_LICENSES"] = info[0].strip()
                lic_info["users"] = []
            
                    
            if "license(s) used by"  in line:
                user = {}
                info = line.split(" ")
                user["NAME"] = info[4].split("@")[0].strip().lower()
                user["HOST"] = info[4].split("@")[1]
                if user["NAME"] in site_code_dict:
                    user["SITE"] = site_code_dict[user["NAME"]]
                else:
                    user["SITE"] = "ZUM"
                user["FEATURE"] = lic_info["NAME"] 
                user["VERSION"] = lic_info["VERSION"]
                user["SERVER"] = info[5][1:-1]
                user["KEY"] = " "
                user["USER_KEY"] = user["NAME"]
                user["USED"] = info[0]
            
            if "Login time:" in line:
                info = line.split(" ")
                user["DATE"] = info[2]
                user["TIME"] = info[3]
            if "Shared on custom string:" in line:
                info = line.split(":")
                if len(info) == 3:
                    user["KEY"] =  info[2].strip()
                    user["USER_KEY"] = info[1].strip() + ":"+ info[2].strip()
                else:
                    user["KEY"] =  info[2].strip() + ":" + info[3].strip()
                    user["USER_KEY"] = info[1].strip() + ":"+ info[2].strip() + ":" + info[3].strip()
                    
                lic_info["users"].append(user)
        except Exception as err:
            logger.info(err,line)
    feature_list.append(lic_info)        
    
    return server_info, feature_list

def read_msc_output(lines):
    server_info ={}
    lic_info ={}
    feature_status_start = False
    feature_list =  []
    user_info_start= False
    site_code_dict = get_redmine_sitecode()
    for line in lines:
        try:
            line = line.strip()
            if not len(line):
                continue
            if user_info_start:
                user = {}
                if "start" in line:
                    user_details = line.split()
                    if len(user_details) == 13 :
                        user["NAME"] = user_details[0].strip().lower()
                        user["HOST"] = user_details[2]
                        if user["NAME"] in site_code_dict:
                            user["SITE"] = site_code_dict[user["NAME"]]
                        else:
                            user["SITE"] = "ZUM"
                        user["FEATURE"] = user_details[3]
                        user["VERSION"] = user_details[4]
                        user["SERVER"] = user_details[5][1:]
                        user["KEY"] = user_details[6][:-2]
                        user["DATE"] = "{} {}".format(user_details[8],user_details[9])
                        user["TIME"] = user_details[10][0:-1]
                        user["USED"] = user_details[11]
                    else:
                        user["NAME"] = user_details[0]
                        user["HOST"] = user_details[2]
                        if user["NAME"] in site_code_dict:
                            user["SITE"] = site_code_dict[user["NAME"]]
                        else:
                            user["SITE"] = "ZUM"
                        user["FEATURE"] = lic_info["NAME"]
                        user["VERSION"] = user_details[3]
                        user["SERVER"] = user_details[4]
                        user["KEY"] = user_details[5][:-2]
                        user["DATE"] = "{} {}".format(user_details[6],user_details[8])
                        user["TIME"] = user_details[9][0:-1]
                        user["USED"] = '1'
                        
                    lic_info["users"].append(user)
            if "License server status" in line:
                server_info["hostname"] = line.strip().split(":")[1]
            if "License file(s) on" in line:
                server_info["lic_file"] = line.strip().split(":")[1]
            if "Users of" in line and "licenses issued" in line and "licenses in use"  in line or "license in use"  in line:
                feature_status_start = True
                if lic_info.keys():
                    feature_list.append(lic_info)
                lic_info ={}
                lic_info["NAME"] =  line.split(":")[0].replace("Users of","").strip()
                lic_info["TOTAL_LICENSES"] = line.split(":")[1].split(";")[0].replace("(Total of ","").replace("licenses issued","").strip()
                lic_info["USED_LICENSES"] = line.split(":")[1].split(";")[1].replace("Total of ","").replace("licenses in use)","").replace("license in use)","").strip()
                lic_info["users"] = []
            if feature_status_start and "expiry: " in line:
                lic_info["END"] = line.split(":")[-1].strip()
            if feature_status_start and "floating license" in line:
                user_info_start = True  
        except Exception as err:
            logger.error(err, line)
            
    feature_list.append(lic_info)
        
    return server_info, feature_list

def read_particleworks_output(lines):
    server_info ={}
    lic_info ={}
    feature_status_start = False
    feature_list =  []
    user_info_start= False
    site_code_dict = get_redmine_sitecode()
    for line in lines:
        try:    

            line = line.strip()
            if not len(line):
                continue
            if user_info_start:
                user = {}
                if "start" in line:
                    user_details = line.split()
                    if len(user_details) == 13 :
                        user["NAME"] = user_details[0].strip()
                        user["SERVER_HOST"] = user_details[2]
                        user["HOST"] = user_details[1]
                        if user["NAME"] in site_code_dict:
                            user["SITE"] = site_code_dict[user["NAME"]]
                        else:
                            user["SITE"] = "ZUM"
                        user["FEATURE"] = user_details[3]
                        user["VERSION"] = user_details[4]
                        user["SERVER"] = user_details[5][1:]
                        user["KEY"] = user_details[6][:-2]
                        user["DATE"] = "{} {}".format(user_details[8],user_details[9])
                        user["TIME"] = user_details[10]
                        user["USED"] = user_details[11]
                    else:
                        user["NAME"] = user_details[0]
                        user["SERVER_HOST"] = user_details[2]
                        user["HOST"] = user_details[1]
                        if user["NAME"] in site_code_dict:
                            user["SITE"] = site_code_dict[user["NAME"]]
                        else:
                            user["SITE"] = "ZUM"
                        user["FEATURE"] = lic_info["NAME"]
                        user["VERSION"] = user_details[3]
                        user["SERVER"] = user_details[4]
                        user["KEY"] = user_details[5][:-2]
                        user["DATE"] = "{} {}".format(user_details[6],user_details[8])
                        user["TIME"] = user_details[9]
                        user["USED"] = '1'
                        
                    lic_info["users"].append(user)
            if "License server status" in line:
                server_info["hostname"] = line.strip().split(":")[1]
            if "License file(s) on" in line:
                server_info["lic_file"] = line.strip().split(":")[1]
            if "Users of" in line and "licenses issued" in line and "licenses in use"  in line or "license in use"  in line:
                feature_status_start = True
                if lic_info.keys():
                    feature_list.append(lic_info)
                lic_info ={}
                lic_info["NAME"] =  line.split(":")[0].replace("Users of","").strip()
                lic_info["TOTAL_LICENSES"] = line.split(":")[1].split(";")[0].replace("(Total of ","").replace("licenses issued","").strip()
                lic_info["USED_LICENSES"] = line.split(":")[1].split(";")[1].replace("Total of ","").replace("licenses in use)","").replace("license in use)","").strip()
                lic_info["users"] = []
            if feature_status_start and "expiry: " in line:
                lic_info["END"] = line.split(":")[-1].strip()
            if feature_status_start and "floating license" in line:
                user_info_start = True  
        except Exception as err:
            logger.info(err, line)
    feature_list.append(lic_info)
    
    return server_info, feature_list

# altair license 
def check_altair_lic_status(almutil_path,server,port_number, inuse):
    feature_list, server_info = check_altair_lic_status_tbl(almutil_path,server,port_number, "-inuse")
    out = check_altair_lic_status_text(almutil_path,server,port_number, inuse)
    
    return feature_list, server_info, out

def check_altair_lic_status_tbl(almutil_path,server,port_number, inuse):
    args = [almutil_path, "-licstat", "-host", server, "-port", str(port_number), inuse]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8")
    out = out.split("\n")
    #logger.info(out)
    
    # read file data for testing
    # f = open("altair_license.txt", "r")
    # out = f.read()
    # out = out.split("\n")
    logger.info("Start read_altair_output(out) method")
    server_info, feature_list = read_altair_output(out)
    logger.info("End read_altair_output(out) method")
    
    
    if len(feature_list) > 0:
        for feature in feature_list:
            chart_data  = {}
            # if no license in used 
            if "TOTAL_LICENSES" in feature:
                lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                chart_data  = {}
                sitecode_chart = {}
                users_info = feature["users"]
                for user in users_info:
                    if user["USER_KEY"] not in chart_data:
                        chart_data[user["USER_KEY"]] = int(user["USED"])
                     
                    #Region based chart
                    if user["SITE"] in sitecode_chart:
                        sitecode_chart[user["SITE"]] += int(user["USED"])
                    else:
                        sitecode_chart[user["SITE"]] = int(user["USED"]) 
                    
                    # else:
                    #     chart_data[user["USER_KEY"]] = int(user["USED"])
                chart_data["Free"] = lic_remain
                feature["CHART_DATA"] = chart_data
                
                sitecode_chart["Free"] = lic_remain
                feature["SITE_CHART_DATA"] = sitecode_chart
            else:
                feature["CHART_DATA"] = chart_data
                feature["SITE_CHART_DATA"] = sitecode_chart 
    return feature_list, server_info

def check_altair_lic_status_text(almutil_path,server,port_number, inuse):
    args = [almutil_path, "-licstat", "-host", server, "-port", str(port_number), inuse]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8")
    out = out.replace("/n","/r/n")
    #logger.info(out)
    # read file data for testing
    # f = open("altair_license.txt", "r")
    # out = f.read()
    return out


# msc license
def check_msc_lic_status(lmutil_path,license_path, inuse): 
    feature_list, server_info = check_msc_lic_status_tbl(lmutil_path,license_path, "-A")
    output_text = check_msc_lic_status_text(lmutil_path,license_path, inuse)
    
    return feature_list, server_info, output_text

def check_msc_lic_status_text(lmutil_path,license_path, inuse): 
    args = [lmutil_path, "lmstat",inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    # read file data for testing
    # f = open("msc_license copy.txt", "r")
    # out = f.read()
    # out = out.split("\n")    
    output = ""
    for line in out:
        if len(line.strip()):
            output += "{}\r\n".format(line.strip())
    #logger.info(output)
    return output

def check_msc_lic_status_tbl(lmutil_path,license_path, inuse): 
    args = [lmutil_path, "lmstat",inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    
    # f = open("msc_license.txt", "r")
    # out = f.read()
    # out = out.split("\n")
    #logger.info(out)
    logger.info("Start read_msc_output(out) method")
    server_info, feature_list = read_msc_output(out)
    logger.info("End read_msc_output(out) method")
    #logger.info(feature_list)
    #  for chart
   
    if len(feature_list) > 0:
        try:
            for feature in feature_list:
                chart_data  = {}
                sitecode_chart = {}
                # if no license in used 
                if "TOTAL_LICENSES" in feature:
                    lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                    
                    users_info = feature["users"]
                    for user in users_info:
                        #user based chart
                        if user["NAME"] in chart_data:
                            chart_data[user["NAME"]] += int(user["USED"])
                        else:
                            chart_data[user["NAME"]] = int(user["USED"])
                        #Region based chart
                        if user["SITE"] in sitecode_chart:
                            sitecode_chart[user["SITE"]] += int(user["USED"])
                        else:
                            sitecode_chart[user["SITE"]] = int(user["USED"])   
                        
                    chart_data["Free"] = lic_remain
                    feature["CHART_DATA"] = chart_data
                    
                    sitecode_chart["Free"] = lic_remain
                    feature["SITE_CHART_DATA"] = sitecode_chart
                else:
                    feature["CHART_DATA"] = chart_data
                    feature["SITE_CHART_DATA"] = sitecode_chart 
        except Exception as err:
            logger.error(err,feature_list)
    return feature_list, server_info
 
 
 
 # 


# Particle works license
def check_particleworks_output(lmutil_path,license_path,inuse ):
    feature_list, server_info = check_particleworks_output_tbl(lmutil_path, license_path, "-A")
    output_text = check_particleworks_output_text(lmutil_path,license_path,inuse )
    return feature_list, server_info, output_text

def check_particleworks_output_tbl(lmutil_path,license_path,inuse ):
    args = [lmutil_path, "lmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    # read file data for testing
    # f = open("parti_license.txt", "r")
    # out = f.read()
    # out = out.split("\n")
    
    #logger.info(out)
    logger.info("Start read_particleworks_output(out) method")
    server_info, feature_list = read_particleworks_output(out)
    logger.info("End read_particleworks_output(out) method")
    
    #logger.info(feature_list)
    # 
    if len(feature_list) > 0:
        try:
            for feature in feature_list:
                chart_data  = {}
                sitecode_chart = {}
                # if no license in used 
                if "TOTAL_LICENSES" in feature:
                    lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                    user_name = []
                    users_info = feature["users"]
                    for user in users_info:
                        if user["NAME"] in chart_data:
                            chart_data[user["NAME"]] += int(user["USED"])
                        else:
                            chart_data[user["NAME"]] = int(user["USED"])
                            
                        if user["SITE"] in sitecode_chart:
                            sitecode_chart[user["SITE"]] += int(user["USED"])
                        else:
                            sitecode_chart[user["SITE"]] = int(user["USED"]) 
                            
                    chart_data["Free"] = lic_remain
                    feature["CHART_DATA"] = chart_data
                    
                    sitecode_chart["Free"] = lic_remain
                    feature["SITE_CHART_DATA"] = sitecode_chart
                else:
                    feature["CHART_DATA"] = chart_data
                    feature["SITE_CHART_DATA"] = sitecode_chart 
        except Exception as err:
            logger.error(err,feature_list)
        
    return feature_list, server_info

def check_particleworks_output_text(lmutil_path,license_path,inuse ):
    args = [lmutil_path, "lmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    output = ""
    for line in out:
        if len(line.strip()):
            output += "{}\r\n".format(line.strip())
    # f = open("parti_license.txt", "r")
    # out = f.read()
    # out =  out.split("\n")
    # logger.info(out)
    output = out
    return output


# Ricardo License
def check_ricardo_output(lmutil_path,license_path,inuse ):
    feature_list, server_info = check_ricardo_output_tbl(lmutil_path, license_path, "-A")
    output_text = check_ricardo_output_text(lmutil_path,license_path,inuse )
    return feature_list, server_info, output_text

def check_ricardo_output_text(lmutil_path,license_path,inuse ):
    args = [lmutil_path, "lmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode()
    # f = open("recardo_license.txt", "r")
    # out = f.read()
   # out =  out.split("\n")
    #logger.info(out)
    return out

def check_ricardo_output_tbl(lmutil_path,license_path,inuse):
    args = [lmutil_path, "lmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    # f = open("recardo_license.txt", "r")
    # out = f.read()
    # out =  out.strip().split("\n")
    logger.info(out)
    logger.info("Start read_ricardo_output(out) method")
    server_info, feature_list = read_ricardo_output(out)
    logger.info("End read_ricardo_output(out) method",feature_list)
    #logger.info(feature_list)
    #  for chart
   
    if len(feature_list) > 0 :
        try:
            for feature in feature_list:
                chart_data  = {}
                sitecode_chart = {}
                # if no license in used 
                if "TOTAL_LICENSES" in feature:
                    lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                    
                    users_info = feature["users"]
                    for user in users_info:
                        #user based chart
                        if user["NAME"] in chart_data:
                            chart_data[user["NAME"]] += int(user["USED"])
                        else:
                            chart_data[user["NAME"]] = int(user["USED"])
                        #Region based chart
                        if user["SITE"] in sitecode_chart:
                            sitecode_chart[user["SITE"]] += int(user["USED"])
                        else:
                            sitecode_chart[user["SITE"]] = int(user["USED"])   
                        
                    chart_data["Free"] = lic_remain
                    feature["CHART_DATA"] = chart_data
                    
                    sitecode_chart["Free"] = lic_remain
                    feature["SITE_CHART_DATA"] = sitecode_chart
                else:
                    feature["CHART_DATA"] = chart_data
                    feature["SITE_CHART_DATA"] = sitecode_chart 
        except Exception as err:
            logger.error(err,feature_list)
    return feature_list, server_info

def read_ricardo_output(lines):
    server_info ={}
    lic_info ={}
    feature_status_start = False
    feature_list =  []
    user_info_start= False
    site_code_dict = get_redmine_sitecode()
    feature = " "
    version = " "
    for line in lines:
        try:
            line = line.strip()
            if not len(line):
                continue
            
            if "RICARDO" in line:
                feature = line.split()[0]
                feature = feature[1:-2]
                version = line.split()[1]
                version = version[0:-1]
                
                
            if user_info_start:
                user = {}
                if "RESERVATION" in line or "RESERVATIONs" in line:
                    user_details = line.split()
                    user["NAME"] = user_details[4].strip().lower()
                    region = user_details[4].split("_")[0]
                    user["HOST"] = " "
                    user["SITE"] = region.upper()
                    # if region in site_code_dict:
                    #     user["SITE"] = region.upper()
                    # else:
                    #     user["SITE"] = "ZUM"
                    user["FEATURE"] = feature
                    user["VERSION"] = version
                    user["SERVER"] = user_details[5]
                    user["KEY"] = " "
                    user["DATE"] = " "
                    user["TIME"] = " "
                    user["USED"] = user_details[0]
                    
                        
                    lic_info["users"].append(user)
            if "License server status" in line:
                server_info["hostname"] = line.strip().split(":")[1]
            if "License file(s) on" in line:
                server_info["lic_file"] = line.strip().split(":")[-1]
            if "Users of" in line and "licenses issued" in line and "licenses in use"  in line or "license in use"  in line:
                feature_status_start = True
                if lic_info.keys():
                    feature_list.append(lic_info)
                lic_info ={}
                lic_info["NAME"] =  line.split(":")[0].replace("Users of","").strip()
                lic_info["TOTAL_LICENSES"] = line.split(":")[1].split(";")[0].replace("(Total of ","").replace("licenses issued","").strip()
                lic_info["USED_LICENSES"] = line.split(":")[1].split(";")[1].replace("Total of ","").replace("licenses in use)","").replace("license in use)","").strip()
                lic_info["users"] = []
            if feature_status_start and "expiry: " in line:
                lic_info["END"] = line.split(":")[-1].strip()
            if feature_status_start and "floating license" in line:
                user_info_start = True  
        except Exception as err:
            logger.error(err, line)
            
    feature_list.append(lic_info)
        
    return server_info, feature_list


# Masta License
def check_masta_output(rlmutil_path,license_path,inuse):
    feature_list, server_info = check_masta_output_tbl(rlmutil_path, license_path, "-a")
    output_text = check_masta_output_text(rlmutil_path,license_path,"-a")
    return feature_list, server_info, output_text

def check_masta_output_text(rlmutil_path,license_path,inuse):
    args = [rlmutil_path, "rlmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode()
    # f = open("masta_license.txt", "r")
    # out = f.read()
    # out =  out.split("\n")
    # logger.info(out)
    return out

def check_masta_output_tbl(rlmutil_path,license_path,inuse ):
    args = [rlmutil_path, "rlmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    # f = open("masta_license.txt", "r")
    # out = f.read()
    # out =  out.strip().split("\n")
    # logger.info(out)
    logger.info("Start read_masta_output(out) method")
    server_info, feature_list = read_masta_output(out)
    logger.info("End read_masta_output(out) method")
    #logger.info(feature_list)
    #  for chart
   
    if len(feature_list) > 0:
        try:
            for feature in feature_list:
                chart_data  = {}
                sitecode_chart = {}
                # if no license in used 
                if "TOTAL_LICENSES" in feature:
                    lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                    
                    users_info = feature["users"]
                    for user in users_info:
                        #user based chart
                        if user["NAME"] in chart_data:
                            chart_data[user["NAME"]] += int(user["USED"])
                        else:
                            chart_data[user["NAME"]] = int(user["USED"])
                        #Region based chart
                        if user["SITE"] in sitecode_chart:
                            sitecode_chart[user["SITE"]] += int(user["USED"])
                        else:
                            sitecode_chart[user["SITE"]] = int(user["USED"])   
                        
                    chart_data["Free"] = lic_remain
                    feature["CHART_DATA"] = chart_data
                    
                    sitecode_chart["Free"] = lic_remain
                    feature["SITE_CHART_DATA"] = sitecode_chart
                else:
                    feature["CHART_DATA"] = chart_data
                    feature["SITE_CHART_DATA"] = sitecode_chart 
        except Exception as err:
            logger.error(err,feature_list)
           
    return feature_list, server_info

def read_masta_output(lines):
    server_info ={}
    lic_info ={}
    users = []
    feature_status_start = False
    feature_list =  []
    user_info_start= False
    site_code_dict = get_redmine_sitecode()
    feature = " "
    version = " "
    for line in lines:
        try:
            line = line.strip()
            if not len(line):
                continue
            if "Setting license file path to" in line:
                server_info["hostname"] = line.strip().split()[-1]
                server_info["lic_file"] = " "    
            if "smt license pool status" in line:
                feature_status_start = True
            if feature_status_start:
                if "v2" in line or "v1" in line:
                    lic_info ={}
                    lic_info["NAME"] =  line.split(" ")[0]
                if "inuse" in line:
                    
                    lic_info["TOTAL_LICENSES"] = line.split(",")[0].split(":")[1].strip()
                    lic_info["USED_LICENSES"] = line.split(",")[2].split(":")[1].strip()
                    lic_info["END"] = line.split(",")[3].split(":")[1].strip()
                    lic_info["users"] = []
                    feature_list.append(lic_info)
                        
            if "smt license usage status" in line:
                user_info_start = True
            if user_info_start:
                user = {}
                if "handle:" in line:
                    user_details = line.split()
                    user["NAME"] = user_details[2].split("@")[0].strip().lower()
                    user["HOST"] = " "
                    user["SERVER"]  = user_details[2].split("@")[1]
                    if  user["NAME"] in site_code_dict:
                        user["SITE"] = site_code_dict[user["NAME"]]
                    else:
                        user["SITE"] = "ZUM"
                    user["FEATURE"] = user_details[0]
                    user["VERSION"] = user_details[1]#[0:-2]
                    user["KEY"] = " "
                    user["DATE"] = user_details[5]
                    user["TIME"] = user_details[6]
                    user["USED"] = user_details[3].split("/")[0]
                    users.append(user)
                       
            
        except Exception as err:
            logger.error(err, line)
               
    for user in users:
        try:
            for feature in feature_list:
                if user["FEATURE"] in feature["NAME"]:
                    feature["users"].append(user)
                    break
        except Exception as err:
            logger.error(err, user)
    
    #added used license first then not used one
    result_feature_list = []
    non_user_feature_list = []
    for feature in feature_list:
        if len(feature["users"]) > 0:
            result_feature_list.append(feature)
        else:
            non_user_feature_list.append(feature)
    
    
    result_feature_list.extend(non_user_feature_list)            
        
    return server_info, result_feature_list



# RLM License
def check_rlm_output(rlmutil_path,license_path,inuse):
    feature_list, server_info = check_rlm_output_tbl(rlmutil_path, license_path, "-a")
    output_text = check_rlm_output_text(rlmutil_path,license_path,"-a")
    return feature_list, server_info, output_text

def check_rlm_output_text(rlmutil_path,license_path,inuse ):
    args = [rlmutil_path, "rlmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode()
    # f = open("rlm_license.txt", "r")
    # out = f.read()
    #out =  out.split("\n")
    #logger.info(out)
    return out

def check_rlm_output_tbl(rlmutil_path,license_path,inuse ):
    args = [rlmutil_path, "rlmstat", inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    # f = open("rlm_license.txt", "r")
    # out = f.read()
    # out =  out.strip().split("\n")
    logger.info(out)
    logger.info("Start read_rlm_output(out) method")
    server_info, feature_list = read_rlm_output(out)
    logger.info("End read_rlm_output(out) method",feature_list)
    #logger.info(feature_list)
    #  for chart
   
    if len(feature_list) > 0:
        try:
            for feature in feature_list:
                chart_data  = {}
                sitecode_chart = {}
                # if no license in used 
                if "TOTAL_LICENSES" in feature:
                    lic_remain = int(feature["TOTAL_LICENSES"]) - int(feature["USED_LICENSES"])
                    
                    users_info = feature["users"]
                    for user in users_info:
                        #user based chart
                        if user["NAME"] in chart_data:
                            chart_data[user["NAME"]] += int(user["USED"])
                        else:
                            chart_data[user["NAME"]] = int(user["USED"])
                        #Region based chart
                        if user["SITE"] in sitecode_chart:
                            sitecode_chart[user["SITE"]] += int(user["USED"])
                        else:
                            sitecode_chart[user["SITE"]] = int(user["USED"])   
                        
                    chart_data["Free"] = lic_remain
                    feature["CHART_DATA"] = chart_data
                    
                    sitecode_chart["Free"] = lic_remain
                    feature["SITE_CHART_DATA"] = sitecode_chart
                else:
                    feature["CHART_DATA"] = chart_data
                    feature["SITE_CHART_DATA"] = sitecode_chart 
        except Exception as err:
            logger.error(err,feature_list)
    return feature_list, server_info

def read_rlm_output(lines):
    server_info ={}
    lic_info ={}
    users = []
    feature_status_start = False
    feature_list =  []
    user_info_start= False
    site_code_dict = get_redmine_sitecode()
    feature = " "
    version = " "
    for line in lines:
        try:
            line = line.strip()
            if not len(line):
                continue
            if "lms license pool status" in line:
                feature_status_start = True
            if feature_status_start:
                if "v2" in line or "v1" in line:
                    lic_info ={}
                    lic_info["NAME"] =  line.split(" ")[0]
                if "inuse" in line:
                    
                    lic_info["TOTAL_LICENSES"] = line.split(",")[0].split(":")[1].strip()
                    lic_info["USED_LICENSES"] = line.split(",")[2].split(":")[1].strip()
                    lic_info["END"] = line.split(",")[3].split(":")[1].strip()
                    lic_info["users"] = []
                    feature_list.append(lic_info)
                        
            if "lms license usage status" in line:
                user_info_start = True
            if user_info_start:
                user = {}
                if "handle:" in line:
                    user_details = line.split()
                    user["NAME"] = user_details[2].split("@")[0].strip().lower()
                    user["HOST"] = " "
                    user["SERVER"]  = user_details[2].split("@")[1]
                    if  user["NAME"] in site_code_dict:
                        user["SITE"] = site_code_dict[user["NAME"]]
                    else:
                        user["SITE"] = "ZUM"
                    user["FEATURE"] = user_details[0]
                    user["VERSION"] = user_details[1]#[0:-2]
                    user["KEY"] = " "
                    user["DATE"] = user_details[5]
                    user["TIME"] = user_details[6]
                    user["USED"] = user_details[3].split("/")[0]
                    users.append(user)
            if "Setting license file path to" in line:
                server_info["hostname"] = line.strip().split()[-1]
                server_info["lic_file"] = " "                
            
        except Exception as err:
            logger.error(err, line)
    for user in users:
        for feature in feature_list:
            if user["FEATURE"] in feature["NAME"]:
                feature["users"].append(user)
                break
    #added used license first then not used one
    result_feature_list = []
    non_user_feature_list = []
    for feature in feature_list:
        if len(feature["users"]) > 0:
            result_feature_list.append(feature)
        else:
            non_user_feature_list.append(feature)
    
    
    result_feature_list.extend(non_user_feature_list)            
        
    return server_info, result_feature_list


#Kill the license 
def kill_particlework_license(lmutil_path,user_name,  software, user_host, unique_key ):
    # Since the normal killing of the license doesnt work we need to ssh into the server and run the command
    import paramiko
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    from flask import current_app
    ssh_host = current_app.config["PARTICLEWORKS"]
    ssh_port = 22 
    ssh_username =current_app.config["LINUX_USER_NAME"]
    ssh_password = current_app.config["LINUX_PASSWORD"]
    ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
    #[lmutil_path, "lmremove", "-c", license_path,"-h",software=>"1002(software)","server(second part of host)","port(first part of host)",unique_key]
    port = current_app.config["PW_PORT"]
    command_to_run = "cd /apps/prod/licenses/Particle/ &&  ./lmutil lmremove -h {} {} {} {}".format(software,user_host,port, unique_key)
    stdin, stdout, stderr = ssh_client.exec_command(command_to_run)
    logger.info(command_to_run)
    err = stderr.read().decode()
    out = stdout.read().decode()
    logger.error(err)
    logger.info(out)
    #args = [lmutil_path, "lmremove", "-c", license_path,"-h", software, server, port, unique_key]
    #logger.info(args)
    #process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #out, err = process.communicate()
    #out = out.decode().split("\n")
    #logger.info("End kill_msc_license() method")
    #logger.info(out, err)
    return out, err
    # return check_particleworks_output(lmutil_path,license_path,inuse )

def kill_msc_license(lmutil_path,license_path, inuse, unique_key, software, server, port ):
    logger.info("Start kill_msc_license() method")
    #[lmutil_path, "lmremove", "-c", license_path,"-h",software=>"1002(software)","server(second part of host)","port(first part of host)",unique_key]
    args = [lmutil_path, "lmremove", "-c", license_path,"-h", software, server, port, unique_key]
    logger.info(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    logger.info("End kill_msc_license() method")
    logger.info(out, err)
    return out, err
    # feature_list, server_info, output_text =  check_msc_lic_status(lmutil_path,license_path, inuse)
    
    # return out, feature_list, server_info, output_text


def get_redmine_sitecode():
    #get site code add all to users table, if the login id is same update else add to table
    from license_tracker.models.easyredmine.users import RedmineUser
    from license_tracker.models.easyredmine.custom_fields import CustomField
    from license_tracker.models.easyredmine.custom_values import CustomValue
    from flask import current_app
    from sqlalchemy import and_

    # Check if Redmine DB is configured, return empty dict if not
    if not current_app.config.get("DB_TYPE") or not current_app.config.get("SERVER_IP"):
        logger.debug("Redmine DB not configured, returning empty site code dict")
        return {}

    try:
        redmine_session = get_redmine_session()
    except Exception as e:
        logger.warning("Failed to connect to Redmine DB: %s", str(e))
        return {}
    site_code_fld  = redmine_session.query(CustomField).filter(CustomField.name==current_app.config["SITECODE"]).first()

    
    data = redmine_session.query(
        RedmineUser.login.label("login"),
        CustomValue.value.label("site") 
    ).join(
        CustomValue,
        and_(RedmineUser.id_ == CustomValue.customized_id, CustomValue.custom_field_id == site_code_fld.id_),
        isouter = True
    ).all()

    site_code_dict = {}
    for user in data:
        site_code_dict[user.login] = user.site
    close_given_db_session(redmine_session)
    return site_code_dict


def construct_uri(ip, port, db_type, db, username, password):
    """Returns an uri for SQLAlchemy using the given parameters."""
    try:
        from urllib import quote_plus
    except ImportError:
        from urllib.parse import quote_plus

    db_type = db_type.lower()
    if db_type == "mysql":
        dialect_driver = "mysql+pymysql"
    elif db_type == "postgresql":
        dialect_driver = "postgres+psycopg2"
    else:
        raise NotImplementedError(("Unable to process {} "
                                   "databases for now.").format(db_type))
    
    uri = "{}://{}:{}@{}:{}/{}".format(dialect_driver, username,
                                       quote_plus(password), ip,
                                       port, db)
    return uri
    


def get_redmine_session():
    
    from flask import current_app
    from license_tracker.models.easyredmine.base import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    uri = construct_uri(current_app.config["SERVER_IP"], current_app.config["PORT"],  current_app.config["DB_TYPE"],
                        current_app.config["DB_NAME"], current_app.config["USERNAME"],current_app.config["PASSWORD"] )
    engine = create_engine(uri, pool_recycle=300)
    #logger.debug("Created engine")
    Base.metadata.create_all(engine, checkfirst=True)
    #logger.debug("Mapped base metadata.")
    Session = sessionmaker(bind=engine)
    #logger.debug("Created Session class bound to engine.")
    session = Session()
    #logger.debug("Created session Object")
    return session

def close_given_db_session(session_object):
    engine_object = session_object.get_bind()
    session_object.close()
    engine_object.dispose()


def get_license_graph_data(from_date, to_date):
    from license_tracker.models.license_details import LicenseDetail
    from datetime import datetime
    import pandas as pd

    license_detail_data = LicenseDetail.query.filter(LicenseDetail.check_out >= from_date,LicenseDetail.check_out <= to_date).all()
    lic_spent_hours_by_site_code = []
    for item in license_detail_data:
        time_fld = item.spent_hours.split(":")
        hours = int(time_fld[0])
        minutes = int(time_fld[1])
        seconds = int(time_fld[2])
        total_hours = hours + ( minutes / 60) + (seconds / 3600)
        lic_spent_hours_by_site_code.append({"check_out":item.check_out.date(), "spent_hours":round(total_hours, 3), "site_code":item.site_code })
    lic_spent_hours_df = pd.DataFrame(lic_spent_hours_by_site_code)  
    lic_spent_hours_by_site_code_df = lic_spent_hours_df.groupby(['check_out', 'site_code']).sum().reset_index()
    
    lic_spent_hours_by_site_code_arr = lic_spent_hours_by_site_code_df.to_dict('records')
    date_arr = []
    series = {}
    for item in lic_spent_hours_by_site_code_arr:
        if item["check_out"] not in date_arr:
            date_arr.append(item["check_out"])
        if item["site_code"] in  series.keys():
            series[item["site_code"]].append(item["spent_hours"])
        else:
            series[item["site_code"]] = [item["spent_hours"]]
            
            
    return date_arr, series

def get_feature_data(app, region):
    pass
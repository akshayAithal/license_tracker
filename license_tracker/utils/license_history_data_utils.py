from license_tracker.logger import logger
from flask import current_app
import subprocess
from license_tracker.models import db
import os


def get_license_data():
    #get data for msc for all region,
    msc_license_history_obj_list = get_msc_data()
    #get data for particleworks for all region
    parti_license_history_obj_list = get_particleworks_data()
    # #add data for altair and for all region
    altair_license_history_obj_list = get_altair_data()
    # add to license db
    db.session.bulk_save_objects(msc_license_history_obj_list)
    db.session.commit()
    logger.info("msc lincese seccussfully added!")
    db.session.bulk_save_objects(parti_license_history_obj_list)
    db.session.commit() 
    logger.info("particleworks lincese seccussfully added!")
    db.session.bulk_save_objects(altair_license_history_obj_list)
    db.session.commit() 
    logger.info("altair lincese seccussfully added!")

# get msc application for all region and return license history object
def get_msc_data():
    app = "msc"
    license_history_obj_list = []
    inuse =  "-A"
    lmutil_path = current_app.config["LMTUTIL_PATH"]
    try:
        # region == "eu":
        feature_list_eu = msc_data(lmutil_path, "{}@{}".format(current_app.config["MSC_PORT"],current_app.config["EU_MSC"]), inuse)
        if feature_list_eu:
            for feature in feature_list_eu:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "eu"))
        
        #region == "apac":
        feature_list_apac = msc_data(lmutil_path, "{}@{}".format(current_app.config["MSC_PORT"],current_app.config["APAC_MSC"]), inuse)
        if feature_list_apac:
            for feature in feature_list_apac:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "apac"))
    
        # region == "ame":
        feature_list_ame = msc_data(lmutil_path, "{}@{}".format(current_app.config["AME_MSC_PORT"],current_app.config["AME_MSC"]), inuse)
        if feature_list_ame:
            for feature in feature_list_ame:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "ame"))
        
        # region == "cluster":
        feature_list_cluster = msc_data(lmutil_path, "{}@{}".format(current_app.config["MSC_PORT"],current_app.config["CLUSTER_MSC"]), inuse)
        if feature_list_cluster:
            for feature in feature_list_cluster:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "cluster"))
    except Exception as err:
        logger.error(err)
    return license_history_obj_list

# read data from msc server and convert to table format
def msc_data(lmutil_path,license_path, inuse):
    from license_tracker.utils.license_utils import read_msc_output
    args = [lmutil_path, "lmstat",inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    #static data for testing
    # f = open("msc_license copy.txt", "r")
    # out = f.read()
    # out = out.split("\n")
    # logger.info(out)
    server_info, feature_list = read_msc_output(out)
    return feature_list

# get particle works application for all region and return license history object
def get_particleworks_data():
    license_history_obj_list = []
    app = "pw"
    inuse =  "-A"
    try:
        feature_list = particleworks_data(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["PW_PORT"],current_app.config["PARTICLEWORKS"]), inuse)
        if feature_list:
            for feature in feature_list:
                license_history_obj_list.extend(license_history_obj_data(feature, app, " "))
    except Exception as err:
        logger.error(err)
        
    return license_history_obj_list

# read data from particle works server and convert to table format and return it
def particleworks_data(lmutil_path,license_path, inuse):
    from license_tracker.utils.license_utils import read_particleworks_output
    args = [lmutil_path, "lmstat",inuse, "-c", license_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode().split("\n")
    server_info, feature_list = read_particleworks_output(out)
    return feature_list

# get altair application for all region and return license history object
def get_altair_data():
    app = "altair"
    license_history_obj_list = []
    inuse =  "-inuse"
    almutil_path = current_app.config["ALMTUTIL_PATH"]
    port = current_app.config["ALTAIR_PORT"]
    try:
        # region == "eu":
        feature_list_eu = altair_data(almutil_path, current_app.config["EU_ALTAIR"], port, inuse)
        if feature_list_eu:
            for feature in feature_list_eu:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "eu"))
        
        # region == "eu_unlimited":
        feature_list_eu_unlmtd = altair_data(almutil_path, current_app.config["EU_UNLIMITED_ALTAIR"], port, inuse)
        if feature_list_eu_unlmtd:
            for feature in feature_list_eu_unlmtd:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "eu_unlimited"))
                
        
        #region == "apac":
        feature_list_apac = altair_data(almutil_path, current_app.config["APAC_ALTAIR"], port, inuse)
        if feature_list_apac:
            for feature in feature_list_apac:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "apac"))
        
        #region == "apac_unlimited":
        feature_list_apac_unlmtd = altair_data(almutil_path, current_app.config["APAC_UNLIMITED_ALTAIR"], port, inuse)
        if feature_list_apac_unlmtd:
            for feature in feature_list_apac_unlmtd:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "apac_unlimited"))
    
        # region == "ame":
        feature_list_ame = altair_data(almutil_path, current_app.config["AME_ALTAIR"], port, inuse)
        if feature_list_ame:
            for feature in feature_list_ame:
                license_history_obj_list.extend(license_history_obj_data(feature, app, "ame"))
    except Exception as err:
        logger.error(err)
    return license_history_obj_list

# read data from altair server and convert to table format and return it
def altair_data(almutil_path,server,port_number, inuse):
    from license_tracker.utils.license_utils import read_altair_output
    args = [almutil_path, "-licstat", "-host", server, "-port", str(port_number), inuse]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8")
    out = out.split("\n")
    # read file data for testing
    # f = open("altair_license.txt", "r")
    # out = f.read()
    # out = out.split("\n")
    server_info, feature_list = read_altair_output(out)
    return feature_list

# convert table format license data in to license history object
def license_history_obj_data(user_list, app, region):
    license_history_obj_list = []
    from license_tracker.models.license_history_logs import LicenseHistoryLog 
    from datetime import datetime
    current_year = datetime.now().year
    total_lic = user_list["TOTAL_LICENSES"]
    ttl_lic_used = user_list["USED_LICENSES"]

    for user in user_list["users"]:
        if app == "altair":
            lic_date = user["DATE"]
            datetime_str = str(lic_date) + " " + user["TIME"]
            datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            
        else:
            lic_date = user["DATE"].split(" ")[1] + "/" + str(current_year)
            datetime_str = str(lic_date) + " " + user["TIME"]
            datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M')
        if app == "altair":
            user_key= user["NAME"] +":"+ user["KEY"]
        else:
            user_key= user["KEY"]
        license_history_obj = LicenseHistoryLog(
            application= app,
            region= region,
            user= user["NAME"],
            server= user["SERVER"],
            host= user["HOST"],
            user_key = user_key,
            software= user_list["NAME"],
            feature= user["FEATURE"],
            version= user["VERSION"],
            site_code= user["SITE"],
            total_license = total_lic,
            date_time= datetime_object,
            license_used= user["USED"],
            total_license_used = ttl_lic_used
        )
        license_history_obj_list.append(license_history_obj)
        
        
    return license_history_obj_list


#method for visualiation
def get_license_history_data():
    from license_tracker.models.license_history_logs import LicenseHistoryLog
    from license_tracker.models.license_details import LicenseDetail
    import pandas as pd
    from sqlalchemy import desc

    last_license_details_data = LicenseDetail.query.order_by(desc(LicenseDetail.created_at)).first()
    #getting all license history log data from license_tracker DB
    #TODO: remove hardcode data
    history_data = LicenseHistoryLog.query.filter(LicenseHistoryLog.created_at > last_license_details_data.check_out).all()
    arr = []
    #coneverting to dict of arrays
    for item in history_data:
        arr.append({"id":item.id_, "application":item.application, "region":item.region,"user":item.user,"server":item.server, "host":item.host, "software":item.software, 
                    "feature":item.feature, "version":item.version, "user_key":item.user_key, "date_time":item.date_time, "license_used":item.license_used, 
                    "total_license":item.total_license, "created_at":item.created_at, "site_code":item.site_code, "total_license_used":item.total_license_used})
    
    user_license_data_df = pd.DataFrame(arr)   
    # user_license_data_df.to_csv("history_data_df.csv", encoding='utf-8', index = False)  
    user_with_spent_hour_arr = get_license_with_spent_hours(user_license_data_df)
    
    #delete user_license_with_spent_hour's existing record from LicenseHistoryLog table 
    # for user_record in user_with_spent_hour_arr:
    #     #insert user_license_with_spent_hour to license_details table
    #     db.session.add(user_record)
    #     #no need to delete the record
    #     # LicenseHistoryLog.query.filter(LicenseHistoryLog.application == user_record.application,LicenseHistoryLog.region == user_record.region, 
    #     #                                          LicenseHistoryLog.user == user_record.user, LicenseHistoryLog.feature == user_record.feature, LicenseHistoryLog.user_key == user_record.user_key, 
    #     #                                          LicenseHistoryLog.license_used == user_record.license_used, LicenseHistoryLog.host == user_record.host, LicenseHistoryLog.date_time == user_record.check_out, 
    #     #                                         LicenseHistoryLog.site_code == user_record.site_code).delete()
    #Bulk Save to the table
    db.session.bulk_save_objects(user_with_spent_hour_arr)
    db.session.commit()
   
    # db.session.bulk_save_objects(user_with_spent_hour_arr)
    # db.session.commit()
    

def get_license_with_spent_hours(user_license_data_df):
    from datetime import datetime , timedelta
    from license_tracker.models.license_details import LicenseDetail 
    #df.to_dict('records')
    import math

    filter_user_license_data  = user_license_data_df[["application", "region", "user", "feature", "user_key","license_used","total_license", "host", "date_time", "site_code", "total_license_used"]]
    
    print("lenth with duplicate",len(filter_user_license_data))
    filter_user_license_data = filter_user_license_data.drop_duplicates()
    print("lenth without duplicate",len(filter_user_license_data)) 
        
    user_with_spent_hour_arr = []
    for id, filter_lic_item in filter_user_license_data.iterrows():
        app = filter_lic_item["application"]
        reg = filter_lic_item["region"]
        user = filter_lic_item["user"]
        feat = filter_lic_item["feature"]
        key = filter_lic_item["user_key"]
        used = filter_lic_item["license_used"]
        total_license = 0 if math.isnan(filter_lic_item["total_license"]) else filter_lic_item["total_license"]
        total_license_used = 0 if math.isnan(filter_lic_item["total_license_used"]) else filter_lic_item["total_license_used"]
        check_out = filter_lic_item["date_time"]
        host = filter_lic_item["host"]
        site = filter_lic_item["site_code"]
        selected_user_lic_data = user_license_data_df[(user_license_data_df["application"] == app) & (user_license_data_df["region"] == reg) & (user_license_data_df["user"] == user) & (user_license_data_df["feature"] == feat) & (user_license_data_df["user_key"] == key) & (user_license_data_df["date_time"] == check_out)]
        #get the check_in time
        selected_user_lic_data = selected_user_lic_data.sort_values('created_at')
        check_in = selected_user_lic_data['created_at'].iloc[-1]
        
        #time when user start using licenses --> checked out licenses from free slot
        check_out_dt= check_out #datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
        
        #time when user stop using licenses --> check in licenses to free slot
        check_in_dt = check_in #datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
        check_in_dt = check_in_dt + timedelta(minutes = 5)
        #total spent time 
        spend_time = check_in_dt - check_out_dt
         
        #calculating spenct time in hours
        days, seconds = spend_time.days, spend_time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        spent_hours = str(hours)+":"+str(minutes)+":"+str(seconds)
        #print(str(hours)+":"+str(minutes)+":"+str(seconds))
        license_detail_obj = LicenseDetail(
            application = app,
            region = reg,
            user = user,
            host = host,
            feature = feat,
            user_key= key,
            license_used= used,
            check_out= check_out_dt,
            check_in= check_in_dt,
            spent_hours= spent_hours,
            site_code= site,
            total_license=total_license,
            total_license_used=total_license_used
        )
        user_with_spent_hour_arr.append(license_detail_obj)
        #user_data_with_spent_hour.append({"application":app, "region":reg,"user":user, "host":host,"feature":feat,"user_key":key, "license_used":used, "check_out":check_out_dt, "check_in":check_in_dt, "spent_hours":spent_hours, "site":site})
        #print({"application":app, "region":reg,"user":user, "host":host,"feature":feat, "license_used":used, "check_out":check_out, "check_in":check_in, "spend_hours":spend_hours})
        #print(id)
    return user_with_spent_hour_arr
            
        
    
    

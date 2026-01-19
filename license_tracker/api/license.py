#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint,jsonify,current_app,request,abort
from license_tracker.logger import logger
from flask_login import login_user, login_required, logout_user, current_user
from license_tracker.models import db
from redminelib import Redmine
# from license_tracker.utils.utils import get_redmine_session,close_given_db_session
license_blueprint = Blueprint("license", __name__)


@license_blueprint.route("/get_feature",methods=["GET","POST"])
def get_feature():
    from license_tracker.utils.license_utils import check_altair_lic_status
    region_arr =  request.get_json()["region"]
    app_arr =  request.get_json()["application"]
    features = "msc"
    return jsonify({"features": features})



@license_blueprint.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logger.info("user logged out : {}".format(current_user.login))
    logout_user()
    return jsonify({"success": True})


@license_blueprint.route("/login",methods=["POST"])
def login():
    """Serve the ReactJS-based index.html"""
    if request.method == "POST":
        data = request.get_json()
        login = data["user_name"]
        password = data["password"]
        remember_me = data["remember_me"]  
        
        logger.info("logging in user:{}".format(login)) 
        
        master_password = current_app.config["MASTER_PASSWORD"]
        address = current_app.config["REDMINE_ADDRESS"]
        try:
            import os
            cert_full_path = False
            if os.getenv("SSL_CERT_DIR"):
                # logger.info("sending data secvurely for user {}".format(login))
                cert_path = os.getenv("SSL_CERT_DIR") 
                cert_full_path = os.path.join(cert_path,"server_certificate.pem")
            
            if master_password == password:
                redmine_user = Redmine(address, impersonate=login, key=current_app.config["REDMINE_API_KEY"], requests={'verify': cert_full_path}).auth()
            else:
                redmine_user = Redmine(address, username=login, password=password, requests={'verify': cert_full_path}).auth()
                
        except Exception as err:
            logger.error("logging in user:{} error".format(login)) 
            redmine_user = None
            return abort(401)
        
        is_session_open = False
        redmine_session = None

        if redmine_user:
            from license_tracker.models.users import User

            user = User.query.filter_by(login=login).first()
            # db.session.delete(user)
            # db.session.commit()
            if user:
                pass
                #login_user(user, remember=remember_me)
            else:
                from license_tracker.models.user_type import UserType
                user_type = UserType.USER
               
                # set site code as null now, later we need to add proper code
                user = User(login=login, type_=user_type, site_code="")
                db.session.add(user)
                db.session.commit() 
               
            login_user(user, remember=remember_me)
        else:
            logger.info("logging in user:{} error".format(login)) 

            # if is_session_open :
            #     close_given_db_session(redmine_session)

            return abort(401)
        
        
        user_id = redmine_user.id
    return jsonify({"success": True,
    "username":login,
    "user_id":user_id})

        

@license_blueprint.route("/<app>/<region>")
def check_license(app,region):
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    from license_tracker.utils.license_utils import check_altair_lic_status,check_msc_lic_status,check_particleworks_output
    if app == "altair":
        if region == "eu":
            out = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["EU_ALTAIR"],current_app.config["ALTAIR_PORT"])
        elif region == "apac":
            out = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["APAC_ALTAIR"],current_app.config["ALTAIR_PORT"])
        elif region == "apac_unlimited":
            out = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["APAC_UNLIMITED_ALTAIR"],current_app.config["ALTAIR_PORT"])
        elif region == "eu_unlimited":
            out = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["EU_UNLIMITED_ALTAIR"],current_app.config["ALTAIR_PORT"])
        elif region == "ame":
            out = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["AME_ALTAIR"],current_app.config["ALTAIR_PORT"])
    elif app == "msc":
        if region == "eu":
            out = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["EU_MSC"]))
        elif region == "apac":
            out = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["APAC_MSC"]))
        elif region == "ame":
            out = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["AME_MSC"]))
    elif app == "pw":
        out = check_particleworks_output(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["PW_PORT"],current_app.config["PARTICLEWORKS"]))
    return jsonify({"feature_list":out})


@license_blueprint.route("/get_data", methods=["POST"])
def get_data():
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    import requests, textwrap, os
    region_arr =  request.get_json()["region"]
    app_arr =  request.get_json()["application"]
    is_inuse =  request.get_json()["is_inuse"]
    try:
        output_tbl_arr, server_info_arr, output_text_arr = get_license_data(region_arr, app_arr, is_inuse)
        return jsonify({"feature_list":output_tbl_arr, "server_info": server_info_arr, "output_text": output_text_arr})
    except Exception as err:
        return abort(err)

def get_license_data(region_arr, app_arr, is_inuse):
    from license_tracker.utils.license_utils import check_altair_lic_status,check_msc_lic_status,check_particleworks_output, check_ricardo_output, check_masta_output, check_rlm_output

    output_tbl = []
    server_info = []
    output_text = """No data found ! Select different configuration"""
    
    output_tbl_arr = []
    server_info_arr = []
    output_text_arr = []
    unique_app = []
    logger.info("Start get_license_data(region_arr, app_arr, is_inuse) method")
    for idx in range(len(app_arr)):
        region = region_arr[idx]
        app = app_arr[idx]
        
        if app == "altair":
            if is_inuse:
                inuse = "-inuse"
            else:
                inuse = ""
                    
            if region == "eu":
                output_tbl, server_info,output_text = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["EU_ALTAIR"],current_app.config["ALTAIR_PORT"],inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "apac":
                output_tbl, server_info, output_text = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["APAC_ALTAIR"],current_app.config["ALTAIR_PORT"], inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "apac_unlimited":
                output_tbl, server_info, output_text = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["APAC_UNLIMITED_ALTAIR"],current_app.config["ALTAIR_PORT"], inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "eu_unlimited":
                output_tbl, server_info, output_text = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["EU_UNLIMITED_ALTAIR"],current_app.config["ALTAIR_PORT"], inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "ame":
                output_tbl, server_info, output_text = check_altair_lic_status(current_app.config["ALMTUTIL_PATH"],current_app.config["AME_ALTAIR"],current_app.config["ALTAIR_PORT"], inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            else:
                output_text = "No data found ! Select different configuration"
            output_tbl = output_tbl
            
        elif app == "msc":
            if is_inuse:
                inuse =  "-A"
            else:
                inuse = "-a"
        
            if region == "eu":
                output_tbl, server_info, output_text = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["EU_MSC"]), inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "apac":
                output_tbl, server_info, output_text = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["APAC_MSC"]), inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "ame":
                output_tbl, server_info, output_text = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["AME_MSC_PORT"],current_app.config["AME_MSC"]), inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            elif region == "cluster":
                output_tbl, server_info, output_text = check_msc_lic_status(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["CLUSTER_MSC"]), inuse)
                server_info["application"] = app
                server_info["region"] = region
                
            else:
                output_text = """No data found ! Select different configuration"""
            output_tbl = output_tbl
        elif app == "pw":
            if is_inuse:
                inuse =  "-A"
            else:
                inuse = "-a"
            output_tbl, server_info, output_text = check_particleworks_output(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["PW_PORT"],current_app.config["PARTICLEWORKS"]), inuse)
            server_info["application"] = app
            server_info["region"] = region
                
            output_tbl = output_tbl
        elif app == "ricardo":
            if is_inuse:
                inuse =  "-A"
            else:
                inuse = "-a"
            output_tbl, server_info, output_text = check_ricardo_output(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["RECARDO_PORT"],current_app.config["RECARDO"]), inuse)
            server_info["application"] = app
            server_info["region"] = region
                
            output_tbl = output_tbl
        elif app == "masta":
            if is_inuse:
                inuse =  "-A"
            else:
                inuse = "-a"
            output_tbl, server_info, output_text = check_masta_output(current_app.config["RLMTUTIL_PATH"],"{}@{}".format(current_app.config["MASTA_PORT"],current_app.config["MASTA"]), inuse)
            server_info["application"] = app
            server_info["region"] = region
                
            output_tbl = output_tbl
        elif app == "rlm":
            if is_inuse:
                inuse =  "-A"
            else:
                inuse = "-a"
            output_tbl, server_info, output_text = check_rlm_output(current_app.config["RLMTUTIL_PATH"],"{}@{}".format(current_app.config["RLM_PORT"],current_app.config["RLM"]), inuse)
            server_info["application"] = app
            server_info["region"] = region
                
            output_tbl = output_tbl
        else:
            output_text = """No data found ! Select different configuration"""
            server_info = []
            output_tbl = []
        
        if app not in unique_app:
            output_tbl_arr.append(output_tbl)
            server_info_arr.append(server_info)
            output_text_arr.append(output_text)
            unique_app.append(app)
        else:
            for idx in range(len(unique_app)):
                if unique_app[idx] == app:
                    op  =  output_tbl_arr[idx][0]
                    op["TOTAL_LICENSES"] = int(op["TOTAL_LICENSES"]) + int(output_tbl[0]["TOTAL_LICENSES"])
                    op["USED_LICENSES"] = int(op["USED_LICENSES"]) + int(output_tbl[0]["USED_LICENSES"])
                    op["users"].extend(output_tbl[0]["users"])
                    for key, value in output_tbl[0]["CHART_DATA"].items():
                        if key not in op["CHART_DATA"]:
                            op["CHART_DATA"][key]=value
                        else:
                             op["CHART_DATA"][key] += value

                    for key, value in output_tbl[0]["SITE_CHART_DATA"].items():
                        if key not in op["SITE_CHART_DATA"]:
                            op["SITE_CHART_DATA"][key]=value
                        else:
                             op["SITE_CHART_DATA"][key] += value
                
                    
                    output_text_arr[idx] = str(output_text_arr[idx]) + "\r\n"+ str(output_text)
                    
    
        
        
    logger.info("End get_license_data(region_arr, app_arr, is_inuse) method")
        #logger.info(output)
    return output_tbl_arr, server_info_arr, output_text_arr
    
@license_blueprint.route("/get_license_by_date", methods=["POST"])
def get_license_by_date():
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    from datetime import datetime, timedelta
    import requests, textwrap, os
    from_date =  request.get_json()["from_date"]
    to_date =  request.get_json()["to_date"]
    
    try:
        from license_tracker.utils.license_utils import get_license_graph_data
        date_arr, series = get_license_graph_data(from_date=from_date, to_date=to_date)
        arr = []
        for key, value in series.items():
            arr.append({"name" :key, "data":value})
            
        return jsonify({"line_date_arr":date_arr, "line_series": arr})
    except Exception as err:
        return abort(err)



@license_blueprint.route("/kill_license", methods=["GET", "POST"])
def kill_license():
    # get 
    selected_app =  request.get_json()["selected_app"]
    selected_region =  request.get_json()["selected_region"]
    region =  request.get_json()["region"]
    app =  request.get_json()["application"]
    is_inuse =  request.get_json()["is_inuse"]
    unique_key =  request.get_json()["key"]
    host_name =  request.get_json()["host_name"]
    software = request.get_json()["software"]
    #for particleworks
    user_host = request.get_json()["user_host"]
    user_name = request.get_json()["user_name"]
    server_host = request.get_json()["server_host"]
    
    software = software.lower()
    host_name = host_name.split("@")
    port = host_name[0].strip()
    server = host_name[1].split(".")[0].strip()
    from license_tracker.utils.license_utils import kill_msc_license,kill_particlework_license
    logger.info("Start kill_license() method")
    if selected_app == "msc":
        if is_inuse:
            inuse =  "-A"
        else:
            inuse = "-a"
    
        if selected_region == "eu":
            kill_out, kill_err = kill_msc_license(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["EU_MSC"]), inuse, unique_key,software, server, port )
        elif selected_region == "apac":
            kill_out, kill_err = kill_msc_license(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["APAC_MSC"]), inuse, unique_key, software, server, port )
        elif selected_region == "ame":
             kill_out, kill_err = kill_msc_license(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["AME_MSC_PORT"],current_app.config["AME_MSC"]), inuse, unique_key, software, server, port )
        elif selected_region == "cluster":
             kill_out, kill_err = kill_msc_license(current_app.config["LMTUTIL_PATH"],"{}@{}".format(current_app.config["MSC_PORT"],current_app.config["CLUSTER_MSC"]), inuse, unique_key, software, server, port )
        else:
            out = """No data found ! Select different configuration"""
    elif selected_app == "pw":
        if is_inuse:
            inuse =  "-A"
        else:
            inuse = "-a"
        logger.info(request.get_json())
        logger.info(unique_key)
        kill_out, kill_err = kill_particlework_license(current_app.config["LMTUTIL_PATH"],user_name,  software, user_host, unique_key )
    else:
        output = """No data found ! Select different configuration"""
    if len(kill_out) >=3:
        kill_out = kill_out[1]
    else:
        kill_out = "Succefully removed!"
    output_tbl_arr, server_info_arr, output_text_arr = get_license_data(region, app, is_inuse)
    logger.info("End kill_license() method")
    return jsonify({"feature_list":output_tbl_arr, "server_info": server_info_arr, "output_text": output_text_arr, "kill_out": kill_out})
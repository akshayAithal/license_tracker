#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint,jsonify,current_app,request,abort
from license_tracker.logger import logger
from flask_login import login_user, login_required, logout_user, current_user
from license_tracker.models import db, User, UserType, AppSettings
from redminelib import Redmine
# from license_tracker.utils.utils import get_redmine_session,close_given_db_session
license_blueprint = Blueprint("license", __name__)


def authenticate_ldap(login, password):
    """Authenticate user against LDAP server."""
    try:
        import ldap3
        from ldap3 import Server, Connection, ALL
        
        settings = AppSettings.get_ldap_settings()
        
        if not settings.get('ldap_server'):
            return None, "LDAP server not configured"
        
        use_ssl = settings.get('ldap_use_ssl', False)
        port = settings.get('ldap_port', 636 if use_ssl else 389)
        
        server = Server(
            settings['ldap_server'],
            port=port,
            use_ssl=use_ssl,
            get_info=ALL
        )
        
        # First bind with service account to search for user
        conn = Connection(
            server,
            user=settings.get('ldap_bind_dn'),
            password=settings.get('ldap_bind_password'),
            auto_bind=True
        )
        
        # Search for user
        user_filter = settings.get('ldap_user_filter', '(uid={username})').replace('{username}', login)
        base_dn = settings.get('ldap_base_dn', '')
        username_attr = settings.get('ldap_username_attribute', 'uid')
        email_attr = settings.get('ldap_email_attribute', 'mail')
        
        conn.search(
            base_dn,
            user_filter,
            attributes=[username_attr, email_attr]
        )
        
        if not conn.entries:
            conn.unbind()
            return None, "User not found in LDAP"
        
        user_dn = conn.entries[0].entry_dn
        user_email = str(conn.entries[0][email_attr]) if email_attr in conn.entries[0] else None
        conn.unbind()
        
        # Now try to bind as the user to verify password
        user_conn = Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True
        )
        user_conn.unbind()
        
        return {'login': login, 'email': user_email}, None
        
    except ImportError:
        return None, "ldap3 library not installed"
    except Exception as e:
        logger.error(f"LDAP authentication failed: {str(e)}")
        return None, str(e)


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
    """Handle user login with support for local, LDAP, and Redmine authentication."""
    if request.method == "POST":
        data = request.get_json()
        login_name = data["user_name"]
        password = data["password"]
        remember_me = data.get("remember_me", False)
        
        logger.info("logging in user:{}".format(login_name))
        
        # Get authentication settings
        auth_mode = AppSettings.get_setting('auth_mode', 'local')
        ldap_enabled = AppSettings.get_setting('ldap_enabled', False)
        redmine_enabled = AppSettings.get_setting('redmine_auth_enabled', False)
        
        user = None
        authenticated = False
        user_id = None
        
        # Try local authentication first
        local_user = User.query.filter_by(login=login_name).first()
        
        if local_user and local_user.password_hash:
            # User has local password, try to authenticate
            if local_user.check_password(password):
                if not local_user.is_active:
                    logger.warning(f"Inactive user {login_name} attempted login")
                    return jsonify({"success": False, "error": "Account is disabled"}), 401
                user = local_user
                authenticated = True
                user_id = local_user.id_
                logger.info(f"User {login_name} authenticated via local password")
        
        # Try LDAP authentication if enabled and not yet authenticated
        if not authenticated and ldap_enabled:
            ldap_result, ldap_error = authenticate_ldap(login_name, password)
            if ldap_result:
                authenticated = True
                logger.info(f"User {login_name} authenticated via LDAP")
                
                # Create or update local user from LDAP
                if not local_user:
                    local_user = User(
                        login=login_name,
                        email=ldap_result.get('email'),
                        type_=UserType.USER,
                        site_code=""
                    )
                    db.session.add(local_user)
                    db.session.commit()
                elif ldap_result.get('email') and not local_user.email:
                    local_user.email = ldap_result.get('email')
                    db.session.commit()
                
                user = local_user
                user_id = local_user.id_
        
        # Try Redmine authentication if enabled and not yet authenticated
        if not authenticated and redmine_enabled:
            master_password = current_app.config.get("MASTER_PASSWORD", "")
            address = current_app.config.get("REDMINE_ADDRESS", "")
            
            if address:
                try:
                    import os
                    cert_full_path = False
                    if os.getenv("SSL_CERT_DIR"):
                        cert_path = os.getenv("SSL_CERT_DIR")
                        cert_full_path = os.path.join(cert_path, "server_certificate.pem")
                    
                    if master_password == password:
                        redmine_user = Redmine(address, impersonate=login_name, key=current_app.config["REDMINE_API_KEY"], requests={'verify': cert_full_path}).auth()
                    else:
                        redmine_user = Redmine(address, username=login_name, password=password, requests={'verify': cert_full_path}).auth()
                    
                    if redmine_user:
                        authenticated = True
                        user_id = redmine_user.id
                        logger.info(f"User {login_name} authenticated via Redmine")
                        
                        # Create or get local user
                        if not local_user:
                            local_user = User(
                                login=login_name,
                                type_=UserType.USER,
                                site_code=""
                            )
                            db.session.add(local_user)
                            db.session.commit()
                        
                        user = local_user
                        if not user_id:
                            user_id = local_user.id_
                            
                except Exception as err:
                    logger.error(f"Redmine auth error for user {login_name}: {str(err)}")
        
        if not authenticated:
            logger.info(f"Login failed for user: {login_name}")
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
        
        login_user(user, remember=remember_me)
        
        return jsonify({
            "success": True,
            "username": login_name,
            "user_id": user_id,
            "is_admin": user.is_admin()
        })


@license_blueprint.route("/register", methods=["POST"])
def register():
    """Handle user registration."""
    # Check if registration is enabled
    if not AppSettings.get_setting('registration_enabled', True):
        return jsonify({"success": False, "error": "Registration is disabled"}), 403
    
    data = request.get_json()
    login_name = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not login_name or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
    
    # Check if user already exists
    if User.query.filter_by(login=login_name).first():
        return jsonify({"success": False, "error": "Username already exists"}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "Email already registered"}), 400
    
    # Create new user
    user = User(
        login=login_name,
        email=email,
        type_=UserType.USER,
        site_code="",
        password=password
    )
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"New user registered: {login_name}")
    
    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": user.to_dict()
    }), 201


@license_blueprint.route("/auth/settings", methods=["GET"])
def get_public_auth_settings():
    """Get public authentication settings (no admin required)."""
    return jsonify({
        "success": True,
        "registration_enabled": AppSettings.get_setting('registration_enabled', True),
        "ldap_enabled": AppSettings.get_setting('ldap_enabled', False),
        "redmine_auth_enabled": AppSettings.get_setting('redmine_auth_enabled', False)
    })


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


@license_blueprint.route("/get_versions", methods=["GET"])
def get_versions():
    """Get all unique versions from license details."""
    from license_tracker.models.license_details import LicenseDetail
    try:
        versions = db.session.query(LicenseDetail.feature).distinct().all()
        version_list = [v[0] for v in versions if v[0]]
        return jsonify({"success": True, "versions": version_list})
    except Exception as err:
        logger.error(f"Error getting versions: {err}")
        return jsonify({"success": False, "versions": []})


@license_blueprint.route("/get_historical_usage", methods=["POST"])
def get_historical_usage():
    """Get historical usage data with filters."""
    from license_tracker.models.license_details import LicenseDetail
    from datetime import datetime
    
    data = request.get_json()
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    application = data.get("application")
    region = data.get("region")
    version = data.get("version")
    
    try:
        query = LicenseDetail.query
        
        if from_date:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(LicenseDetail.check_out >= from_dt)
        
        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(LicenseDetail.check_out <= to_dt)
        
        if application:
            query = query.filter(LicenseDetail.application == application)
        
        if region:
            query = query.filter(LicenseDetail.region == region)
        
        if version:
            query = query.filter(LicenseDetail.feature == version)
        
        results = query.order_by(LicenseDetail.check_out.desc()).limit(500).all()
        
        usage_data = []
        total_licenses_used = 0
        unique_users = set()
        total_duration_hours = 0
        
        for item in results:
            usage_data.append({
                "user": item.user,
                "application": item.application,
                "region": item.region,
                "feature": item.feature,
                "version": item.feature,
                "host": item.host,
                "license_used": item.license_used or 0,
                "check_out": item.check_out.strftime('%Y-%m-%d %H:%M') if item.check_out else None,
                "check_in": item.check_in.strftime('%Y-%m-%d %H:%M') if item.check_in else None,
                "spent_hours": item.spent_hours,
            })
            total_licenses_used += item.license_used or 0
            unique_users.add(item.user)
            
            if item.spent_hours:
                try:
                    parts = item.spent_hours.split(':')
                    hours = int(parts[0]) + int(parts[1])/60 if len(parts) >= 2 else 0
                    total_duration_hours += hours
                except:
                    pass
        
        avg_duration = total_duration_hours / len(results) if results else 0
        
        summary = {
            "total_sessions": len(results),
            "unique_users": len(unique_users),
            "total_licenses_used": total_licenses_used,
            "avg_duration_hours": round(avg_duration, 2),
        }
        
        return jsonify({
            "success": True,
            "usage_data": usage_data,
            "summary": summary
        })
    except Exception as err:
        logger.error(f"Error getting historical usage: {err}")
        return jsonify({"success": False, "usage_data": [], "summary": {}})


@license_blueprint.route("/get_utilization", methods=["POST"])
def get_utilization():
    """Get license utilization data with version breakdown."""
    from license_tracker.models.license_details import LicenseDetail
    from sqlalchemy import func
    from datetime import datetime
    
    data = request.get_json()
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    application = data.get("application")
    region = data.get("region")
    version = data.get("version")
    
    try:
        query = LicenseDetail.query
        
        if from_date:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(LicenseDetail.check_out >= from_dt)
        
        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(LicenseDetail.check_out <= to_dt)
        
        if application:
            query = query.filter(LicenseDetail.application == application)
        
        if region:
            query = query.filter(LicenseDetail.region == region)
        
        if version:
            query = query.filter(LicenseDetail.feature == version)
        
        results = query.all()
        
        # Calculate utilization by feature
        feature_stats = {}
        version_stats = {}
        
        for item in results:
            feature_key = f"{item.application}_{item.region}_{item.feature}"
            
            if feature_key not in feature_stats:
                feature_stats[feature_key] = {
                    "application": item.application,
                    "region": item.region,
                    "feature": item.feature,
                    "total_license": item.total_license or 0,
                    "used_values": [],
                    "peak_used": 0,
                }
            
            used = item.total_license_used or item.license_used or 0
            feature_stats[feature_key]["used_values"].append(used)
            if used > feature_stats[feature_key]["peak_used"]:
                feature_stats[feature_key]["peak_used"] = used
            
            # Version breakdown
            ver = item.feature or "Unknown"
            if ver not in version_stats:
                version_stats[ver] = {
                    "version": ver,
                    "usage_count": 0,
                    "unique_users": set(),
                    "total_hours": 0,
                }
            version_stats[ver]["usage_count"] += 1
            version_stats[ver]["unique_users"].add(item.user)
            
            if item.spent_hours:
                try:
                    parts = item.spent_hours.split(':')
                    hours = int(parts[0]) + int(parts[1])/60 if len(parts) >= 2 else 0
                    version_stats[ver]["total_hours"] += hours
                except:
                    pass
        
        # Build utilization data
        utilization_data = []
        total_utilization = 0
        peak_util = 0
        
        for key, stats in feature_stats.items():
            avg_used = sum(stats["used_values"]) / len(stats["used_values"]) if stats["used_values"] else 0
            util_percent = (avg_used / stats["total_license"] * 100) if stats["total_license"] > 0 else 0
            peak_percent = (stats["peak_used"] / stats["total_license"] * 100) if stats["total_license"] > 0 else 0
            
            utilization_data.append({
                "application": stats["application"],
                "region": stats["region"],
                "feature": stats["feature"],
                "total_license": stats["total_license"],
                "avg_used": avg_used,
                "peak_used": stats["peak_used"],
                "utilization_percent": util_percent,
            })
            
            total_utilization += util_percent
            if peak_percent > peak_util:
                peak_util = peak_percent
        
        # Build version breakdown
        total_usage = sum(v["usage_count"] for v in version_stats.values())
        version_breakdown = []
        
        for ver, stats in version_stats.items():
            share = (stats["usage_count"] / total_usage * 100) if total_usage > 0 else 0
            version_breakdown.append({
                "version": stats["version"],
                "usage_count": stats["usage_count"],
                "unique_users": len(stats["unique_users"]),
                "total_hours": round(stats["total_hours"], 1),
                "share_percent": share,
            })
        
        version_breakdown.sort(key=lambda x: x["usage_count"], reverse=True)
        
        avg_util = total_utilization / len(utilization_data) if utilization_data else 0
        
        summary = {
            "overall_utilization": round(avg_util, 1),
            "peak_utilization": round(peak_util, 1),
            "total_features": len(utilization_data),
            "versions_count": len(version_breakdown),
        }
        
        return jsonify({
            "success": True,
            "utilization_data": utilization_data,
            "version_breakdown": version_breakdown,
            "summary": summary
        })
    except Exception as err:
        logger.error(f"Error getting utilization: {err}")
        return jsonify({"success": False, "utilization_data": [], "version_breakdown": [], "summary": {}})

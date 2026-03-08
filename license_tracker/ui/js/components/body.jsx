import React, { useState } from 'react';
import { Button, Col, Row, Tabs, Layout, Menu, notification, Input, Select, Spin, Radio } from 'antd';
import { Table, Anchor, Checkbox } from 'antd';
import { UserOutlined, LogoutOutlined, LoginOutlined, SettingOutlined, UserAddOutlined, HomeOutlined, DashboardOutlined, BarChartOutlined, DollarOutlined, FileTextOutlined, ThunderboltOutlined, DeleteOutlined, MessageOutlined, ProfileOutlined } from '@ant-design/icons';
const { Header, Content, Sider } = Layout;
const { TabPane } = Tabs;
const { TextArea } = Input;
import axios from 'axios';
import { GenericFooter } from './footer';
import 'antd/dist/antd.css';
const { Option } = Select;
const { Search } = Input;
import ChartItem from './chart';
import { LoginPage } from './loginpage';
import { AdminPanel } from './adminpanel';
import License_Table from './license_table'
import { LoginGraph } from './license_graph';
import { HistoricalUsage } from './historical_usage';
import { HistoricalUtilization } from './historical_utilization';
import { ReportingPage } from './reporting';
import { Dashboard } from './dashboard';
import { HomePage } from './homepage';
import { CostingPage } from './costing';
import { ChatPage } from './chat';
import { HomeChatPage } from './home_chat';

const { Link } = Anchor;

const axiosInstance = axios.create({
  baseURL: window.location.href.split('?')[0],
});

const onSearch = (value) => console.log(value);

let message = '';
const currentUrl = window.location.href;
if (false)
  message = (
    <div style={{ color: "red", right: 0, position: 'absolute' }}>
      <p>This is a test version.</p>
    </div>
  );

export class Body extends React.Component {
  constructor(props) {
    super(props);
    var type = null
    this.state = {
      application: [],
      region: [],
      is_inuse: true,
      loading: false,
      fearture_list: [],
      server_info: {},
      output_text: "",
      fearture_list_arr: [],
      server_info_arr: [],
      output_text_arr: [],
      features: [],
      currentPage: "login",
      isLoggedIn: false,
      isAdmin: false,
      user: "",
      mail_id: "",
      radio_val: 1,
      registrationEnabled: true,
      generatingLiveData: false,
    };

    this.generateLiveData = this.generateLiveData.bind(this);
    this.clearLiveData = this.clearLiveData.bind(this);
  }

  componentDidMount() {
    axiosInstance.get("/license/check_session")
      .then(res => {
        if (res.data.logged_in) {
          this.setState({
            isLoggedIn: true,
            user: res.data.username,
            isAdmin: res.data.is_admin || false,
            currentPage: 'home',
          });
        }
      })
      .catch(err => {});
  }

  onCheckboxChange(e) {
    e.target.checked ? this.setState({ is_inuse: true }) : this.setState({ is_inuse: false })
  }

  onMenuSelect(i) {
    let currentPage = i.selectedKeys;
    if (currentPage == 3) {
      this.setState({ loading: true })
      axiosInstance.get("/license/logout")
        .then(res => {
          this.setState({
            isLoggedIn: false,
            isAdmin: false,
            user: "",
            mail_id: "",
            currentPage: "login",
            loading: false
          });
          notification["success"]({
            message: "Success",
            description: "Successfully logged out!"
          })
        }).catch(error => {
        }
        )
    }
    this.setState({ currentPage });
  }

  select_application(value) {
    this.setState({ application: value })
  }
  select_app_region(value) {
    let regions = []
    let apps = []
    let app_reg = []
    value.map(item =>
    {
      app_reg =  item.split(" ")
      regions.push(app_reg[1])
      apps.push(app_reg[0])
    }    
    )
    this.setState({ region: regions })
    this.setState({ application: apps })

    axiosInstance.post('/license/get_feature', {
      "application": this.state.application,
      "region": this.state.region,
    }).then(res => {
      const features = res.data.features
      this.setState({
        features: features,
      })
    }).catch(function (error) {
      //console.log(error)
      notification["error"]({
        message: "Error!",
        duration: 5,
        description: `Unable to get feature!`
      });
    }
    ).finally(() => {
      this.setState({ loading: false })
    })
  }

  select_feature(value){
    this.setState({ features: value })
  }

  select_region(value) {
    this.setState({ region: value })
  }

  getlicensedata() {
    this.setState({ loading: true })
    axiosInstance.post("/license/get_data",
      {
        "application": this.state.application,
        "region": this.state.region,
        "is_inuse": this.state.is_inuse

      }).then((response) => {
        console.log(response)
        this.setState({
          loading: false,
          fearture_list_arr: response.data.feature_list,
          server_info_arr: response.data.server_info,
          output_text_arr: response.data.output_text
        });
      }
      ).catch((error) => {
        console.log(error)
        let description = `Unable to get the license data`
        let duration = 20
        
        if (error.response && error.response.data) {
          if (error.response.data.error === "RATE_LIMIT") {
            description = error.response.data.output_text[0] || "License server rate limit exceeded. Please wait and try again."
            duration = 10
          } else if (error.response.data.error) {
            description = error.response.data.error
          }
        }
        
        notification["error"]({
          message: "Error!",
          duration: duration,
          description: description
        });
      }).finally(() => {
        this.setState({ loading: false })
      })
  }

  generateLiveData() {
    this.setState({ generatingLiveData: true });
    axiosInstance.post('/license/generate_live_data', {
      duration_minutes: 60,
      num_events: 50
    }).then(res => {
      notification["success"]({
        message: "Live Data Generated",
        description: res.data.message || 'Generated live data successfully',
        duration: 5
      });
    }).catch(error => {
      notification["error"]({
        message: "Error",
        description: (error.response && error.response.data && error.response.data.error) || 'Failed to generate live data. Make sure you are logged in.',
        duration: 5
      });
    }).finally(() => {
      this.setState({ generatingLiveData: false });
    });
  }

  clearLiveData() {
    this.setState({ generatingLiveData: true });
    axiosInstance.post('/license/clear_live_data', {
      clear_history: false
    }).then(res => {
      notification["success"]({
        message: "Live Data Cleared",
        description: 'Cleared active license records',
        duration: 5
      });
    }).catch(error => {
      notification["error"]({
        message: "Error",
        description: (error.response && error.response.data && error.response.data.error) || 'Failed to clear live data',
        duration: 5
      });
    }).finally(() => {
      this.setState({ generatingLiveData: false });
    });
  }

  render() {
    const formPageStyle = {
      overflowY: 'auto',
      marginTop: "80",
      paddingLeft: "24",
      paddingRight: "24",
      minHeight: "90vh",
      height: "90%",
      marginBottom: "2%",
      paddingBottom: "2%",
      backgroundImage: window.location.href + "assets/images/absurdity.png",
      backgroundRepeat: "repeat",
    }
    const layout = {
      labelCol: { span: 8 },
      wrapperCol: { span: 16 },
    };

    const onClickKill = (record, software, Application, region, hostname) => {
      this.setState({ loading: true })

      axiosInstance.post("/license/kill_license",
        {
         
          "application": this.state.application,
          "region": this.state.region,
          "is_inuse": this.state.is_inuse,
          "selected_app": Application,
          "selected_region": region,
          "host_name": hostname,
          "software": software,
          "user_host" : record.HOST,
          "user_name": record.NAME,
          "server_host":record.SERVER_HOST,
          "key": record.KEY
        }).then((response) => {
          console.log(response)
          this.setState({
            loading: false,
            fearture_list_arr: response.data.feature_list,
            server_info_arr: response.data.server_info,
            output_text_arr: response.data.output_text

          });
          notification["success"]({
            message: "Success",
            duration: 20,
            description: response.data.kill_out,
          });
        }).catch(function (error) {
          console.log(error)
          notification["error"]({
            message: "Error!",
            duration: 5,
            description: error
          });
        }
        ).finally(() => {
          this.setState({ loading: false })
        })
    };

    const onLoginFinish = values => {
      this.setState({ loading: true })
      axiosInstance.post('/license/login', {
        user_name: values["username"],
        password: values["password"],
        remember_me: values["remember"],
      }).then(res => {
        const username = res.data.username
        const isAdmin = res.data.is_admin || false
        this.setState({
          user: username,
          isLoggedIn: true,
          isAdmin: isAdmin,
          currentPage: 'home',
          loading: false
        })
        notification["success"]({
          message: "Welcome, " + username,
          duration: 3,
          description: 'Successfully logged in' + (isAdmin ? ' as administrator' : ''),
        });
      }).catch(function (error) {
        notification["error"]({
          message: "Login Failed",
          duration: 5,
          description: (error.response && error.response.data && error.response.data.error) || 'Invalid username or password'
        });
      }
      ).finally(() => {
        this.setState({ loading: false })
      })

    };

    const onRegisterSuccess = () => {
      this.setState({ currentPage: '2' });
    };

    const onBackToLogin = () => {
      this.setState({ currentPage: '2' });
    };

    const onRadioChange = e => {
      this.setState({ radio_val: e.target.value });
    };

    const onLogout = () => {
      this.setState({ loading: true })
      axiosInstance.get("/license/logout")
        .then(res => {
          this.setState({
            isLoggedIn: false,
            isAdmin: false,
            user: "",
            mail_id: "",
            currentPage: "login",
            loading: false
          });
          notification["success"]({
            message: "Logged Out",
            duration: 3,
            description: "Successfully logged out"
          })
        }).catch(error => {
          this.setState({ loading: false })
        })
    };

    const menuUserName = (
      <Menu.Item
        key='1'
        id="username"
        style={{ top: "0", right: "80px", position: 'absolute', height: "100%", float: "right !important" }}>
        <UserOutlined />
        {this.state.user}
      </Menu.Item>
    )
    const menuLoggedOut = (
      <Menu.Item
        key='2'
        id="loginPage"
        style={{ top: "0", right: "0", position: 'absolute', height: "100%" }}>
        <LoginOutlined />
        Login
      </Menu.Item>
    )
    const menuLoggedIn = (
      <Menu.Item
        key='3'
        id="loginPage"
        style={{ top: "0", right: "0", position: 'absolute', height: "100%" }}>
        <LogoutOutlined />
        Logout
      </Menu.Item>
    )
    const menuLicenseGraph = (
      <Menu.Item
        key='4'
        id="licensegraph"
        style={{
          opacity: "1",
          height: " 100%",
          order: "2",
          position: "static"
        }}>
        Graph
      </Menu.Item>
    )

    const menuReporting = (
      <Menu.Item
        key='7'
        id="reporting"
        style={{
          opacity: "1",
          height: " 100%",
          float: "left !important",
          color: "white"
        }}>
        Reporting
      </Menu.Item>
    )

    const menuAdminPanel = (
      <Menu.Item
        key='5'
        id="adminPanel"
        style={{ height: "100%" }}>
        <SettingOutlined />
        Admin
      </Menu.Item>
    )

    const menuRegister = (
      <Menu.Item
        key='6'
        id="registerPage"
        style={{ height: "100%" }}>
        <UserAddOutlined />
        Register
      </Menu.Item>
    )

    const menu = (
      <Menu
        theme='light'
        mode='horizontal'
        defaultSelectedKeys={['0']}
        //selectedKeys={[this.state.currentPage]} 
        style={{ height: '100%', background: 'linear-gradient(90deg, #0d9488 0%, #0891b2 100%)' }}
        onSelect={(i) => this.onMenuSelect(i)}>
        <Menu.Item key='1' id="treeButton" style={{ fontSize: 20, float: "left", color: "white", fontWeight: "bold" }}>
          {"Vizvalytics - license tracker"}
        </Menu.Item>

        {menuReporting}
        {this.state.isLoggedIn && this.state.isAdmin ? menuAdminPanel : null}
        {this.state.isLoggedIn ? menuUserName : null}
        {this.state.isLoggedIn ? menuLoggedIn : menuLoggedOut}
        {!this.state.isLoggedIn && this.state.registrationEnabled ? menuRegister : null}
      </Menu>
    );
    const header = (
      <Header className="header" style={{ position: 'fixed', zIndex: 1, width: '100%', height: 80, background: 'linear-gradient(90deg, #0d9488 0%, #0891b2 100%)' }}>
        <div className="logo" /><span className="logo_text"></span>
        {/* How do I set up the logo in the right way?I'm using a hack right now. */}
        {menu}
      </Header>
    )

    const pageHeaderStyle = {
      padding: '16px 24px',
      background: '#fff',
      borderBottom: '1px solid #e5e7eb',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    };
    const pageHeaderTitle = {
      fontSize: '18px',
      fontWeight: '600',
      color: '#1e3a5f',
    };
    const pageHeaderUser = {
      fontSize: '13px',
      color: '#6b7280',
    };

    const pageNames = {
      'home': 'Home',
      'licenses': 'Licenses',
      '1': 'Licenses',
      'dashboard': 'Dashboard',
      '': 'Dashboard',
      'chat': 'Chat',
      '7': 'Reporting',
      '8': 'Documents & Costing',
      'admin': 'Admin Panel',
    };
    const currentPageName = pageNames[this.state.currentPage] || 'Dashboard';

    const pageHeader = (
      <div style={pageHeaderStyle}>
        <span style={pageHeaderTitle}>{currentPageName}</span>
        <span style={pageHeaderUser}><UserOutlined style={{ marginRight: 6 }} />{this.state.user}</span>
      </div>
    );

    const license_tracker_overview_page = (
      <HomePage user={this.state.user} isLoggedIn={this.state.isLoggedIn} isAdmin={this.state.isAdmin} />
    );

    let displayedPage = <div></div>;
    if (this.state.currentPage === 'home') {
      displayedPage = <HomeChatPage />;
    }
    else if (this.state.currentPage === 'licenses' || this.state.currentPage === '1') {
      displayedPage = license_tracker_overview_page;
    }
    else if (this.state.currentPage === 'dashboard' || this.state.currentPage === '') {
      displayedPage = <Dashboard />;
    }
    else if (this.state.currentPage === 'chat') {
      displayedPage = <ChatPage />;
    }
    else if (this.state.currentPage === '7') {
      displayedPage = <ReportingPage />;
    }
    else if (this.state.currentPage === '8') {
      displayedPage = <CostingPage />
    }
    else if (this.state.currentPage === 'admin' && this.state.isAdmin) {
      displayedPage = <AdminPanel />
    }
    else {
      displayedPage = <Dashboard />;
    }

    const sidebarStyle = {
      background: '#ffffff',
      boxShadow: '2px 0 8px rgba(0,0,0,0.08)',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 100,
      width: 80,
    };

    const menuItemStyle = {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px 0',
      cursor: 'pointer',
      color: '#6b7280',
      transition: 'all 0.3s',
    };

    const menuItemActiveStyle = {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px 0',
      cursor: 'pointer',
      color: '#2563eb',
      backgroundColor: '#eff6ff',
      borderLeft: '3px solid #2563eb',
      transition: 'all 0.3s',
    };

    const menuIconStyle = {
      fontSize: '22px',
      marginBottom: '4px',
    };

    const menuLabelStyle = {
      fontSize: '10px',
      fontWeight: '500',
      letterSpacing: '0.5px',
    };

    const sidebarMenu = (
      <div style={sidebarStyle}>
        <div style={{ padding: '16px 8px', textAlign: 'center', borderBottom: '1px solid #e5e7eb' }}>
          <span style={{ fontSize: '9px', fontWeight: 'bold', color: '#1e3a5f', letterSpacing: '0.3px' }}>Vizvalytics<br/><span style={{ fontWeight: 400, fontSize: '8px' }}>license tracker</span></span>
        </div>
        <div 
          style={this.state.currentPage === 'home' ? menuItemActiveStyle : menuItemStyle}
          onClick={() => this.setState({ currentPage: 'home' })}
        >
          <HomeOutlined style={menuIconStyle} />
          <span style={menuLabelStyle}>HOME</span>
        </div>
        <div 
          style={this.state.currentPage === 'licenses' || this.state.currentPage === '1' ? menuItemActiveStyle : menuItemStyle}
          onClick={() => this.setState({ currentPage: 'licenses' })}
        >
          <FileTextOutlined style={menuIconStyle} />
          <span style={menuLabelStyle}>LICENSES</span>
        </div>
        <div 
          style={this.state.currentPage === 'dashboard' || this.state.currentPage === '' ? menuItemActiveStyle : menuItemStyle}
          onClick={() => this.setState({ currentPage: 'dashboard' })}
        >
          <DashboardOutlined style={menuIconStyle} />
          <span style={menuLabelStyle}>DASHBOARD</span>
        </div>
        <div 
          style={this.state.currentPage === 'chat' ? menuItemActiveStyle : menuItemStyle}
          onClick={() => this.setState({ currentPage: 'chat' })}
        >
          <MessageOutlined style={menuIconStyle} />
          <span style={menuLabelStyle}>CHAT</span>
        </div>
        {this.state.isAdmin ? (
          <div 
            style={this.state.currentPage === '7' ? menuItemActiveStyle : menuItemStyle}
            onClick={() => this.setState({ currentPage: '7' })}
          >
            <BarChartOutlined style={menuIconStyle} />
            <span style={menuLabelStyle}>REPORTING</span>
          </div>
        ) : null}
        {this.state.isAdmin ? (
          <div 
            style={this.state.currentPage === '8' ? menuItemActiveStyle : menuItemStyle}
            onClick={() => this.setState({ currentPage: '8' })}
          >
            <DollarOutlined style={menuIconStyle} />
            <span style={menuLabelStyle}>COSTING</span>
          </div>
        ) : null}
        {this.state.isAdmin ? (
          <div 
            style={this.state.currentPage === 'admin' ? menuItemActiveStyle : menuItemStyle}
            onClick={() => this.setState({ currentPage: 'admin' })}
          >
            <SettingOutlined style={menuIconStyle} />
            <span style={menuLabelStyle}>ADMIN</span>
          </div>
        ) : null}
        {/* Spacer */}
        <div style={{ flex: 1 }}></div>
        {/* User info + Logout at bottom */}
        <div style={{ position: 'absolute', bottom: 0, width: '100%', borderTop: '1px solid #e5e7eb' }}>
          <div style={{ padding: '10px 8px', textAlign: 'center' }}>
            <UserOutlined style={{ fontSize: '14px', color: '#1e3a5f' }} />
            <div style={{ fontSize: '9px', color: '#333', fontWeight: '500', marginTop: '2px', wordBreak: 'break-all' }}>{this.state.user}</div>
          </div>
          <div 
            style={Object.assign({}, menuItemStyle, { color: '#ef4444', borderTop: '1px solid #f3f4f6' })}
            onClick={onLogout}
          >
            <LogoutOutlined style={menuIconStyle} />
            <span style={menuLabelStyle}>LOGOUT</span>
          </div>
        </div>
      </div>
    );

    if (!this.state.isLoggedIn) {
      return (
        <Layout className="layout" style={{ overflowY: "hidden", minHeight: '100vh', background: 'linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%)' }}>
          <Content style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
            <div style={{
              width: '100%',
              maxWidth: 460,
              padding: '48px 40px',
              backgroundColor: 'rgba(255,255,255,0.97)',
              borderRadius: '20px',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)',
              backdropFilter: 'blur(10px)',
            }}>
              <div style={{ textAlign: 'center', marginBottom: '36px' }}>
                <div style={{
                  width: 56,
                  height: 56,
                  margin: '0 auto 16px',
                  borderRadius: 14,
                  background: 'linear-gradient(135deg, #1e3a5f 0%, #2d6cad 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 14px rgba(30, 58, 95, 0.35)',
                }}>
                  <span style={{ fontSize: 24, fontWeight: 'bold', color: '#fff', letterSpacing: 1 }}>LT</span>
                </div>
                <div style={{ fontSize: '22px', fontWeight: '700', color: '#1e3a5f', letterSpacing: '2px' }}>Vizvalytics</div>
                <div style={{ fontSize: '13px', fontWeight: '400', color: '#1e3a5f', letterSpacing: '1px', marginTop: '2px' }}>license tracker</div>
                <div style={{ fontSize: '14px', color: '#8c95a6', marginTop: '6px', fontWeight: 400 }}>License Management Platform</div>
              </div>
              {this.state.loading ? <Spin tip="Signing in..." style={{ display: 'block', margin: '20px auto' }} /> : null}
              <LoginPage onLoginFinish={onLoginFinish} />
              <div style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: '#b0b8c4' }}>
                Secure access · Enterprise edition
              </div>
            </div>
          </Content>
        </Layout>
      );
    }

    return (
      <Layout className="layout" style={{ overflowY: "hidden", minHeight: '100vh' }}>
        {sidebarMenu}
        <Layout style={{ marginLeft: 80, backgroundColor: '#e8ecf1' }}>
          {pageHeader}
          <Content style={{ backgroundColor: '#e8ecf1', minHeight: '100vh' }}>
            {displayedPage}
          </Content>
        </Layout>
      </Layout>
    );
  }
}
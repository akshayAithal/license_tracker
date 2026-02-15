import React, { useState } from 'react';
import { Button, Col, Row, Tabs, Layout, Menu, notification, Input, Select, Spin, Radio } from 'antd';
import { Table, Anchor, Checkbox } from 'antd';
import { UserOutlined, LogoutOutlined, LoginOutlined, SettingOutlined, UserAddOutlined } from '@ant-design/icons';
const { Header, Content } = Layout;
const { TabPane } = Tabs;
const { TextArea } = Input;
import axios from 'axios';
import { GenericFooter } from './footer';
import 'antd/dist/antd.css';
const { Option } = Select;
const { Search } = Input;
import ChartItem from './chart';
import { LoginPage } from './loginpage';
// import { RegisterPage } from './registerpage';
// import { AdminPanel } from './adminpanel';
import License_Table from './license_table'
import { LoginGraph } from './license_graph';
import { HistoricalUsage } from './historical_usage';
import { HistoricalUtilization } from './historical_utilization';

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
      features:[],
      currentPage: "",
      isLoggedIn: false,
      isAdmin: false,
      user: "",
      mail_id: "",
      radio_val: 1,
      registrationEnabled: true,
    };
    
    //this.formRef = React.createRef();
    //this.searchInput = React.createRef();
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
            currentPage: 1,
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
    value.map(item=>
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
      ).catch(function (error) {
        console.log(error)
        notification["error"]({
          message: "Error!",
          duration: 20,
          description: `Unable to get the license data`
        });
      }).finally(() => {
        this.setState({ loading: false })
      })
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
      //console.log('Received values of form: ', values);
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
          currentPage: 1,
          loading: false
        })
        notification["success"]({
          message: "Success",
          duration: 20,
          description: 'Successfully logged in',
        });
      }).catch(function (error) {
        //console.log(error)
        notification["error"]({
          message: "Error!",
          duration: 5,
          description: (error.response && error.response.data && error.response.data.error) || 'Unable to login'
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

    const menuHistoricalUsage = (
      <Menu.Item
        key='7'
        id="historicalUsage"
        style={{
          opacity: "1",
          height: "100%",
          order: "3",
          position: "static"
        }}>
        Historical Usage
      </Menu.Item>
    )

    const menuHistoricalUtilization = (
      <Menu.Item
        key='8'
        id="historicalUtilization"
        style={{
          opacity: "1",
          height: "100%",
          order: "4",
          position: "static"
        }}>
        Utilization
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
          {"License Tracker"}
        </Menu.Item>

        {menuHistoricalUsage}
        {menuHistoricalUtilization}
        {this.state.isLoggedIn && this.state.isAdmin ? menuAdminPanel : null}
        {this.state.isLoggedIn ? menuUserName : null}
        {this.state.isLoggedIn ? menuLoggedIn : menuLoggedOut}
        {!this.state.isLoggedIn && this.state.registrationEnabled ? menuRegister : null}
      </Menu>);
    const header = (
      <Header className="header" style={{ position: 'fixed', zIndex: 1, width: '100%', height: 80, background: 'linear-gradient(90deg, #0d9488 0%, #0891b2 100%)' }}>
        <div className="logo" /><span className="logo_text"></span>
        {/* How do I set up the logo in the right way?I'm using a hack right now. */}
        {menu}
      </Header>
    )

    const license_tracker_overview_page = (
      <div style={formPageStyle}>
        {message}
        <br />
        <br />
        <Select
          mode="multiple"
          showSearch
          allowClear
          style={{
            width: 300,
          }}
          placeholder="Select an Application"
          onChange={this.select_app_region.bind(this)}
        // options={options}
        >
          <Option value="altair eu" key="altair eu">Altair EU</Option>
          <Option value="altair eu_unlimited" key="altair eu_unlimited">Altair EU Unlimited</Option>
          <Option value="altair apac" key="altair apac">Altair APAC</Option>
          <Option value="altair apac_unlimited" key="altair apac_unlimited">Altair APAC Unlimited</Option>
          <Option value="altair ame" key="altair ame">Altair AME</Option>
          <Option value="msc eu" key="msc eu">MSC EU</Option>
          <Option value="msc apac" key="msc apac">MSC APAC</Option>
          <Option value="msc ame" key="msc ame">MSC AME</Option>
          <Option value="msc cluster" key="msc cluster">MSC Cluster</Option>
          <Option value="pw" key="pw">Particleworks</Option>
          <Option value="ricardo" key="ricardo">Ricardo</Option>
          <Option value="masta" key="masta">Masta</Option>
          <Option value="rlm" key="rlm">RLM</Option>
        </Select>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        {/* <Select
          mode="multiple"
          showSearch
          allowClear
          style={{
            width: 300,
          }}
          placeholder="Select an Feature"
          onChange={this.select_feature.bind(this)}
          options={this.state.fearture_list}
        ></Select> */}
        {/* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; */}
        <Checkbox defaultChecked={this.state.is_inuse} onChange={this.onCheckboxChange.bind(this)}>In Use</Checkbox>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <Button
          type="primary"
          size="large"
          loading={this.state.loading}
          onClick={this.getlicensedata.bind(this)}>
          <UserOutlined />
          Submit
        </Button>
        <br />
        <br />
        <h1>License Info :</h1>
        {this.state.loading ? <Spin tip="Loading..." style={{ position: "absolute", left: "0px", top: "45%", width: "100%", height: "100%", zIndex: "100" }} /> : null}
        {this.state.output_text_arr.length > 0 ?
          (
            <div>
              {this.state.output_text_arr.map((output_text, index) =>
                <div>
                  <h2>Host Name : {this.state.server_info_arr[index]["hostname"]}</h2>
                  {this.state.fearture_list_arr[index].map(feat_item =>
                    <div>
                      <b> Software: {feat_item["NAME"]}</b>
                      <p> Total license: <b>{feat_item["TOTAL_LICENSES"]}</b>,  Current licenses in use: <b>{feat_item["USED_LICENSES"]}</b> </p>
                      <Row>
                        <Col span={16}>
                          <Tabs defaultActiveKey="1">
                            <TabPane tab="Table" key="1">
                              {/* {this.state.users = feat_item["users"]} */}
                              <License_Table onClickKill={onClickKill} Username={this.state.user} DataSource={feat_item["users"]} Application={this.state.server_info_arr[index]["application"]} 
                              region={this.state.server_info_arr[index]["region"]} hostname={this.state.server_info_arr[index]["hostname"]}  software={feat_item["NAME"]}></License_Table>
                            </TabPane>
                            <TabPane tab="Text" key="2" >

                              <TextArea overflowY={scroll} style={{ height: "432px" }} rows={40} placeholder="License Info" value={output_text} />
                            </TabPane>
                          </Tabs>
                        </Col>
                        <Col span={8} >
                          <Radio.Group name="radiogroup" onChange={onRadioChange} defaultValue={1}>
                            <Radio value={1}>User</Radio>
                            <Radio value={2}>Region</Radio>
                          </Radio.Group>
                          <div style={{ position: 'absolute', width: '100%', height: '100%', background: 'rgb(0 0 0 / 0%)' }} >
                            <h3 style={{ position: "relative", textAlign: 'center', top: "2%" }}>Current License Usage {feat_item["NAME"]}</h3>
                            {this.state.radio_val == 1 ?
                              <ChartItem Labels={Object.keys(feat_item["CHART_DATA"]).map((key) => key)} Series={Object.values(feat_item["CHART_DATA"]).map((value) => value)}></ChartItem>
                              :
                              <ChartItem Labels={Object.keys(feat_item["SITE_CHART_DATA"]).map((key) => key)} Series={Object.values(feat_item["SITE_CHART_DATA"]).map((value) => value)}></ChartItem>
                            }
                          </div>
                        </Col>
                      </Row>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
          : null}
      </div>
    );

    let displayedPage = <div></div>;
    if (this.state.currentPage == '1') {
      displayedPage = license_tracker_overview_page;
    }
    else if (this.state.currentPage == '2') {
      displayedPage = <div> {this.state.loading ? <Spin tip="Loading..." style={{ position: "absolute", left: "0px", top: "45%", width: "100%", height: "100%", zIndex: "100" }} /> : null}
        <LoginPage onLoginFinish={onLoginFinish} />
      </div>
    }
    else if (this.state.currentPage == '4') {
      displayedPage = <div> {this.state.loading ? <Spin tip="Loading..." style={{ position: "absolute", left: "0px", top: "45%", width: "100%", height: "100%", zIndex: "100" }} /> : null}
        <LoginGraph />
      </div>
    }
    else if (this.state.currentPage == '7') {
      displayedPage = <div> {this.state.loading ? <Spin tip="Loading..." style={{ position: "absolute", left: "0px", top: "45%", width: "100%", height: "100%", zIndex: "100" }} /> : null}
        <HistoricalUsage />
      </div>
    }
    else if (this.state.currentPage == '8') {
      displayedPage = <div> {this.state.loading ? <Spin tip="Loading..." style={{ position: "absolute", left: "0px", top: "45%", width: "100%", height: "100%", zIndex: "100" }} /> : null}
        <HistoricalUtilization />
      </div>
    }
    // Admin panel and register page temporarily disabled
    // else if (this.state.currentPage == '5') {
    //   displayedPage = <AdminPanel />
    // }
    // else if (this.state.currentPage == '6') {
    //   displayedPage = <RegisterPage onRegisterSuccess={onRegisterSuccess} onBackToLogin={onBackToLogin} />
    // }
    else {
      displayedPage = license_tracker_overview_page;
    }

    return (
      <Layout className="layout" style={{ overflowY: "hidden" }}>
        {header}
        <Content style={{ paddingLeft: '0.5rem', backgroundColor: '#eaeae8' }}>
          {displayedPage}
        </Content>
        <GenericFooter name="License Tracker" id="99999999" />
      </Layout>
    );
  }
}
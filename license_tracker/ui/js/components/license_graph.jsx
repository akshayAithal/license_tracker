import { Button } from 'antd'; // Button = antd.Button
import { Col } from 'antd';
import { Row } from 'antd';
import { Form } from 'antd';
import { Input } from 'antd';
import { Select } from 'antd';
import {  Checkbox  } from 'antd';
import {UploadOutlined, UserOutlined, LockOutlined , LogoutOutlined, LoginOutlined, } from '@ant-design/icons';
import { FormInstance } from 'antd/es/form'
import React from 'react';
import ReactDOM from 'react-dom';
import { DatePicker, Space } from 'antd';
import axios from 'axios';
import dayjs from 'dayjs';
const { RangePicker } = DatePicker;
import LineChart from './line_chart';
import Iframe from 'react-iframe'


const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0] , 
});

const onSearch = (value) => console.log(value);



const rangePresets = [
  {
    label: 'Last 7 Days',
    value: [dayjs().add(-7, 'd'), dayjs()],
  },
  {
    label: 'Last 14 Days',
    value: [dayjs().add(-14, 'd'), dayjs()],
  },
  {
    label: 'Last 30 Days',
    value: [dayjs().add(-30, 'd'), dayjs()],
  },
  {
    label: 'Last 90 Days',
    value: [dayjs().add(-90, 'd'), dayjs()],
  },
];


export class LoginGraph extends React.Component {
  constructor(props) {
    super(props);
    var type = null
    this.state ={ 
      application:undefined,
      region:undefined,
      fromDate:null,
      toDate:null,
      line_date_arr:[],
      line_series:{},
      loading:false,
      output_text: "",
      currentPage:"",
      isLoggedIn:false,
      user:"",
      mail_id:"",
      radio_val:1, 
    };
    //this.formRef = React.createRef();
    //this.searchInput = React.createRef();
  }  
  
  select_application(value){
    this.setState({application:value})
  }

  select_region(value){
    this.setState({region:value})
  }

  getlicensedata()
  {
    this.setState({ loading: true })
    axiosInstance.post("/license/get_license_by_date",
    {"from_date":this.state.fromDate,
      "to_date":this.state.toDate,   
    }).then((response) => {
      console.log(response)
    this.setState({
      loading:false,
      line_date_arr:response.data.line_date_arr,
      line_series:response.data.line_series
    });
    }
    ).catch(function (error) {
      console.log(error)
      notification["error"]({
          message: "Error!",
          duration: 20,
          description: `Unable to get the license data`
      });
      }).finally(()=>{
        this.setState({ loading: false })   
      })
  }
   
  render() {
  const formPageStyle = {
      overflowY: 'auto',
      marginTop: "80",
      paddingLeft: "24",
      paddingRight: "24",
      minHeight:"90vh",
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
    

    const onRangeChange = (dates, dateStrings) => {
      if (dates) {
          this.setState({
            fromDate:dateStrings[0],
            toDate:dateStrings[1],
            
          });
        console.log('From: ', dates[0], ', to: ', dates[1]);
        console.log('From: ', dateStrings[0], ', to: ', dateStrings[1]);
      } else {
        console.log('Clear');
      }
    };

  const licenseGraph= ( 
    <div style={formPageStyle}>
    <div style={{color:"red",right:0, position:'absolute'}}> </div>
    <br/>
    <br/>        
    <Space direction="vertical" size={12}>
          <RangePicker presets={[
          {
            label: 'Last 7 Days',
            value: [dayjs().add(-7, 'd'), dayjs()],
          },
          {
            label: 'Last 14 Days',
            value: [dayjs().add(-14, 'd'), dayjs()],
          },
          {
            label: 'Last 30 Days',
            value: [dayjs().add(-30, 'd'), dayjs()],
          },
          {
            label: 'Last 90 Days',
            value: [dayjs().add(-90, 'd'), dayjs()],
          },
        ]} onChange={onRangeChange} />
    </Space>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <Button
      type="primary"
      size="large"
      loading={this.state.loading}
      onClick={this.getlicensedata.bind(this)}>
      <UserOutlined />
      Submit
    </Button>
    <br/>
    <br/>
      {/* <div>
        <h2>Grafana Dashboard</h2>
        <iframe
          src={"http://10.143.1.219:3000/d/sIca8elIz/license_trakcer?orgId=1"}
          width="100%"
          height="500px"
          frameBorder="0"
          allowFullScreen
        ></iframe>
      </div> */}
        {this.state.line_date_arr.length>0?
          (
            <div>
              <LineChart  Labels = { this.state.line_date_arr} Series = {this.state.line_series}></LineChart>
            </div>
          )
        :null}
    </div>
    )

  return (
      <div>
      {licenseGraph}
      </div>
      );

  }

}
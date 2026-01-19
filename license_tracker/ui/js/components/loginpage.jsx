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


export const LoginPage = (props)=>
{

    const LoginProps = {
        style: {
            width: '50%',
            height: "50%",
            marginTop: "10%",
            marginLeft: '25%',
            marginRight: '25%',
            marginBottom: "25%",
            paddingTop: '5%',
            paddingBottom: "5%",
            paddingLeft: '10%',
            paddingRight: '10%',
            // border: "2px solid red",
            resize: "none"
        }}

        const loginPage = (  <div  {...LoginProps}>
            <Row gutter={24}>  
            <Col span={ 20 }style={{ maxHeight: "100%" , padding: 10, overflowX: 'auto', overflowY: 'auto'}}>
            <Form
            name="normal_login"
            className="login-form"
            initialValues={{
              remember: true,
            }}
            onFinish={props.onLoginFinish}
          >
            <Form.Item
              name="username"
              rules={[
                {
                  required: true,
                  message: 'Please input your Username!',
                },
              ]}
            >
              <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="Username" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[
                {
                  required: true,
                  message: 'Please input your Password!',
                },
              ]}
            >
              <Input
                prefix={<LockOutlined className="site-form-item-icon" />}
                type="password"
                placeholder="Password"
              />
            </Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>Remember me</Checkbox>
            </Form.Item>
    
            <Form.Item>
              <Button type="primary" htmlType="submit" className="login-form-button">
                Log in
              </Button>
            </Form.Item>
          </Form> 
      </Col>
      </Row>
      </div>)

return (
    <div>
    {loginPage}
    </div>
    );


}
import React from 'react';
import { Button, Col, Row, Form, Input, notification } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

export const RegisterPage = (props) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = React.useState(false);

    const onFinish = async (values) => {
        if (values.password !== values.confirmPassword) {
            notification.error({
                message: 'Error',
                description: 'Passwords do not match'
            });
            return;
        }

        setLoading(true);
        try {
            const res = await axiosInstance.post('/license/register', {
                username: values.username,
                email: values.email,
                password: values.password
            });
            
            notification.success({
                message: 'Success',
                description: 'Registration successful! You can now login.'
            });
            
            if (props.onRegisterSuccess) {
                props.onRegisterSuccess();
            }
        } catch (error) {
            notification.error({
                message: 'Registration Failed',
                description: error.response?.data?.error || 'Unable to register'
            });
        } finally {
            setLoading(false);
        }
    };

    const RegisterProps = {
        style: {
            width: '50%',
            height: "auto",
            marginTop: "10%",
            marginLeft: '25%',
            marginRight: '25%',
            marginBottom: "10%",
            paddingTop: '5%',
            paddingBottom: "5%",
            paddingLeft: '10%',
            paddingRight: '10%',
            backgroundColor: '#fff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }
    };

    return (
        <div {...RegisterProps}>
            <h2 style={{ textAlign: 'center', marginBottom: '24px' }}>Create Account</h2>
            <Form
                form={form}
                name="register"
                onFinish={onFinish}
                layout="vertical"
            >
                <Form.Item
                    name="username"
                    rules={[
                        { required: true, message: 'Please input your username!' },
                        { min: 3, message: 'Username must be at least 3 characters' }
                    ]}
                >
                    <Input 
                        prefix={<UserOutlined />} 
                        placeholder="Username" 
                        size="large"
                    />
                </Form.Item>

                <Form.Item
                    name="email"
                    rules={[
                        { type: 'email', message: 'Please enter a valid email!' }
                    ]}
                >
                    <Input 
                        prefix={<MailOutlined />} 
                        placeholder="Email (optional)" 
                        size="large"
                    />
                </Form.Item>

                <Form.Item
                    name="password"
                    rules={[
                        { required: true, message: 'Please input your password!' },
                        { min: 6, message: 'Password must be at least 6 characters' }
                    ]}
                >
                    <Input.Password 
                        prefix={<LockOutlined />} 
                        placeholder="Password" 
                        size="large"
                    />
                </Form.Item>

                <Form.Item
                    name="confirmPassword"
                    rules={[
                        { required: true, message: 'Please confirm your password!' }
                    ]}
                >
                    <Input.Password 
                        prefix={<LockOutlined />} 
                        placeholder="Confirm Password" 
                        size="large"
                    />
                </Form.Item>

                <Form.Item>
                    <Button 
                        type="primary" 
                        htmlType="submit" 
                        loading={loading}
                        block
                        size="large"
                    >
                        Register
                    </Button>
                </Form.Item>

                <div style={{ textAlign: 'center' }}>
                    Already have an account?{' '}
                    <a onClick={props.onBackToLogin} style={{ cursor: 'pointer' }}>
                        Login here
                    </a>
                </div>
            </Form>
        </div>
    );
};

export default RegisterPage;

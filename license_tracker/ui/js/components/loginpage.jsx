import { Button, Form, Input, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import React from 'react';


export const LoginPage = (props) => {

    const inputStyle = {
        height: 48,
        fontSize: 15,
        borderRadius: 10,
        backgroundColor: '#f4f6fa',
        border: '1.5px solid #e0e4ec',
    };

    const prefixStyle = {
        color: '#8c95a6',
        fontSize: 18,
        marginRight: 8,
    };

    return (
        <Form
            name="normal_login"
            initialValues={{ remember: true }}
            onFinish={props.onLoginFinish}
            size="large"
            style={{ width: '100%' }}
        >
            <Form.Item
                name="username"
                rules={[{ required: true, message: 'Please enter your username' }]}
                style={{ marginBottom: 20 }}
            >
                <Input
                    prefix={<UserOutlined style={prefixStyle} />}
                    placeholder="Username"
                    style={inputStyle}
                />
            </Form.Item>

            <Form.Item
                name="password"
                rules={[{ required: true, message: 'Please enter your password' }]}
                style={{ marginBottom: 16 }}
            >
                <Input.Password
                    prefix={<LockOutlined style={prefixStyle} />}
                    placeholder="Password"
                    style={inputStyle}
                />
            </Form.Item>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                    <Checkbox style={{ fontSize: 13, color: '#6b7280' }}>Remember me</Checkbox>
                </Form.Item>
            </div>

            <Form.Item style={{ marginBottom: 0 }}>
                <Button
                    type="primary"
                    htmlType="submit"
                    block
                    style={{
                        height: 48,
                        fontSize: 16,
                        fontWeight: 600,
                        borderRadius: 10,
                        background: 'linear-gradient(135deg, #1e3a5f 0%, #2d6cad 100%)',
                        border: 'none',
                        boxShadow: '0 4px 14px rgba(30, 58, 95, 0.35)',
                        letterSpacing: 0.5,
                    }}
                >
                    Sign In
                </Button>
            </Form.Item>
        </Form>
    );
}
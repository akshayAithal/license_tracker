import React, { useState, useEffect } from 'react';
import { 
    Button, Col, Row, Tabs, Layout, Menu, notification, Input, Select, 
    Spin, Switch, Table, Modal, Form, Card, Divider, Space, Tag, Popconfirm 
} from 'antd';
import { 
    UserOutlined, SettingOutlined, SafetyOutlined, PlusOutlined, 
    EditOutlined, DeleteOutlined, ReloadOutlined, CheckCircleOutlined,
    CloseCircleOutlined, LockOutlined, MailOutlined, RobotOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { Option } = Select;

const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

export const AdminPanel = (props) => {
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [settings, setSettings] = useState({});
    const [ldapSettings, setLdapSettings] = useState({});
    const [authSettings, setAuthSettings] = useState({});
    const [userModalVisible, setUserModalVisible] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [userForm] = Form.useForm();
    const [ldapForm] = Form.useForm();
    const [aiSettings, setAiSettings] = useState({});
    const [aiForm] = Form.useForm();

    useEffect(() => {
        fetchUsers();
        fetchSettings();
        fetchLdapSettings();
        fetchAuthSettings();
        fetchAiSettings();
    }, []);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const res = await axiosInstance.get('/api/admin/users');
            setUsers(res.data.users || []);
        } catch (error) {
            notification.error({
                message: 'Error',
                description: 'Failed to fetch users'
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchSettings = async () => {
        try {
            const res = await axiosInstance.get('/api/admin/settings');
            setSettings(res.data.settings || {});
        } catch (error) {
            console.error('Failed to fetch settings', error);
        }
    };

    const fetchLdapSettings = async () => {
        try {
            const res = await axiosInstance.get('/api/admin/ldap/settings');
            setLdapSettings(res.data.ldap_settings || {});
            ldapForm.setFieldsValue(res.data.ldap_settings || {});
        } catch (error) {
            console.error('Failed to fetch LDAP settings', error);
        }
    };

    const fetchAuthSettings = async () => {
        try {
            const res = await axiosInstance.get('/api/admin/auth/settings');
            setAuthSettings(res.data.auth_settings || {});
        } catch (error) {
            console.error('Failed to fetch auth settings', error);
        }
    };

    const handleCreateUser = () => {
        setEditingUser(null);
        userForm.resetFields();
        setUserModalVisible(true);
    };

    const handleEditUser = (user) => {
        setEditingUser(user);
        userForm.setFieldsValue({
            login: user.login,
            email: user.email,
            type: user.type,
            site_code: user.site_code,
            is_active: user.is_active
        });
        setUserModalVisible(true);
    };

    const handleDeleteUser = async (userId) => {
        try {
            await axiosInstance.delete(`/api/admin/users/${userId}`);
            notification.success({
                message: 'Success',
                description: 'User deleted successfully'
            });
            fetchUsers();
        } catch (error) {
            notification.error({
                message: 'Error',
                description: (error.response && error.response.data && error.response.data.error) || 'Failed to delete user'
            });
        }
    };

    const handleUserSubmit = async (values) => {
        setLoading(true);
        try {
            if (editingUser) {
                await axiosInstance.put(`/api/admin/users/${editingUser.id}`, values);
                notification.success({
                    message: 'Success',
                    description: 'User updated successfully'
                });
            } else {
                await axiosInstance.post('/api/admin/users', values);
                notification.success({
                    message: 'Success',
                    description: 'User created successfully'
                });
            }
            setUserModalVisible(false);
            fetchUsers();
        } catch (error) {
            notification.error({
                message: 'Error',
                description: (error.response && error.response.data && error.response.data.error) || 'Failed to save user'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleLdapSubmit = async (values) => {
        setLoading(true);
        try {
            await axiosInstance.put('/api/admin/ldap/settings', values);
            notification.success({
                message: 'Success',
                description: 'LDAP settings updated successfully'
            });
            fetchLdapSettings();
        } catch (error) {
            notification.error({
                message: 'Error',
                description: 'Failed to update LDAP settings'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleTestLdap = async () => {
        setLoading(true);
        try {
            const res = await axiosInstance.post('/api/admin/ldap/test');
            notification.success({
                message: 'Success',
                description: res.data.message || 'LDAP connection successful'
            });
        } catch (error) {
            notification.error({
                message: 'LDAP Test Failed',
                description: (error.response && error.response.data && error.response.data.error) || 'Connection failed'
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchAiSettings = async () => {
        try {
            var res = await axiosInstance.get('/api/admin/ai/settings');
            setAiSettings(res.data.ai_settings || {});
            aiForm.setFieldsValue(res.data.ai_settings || {});
        } catch (error) {
            console.error('Failed to fetch AI settings', error);
        }
    };

    const handleAiSubmit = async (values) => {
        setLoading(true);
        try {
            await axiosInstance.put('/api/admin/ai/settings', values);
            notification.success({
                message: 'Success',
                description: 'AI settings updated successfully'
            });
            fetchAiSettings();
        } catch (error) {
            notification.error({
                message: 'Error',
                description: 'Failed to update AI settings'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleTestAi = async () => {
        setLoading(true);
        try {
            var res = await axiosInstance.post('/api/admin/ai/test');
            notification.success({
                message: 'Success',
                description: res.data.message || 'AI connection successful'
            });
        } catch (error) {
            notification.error({
                message: 'AI Test Failed',
                description: (error.response && error.response.data && error.response.data.error) || 'Connection failed'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleAuthSettingChange = async (key, value) => {
        try {
            await axiosInstance.put('/api/admin/auth/settings', { [key]: value });
            notification.success({
                message: 'Success',
                description: 'Setting updated'
            });
            fetchAuthSettings();
        } catch (error) {
            notification.error({
                message: 'Error',
                description: 'Failed to update setting'
            });
        }
    };

    const userColumns = [
        {
            title: 'Login',
            dataIndex: 'login',
            key: 'login',
            sorter: (a, b) => a.login.localeCompare(b.login)
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email'
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (type) => (
                <Tag color={type === 'ADMIN' ? 'red' : 'blue'}>
                    {type}
                </Tag>
            )
        },
        {
            title: 'Site Code',
            dataIndex: 'site_code',
            key: 'site_code'
        },
        {
            title: 'Status',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (isActive) => (
                isActive ? 
                    <Tag icon={<CheckCircleOutlined />} color="success">Active</Tag> : 
                    <Tag icon={<CloseCircleOutlined />} color="error">Inactive</Tag>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button 
                        icon={<EditOutlined />} 
                        onClick={() => handleEditUser(record)}
                        size="small"
                    />
                    <Popconfirm
                        title="Are you sure you want to delete this user?"
                        onConfirm={() => handleDeleteUser(record.id)}
                        okText="Yes"
                        cancelText="No"
                    >
                        <Button 
                            icon={<DeleteOutlined />} 
                            danger
                            size="small"
                        />
                    </Popconfirm>
                </Space>
            )
        }
    ];

    const usersTab = (
        <div>
            <div style={{ marginBottom: 16 }}>
                <Button 
                    type="primary" 
                    icon={<PlusOutlined />}
                    onClick={handleCreateUser}
                >
                    Add User
                </Button>
                <Button 
                    icon={<ReloadOutlined />}
                    onClick={fetchUsers}
                    style={{ marginLeft: 8 }}
                >
                    Refresh
                </Button>
            </div>
            <Table 
                columns={userColumns} 
                dataSource={users}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />
        </div>
    );

    const authSettingsTab = (
        <div>
            <Card title="Authentication Settings" style={{ marginBottom: 16 }}>
                <Row gutter={[16, 16]}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <span style={{ marginRight: 16 }}>Enable LDAP Authentication:</span>
                            <Switch 
                                checked={authSettings.ldap_enabled}
                                onChange={(checked) => handleAuthSettingChange('ldap_enabled', checked)}
                            />
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <span style={{ marginRight: 16 }}>Enable Redmine/ERM Authentication:</span>
                            <Switch 
                                checked={authSettings.redmine_auth_enabled}
                                onChange={(checked) => handleAuthSettingChange('redmine_auth_enabled', checked)}
                            />
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <span style={{ marginRight: 16 }}>Allow User Registration:</span>
                            <Switch 
                                checked={authSettings.registration_enabled}
                                onChange={(checked) => handleAuthSettingChange('registration_enabled', checked)}
                            />
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <span style={{ marginRight: 16 }}>Authentication Mode:</span>
                            <Select 
                                value={authSettings.auth_mode}
                                onChange={(value) => handleAuthSettingChange('auth_mode', value)}
                                style={{ width: 150 }}
                            >
                                <Option value="local">Local</Option>
                                <Option value="ldap">LDAP</Option>
                                <Option value="redmine">Redmine</Option>
                            </Select>
                        </div>
                    </Col>
                </Row>
            </Card>
        </div>
    );

    const ldapSettingsTab = (
        <div>
            <Card title="LDAP Configuration" style={{ marginBottom: 16 }}>
                <Form
                    form={ldapForm}
                    layout="vertical"
                    onFinish={handleLdapSubmit}
                    initialValues={ldapSettings}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="ldap_server"
                                label="LDAP Server URL"
                                rules={[{ required: true, message: 'Please enter LDAP server URL' }]}
                            >
                                <Input placeholder="ldap://ldap.example.com" />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="ldap_port"
                                label="Port"
                            >
                                <Input placeholder="389" />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="ldap_use_ssl"
                                label="Use SSL"
                                valuePropName="checked"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="ldap_bind_dn"
                                label="Bind DN"
                            >
                                <Input placeholder="cn=admin,dc=example,dc=com" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="ldap_bind_password"
                                label="Bind Password"
                            >
                                <Input.Password placeholder="Password" />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={24}>
                            <Form.Item
                                name="ldap_base_dn"
                                label="Base DN"
                            >
                                <Input placeholder="ou=users,dc=example,dc=com" />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="ldap_user_filter"
                                label="User Filter"
                            >
                                <Input placeholder="(uid={username})" />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="ldap_username_attribute"
                                label="Username Attribute"
                            >
                                <Input placeholder="uid" />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="ldap_email_attribute"
                                label="Email Attribute"
                            >
                                <Input placeholder="mail" />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                Save LDAP Settings
                            </Button>
                            <Button onClick={handleTestLdap} loading={loading}>
                                Test Connection
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );

    const adminPanelStyle = {
        padding: '24px',
        marginTop: '80px',
        minHeight: '90vh',
        backgroundColor: '#f5f5f5'
    };

    return (
        <div style={adminPanelStyle}>
            <h1><SettingOutlined /> Admin Panel</h1>
            <Tabs defaultActiveKey="1">
                <TabPane 
                    tab={<span><UserOutlined /> User Management</span>} 
                    key="1"
                >
                    {usersTab}
                </TabPane>
                <TabPane 
                    tab={<span><SafetyOutlined /> Authentication</span>} 
                    key="2"
                >
                    {authSettingsTab}
                </TabPane>
                <TabPane 
                    tab={<span><LockOutlined /> LDAP Settings</span>} 
                    key="3"
                >
                    {ldapSettingsTab}
                </TabPane>
                <TabPane
                    tab={<span><RobotOutlined /> AI / Models</span>}
                    key="4"
                >
                    <Card title="AI / Model Configuration" style={{ marginBottom: 16 }}>
                        <Form
                            form={aiForm}
                            layout="vertical"
                            onFinish={handleAiSubmit}
                            initialValues={aiSettings}
                        >
                            <Row gutter={16}>
                                <Col span={8}>
                                    <Form.Item name="ai_provider" label="AI Provider">
                                        <Select placeholder="Select provider">
                                            <Option value="openai">OpenAI</Option>
                                            <Option value="local">Local Model</Option>
                                        </Select>
                                    </Form.Item>
                                </Col>
                            </Row>
                            <Divider>OpenAI Settings</Divider>
                            <Row gutter={16}>
                                <Col span={12}>
                                    <Form.Item name="openai_api_key" label="OpenAI API Key">
                                        <Input.Password placeholder="sk-..." />
                                    </Form.Item>
                                </Col>
                                <Col span={12}>
                                    <Form.Item name="openai_model" label="OpenAI Model">
                                        <Select placeholder="Select model">
                                            <Option value="gpt-4o-mini">GPT-4o Mini</Option>
                                            <Option value="gpt-4o">GPT-4o</Option>
                                            <Option value="gpt-4-turbo">GPT-4 Turbo</Option>
                                            <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
                                        </Select>
                                    </Form.Item>
                                </Col>
                            </Row>
                            <Divider>Local Model Settings</Divider>
                            <Row gutter={16}>
                                <Col span={12}>
                                    <Form.Item name="local_model_url" label="Local Model URL">
                                        <Input placeholder="http://localhost:11434" />
                                    </Form.Item>
                                </Col>
                                <Col span={6}>
                                    <Form.Item name="local_model_name" label="Model Name">
                                        <Input placeholder="llama3" />
                                    </Form.Item>
                                </Col>
                                <Col span={6}>
                                    <Form.Item name="local_model_api_key" label="API Key (optional)">
                                        <Input.Password placeholder="Token" />
                                    </Form.Item>
                                </Col>
                            </Row>
                            <Form.Item>
                                <Space>
                                    <Button type="primary" htmlType="submit" loading={loading}>
                                        Save AI Settings
                                    </Button>
                                    <Button onClick={handleTestAi} loading={loading}>
                                        Test Connection
                                    </Button>
                                </Space>
                            </Form.Item>
                        </Form>
                    </Card>
                </TabPane>
            </Tabs>

            <Modal
                title={editingUser ? 'Edit User' : 'Create User'}
                visible={userModalVisible}
                onCancel={() => setUserModalVisible(false)}
                footer={null}
                width={600}
            >
                <Form
                    form={userForm}
                    layout="vertical"
                    onFinish={handleUserSubmit}
                >
                    <Form.Item
                        name="login"
                        label="Username"
                        rules={[{ required: true, message: 'Please enter username' }]}
                    >
                        <Input 
                            prefix={<UserOutlined />} 
                            placeholder="Username"
                            disabled={!!editingUser}
                        />
                    </Form.Item>
                    <Form.Item
                        name="email"
                        label="Email"
                        rules={[{ type: 'email', message: 'Please enter a valid email' }]}
                    >
                        <Input prefix={<MailOutlined />} placeholder="Email" />
                    </Form.Item>
                    {!editingUser && (
                        <Form.Item
                            name="password"
                            label="Password"
                            rules={[
                                { required: !editingUser, message: 'Please enter password' },
                                { min: 6, message: 'Password must be at least 6 characters' }
                            ]}
                        >
                            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
                        </Form.Item>
                    )}
                    {editingUser && (
                        <Form.Item
                            name="password"
                            label="New Password (leave blank to keep current)"
                        >
                            <Input.Password prefix={<LockOutlined />} placeholder="New Password" />
                        </Form.Item>
                    )}
                    <Form.Item
                        name="type"
                        label="User Type"
                        rules={[{ required: true, message: 'Please select user type' }]}
                    >
                        <Select placeholder="Select user type">
                            <Option value="USER">User</Option>
                            <Option value="ADMIN">Admin</Option>
                        </Select>
                    </Form.Item>
                    <Form.Item
                        name="site_code"
                        label="Site Code"
                    >
                        <Input placeholder="Site Code" />
                    </Form.Item>
                    <Form.Item
                        name="is_active"
                        label="Active"
                        valuePropName="checked"
                        initialValue={true}
                    >
                        <Switch />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                {editingUser ? 'Update' : 'Create'}
                            </Button>
                            <Button onClick={() => setUserModalVisible(false)}>
                                Cancel
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default AdminPanel;

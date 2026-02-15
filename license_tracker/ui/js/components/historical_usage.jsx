import { Button } from 'antd';
import { Col } from 'antd';
import { Row } from 'antd';
import { Input } from 'antd';
import { Select, Table, Card, Statistic, notification, Spin } from 'antd';
import { HistoryOutlined, SearchOutlined } from '@ant-design/icons';
import React from 'react';
import { DatePicker, Space } from 'antd';
import axios from 'axios';
import dayjs from 'dayjs';
const { RangePicker } = DatePicker;
const { Option } = Select;

const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

export class HistoricalUsage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            application: undefined,
            region: undefined,
            version: undefined,
            fromDate: null,
            toDate: null,
            loading: false,
            usageData: [],
            summary: {},
            versions: [],
        };
    }

    componentDidMount() {
        this.fetchVersions();
    }

    fetchVersions() {
        axiosInstance.get("/license/get_versions")
            .then(res => {
                this.setState({ versions: res.data.versions || [] });
            })
            .catch(err => {
                console.log("Could not fetch versions:", err);
            });
    }

    selectApplication = (value) => {
        this.setState({ application: value });
    }

    selectRegion = (value) => {
        this.setState({ region: value });
    }

    selectVersion = (value) => {
        this.setState({ version: value });
    }

    onRangeChange = (dates, dateStrings) => {
        if (dates) {
            this.setState({
                fromDate: dateStrings[0],
                toDate: dateStrings[1],
            });
        } else {
            this.setState({
                fromDate: null,
                toDate: null,
            });
        }
    };

    getHistoricalUsage = () => {
        this.setState({ loading: true });
        axiosInstance.post("/license/get_historical_usage", {
            "from_date": this.state.fromDate,
            "to_date": this.state.toDate,
            "application": this.state.application,
            "region": this.state.region,
            "version": this.state.version,
        }).then((response) => {
            this.setState({
                loading: false,
                usageData: response.data.usage_data || [],
                summary: response.data.summary || {},
            });
        }).catch((error) => {
            console.log(error);
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Unable to get historical usage data`
            });
        }).finally(() => {
            this.setState({ loading: false });
        });
    }

    render() {
        const formPageStyle = {
            overflowY: 'auto',
            marginTop: "90px",
            paddingLeft: "24px",
            paddingRight: "24px",
            minHeight: "85vh",
            height: "90%",
            marginBottom: "2%",
            paddingBottom: "2%",
        };

        const columns = [
            {
                title: 'User',
                dataIndex: 'user',
                key: 'user',
                sorter: (a, b) => a.user.localeCompare(b.user),
            },
            {
                title: 'Application',
                dataIndex: 'application',
                key: 'application',
                filters: [...new Set(this.state.usageData.map(item => item.application))].map(app => ({ text: app, value: app })),
                onFilter: (value, record) => record.application === value,
            },
            {
                title: 'Region',
                dataIndex: 'region',
                key: 'region',
                filters: [...new Set(this.state.usageData.map(item => item.region))].map(reg => ({ text: reg, value: reg })),
                onFilter: (value, record) => record.region === value,
            },
            {
                title: 'Feature',
                dataIndex: 'feature',
                key: 'feature',
            },
            {
                title: 'Version',
                dataIndex: 'version',
                key: 'version',
                filters: [...new Set(this.state.usageData.map(item => item.version))].filter(v => v).map(ver => ({ text: ver, value: ver })),
                onFilter: (value, record) => record.version === value,
            },
            {
                title: 'Host',
                dataIndex: 'host',
                key: 'host',
            },
            {
                title: 'Licenses Used',
                dataIndex: 'license_used',
                key: 'license_used',
                sorter: (a, b) => a.license_used - b.license_used,
            },
            {
                title: 'Check Out',
                dataIndex: 'check_out',
                key: 'check_out',
                sorter: (a, b) => new Date(a.check_out) - new Date(b.check_out),
            },
            {
                title: 'Check In',
                dataIndex: 'check_in',
                key: 'check_in',
            },
            {
                title: 'Duration',
                dataIndex: 'spent_hours',
                key: 'spent_hours',
            },
        ];

        return (
            <div style={formPageStyle}>
                <h1 style={{ color: '#0d9488', marginBottom: '24px' }}>
                    <HistoryOutlined /> Historical Usage
                </h1>

                <Card style={{ marginBottom: '24px', background: '#f8f9fa' }}>
                    <Row gutter={16}>
                        <Col span={6}>
                            <Select
                                allowClear
                                style={{ width: '100%' }}
                                placeholder="Select Application"
                                onChange={this.selectApplication}
                            >
                                <Option value="altair">Altair</Option>
                                <Option value="msc">MSC</Option>
                                <Option value="pw">Particleworks</Option>
                                <Option value="ricardo">Ricardo</Option>
                                <Option value="masta">Masta</Option>
                                <Option value="rlm">RLM</Option>
                            </Select>
                        </Col>
                        <Col span={5}>
                            <Select
                                allowClear
                                style={{ width: '100%' }}
                                placeholder="Select Region"
                                onChange={this.selectRegion}
                            >
                                <Option value="eu">EU</Option>
                                <Option value="apac">APAC</Option>
                                <Option value="ame">AME</Option>
                                <Option value="cluster">Cluster</Option>
                            </Select>
                        </Col>
                        <Col span={5}>
                            <Select
                                allowClear
                                style={{ width: '100%' }}
                                placeholder="Select Version"
                                onChange={this.selectVersion}
                            >
                                {this.state.versions.map(ver => (
                                    <Option value={ver} key={ver}>{ver}</Option>
                                ))}
                            </Select>
                        </Col>
                        <Col span={6}>
                            <RangePicker
                                style={{ width: '100%' }}
                                presets={[
                                    { label: 'Last 7 Days', value: [dayjs().add(-7, 'd'), dayjs()] },
                                    { label: 'Last 30 Days', value: [dayjs().add(-30, 'd'), dayjs()] },
                                    { label: 'Last 90 Days', value: [dayjs().add(-90, 'd'), dayjs()] },
                                ]}
                                onChange={this.onRangeChange}
                            />
                        </Col>
                        <Col span={2}>
                            <Button
                                type="primary"
                                icon={<SearchOutlined />}
                                loading={this.state.loading}
                                onClick={this.getHistoricalUsage}
                                style={{ background: '#0d9488', borderColor: '#0d9488' }}
                            >
                                Search
                            </Button>
                        </Col>
                    </Row>
                </Card>

                {this.state.summary && Object.keys(this.state.summary).length > 0 && (
                    <Row gutter={16} style={{ marginBottom: '24px' }}>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Total Sessions"
                                    value={this.state.summary.total_sessions || 0}
                                    valueStyle={{ color: '#0d9488' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Unique Users"
                                    value={this.state.summary.unique_users || 0}
                                    valueStyle={{ color: '#0891b2' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Total Licenses Used"
                                    value={this.state.summary.total_licenses_used || 0}
                                    valueStyle={{ color: '#059669' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Avg Duration (hrs)"
                                    value={this.state.summary.avg_duration_hours || 0}
                                    precision={2}
                                    valueStyle={{ color: '#7c3aed' }}
                                />
                            </Card>
                        </Col>
                    </Row>
                )}

                {this.state.loading ? (
                    <Spin tip="Loading..." style={{ display: 'block', margin: '50px auto' }} />
                ) : (
                    <Table
                        dataSource={this.state.usageData}
                        columns={columns}
                        rowKey={(record, index) => index}
                        pagination={{ pageSize: 20, showSizeChanger: true }}
                        scroll={{ x: 1200 }}
                    />
                )}
            </div>
        );
    }
}

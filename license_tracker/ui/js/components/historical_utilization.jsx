import { Button } from 'antd';
import { Col } from 'antd';
import { Row } from 'antd';
import { Select, Table, Card, Statistic, Progress, notification, Spin } from 'antd';
import { PieChartOutlined, SearchOutlined } from '@ant-design/icons';
import React from 'react';
import { DatePicker, Space } from 'antd';
import axios from 'axios';
import dayjs from 'dayjs';
import ChartItem from './chart';
const { RangePicker } = DatePicker;
const { Option } = Select;

const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

export class HistoricalUtilization extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            application: undefined,
            region: undefined,
            version: undefined,
            fromDate: null,
            toDate: null,
            loading: false,
            utilizationData: [],
            versionBreakdown: [],
            summary: {},
            versions: [],
            chartLabels: [],
            chartSeries: [],
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

    getUtilizationData = () => {
        this.setState({ loading: true });
        axiosInstance.post("/license/get_utilization", {
            "from_date": this.state.fromDate,
            "to_date": this.state.toDate,
            "application": this.state.application,
            "region": this.state.region,
            "version": this.state.version,
        }).then((response) => {
            const versionBreakdown = response.data.version_breakdown || [];
            this.setState({
                loading: false,
                utilizationData: response.data.utilization_data || [],
                versionBreakdown: versionBreakdown,
                summary: response.data.summary || {},
                chartLabels: versionBreakdown.map(item => item.version || 'Unknown'),
                chartSeries: versionBreakdown.map(item => item.usage_count || 0),
            });
        }).catch((error) => {
            console.log(error);
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Unable to get utilization data`
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

        const utilizationColumns = [
            {
                title: 'Application',
                dataIndex: 'application',
                key: 'application',
                filters: [...new Set(this.state.utilizationData.map(item => item.application))].map(app => ({ text: app, value: app })),
                onFilter: (value, record) => record.application === value,
            },
            {
                title: 'Region',
                dataIndex: 'region',
                key: 'region',
                filters: [...new Set(this.state.utilizationData.map(item => item.region))].map(reg => ({ text: reg, value: reg })),
                onFilter: (value, record) => record.region === value,
            },
            {
                title: 'Feature',
                dataIndex: 'feature',
                key: 'feature',
            },
            {
                title: 'Total Licenses',
                dataIndex: 'total_license',
                key: 'total_license',
                sorter: (a, b) => a.total_license - b.total_license,
            },
            {
                title: 'Avg Used',
                dataIndex: 'avg_used',
                key: 'avg_used',
                sorter: (a, b) => a.avg_used - b.avg_used,
                render: (value) => value?.toFixed(1) || 0,
            },
            {
                title: 'Peak Used',
                dataIndex: 'peak_used',
                key: 'peak_used',
                sorter: (a, b) => a.peak_used - b.peak_used,
            },
            {
                title: 'Utilization %',
                dataIndex: 'utilization_percent',
                key: 'utilization_percent',
                sorter: (a, b) => a.utilization_percent - b.utilization_percent,
                render: (value) => (
                    <Progress
                        percent={value?.toFixed(1) || 0}
                        size="small"
                        strokeColor={value > 80 ? '#ff4d4f' : value > 50 ? '#faad14' : '#52c41a'}
                    />
                ),
            },
        ];

        const versionColumns = [
            {
                title: 'Version',
                dataIndex: 'version',
                key: 'version',
                render: (value) => value || 'Unknown',
            },
            {
                title: 'Usage Count',
                dataIndex: 'usage_count',
                key: 'usage_count',
                sorter: (a, b) => a.usage_count - b.usage_count,
            },
            {
                title: 'Unique Users',
                dataIndex: 'unique_users',
                key: 'unique_users',
                sorter: (a, b) => a.unique_users - b.unique_users,
            },
            {
                title: 'Total Hours',
                dataIndex: 'total_hours',
                key: 'total_hours',
                sorter: (a, b) => a.total_hours - b.total_hours,
                render: (value) => value?.toFixed(1) || 0,
            },
            {
                title: 'Share %',
                dataIndex: 'share_percent',
                key: 'share_percent',
                render: (value) => (
                    <Progress
                        percent={value?.toFixed(1) || 0}
                        size="small"
                        strokeColor="#0891b2"
                    />
                ),
            },
        ];

        return (
            <div style={formPageStyle}>
                <h1 style={{ color: '#0891b2', marginBottom: '24px' }}>
                    <PieChartOutlined /> License Utilization
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
                                onClick={this.getUtilizationData}
                                style={{ background: '#0891b2', borderColor: '#0891b2' }}
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
                                    title="Overall Utilization"
                                    value={this.state.summary.overall_utilization || 0}
                                    suffix="%"
                                    valueStyle={{ color: '#0d9488' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Peak Utilization"
                                    value={this.state.summary.peak_utilization || 0}
                                    suffix="%"
                                    valueStyle={{ color: '#dc2626' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Total Features"
                                    value={this.state.summary.total_features || 0}
                                    valueStyle={{ color: '#059669' }}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="Versions in Use"
                                    value={this.state.summary.versions_count || 0}
                                    valueStyle={{ color: '#7c3aed' }}
                                />
                            </Card>
                        </Col>
                    </Row>
                )}

                {this.state.loading ? (
                    <Spin tip="Loading..." style={{ display: 'block', margin: '50px auto' }} />
                ) : (
                    <>
                        <Row gutter={24}>
                            <Col span={16}>
                                <Card title="Feature Utilization" style={{ marginBottom: '24px' }}>
                                    <Table
                                        dataSource={this.state.utilizationData}
                                        columns={utilizationColumns}
                                        rowKey={(record, index) => index}
                                        pagination={{ pageSize: 10 }}
                                        scroll={{ x: 800 }}
                                    />
                                </Card>
                            </Col>
                            <Col span={8}>
                                {this.state.chartLabels.length > 0 && (
                                    <Card title="Version Distribution" style={{ marginBottom: '24px' }}>
                                        <ChartItem Labels={this.state.chartLabels} Series={this.state.chartSeries} />
                                    </Card>
                                )}
                            </Col>
                        </Row>

                        <Card title="Version Breakdown" style={{ marginBottom: '24px' }}>
                            <Table
                                dataSource={this.state.versionBreakdown}
                                columns={versionColumns}
                                rowKey={(record, index) => index}
                                pagination={{ pageSize: 10 }}
                            />
                        </Card>
                    </>
                )}
            </div>
        );
    }
}

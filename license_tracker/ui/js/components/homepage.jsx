import React from 'react';
import { Button, Col, Row, Spin, Table, Tag, Card, notification, Badge } from 'antd';
import { ThunderboltOutlined, DeleteOutlined, WarningOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';

var axiosInstance = axios.create({
  baseURL: window.location.href.split('?')[0],
});

function getUniqueFilters(data, key) {
  var seen = {};
  var filters = [];
  data.forEach(function(row) {
    var val = row[key];
    if (val && !seen[val]) {
      seen[val] = true;
      filters.push({ text: val, value: val });
    }
  });
  filters.sort(function(a, b) { return a.text < b.text ? -1 : 1; });
  return filters;
}

export class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      data: [],
      count: 0,
      expiryData: [],
      expiryLoading: false,
      generatingLiveData: false,
    };
    this.fetchData = this.fetchData.bind(this);
    this.fetchExpiryData = this.fetchExpiryData.bind(this);
    this.generateLiveData = this.generateLiveData.bind(this);
    this.clearLiveData = this.clearLiveData.bind(this);
  }

  componentDidMount() {
    this.fetchData();
    this.fetchExpiryData();
  }

  fetchData() {
    var self = this;
    this.setState({ loading: true });
    axiosInstance.get('/license/get_active_checkouts').then(function(res) {
      if (res.data.success) {
        self.setState({ data: res.data.data || [], count: res.data.count || 0, loading: false });
      } else {
        self.setState({ data: [], count: 0, loading: false });
      }
    }).catch(function(err) {
      notification['error']({
        message: 'Error',
        description: (err.response && err.response.data && err.response.data.error) || 'Failed to fetch license data',
        duration: 5,
      });
      self.setState({ data: [], count: 0, loading: false });
    });
  }

  fetchExpiryData() {
    var self = this;
    this.setState({ expiryLoading: true });
    axiosInstance.get('/api/dashboard/expiry_alerts').then(function(res) {
      if (res.data.success) {
        self.setState({ expiryData: res.data.expiry_details || [] });
      }
    }).catch(function() {}).finally(function() {
      self.setState({ expiryLoading: false });
    });
  }

  generateLiveData() {
    var self = this;
    this.setState({ generatingLiveData: true });
    axiosInstance.post('/license/generate_live_data', {
      duration_minutes: 60,
      num_events: 50,
    }).then(function(res) {
      notification['success']({
        message: 'Live Data Generated',
        description: res.data.message || 'Generated live data successfully',
        duration: 5,
      });
      self.fetchData();
    }).catch(function(error) {
      notification['error']({
        message: 'Error',
        description: (error.response && error.response.data && error.response.data.error) || 'Failed to generate live data',
        duration: 5,
      });
    }).finally(function() {
      self.setState({ generatingLiveData: false });
    });
  }

  clearLiveData() {
    var self = this;
    this.setState({ generatingLiveData: true });
    axiosInstance.post('/license/clear_live_data', {
      clear_history: false,
    }).then(function(res) {
      notification['success']({
        message: 'Live Data Cleared',
        description: 'Cleared active license records',
        duration: 5,
      });
      self.fetchData();
    }).catch(function(error) {
      notification['error']({
        message: 'Error',
        description: (error.response && error.response.data && error.response.data.error) || 'Failed to clear live data',
        duration: 5,
      });
    }).finally(function() {
      self.setState({ generatingLiveData: false });
    });
  }

  render() {
    var self = this;
    var isLoggedIn = this.props.isLoggedIn;
    var data = this.state.data;

    var columns = [
      {
        title: 'Application',
        dataIndex: 'application',
        key: 'application',
        filters: getUniqueFilters(data, 'application'),
        onFilter: function(value, record) { return record.application === value; },
        render: function(text) { return <Tag color="blue">{text}</Tag>; },
        width: 120,
      },
      {
        title: 'Region',
        dataIndex: 'region',
        key: 'region',
        filters: getUniqueFilters(data, 'region'),
        onFilter: function(value, record) { return record.region === value; },
        width: 90,
      },
      {
        title: 'User',
        dataIndex: 'user',
        key: 'user',
        filters: getUniqueFilters(data, 'user'),
        onFilter: function(value, record) { return record.user === value; },
        sorter: function(a, b) { return (a.user || '').localeCompare(b.user || ''); },
      },
      {
        title: 'Host',
        dataIndex: 'host',
        key: 'host',
      },
      {
        title: 'Feature',
        dataIndex: 'feature',
        key: 'feature',
        filters: getUniqueFilters(data, 'feature'),
        onFilter: function(value, record) { return record.feature === value; },
      },
      {
        title: 'Used',
        dataIndex: 'license_used',
        key: 'license_used',
        align: 'center',
        sorter: function(a, b) { return a.license_used - b.license_used; },
        width: 70,
      },
      {
        title: 'Total',
        dataIndex: 'total_license',
        key: 'total_license',
        align: 'center',
        sorter: function(a, b) { return a.total_license - b.total_license; },
        width: 70,
      },
      {
        title: 'Site',
        dataIndex: 'site_code',
        key: 'site_code',
        filters: getUniqueFilters(data, 'site_code'),
        onFilter: function(value, record) { return record.site_code === value; },
        width: 90,
      },
      {
        title: 'Checked Out',
        dataIndex: 'check_out',
        key: 'check_out',
        sorter: function(a, b) { return (a.check_out || '').localeCompare(b.check_out || ''); },
        width: 140,
      },
    ];

    var expiryColumns = [
      {
        title: 'Vendor', dataIndex: 'vendor', key: 'vendor',
        render: function(text) { return <Tag color="blue">{text}</Tag>; },
        filters: getUniqueFilters(this.state.expiryData, 'vendor'),
        onFilter: function(value, record) { return record.vendor === value; },
      },
      { title: 'Feature', dataIndex: 'feature', key: 'feature' },
      { title: 'Region', dataIndex: 'region', key: 'region' },
      { title: 'Total Licenses', dataIndex: 'total_license', key: 'total_license', align: 'center' },
      {
        title: 'Expiry Date', dataIndex: 'expiry_date', key: 'expiry_date',
        sorter: function(a, b) { return (a.expiry_date || '').localeCompare(b.expiry_date || ''); },
      },
      {
        title: 'Days Until', dataIndex: 'days_until', key: 'days_until', align: 'center',
        sorter: function(a, b) { return a.days_until - b.days_until; },
        render: function(days) {
          var color = '#52c41a';
          if (days <= 0) color = '#ff4d4f';
          else if (days <= 30) color = '#ff4d4f';
          else if (days <= 90) color = '#faad14';
          return <span style={{ color: color, fontWeight: 600 }}>{days}</span>;
        },
      },
      {
        title: 'Status', dataIndex: 'status', key: 'status',
        filters: [
          { text: 'Active', value: 'active' },
          { text: 'Warning', value: 'warning' },
          { text: 'Critical', value: 'critical' },
          { text: 'Expired', value: 'expired' },
        ],
        onFilter: function(value, record) { return record.status === value; },
        render: function(status) {
          var colors = { expired: 'red', critical: 'red', warning: 'orange', active: 'green' };
          return <Tag color={colors[status] || 'default'}>{(status || '').toUpperCase()}</Tag>;
        },
      },
    ];

    return (
      <div style={{ padding: '24px' }}>
        {/* Action Bar */}
        <Card
          style={{ marginBottom: 16, borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
          bodyStyle={{ padding: '12px 20px' }}
        >
          <Row gutter={[12, 12]} align="middle">
            <Col flex="auto">
              <span style={{ fontSize: 16, fontWeight: 600, color: '#1e3a5f' }}>
                Active License Checkouts
              </span>
              <Badge
                count={this.state.count}
                style={{ backgroundColor: this.state.count > 0 ? '#3b82f6' : '#d1d5db', marginLeft: 12 }}
                overflowCount={9999}
              />
            </Col>
            <Col>
              <Button
                type="primary"
                loading={this.state.loading}
                onClick={this.fetchData}
                style={{ borderRadius: 8 }}
              >
                <ReloadOutlined /> Refresh
              </Button>
            </Col>
            {isLoggedIn ? (
              <Col>
                <Button
                  loading={this.state.generatingLiveData}
                  onClick={this.generateLiveData}
                  style={{ backgroundColor: '#52c41a', borderColor: '#52c41a', color: 'white', borderRadius: 8 }}
                >
                  <ThunderboltOutlined /> Generate Live Data
                </Button>
              </Col>
            ) : null}
            {isLoggedIn ? (
              <Col>
                <Button
                  loading={this.state.generatingLiveData}
                  onClick={this.clearLiveData}
                  danger
                  style={{ borderRadius: 8 }}
                >
                  <DeleteOutlined /> Clear Live Data
                </Button>
              </Col>
            ) : null}
          </Row>
        </Card>

        {/* Main License Table */}
        <Card
          style={{ marginBottom: 16, borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
          bodyStyle={{ padding: 0 }}
        >
          <Table
            columns={columns}
            dataSource={data}
            loading={this.state.loading}
            pagination={{ pageSize: 20, showSizeChanger: true, pageSizeOptions: ['10', '20', '50', '100'], showTotal: function(total) { return 'Total ' + total + ' records'; } }}
            size="middle"
            rowKey={function(record) { return record.id; }}
            scroll={{ x: 900 }}
          />
        </Card>

        {/* Expiry View */}
        <Card
          title={
            <span style={{ fontSize: 16, fontWeight: 600 }}>
              <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
              License Expiry Overview
            </span>
          }
          style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
        >
          <Table
            columns={expiryColumns}
            dataSource={this.state.expiryData}
            loading={this.state.expiryLoading}
            pagination={{ pageSize: 10, showSizeChanger: true, pageSizeOptions: ['10', '25', '50'] }}
            size="middle"
            rowKey={function(record, idx) { return idx; }}
            scroll={{ x: true }}
          />
        </Card>
      </div>
    );
  }
}

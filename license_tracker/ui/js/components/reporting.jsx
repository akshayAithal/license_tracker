import React from 'react';
import { Tabs } from 'antd';
import { HistoricalUsage } from './historical_usage';
import { HistoricalUtilization } from './historical_utilization';

const { TabPane } = Tabs;

export class ReportingPage extends React.Component {
  render() {
    return (
      <div style={{ padding: '24px' }}>
        <Tabs defaultActiveKey="1" size="large">
          <TabPane tab="Historical Usage" key="1">
            <HistoricalUsage />
          </TabPane>
          <TabPane tab="Historical Utilization" key="2">
            <HistoricalUtilization />
          </TabPane>
        </Tabs>
      </div>
    );
  }
}

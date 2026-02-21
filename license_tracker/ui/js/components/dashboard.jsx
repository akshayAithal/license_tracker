import React from 'react';
import { Card, Row, Col, Progress } from 'antd';
import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

// Styles
const cardStyle = {
    borderRadius: '16px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
    border: 'none',
    height: '100%',
};

const cardTitleStyle = {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#333',
    letterSpacing: '1px',
    marginBottom: '16px',
};

export class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            realTimeUsage: [],
            expiryData: [],
            denialData: [],
            heatMapData: [],
        };
        this.fetchDashboardData = this.fetchDashboardData.bind(this);
    }

    componentDidMount() {
        this.fetchDashboardData();
    }

    fetchDashboardData() {
        // Simulated data - replace with actual API calls
        this.setState({
            realTimeUsage: [
                { name: 'ANSYS', usage: 85, color: 'linear-gradient(90deg, #1e3a5f, #3b82f6, #93c5fd)' },
                { name: 'ALTAIR', usage: 70, color: 'linear-gradient(90deg, #1e3a5f, #3b82f6, #93c5fd)' },
                { name: 'SIEMENS', usage: 45, color: 'linear-gradient(90deg, #6b7280, #9ca3af, #d1d5db)' },
                { name: 'DASSAULT', usage: 30, color: 'linear-gradient(90deg, #6b7280, #9ca3af)' },
                { name: 'HEXAGON', usage: 20, color: 'linear-gradient(90deg, #9ca3af, #d1d5db)' },
                { name: 'PTC', usage: 10, color: 'linear-gradient(90deg, #d1d5db, #e5e7eb)' },
            ],
            expiryData: [
                { month: 'JAN', count1: 3, count2: 4 },
                { month: 'FEB', count1: 5, count2: 6 },
                { month: 'MAR', count1: 4, count2: 7 },
                { month: 'APRL', count1: 6, count2: 5 },
                { month: 'MAY', count1: 7, count2: 3 },
            ],
            heatMapData: this.generateHeatMapData(),
        });
    }

    generateHeatMapData() {
        const data = [];
        for (let row = 0; row < 6; row++) {
            const rowData = [];
            for (let col = 0; col < 19; col++) {
                // Generate intensity based on position (simulating usage pattern)
                let intensity;
                if (col < 7) {
                    intensity = Math.random() * 0.3; // Low usage (blue)
                } else if (col < 12) {
                    intensity = 0.3 + Math.random() * 0.4; // Medium (yellow/orange)
                } else {
                    intensity = 0.7 + Math.random() * 0.3; // High usage (red)
                }
                rowData.push(intensity);
            }
            data.push(rowData);
        }
        return data;
    }

    getHeatMapColor(intensity) {
        // Blue to Yellow to Red gradient
        if (intensity < 0.33) {
            const ratio = intensity / 0.33;
            const r = Math.round(30 + ratio * 100);
            const g = Math.round(80 + ratio * 150);
            const b = Math.round(180 - ratio * 80);
            return `rgb(${r}, ${g}, ${b})`;
        } else if (intensity < 0.66) {
            const ratio = (intensity - 0.33) / 0.33;
            const r = Math.round(130 + ratio * 125);
            const g = Math.round(230 - ratio * 80);
            const b = Math.round(100 - ratio * 50);
            return `rgb(${r}, ${g}, ${b})`;
        } else {
            const ratio = (intensity - 0.66) / 0.34;
            const r = Math.round(255);
            const g = Math.round(150 - ratio * 100);
            const b = Math.round(50 - ratio * 30);
            return `rgb(${r}, ${g}, ${b})`;
        }
    }

    render() {
        const { realTimeUsage, expiryData, heatMapData } = this.state;

        return (
            <div style={{ padding: '24px', backgroundColor: '#e8ecf1', minHeight: 'calc(100vh - 60px)' }}>
                <h1 style={{ 
                    fontSize: '24px', 
                    fontWeight: 'bold', 
                    color: '#1e3a5f', 
                    marginBottom: '24px',
                    letterSpacing: '2px'
                }}>
                    GLOBAL OVERVIEW
                </h1>

                {/* Top Row - 3 Cards */}
                <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
                    {/* Expiry Alert Card */}
                    <Col xs={24} md={10}>
                        <Card style={cardStyle} bodyStyle={{ padding: '20px' }}>
                            <div style={cardTitleStyle}>EXPIRY ALERT</div>
                            <div style={{ display: 'flex', alignItems: 'flex-end', height: '150px', gap: '12px', justifyContent: 'center' }}>
                                {expiryData.map(function(item, index) {
                                    return (
                                        <div key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                                            <div style={{ display: 'flex', gap: '4px', alignItems: 'flex-end' }}>
                                                <div style={{
                                                    width: '20px',
                                                    height: (item.count1 * 15) + 'px',
                                                    backgroundColor: '#3b82f6',
                                                    borderRadius: '2px',
                                                }}></div>
                                                <div style={{
                                                    width: '20px',
                                                    height: (item.count2 * 15) + 'px',
                                                    backgroundColor: '#ef4444',
                                                    borderRadius: '2px',
                                                }}></div>
                                            </div>
                                            <span style={{ fontSize: '11px', color: '#666', fontWeight: '500' }}>{item.month}</span>
                                        </div>
                                    );
                                })}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px', fontSize: '10px', color: '#666' }}>
                                <span style={{ marginLeft: '0', transform: 'rotate(-90deg)', position: 'absolute', left: '-15px', top: '50%' }}>COUNTS</span>
                            </div>
                        </Card>
                    </Col>

                    {/* Real Time Usage Card */}
                    <Col xs={24} md={8}>
                        <Card style={cardStyle} bodyStyle={{ padding: '20px' }}>
                            <div style={cardTitleStyle}>REAL TIME USAGE</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {realTimeUsage.map(function(item, index) {
                                    return (
                                        <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            <span style={{ fontSize: '11px', color: '#333', width: '70px', fontWeight: '500' }}>{item.name}</span>
                                            <div style={{ 
                                                flex: 1, 
                                                height: '12px', 
                                                backgroundColor: '#e5e7eb', 
                                                borderRadius: '6px',
                                                overflow: 'hidden'
                                            }}>
                                                <div style={{
                                                    width: item.usage + '%',
                                                    height: '100%',
                                                    background: item.color,
                                                    borderRadius: '6px',
                                                }}></div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </Card>
                    </Col>

                    {/* Denials Card */}
                    <Col xs={24} md={6}>
                        <Card style={cardStyle} bodyStyle={{ padding: '20px' }}>
                            <div style={cardTitleStyle}>DENIALS</div>
                            <div style={{ 
                                display: 'flex', 
                                flexDirection: 'column', 
                                alignItems: 'center',
                                gap: '8px',
                                marginTop: '20px'
                            }}>
                                <div style={{
                                    width: '100%',
                                    height: '80px',
                                    background: 'linear-gradient(90deg, #3b82f6 0%, #22c55e 25%, #eab308 50%, #f97316 75%, #ef4444 100%)',
                                    borderRadius: '8px',
                                    position: 'relative',
                                }}>
                                    {/* Indicator lines */}
                                    {[0, 1, 2, 3, 4].map(function(i) {
                                        return (
                                            <div key={i} style={{
                                                position: 'absolute',
                                                left: (i * 25) + '%',
                                                top: 0,
                                                bottom: 0,
                                                width: '1px',
                                                backgroundColor: 'rgba(255,255,255,0.3)',
                                            }}></div>
                                        );
                                    })}
                                </div>
                                <span style={{ fontSize: '11px', color: '#666', fontWeight: '500' }}>30 DAYS</span>
                            </div>
                        </Card>
                    </Col>
                </Row>

                {/* Bottom Row - Heat Map */}
                <Row>
                    <Col span={24}>
                        <Card style={cardStyle} bodyStyle={{ padding: '24px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
                                <div style={{ 
                                    fontSize: '28px', 
                                    fontWeight: 'bold', 
                                    color: '#1e3a5f',
                                    letterSpacing: '3px',
                                    minWidth: '200px'
                                }}>
                                    HEAT MAP
                                </div>
                                <div style={{ flex: 1 }}>
                                    {/* Y-axis labels */}
                                    <div style={{ display: 'flex', gap: '2px' }}>
                                        <div style={{ width: '30px', display: 'flex', flexDirection: 'column', justifyContent: 'space-around', height: '150px' }}>
                                            {[6, 5, 4, 3, 2, 1].map(function(n) {
                                                return <span key={n} style={{ fontSize: '10px', color: '#666', textAlign: 'right' }}>{n}</span>;
                                            })}
                                        </div>
                                        {/* Heat Map Grid */}
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                            {heatMapData.map(function(row, rowIndex) {
                                                return (
                                                    <div key={rowIndex} style={{ display: 'flex', gap: '2px' }}>
                                                        {row.map(function(cell, colIndex) {
                                                            return (
                                                                <div
                                                                    key={colIndex}
                                                                    style={{
                                                                        width: '28px',
                                                                        height: '22px',
                                                                        backgroundColor: this.getHeatMapColor(cell),
                                                                        borderRadius: '2px',
                                                                    }}
                                                                ></div>
                                                            );
                                                        }.bind(this))}
                                                    </div>
                                                );
                                            }.bind(this))}
                                        </div>
                                    </div>
                                    {/* X-axis labels */}
                                    <div style={{ display: 'flex', marginLeft: '30px', marginTop: '4px' }}>
                                        {Array.from({ length: 19 }, function(_, i) { return i; }).map(function(n) {
                                            return (
                                                <span key={n} style={{ 
                                                    width: '30px', 
                                                    fontSize: '10px', 
                                                    color: '#666', 
                                                    textAlign: 'center' 
                                                }}>
                                                    {n}
                                                </span>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </Col>
                </Row>
            </div>
        );
    }
}

export default Dashboard;

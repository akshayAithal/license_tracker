import React from 'react';
import { Card, Row, Col, Button, notification, Spin, Tooltip, Badge, Select } from 'antd';
import { SaveOutlined, ReloadOutlined, LockOutlined, UnlockOutlined, DragOutlined } from '@ant-design/icons';
import axios from 'axios';

var Option = Select.Option;
var VENDORS = ['MSC', 'Altair', 'RLM', 'Particleworks'];

var axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

var cardStyle = {
    borderRadius: '16px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
    border: 'none',
    height: '100%',
    overflow: 'hidden',
};

var cardTitleStyle = {
    fontSize: '13px',
    fontWeight: 'bold',
    color: '#333',
    letterSpacing: '1px',
    marginBottom: '12px',
};

// Default widget order: [widgetId, colSpan (out of 24)]
var DEFAULT_WIDGETS = [
    { id: 'expiry_alert', span: 10, label: 'Expiry Alert' },
    { id: 'realtime_usage', span: 8, label: 'Real Time Usage' },
    { id: 'denials', span: 6, label: 'Denials' },
    { id: 'heatmap', span: 24, label: 'Heat Map' },
];

function getUsageBarColor(pct) {
    if (pct >= 80) return 'linear-gradient(90deg, #dc2626, #ef4444, #f87171)';
    if (pct >= 50) return 'linear-gradient(90deg, #1e3a5f, #3b82f6, #93c5fd)';
    return 'linear-gradient(90deg, #6b7280, #9ca3af, #d1d5db)';
}

function getHeatMapColor(pct) {
    if (pct <= 0) return '#e8ecf1';
    var intensity = Math.min(pct / 100, 1);
    if (intensity < 0.33) {
        var r = Math.round(30 + (intensity / 0.33) * 100);
        var g = Math.round(80 + (intensity / 0.33) * 150);
        var b = Math.round(180 - (intensity / 0.33) * 80);
        return 'rgb(' + r + ',' + g + ',' + b + ')';
    } else if (intensity < 0.66) {
        var ratio = (intensity - 0.33) / 0.33;
        return 'rgb(' + Math.round(130 + ratio * 125) + ',' + Math.round(230 - ratio * 80) + ',' + Math.round(100 - ratio * 50) + ')';
    } else {
        var ratio2 = (intensity - 0.66) / 0.34;
        return 'rgb(255,' + Math.round(150 - ratio2 * 100) + ',' + Math.round(50 - ratio2 * 30) + ')';
    }
}

export class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: true,
            layoutLocked: true,
            widgets: DEFAULT_WIDGETS.map(function(w) { return Object.assign({}, w); }),
            draggedIdx: null,
            dragOverIdx: null,
            realTimeUsage: [],
            expiryMonthly: [],
            expiryDetails: [],
            totalCritical: 0,
            expiryVendor: null,
            heatmapVendor: null,
            denialData: {},
            heatmapData: [],
            summary: {},
            refreshInterval: null,
        };
        this.fetchAll = this.fetchAll.bind(this);
        this.saveLayout = this.saveLayout.bind(this);
        this.toggleLock = this.toggleLock.bind(this);
    }

    componentDidMount() {
        this.fetchLayout();
        this.fetchAll();
        var self = this;
        var interval = setInterval(function() { self.fetchAll(); }, 60000);
        this.setState({ refreshInterval: interval });
    }

    componentWillUnmount() {
        if (this.state.refreshInterval) clearInterval(this.state.refreshInterval);
    }

    fetchAll() {
        this.fetchRealtimeUsage();
        this.fetchExpiryAlerts();
        this.fetchDenials();
        this.fetchHeatmap();
        this.fetchSummary();
    }

    fetchLayout() {
        var self = this;
        axiosInstance.get('/api/dashboard/layout').then(function(res) {
            if (res.data.success && res.data.layout) {
                try {
                    var parsed = JSON.parse(res.data.layout);
                    if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].id) {
                        self.setState({ widgets: parsed });
                    }
                } catch (e) { /* use default */ }
            }
        }).catch(function() {});
    }

    fetchRealtimeUsage() {
        var self = this;
        axiosInstance.get('/api/dashboard/realtime_usage').then(function(res) {
            if (res.data.success) self.setState({ realTimeUsage: res.data.data, loading: false });
        }).catch(function() { self.setState({ loading: false }); });
    }

    fetchExpiryAlerts(vendor) {
        var self = this;
        var url = '/api/dashboard/expiry_alerts';
        var v = vendor !== undefined ? vendor : this.state.expiryVendor;
        if (v) url += '?application=' + encodeURIComponent(v);
        axiosInstance.get(url).then(function(res) {
            if (res.data.success) {
                self.setState({
                    expiryMonthly: res.data.monthly || [],
                    expiryDetails: res.data.expiry_details || [],
                    totalCritical: res.data.total_critical || 0,
                });
            }
        }).catch(function() {});
    }

    fetchDenials() {
        var self = this;
        axiosInstance.get('/api/dashboard/denials?days=30').then(function(res) {
            if (res.data.success) self.setState({ denialData: res.data });
        }).catch(function() {});
    }

    fetchHeatmap(vendor) {
        var self = this;
        var url = '/api/dashboard/heatmap?days=7';
        var v = vendor !== undefined ? vendor : this.state.heatmapVendor;
        if (v) url += '&application=' + encodeURIComponent(v);
        axiosInstance.get(url).then(function(res) {
            if (res.data.success) self.setState({ heatmapData: res.data.heatmap || [] });
        }).catch(function() {});
    }

    onExpiryVendorChange(value) {
        this.setState({ expiryVendor: value || null });
        this.fetchExpiryAlerts(value || null);
    }

    onHeatmapVendorChange(value) {
        this.setState({ heatmapVendor: value || null });
        this.fetchHeatmap(value || null);
    }

    fetchSummary() {
        var self = this;
        axiosInstance.get('/api/dashboard/summary').then(function(res) {
            if (res.data.success) self.setState({ summary: res.data });
        }).catch(function() {});
    }

    saveLayout() {
        var layoutJson = JSON.stringify(this.state.widgets);
        axiosInstance.post('/api/dashboard/layout', {
            layout: layoutJson, layout_name: 'default',
        }).then(function(res) {
            if (res.data.success) {
                notification['success']({ message: 'Layout Saved', description: 'Your dashboard layout has been saved.', duration: 3 });
            } else {
                notification['warning']({ message: 'Login Required', description: 'Log in to save your layout.', duration: 3 });
            }
        }).catch(function() {
            notification['warning']({ message: 'Login Required', description: 'Log in to save your dashboard layout.', duration: 3 });
        });
    }

    toggleLock() { this.setState({ layoutLocked: !this.state.layoutLocked }); }

    onDragStart(idx, e) {
        if (this.state.layoutLocked) { e.preventDefault(); return; }
        this.setState({ draggedIdx: idx });
        e.dataTransfer.effectAllowed = 'move';
    }

    onDragOver(idx, e) {
        e.preventDefault();
        if (this.state.draggedIdx === null || this.state.draggedIdx === idx) return;
        this.setState({ dragOverIdx: idx });
    }

    onDrop(idx, e) {
        e.preventDefault();
        var from = this.state.draggedIdx;
        if (from === null || from === idx) { this.setState({ draggedIdx: null, dragOverIdx: null }); return; }
        var widgets = this.state.widgets.slice();
        var item = widgets.splice(from, 1)[0];
        widgets.splice(idx, 0, item);
        this.setState({ widgets: widgets, draggedIdx: null, dragOverIdx: null });
    }

    onDragEnd() { this.setState({ draggedIdx: null, dragOverIdx: null }); }

    renderExpiryAlert() {
        var self = this;
        var data = this.state.expiryMonthly;
        var details = this.state.expiryDetails;
        var maxVal = 1;
        if (data && data.length > 0) {
            data.forEach(function(item) {
                if (item.expiring > maxVal) maxVal = item.expiring;
                if (item.critical > maxVal) maxVal = item.critical;
            });
        }

        var vendorFilter = React.createElement(Select, {
            allowClear: true, placeholder: 'All Vendors', size: 'small',
            style: { width: 140, fontSize: 11 },
            value: this.state.expiryVendor || undefined,
            onChange: function(v) { self.onExpiryVendorChange(v); },
        }, VENDORS.map(function(v) { return React.createElement(Option, { key: v, value: v }, v); }));

        var statusColor = { critical: '#ef4444', warning: '#f59e0b', expired: '#9ca3af', active: '#22c55e' };

        return React.createElement('div', { style: { padding: '16px 20px', height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' } },
            // Header row
            React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8, flexShrink: 0 } },
                React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 10 } },
                    React.createElement('span', { style: cardTitleStyle }, 'EXPIRY ALERT'),
                    this.state.totalCritical > 0 ? React.createElement(Badge, { count: this.state.totalCritical, style: { backgroundColor: '#ef4444' } }) : null
                ),
                vendorFilter
            ),
            // Chart row
            data && data.length > 0 ? React.createElement('div', { style: { flexShrink: 0 } },
                React.createElement('div', { style: { display: 'flex', gap: 4, marginBottom: 6, fontSize: 10, color: '#666' } },
                    React.createElement('span', { style: { display: 'inline-block', width: 10, height: 10, backgroundColor: '#3b82f6', borderRadius: 2, marginRight: 3 } }), 'Expiring',
                    React.createElement('span', { style: { display: 'inline-block', width: 10, height: 10, backgroundColor: '#ef4444', borderRadius: 2, marginLeft: 10, marginRight: 3 } }), 'Critical'
                ),
                React.createElement('div', { style: { display: 'flex', alignItems: 'flex-end', gap: 8, justifyContent: 'center', paddingBottom: 8, height: 100 } },
                    data.slice(0, 8).map(function(item, idx) {
                        var h1 = Math.max(8, (item.expiring / maxVal) * 80);
                        var h2 = Math.max(8, (item.critical / maxVal) * 80);
                        return React.createElement('div', { key: idx, style: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 } },
                            React.createElement('div', { style: { display: 'flex', gap: 3, alignItems: 'flex-end' } },
                                React.createElement(Tooltip, { title: item.expiring + ' expiring' },
                                    React.createElement('div', { style: { width: 16, height: h1, backgroundColor: '#3b82f6', borderRadius: 2, transition: 'height 0.5s' } })
                                ),
                                React.createElement(Tooltip, { title: item.critical + ' critical' },
                                    React.createElement('div', { style: { width: 16, height: h2, backgroundColor: '#ef4444', borderRadius: 2, transition: 'height 0.5s' } })
                                )
                            ),
                            React.createElement('span', { style: { fontSize: 9, color: '#666', fontWeight: 500 } }, item.month)
                        );
                    })
                )
            ) : null,
            // Expiry details table
            React.createElement('div', { style: { flex: 1, overflow: 'auto', marginTop: 6, borderTop: '1px solid #e5e7eb', paddingTop: 6 } },
                details && details.length > 0
                    ? React.createElement('div', null,
                        React.createElement('div', { style: { display: 'flex', fontSize: 10, fontWeight: 600, color: '#555', borderBottom: '1px solid #eee', paddingBottom: 4, marginBottom: 4 } },
                            React.createElement('span', { style: { width: '22%' } }, 'Vendor'),
                            React.createElement('span', { style: { width: '22%' } }, 'Feature'),
                            React.createElement('span', { style: { width: '22%' } }, 'Expiry Date'),
                            React.createElement('span', { style: { width: '16%', textAlign: 'center' } }, 'Days'),
                            React.createElement('span', { style: { width: '18%', textAlign: 'center' } }, 'Status')
                        ),
                        details.map(function(d, idx) {
                            return React.createElement('div', { key: idx, style: { display: 'flex', fontSize: 10, color: '#444', padding: '3px 0', borderBottom: '1px solid #f3f4f6' } },
                                React.createElement('span', { style: { width: '22%', fontWeight: 500 } }, d.vendor),
                                React.createElement('span', { style: { width: '22%' } }, d.feature),
                                React.createElement('span', { style: { width: '22%' } }, d.expiry_date),
                                React.createElement('span', { style: { width: '16%', textAlign: 'center' } }, d.days_until),
                                React.createElement('span', { style: { width: '18%', textAlign: 'center', color: statusColor[d.status] || '#666', fontWeight: 600, textTransform: 'uppercase' } }, d.status)
                            );
                        })
                    )
                    : React.createElement('div', { style: { color: '#999', textAlign: 'center', paddingTop: 16, fontSize: 11 } }, 'No expiry details available')
            )
        );
    }

    renderRealtimeUsage() {
        var data = this.state.realTimeUsage;
        if (!data || data.length === 0) return React.createElement('div', { style: { color: '#999', textAlign: 'center', paddingTop: '40px' } }, 'No usage data yet');
        return React.createElement('div', { style: { padding: '16px 20px', height: '100%', display: 'flex', flexDirection: 'column' } },
            React.createElement('div', { style: cardTitleStyle }, 'REAL TIME USAGE'),
            React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 10, flex: 1, justifyContent: 'center' } },
                data.map(function(item, idx) {
                    return React.createElement('div', { key: idx, style: { display: 'flex', alignItems: 'center', gap: 10 } },
                        React.createElement('span', { style: { fontSize: 11, color: '#333', width: 90, fontWeight: 500, textTransform: 'uppercase' } }, item.name),
                        React.createElement('div', { style: { flex: 1, height: 14, backgroundColor: '#e5e7eb', borderRadius: 7, overflow: 'hidden', position: 'relative' } },
                            React.createElement('div', { style: { width: item.usage + '%', height: '100%', background: getUsageBarColor(item.usage), borderRadius: 7, transition: 'width 0.8s ease' } }),
                            React.createElement('span', { style: { position: 'absolute', right: 6, top: 0, lineHeight: '14px', fontSize: 9, color: '#555', fontWeight: 600 } }, item.usage + '%')
                        ),
                        React.createElement(Tooltip, { title: item.used + ' / ' + item.total + ' licenses' },
                            React.createElement('span', { style: { fontSize: 10, color: '#888', width: 55, textAlign: 'right' } }, item.used + '/' + item.total)
                        )
                    );
                })
            )
        );
    }

    renderDenials() {
        var data = this.state.denialData;
        var total = data.total_denials || 0;
        var topFeatures = data.top_features || [];
        return React.createElement('div', { style: { padding: '16px 20px', height: '100%', display: 'flex', flexDirection: 'column' } },
            React.createElement('div', { style: cardTitleStyle }, 'DENIALS'),
            React.createElement('div', { style: { textAlign: 'center', marginBottom: 12 } },
                React.createElement('div', { style: { fontSize: 36, fontWeight: 'bold', color: total > 50 ? '#ef4444' : total > 20 ? '#f59e0b' : '#22c55e' } }, total),
                React.createElement('div', { style: { fontSize: 11, color: '#666' } }, 'Last 30 days')
            ),
            React.createElement('div', { style: { flex: 1, overflow: 'auto' } },
                topFeatures.slice(0, 5).map(function(item, idx) {
                    var maxC = topFeatures.length > 0 ? topFeatures[0].count : 1;
                    var pct = (item.count / maxC) * 100;
                    return React.createElement('div', { key: idx, style: { marginBottom: 6 } },
                        React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#555', marginBottom: 2 } },
                            React.createElement('span', null, item.app + ' - ' + item.feature),
                            React.createElement('span', { style: { fontWeight: 600 } }, item.count)
                        ),
                        React.createElement('div', { style: { height: 6, backgroundColor: '#e5e7eb', borderRadius: 3, overflow: 'hidden' } },
                            React.createElement('div', { style: { width: pct + '%', height: '100%', backgroundColor: '#ef4444', borderRadius: 3, transition: 'width 0.5s' } })
                        )
                    );
                })
            )
        );
    }

    renderHeatmap() {
        var self = this;
        var data = this.state.heatmapData;

        var vendorFilter = React.createElement(Select, {
            allowClear: true, placeholder: 'All Vendors', size: 'small',
            style: { width: 150 },
            value: this.state.heatmapVendor || undefined,
            onChange: function(v) { self.onHeatmapVendorChange(v); },
        }, VENDORS.map(function(v) { return React.createElement(Option, { key: v, value: v }, v); }));

        if (!data || data.length === 0) return React.createElement('div', { style: { padding: '16px 20px', display: 'flex', flexDirection: 'column' } },
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 20, marginBottom: 12 } },
                React.createElement('div', { style: { fontSize: 24, fontWeight: 'bold', color: '#1e3a5f', letterSpacing: 3 } }, 'HEAT MAP'),
                vendorFilter
            ),
            React.createElement('div', { style: { color: '#999', textAlign: 'center', paddingTop: 30 } }, 'No heatmap data yet')
        );

        return React.createElement('div', { style: { padding: '16px 20px', height: '100%', display: 'flex', flexDirection: 'column' } },
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 20, marginBottom: 12 } },
                React.createElement('div', { style: { fontSize: 24, fontWeight: 'bold', color: '#1e3a5f', letterSpacing: 3 } }, 'HEAT MAP'),
                vendorFilter,
                React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#666' } },
                    React.createElement('span', null, 'Low'),
                    [0, 20, 40, 60, 80, 100].map(function(v) {
                        return React.createElement('div', { key: v, style: { width: 14, height: 10, backgroundColor: getHeatMapColor(v), borderRadius: 1 } });
                    }),
                    React.createElement('span', null, 'High')
                )
            ),
            React.createElement('div', { style: { flex: 1, display: 'flex', gap: 2 } },
                React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 2, paddingTop: 2 } },
                    data.map(function(row, ri) {
                        return React.createElement('div', { key: ri, style: { height: 22, lineHeight: '22px', fontSize: 10, color: '#666', textAlign: 'right', paddingRight: 6, width: 36 } }, row.day);
                    })
                ),
                React.createElement('div', { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 2, overflow: 'auto' } },
                    data.map(function(row, ri) {
                        return React.createElement('div', { key: ri, style: { display: 'flex', gap: 2 } },
                            row.hours.map(function(val, ci) {
                                return React.createElement(Tooltip, { key: ci, title: row.day + ' ' + ci + ':00 - ' + Math.round(val) + '% usage' },
                                    React.createElement('div', { style: { flex: 1, minWidth: 18, height: 22, backgroundColor: getHeatMapColor(val), borderRadius: 2, transition: 'background-color 0.3s' } })
                                );
                            })
                        );
                    }),
                    React.createElement('div', { style: { display: 'flex', gap: 2, paddingTop: 4 } },
                        Array.from({ length: 24 }, function(_, i) { return i; }).map(function(h) {
                            return React.createElement('div', { key: h, style: { flex: 1, minWidth: 18, fontSize: 9, color: '#888', textAlign: 'center' } }, h);
                        })
                    )
                )
            )
        );
    }

    render() {
        var self = this;
        var summary = this.state.summary;

        if (this.state.loading) {
            return React.createElement('div', { style: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' } },
                React.createElement(Spin, { size: 'large', tip: 'Loading dashboard...' })
            );
        }

        var widgetRenderers = {
            'expiry_alert': this.renderExpiryAlert.bind(this),
            'realtime_usage': this.renderRealtimeUsage.bind(this),
            'denials': this.renderDenials.bind(this),
            'heatmap': this.renderHeatmap.bind(this),
        };

        var locked = this.state.layoutLocked;

        return React.createElement('div', { style: { padding: '24px', backgroundColor: '#e8ecf1', minHeight: 'calc(100vh - 60px)' } },
            // Header
            React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 } },
                React.createElement('div', null,
                    React.createElement('h1', { style: { fontSize: 24, fontWeight: 'bold', color: '#1e3a5f', margin: 0, letterSpacing: 2 } }, 'GLOBAL OVERVIEW'),
                    React.createElement('div', { style: { display: 'flex', gap: 24, marginTop: 8 } },
                        React.createElement('span', { style: { fontSize: 12, color: '#666' } }, 'Active Licenses: ', React.createElement('strong', null, summary.active_licenses || 0)),
                        React.createElement('span', { style: { fontSize: 12, color: '#666' } }, 'Users Today: ', React.createElement('strong', null, summary.active_users || 0)),
                        React.createElement('span', { style: { fontSize: 12, color: summary.today_denials > 0 ? '#ef4444' : '#666' } }, 'Denials Today: ', React.createElement('strong', null, summary.today_denials || 0))
                    )
                ),
                React.createElement('div', { style: { display: 'flex', gap: 8 } },
                    React.createElement(Tooltip, { title: locked ? 'Unlock to rearrange' : 'Lock layout' },
                        React.createElement(Button, {
                            icon: locked ? React.createElement(LockOutlined) : React.createElement(UnlockOutlined),
                            onClick: this.toggleLock, type: locked ? 'default' : 'dashed',
                        })
                    ),
                    React.createElement(Tooltip, { title: 'Refresh data' },
                        React.createElement(Button, { icon: React.createElement(ReloadOutlined), onClick: this.fetchAll })
                    ),
                    React.createElement(Tooltip, { title: 'Save layout (login required)' },
                        React.createElement(Button, { type: 'primary', icon: React.createElement(SaveOutlined), onClick: this.saveLayout }, 'Save Layout')
                    )
                )
            ),
            !locked ? React.createElement('div', { style: { fontSize: 11, color: '#888', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 } },
                React.createElement(DragOutlined), 'Drag widgets to rearrange. Click the lock icon when done.'
            ) : null,
            // Widget grid
            React.createElement(Row, { gutter: [20, 20] },
                this.state.widgets.map(function(w, idx) {
                    var renderFn = widgetRenderers[w.id];
                    var isDragOver = self.state.dragOverIdx === idx;
                    return React.createElement(Col, {
                        key: w.id,
                        xs: 24,
                        md: w.span === 24 ? 24 : w.span,
                        draggable: !locked,
                        onDragStart: function(e) { self.onDragStart(idx, e); },
                        onDragOver: function(e) { self.onDragOver(idx, e); },
                        onDrop: function(e) { self.onDrop(idx, e); },
                        onDragEnd: function() { self.onDragEnd(); },
                        style: { transition: 'transform 0.2s' },
                    },
                        React.createElement(Card, {
                            style: Object.assign({}, cardStyle, isDragOver ? { border: '2px dashed #3b82f6', boxShadow: '0 0 12px rgba(59,130,246,0.3)' } : {}),
                            bodyStyle: { padding: 0, height: '100%', minHeight: w.span === 24 ? 220 : 260 },
                        },
                            renderFn ? renderFn() : React.createElement('div', null, 'Widget: ' + w.id)
                        )
                    );
                })
            )
        );
    }
}

export default Dashboard;

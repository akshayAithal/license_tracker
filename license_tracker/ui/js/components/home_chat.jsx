import React from 'react';
import { Input, Spin, Table, Card, Tag, Typography } from 'antd';
import { SendOutlined, SearchOutlined } from '@ant-design/icons';
import axios from 'axios';

var axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

export class HomeChatPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            inputValue: '',
            loading: false,
            result: null,
        };
        this.inputRef = React.createRef();
        this.handleSend = this.handleSend.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    componentDidMount() {
        if (this.inputRef.current) {
            this.inputRef.current.focus();
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSend();
        }
    }

    handleSend() {
        var query = this.state.inputValue.trim();
        if (!query || this.state.loading) return;

        var self = this;
        this.setState({ loading: true, result: null });

        axiosInstance.post('/api/chat/query', { query: query })
            .then(function(res) {
                self.setState({ loading: false, result: res.data });
            })
            .catch(function(err) {
                var errorMsg = 'Something went wrong. Please try again.';
                if (err.response && err.response.data && err.response.data.error) {
                    errorMsg = err.response.data.error;
                }
                self.setState({
                    loading: false,
                    result: { type: 'error', summary: errorMsg },
                });
            });
    }

    renderResult() {
        var result = this.state.result;
        if (!result) return null;

        var resultStyle = {
            marginTop: 32,
            width: '100%',
            maxWidth: 800,
            textAlign: 'left',
        };

        if (result.type === 'error') {
            return (
                <div style={resultStyle}>
                    <Card style={{ borderRadius: 12, borderColor: '#ffa39e', background: '#fff2f0' }}>
                        <span style={{ color: '#cf1322' }}>{result.summary}</span>
                    </Card>
                </div>
            );
        }

        // Build table columns from result data
        var tableNode = null;
        if (result.columns && result.data && result.data.length > 0) {
            var columns = result.columns.map(function(col) {
                return {
                    title: col.replace(/_/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); }),
                    dataIndex: col,
                    key: col,
                    ellipsis: true,
                };
            });
            tableNode = (
                <Table
                    columns={columns}
                    dataSource={result.data.map(function(row, idx) {
                        return Object.assign({}, row, { key: idx });
                    })}
                    size="small"
                    pagination={{ pageSize: 8 }}
                    style={{ marginTop: 16 }}
                    scroll={{ x: true }}
                />
            );
        }

        // Stats cards
        var statsNode = null;
        if (result.stats && result.stats.length > 0) {
            statsNode = (
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 16 }}>
                    {result.stats.map(function(stat, idx) {
                        return (
                            <Card key={idx} size="small" style={{ borderRadius: 10, minWidth: 120, textAlign: 'center' }}>
                                <div style={{ fontSize: 22, fontWeight: 700, color: '#1e3a5f' }}>{stat.value}</div>
                                <div style={{ fontSize: 12, color: '#6b7280' }}>{stat.label}</div>
                            </Card>
                        );
                    })}
                </div>
            );
        }

        return (
            <div style={resultStyle}>
                <Card style={{ borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
                    {result.title ? (
                        <div style={{ fontSize: 16, fontWeight: 600, color: '#1e3a5f', marginBottom: 8 }}>
                            {result.title}
                        </div>
                    ) : null}
                    {result.summary ? (
                        <div style={{ fontSize: 14, color: '#374151', lineHeight: 1.6 }}>
                            {result.summary}
                        </div>
                    ) : null}
                    {statsNode}
                    {tableNode}
                </Card>
            </div>
        );
    }

    render() {
        var self = this;
        var hasResult = !!this.state.result;

        return (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: hasResult ? 'flex-start' : 'center',
                minHeight: 'calc(100vh - 56px)',
                padding: '40px 24px',
                transition: 'all 0.3s ease',
            }}>
                {/* Title area - only show when no result */}
                {!hasResult ? (
                    <div style={{ textAlign: 'center', marginBottom: 40 }}>
                        <div style={{
                            width: 56, height: 56, margin: '0 auto 16px',
                            borderRadius: 14,
                            background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 4px 14px rgba(30, 58, 95, 0.25)',
                        }}>
                            <SearchOutlined style={{ fontSize: 26, color: '#fff' }} />
                        </div>
                        <div style={{ fontSize: 22, fontWeight: 700, color: '#1e3a5f' }}>
                            What would you like to know?
                        </div>
                        <div style={{ fontSize: 14, color: '#6b7280', marginTop: 6 }}>
                            Ask about licenses, usage, denials, or any license data
                        </div>
                    </div>
                ) : null}

                {/* Input box */}
                <div style={{
                    width: '100%',
                    maxWidth: 650,
                    position: 'relative',
                }}>
                    <Input
                        ref={this.inputRef}
                        size="large"
                        placeholder="Ask a question about license data..."
                        value={this.state.inputValue}
                        onChange={function(e) { self.setState({ inputValue: e.target.value }); }}
                        onKeyDown={this.handleKeyDown}
                        disabled={this.state.loading}
                        suffix={
                            this.state.loading ? (
                                <Spin size="small" />
                            ) : (
                                <SendOutlined
                                    style={{
                                        fontSize: 18,
                                        color: this.state.inputValue.trim() ? '#3b82f6' : '#d1d5db',
                                        cursor: this.state.inputValue.trim() ? 'pointer' : 'default',
                                    }}
                                    onClick={this.handleSend}
                                />
                            )
                        }
                        style={{
                            borderRadius: 16,
                            padding: '12px 20px',
                            fontSize: 15,
                            boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                            border: '1px solid #e5e7eb',
                        }}
                    />
                </div>

                {/* Loading */}
                {this.state.loading ? (
                    <div style={{ marginTop: 32, textAlign: 'center' }}>
                        <Spin size="large" tip="Searching..." />
                    </div>
                ) : null}

                {/* Result */}
                {this.renderResult()}
            </div>
        );
    }
}

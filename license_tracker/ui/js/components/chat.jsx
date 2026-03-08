import React from 'react';
import { Input, Button, Spin, Table, Card, Tag, Typography, Tooltip } from 'antd';
import { SendOutlined, BulbOutlined, DatabaseOutlined, HistoryOutlined, StopOutlined, BarChartOutlined, UserOutlined, RobotOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

var axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});

var SUGGESTION_ICONS = {
    0: <DatabaseOutlined />,
    1: <BarChartOutlined />,
    2: <StopOutlined />,
    3: <HistoryOutlined />,
    4: <BulbOutlined />,
    5: <UserOutlined />,
    6: <HistoryOutlined />,
    7: <BarChartOutlined />,
};

var SUGGESTION_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec4899', '#14b8a6'];

export class ChatPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            inputValue: '',
            loading: false,
            suggestions: [],
        };
        this.messagesEndRef = React.createRef();
        this.inputRef = React.createRef();
        this.handleSend = this.handleSend.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleSuggestionClick = this.handleSuggestionClick.bind(this);
        this.clearChat = this.clearChat.bind(this);
    }

    componentDidMount() {
        this.fetchSuggestions();
        if (this.inputRef.current) {
            this.inputRef.current.focus();
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.messages.length !== this.state.messages.length) {
            this.scrollToBottom();
        }
    }

    scrollToBottom() {
        if (this.messagesEndRef.current) {
            this.messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }

    fetchSuggestions() {
        var self = this;
        axiosInstance.get('/api/chat/suggestions').then(function (res) {
            if (res.data.success) {
                self.setState({ suggestions: res.data.suggestions });
            }
        }).catch(function () { });
    }

    handleSend() {
        var query = this.state.inputValue.trim();
        if (!query || this.state.loading) return;

        var userMsg = { role: 'user', content: query, timestamp: new Date() };
        var self = this;

        this.setState({
            messages: this.state.messages.concat([userMsg]),
            inputValue: '',
            loading: true,
        });

        axiosInstance.post('/api/chat/query', { query: query }).then(function (res) {
            if (res.data.success) {
                var botMsg = {
                    role: 'assistant',
                    result: res.data.result,
                    timestamp: new Date(),
                };
                self.setState({ messages: self.state.messages.concat([botMsg]) });
            } else {
                var errMsg = {
                    role: 'assistant',
                    error: res.data.error || 'Something went wrong.',
                    timestamp: new Date(),
                };
                self.setState({ messages: self.state.messages.concat([errMsg]) });
            }
        }).catch(function (err) {
            var errorText = 'Failed to process your query. Please try again.';
            if (err.response && err.response.data && err.response.data.error) {
                errorText = err.response.data.error;
            }
            var errMsg = {
                role: 'assistant',
                error: errorText,
                timestamp: new Date(),
            };
            self.setState({ messages: self.state.messages.concat([errMsg]) });
        }).finally(function () {
            self.setState({ loading: false });
        });
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSend();
        }
    }

    handleSuggestionClick(suggestion) {
        var self = this;
        this.setState({ inputValue: suggestion }, function () {
            self.handleSend();
        });
    }

    clearChat() {
        this.setState({ messages: [] });
    }

    renderResult(result) {
        if (!result) return null;

        if (result.type === 'stats') {
            return (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 12 }}>
                    {result.data.map(function (stat, idx) {
                        return (
                            <div key={idx} style={{
                                background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                                borderRadius: 12,
                                padding: '16px 24px',
                                minWidth: 160,
                                flex: '1 1 160px',
                                textAlign: 'center',
                                border: '1px solid #e2e8f0',
                            }}>
                                <div style={{ fontSize: 28, fontWeight: 700, color: '#1e3a5f' }}>
                                    {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                                </div>
                                <div style={{ fontSize: 12, color: '#64748b', marginTop: 4, fontWeight: 500 }}>
                                    {stat.label}
                                </div>
                            </div>
                        );
                    })}
                </div>
            );
        }

        if (result.type === 'table' && result.data && result.data.length > 0) {
            var columns = result.columns.map(function (col) {
                return {
                    title: col.replace(/_/g, ' ').replace(/\b\w/g, function (l) { return l.toUpperCase(); }),
                    dataIndex: col,
                    key: col,
                    ellipsis: true,
                    render: function (text) {
                        if (text === null || text === undefined) return <span style={{ color: '#ccc' }}>—</span>;
                        return text;
                    },
                };
            });

            return (
                <Table
                    columns={columns}
                    dataSource={result.data.map(function (row, idx) {
                        return Object.assign({}, row, { key: idx });
                    })}
                    size="small"
                    pagination={result.data.length > 10 ? { pageSize: 10, size: 'small' } : false}
                    style={{ marginTop: 12 }}
                    scroll={{ x: true }}
                />
            );
        }

        if (result.data && result.data.length === 0) {
            return (
                <div style={{ marginTop: 12, padding: '24px', textAlign: 'center', color: '#94a3b8', background: '#f8fafc', borderRadius: 8 }}>
                    No records found matching your query.
                </div>
            );
        }

        return null;
    }

    renderMarkdown(text) {
        if (!text) return null;
        var parts = text.split(/(\*\*[^*]+\*\*)/g);
        return parts.map(function (part, i) {
            if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={i}>{part.slice(2, -2)}</strong>;
            }
            return <span key={i}>{part}</span>;
        });
    }

    render() {
        var self = this;
        var isWelcome = this.state.messages.length === 0;

        var welcomeScreen = (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flex: 1,
                padding: '40px 20px',
                minHeight: '60vh',
            }}>
                <div style={{
                    width: 64,
                    height: 64,
                    borderRadius: 20,
                    background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 24,
                    boxShadow: '0 8px 32px rgba(59, 130, 246, 0.3)',
                }}>
                    <RobotOutlined style={{ fontSize: 32, color: '#fff' }} />
                </div>
                <div style={{
                    fontSize: 28,
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 50%, #06b6d4 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    marginBottom: 8,
                }}>
                    License Data Assistant
                </div>
                <div style={{ fontSize: 15, color: '#64748b', marginBottom: 40, textAlign: 'center', maxWidth: 480 }}>
                    Ask me anything about your license data — active checkouts, usage history, denials, top users, and more.
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                    gap: 12,
                    width: '100%',
                    maxWidth: 720,
                }}>
                    {this.state.suggestions.map(function (s, idx) {
                        return (
                            <div
                                key={idx}
                                onClick={function () { self.handleSuggestionClick(s); }}
                                style={{
                                    padding: '14px 18px',
                                    borderRadius: 12,
                                    border: '1px solid #e2e8f0',
                                    background: '#fff',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 12,
                                    fontSize: 13,
                                    color: '#334155',
                                    fontWeight: 500,
                                }}
                                onMouseEnter={function (e) {
                                    e.currentTarget.style.borderColor = SUGGESTION_COLORS[idx % SUGGESTION_COLORS.length];
                                    e.currentTarget.style.background = '#f8fafc';
                                    e.currentTarget.style.transform = 'translateY(-1px)';
                                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
                                }}
                                onMouseLeave={function (e) {
                                    e.currentTarget.style.borderColor = '#e2e8f0';
                                    e.currentTarget.style.background = '#fff';
                                    e.currentTarget.style.transform = 'none';
                                    e.currentTarget.style.boxShadow = 'none';
                                }}
                            >
                                <span style={{
                                    color: SUGGESTION_COLORS[idx % SUGGESTION_COLORS.length],
                                    fontSize: 16,
                                    flexShrink: 0,
                                }}>
                                    {SUGGESTION_ICONS[idx] || <BulbOutlined />}
                                </span>
                                {s}
                            </div>
                        );
                    })}
                </div>
            </div>
        );

        var messagesView = (
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '24px 0',
                display: 'flex',
                flexDirection: 'column',
                gap: 24,
            }}>
                {this.state.messages.map(function (msg, idx) {
                    if (msg.role === 'user') {
                        return (
                            <div key={idx} style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 24px' }}>
                                <div style={{
                                    maxWidth: '70%',
                                    padding: '12px 18px',
                                    borderRadius: '18px 18px 4px 18px',
                                    background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)',
                                    color: '#fff',
                                    fontSize: 14,
                                    lineHeight: 1.5,
                                    boxShadow: '0 2px 8px rgba(37, 99, 235, 0.2)',
                                }}>
                                    {msg.content}
                                </div>
                            </div>
                        );
                    }

                    // Assistant message
                    return (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'flex-start', padding: '0 24px' }}>
                            <div style={{
                                maxWidth: '85%',
                                width: '100%',
                            }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 8,
                                    marginBottom: 8,
                                }}>
                                    <div style={{
                                        width: 28,
                                        height: 28,
                                        borderRadius: 8,
                                        background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0,
                                    }}>
                                        <RobotOutlined style={{ fontSize: 14, color: '#fff' }} />
                                    </div>
                                    <span style={{ fontSize: 13, fontWeight: 600, color: '#1e3a5f' }}>License Assistant</span>
                                </div>
                                {msg.error ? (
                                    <div style={{
                                        padding: '12px 18px',
                                        borderRadius: '4px 18px 18px 18px',
                                        background: '#fef2f2',
                                        border: '1px solid #fecaca',
                                        color: '#dc2626',
                                        fontSize: 14,
                                    }}>
                                        {msg.error}
                                    </div>
                                ) : (
                                    <div style={{
                                        padding: '16px 20px',
                                        borderRadius: '4px 18px 18px 18px',
                                        background: '#fff',
                                        border: '1px solid #e2e8f0',
                                        fontSize: 14,
                                        lineHeight: 1.6,
                                        boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
                                    }}>
                                        {msg.result && msg.result.title ? (
                                            <div style={{ fontSize: 15, fontWeight: 600, color: '#1e3a5f', marginBottom: 6 }}>
                                                {msg.result.title}
                                            </div>
                                        ) : null}
                                        {msg.result && msg.result.summary ? (
                                            <div style={{ color: '#475569', marginBottom: 4, whiteSpace: 'pre-line' }}>
                                                {self.renderMarkdown(msg.result.summary)}
                                            </div>
                                        ) : null}
                                        {msg.result ? self.renderResult(msg.result) : null}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}

                {this.state.loading ? (
                    <div style={{ display: 'flex', justifyContent: 'flex-start', padding: '0 24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <div style={{
                                width: 28, height: 28, borderRadius: 8,
                                background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                <RobotOutlined style={{ fontSize: 14, color: '#fff' }} />
                            </div>
                            <div style={{
                                padding: '12px 20px',
                                borderRadius: '4px 18px 18px 18px',
                                background: '#fff',
                                border: '1px solid #e2e8f0',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 10,
                            }}>
                                <Spin size="small" />
                                <span style={{ color: '#94a3b8', fontSize: 13 }}>Querying license data...</span>
                            </div>
                        </div>
                    </div>
                ) : null}

                <div ref={this.messagesEndRef} />
            </div>
        );

        return (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(100vh - 53px)',
                background: '#f8fafc',
            }}>
                {/* Messages area or welcome screen */}
                {isWelcome && !this.state.loading ? welcomeScreen : messagesView}

                {/* Input area */}
                <div style={{
                    borderTop: '1px solid #e2e8f0',
                    background: '#fff',
                    padding: '16px 24px 20px',
                }}>
                    <div style={{
                        maxWidth: 800,
                        margin: '0 auto',
                        display: 'flex',
                        alignItems: 'flex-end',
                        gap: 12,
                    }}>
                        {this.state.messages.length > 0 ? (
                            <Tooltip title="Clear chat">
                                <Button
                                    icon={<DeleteOutlined />}
                                    onClick={this.clearChat}
                                    style={{
                                        borderRadius: 12,
                                        height: 48,
                                        width: 48,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        border: '1px solid #e2e8f0',
                                        color: '#94a3b8',
                                        flexShrink: 0,
                                    }}
                                />
                            </Tooltip>
                        ) : null}
                        <div style={{
                            flex: 1,
                            position: 'relative',
                            border: '2px solid #e2e8f0',
                            borderRadius: 16,
                            overflow: 'hidden',
                            transition: 'border-color 0.2s',
                            background: '#fff',
                        }}
                            onFocus={function (e) { e.currentTarget.style.borderColor = '#3b82f6'; }}
                            onBlur={function (e) { e.currentTarget.style.borderColor = '#e2e8f0'; }}
                        >
                            <Input.TextArea
                                ref={this.inputRef}
                                value={this.state.inputValue}
                                onChange={function (e) { self.setState({ inputValue: e.target.value }); }}
                                onKeyDown={this.handleKeyDown}
                                placeholder="Ask about license data..."
                                autoSize={{ minRows: 1, maxRows: 4 }}
                                bordered={false}
                                style={{
                                    padding: '12px 56px 12px 18px',
                                    fontSize: 15,
                                    resize: 'none',
                                    lineHeight: 1.5,
                                }}
                            />
                            <Button
                                type="primary"
                                icon={<SendOutlined />}
                                onClick={this.handleSend}
                                disabled={!this.state.inputValue.trim() || this.state.loading}
                                style={{
                                    position: 'absolute',
                                    right: 8,
                                    bottom: 8,
                                    borderRadius: 10,
                                    width: 36,
                                    height: 36,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: this.state.inputValue.trim() ? 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)' : '#e2e8f0',
                                    border: 'none',
                                    boxShadow: this.state.inputValue.trim() ? '0 2px 8px rgba(37, 99, 235, 0.3)' : 'none',
                                }}
                            />
                        </div>
                    </div>
                    <div style={{
                        maxWidth: 800,
                        margin: '8px auto 0',
                        textAlign: 'center',
                        fontSize: 11,
                        color: '#94a3b8',
                    }}>
                        Queries your license database directly. Try asking about active checkouts, usage history, or denials.
                    </div>
                </div>
            </div>
        );
    }
}

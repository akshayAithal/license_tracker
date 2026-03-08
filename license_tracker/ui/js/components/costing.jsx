import React from 'react';
import {
    Button, Col, Row, Table, Card, Upload, Input, Select, notification,
    Spin, Tag, Modal, Tabs, Statistic, Popconfirm, Form, Space, Empty,
    Breadcrumb
} from 'antd';
import {
    FolderOutlined, FileTextOutlined, FilePdfOutlined, UploadOutlined,
    DeleteOutlined, DownloadOutlined, FolderAddOutlined, RobotOutlined,
    DollarOutlined, PlusOutlined, EditOutlined, HomeOutlined,
    ArrowLeftOutlined, ReloadOutlined, SendOutlined
} from '@ant-design/icons';
import axios from 'axios';

var TabPane = Tabs.TabPane;
var Option = Select.Option;
var TextArea = Input.TextArea;

var axiosInstance = axios.create({
    baseURL: window.location.href.split('?')[0],
});


function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    var k = 1024;
    var sizes = ['B', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getFileIcon(ext) {
    if (ext === 'pdf') return React.createElement(FilePdfOutlined, { style: { color: '#ff4d4f', fontSize: 20 } });
    return React.createElement(FileTextOutlined, { style: { color: '#1890ff', fontSize: 20 } });
}


export class CostingPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // File browser
            currentPath: '',
            files: [],
            filesLoading: false,
            newFolderName: '',
            newFolderModalVisible: false,
            // AI analysis
            selectedFile: null,
            analysisPrompt: 'Analyze this license document and extract: vendor names, feature names, license counts, costs per license, billing periods, and any expiry dates. Provide a structured summary.',
            analysisResult: '',
            analyzing: false,
            analysisModalVisible: false,
            inlineApiKey: '',
            needsKey: false,
            // License costs
            costs: [],
            costsLoading: false,
            costSummary: { vendors: [], grand_total: 0 },
            costModalVisible: false,
            editingCost: null,
        };
        this.fetchFiles = this.fetchFiles.bind(this);
        this.fetchCosts = this.fetchCosts.bind(this);
        this.fetchCostSummary = this.fetchCostSummary.bind(this);
        this.navigateTo = this.navigateTo.bind(this);
        this.handleUpload = this.handleUpload.bind(this);
        this.createFolder = this.createFolder.bind(this);
        this.deleteItem = this.deleteItem.bind(this);
        this.analyzeFile = this.analyzeFile.bind(this);
        this.saveCost = this.saveCost.bind(this);
        this.deleteCost = this.deleteCost.bind(this);
    }

    componentDidMount() {
        this.fetchFiles();
        this.fetchCosts();
        this.fetchCostSummary();
    }

    fetchFiles() {
        var self = this;
        this.setState({ filesLoading: true });
        axiosInstance.get('/api/costing/files', {
            params: { path: this.state.currentPath }
        }).then(function(res) {
            self.setState({ files: res.data.items || [], filesLoading: false });
        }).catch(function(err) {
            self.setState({ filesLoading: false });
            notification.error({ message: 'Error', description: 'Failed to load files' });
        });
    }

    navigateTo(path) {
        var self = this;
        this.setState({ currentPath: path || '' }, function() {
            self.fetchFiles();
        });
    }

    navigateUp() {
        var parts = this.state.currentPath.split('/');
        parts.pop();
        this.navigateTo(parts.join('/'));
    }

    handleUpload(info) {
        var self = this;
        var formData = new FormData();
        formData.append('file', info.file);
        formData.append('path', this.state.currentPath);

        axiosInstance.post('/api/costing/files/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(function(res) {
            notification.success({ message: 'Uploaded', description: res.data.filename + ' uploaded successfully' });
            self.fetchFiles();
        }).catch(function(err) {
            var msg = (err.response && err.response.data && err.response.data.error) || 'Upload failed';
            notification.error({ message: 'Error', description: msg });
        });
    }

    createFolder() {
        var self = this;
        var name = this.state.newFolderName.trim();
        if (!name) return;

        axiosInstance.post('/api/costing/files/folder', {
            name: name,
            path: this.state.currentPath
        }).then(function() {
            notification.success({ message: 'Created', description: 'Folder "' + name + '" created' });
            self.setState({ newFolderModalVisible: false, newFolderName: '' });
            self.fetchFiles();
        }).catch(function(err) {
            var msg = (err.response && err.response.data && err.response.data.error) || 'Failed to create folder';
            notification.error({ message: 'Error', description: msg });
        });
    }

    deleteItem(path) {
        var self = this;
        axiosInstance.post('/api/costing/files/delete', { path: path })
            .then(function() {
                notification.success({ message: 'Deleted' });
                self.fetchFiles();
            }).catch(function(err) {
                var msg = (err.response && err.response.data && err.response.data.error) || 'Delete failed';
                notification.error({ message: 'Error', description: msg });
            });
    }

    analyzeFile() {
        var self = this;
        if (!this.state.selectedFile) return;
        this.setState({ analyzing: true, needsKey: false });

        var payload = {
            path: this.state.selectedFile.path,
            prompt: this.state.analysisPrompt,
        };
        if (this.state.inlineApiKey.trim()) {
            payload.api_key = this.state.inlineApiKey.trim();
        }

        axiosInstance.post('/api/costing/files/analyze', payload).then(function(res) {
            if (res.data.success) {
                self.setState({ analysisResult: res.data.response, analyzing: false, needsKey: false });
            } else {
                notification.error({ message: 'Analysis Failed', description: res.data.error });
                self.setState({ analyzing: false });
            }
        }).catch(function(err) {
            var respData = err.response && err.response.data;
            var msg = (respData && respData.error) || 'Analysis failed';
            if (respData && respData.needs_key) {
                self.setState({ analyzing: false, needsKey: true });
            } else {
                notification.error({ message: 'Error', description: msg });
                self.setState({ analyzing: false });
            }
        });
    }

    // License costs
    fetchCosts() {
        var self = this;
        this.setState({ costsLoading: true });
        axiosInstance.get('/api/costing/costs').then(function(res) {
            self.setState({ costs: res.data.costs || [], costsLoading: false });
        }).catch(function() {
            self.setState({ costsLoading: false });
        });
    }

    fetchCostSummary() {
        var self = this;
        axiosInstance.get('/api/costing/costs/summary').then(function(res) {
            self.setState({ costSummary: { vendors: res.data.vendors || [], grand_total: res.data.grand_total || 0 } });
        }).catch(function() {});
    }

    saveCost(values) {
        var self = this;
        var editing = this.state.editingCost;
        var promise;
        if (editing) {
            promise = axiosInstance.put('/api/costing/costs/' + editing.id, values);
        } else {
            promise = axiosInstance.post('/api/costing/costs', values);
        }
        promise.then(function() {
            notification.success({ message: 'Saved' });
            self.setState({ costModalVisible: false, editingCost: null });
            self.fetchCosts();
            self.fetchCostSummary();
        }).catch(function(err) {
            var msg = (err.response && err.response.data && err.response.data.error) || 'Save failed';
            notification.error({ message: 'Error', description: msg });
        });
    }

    deleteCost(id) {
        var self = this;
        axiosInstance.delete('/api/costing/costs/' + id).then(function() {
            notification.success({ message: 'Deleted' });
            self.fetchCosts();
            self.fetchCostSummary();
        }).catch(function() {
            notification.error({ message: 'Error', description: 'Delete failed' });
        });
    }

    render() {
        var self = this;

        // Breadcrumb from currentPath
        var pathParts = this.state.currentPath ? this.state.currentPath.split('/') : [];
        var breadcrumbItems = [
            React.createElement(Breadcrumb.Item, { key: 'root' },
                React.createElement('a', { onClick: function() { self.navigateTo(''); } },
                    React.createElement(HomeOutlined, null), ' My Files'
                )
            )
        ];
        pathParts.forEach(function(part, idx) {
            var subPath = pathParts.slice(0, idx + 1).join('/');
            breadcrumbItems.push(
                React.createElement(Breadcrumb.Item, { key: subPath },
                    React.createElement('a', { onClick: function() { self.navigateTo(subPath); } }, part)
                )
            );
        });

        // File table columns
        var fileColumns = [
            {
                title: 'Name', dataIndex: 'name', key: 'name',
                render: function(text, record) {
                    if (record.type === 'folder') {
                        return React.createElement('a', {
                            onClick: function() { self.navigateTo(record.path); },
                            style: { fontWeight: 500 }
                        }, React.createElement(FolderOutlined, { style: { color: '#faad14', marginRight: 8 } }), text);
                    }
                    return React.createElement('span', null,
                        getFileIcon(record.ext),
                        React.createElement('span', { style: { marginLeft: 8 } }, text)
                    );
                },
                sorter: function(a, b) { return a.name.localeCompare(b.name); },
            },
            {
                title: 'Type', dataIndex: 'type', key: 'type', width: 100,
                render: function(type, record) {
                    if (type === 'folder') return React.createElement(Tag, { color: 'gold' }, 'Folder');
                    return React.createElement(Tag, { color: 'blue' }, (record.ext || '').toUpperCase());
                }
            },
            {
                title: 'Size', dataIndex: 'size', key: 'size', width: 100,
                render: function(size, record) {
                    return record.type === 'folder' ? '-' : formatBytes(size);
                }
            },
            {
                title: 'Actions', key: 'actions', width: 200,
                render: function(_, record) {
                    var btns = [];
                    if (record.type === 'file') {
                        btns.push(React.createElement(Button, {
                            key: 'dl', icon: React.createElement(DownloadOutlined, null), size: 'small',
                            onClick: function() { window.open(axiosInstance.defaults.baseURL + '/api/costing/files/download?path=' + encodeURIComponent(record.path)); }
                        }));
                        btns.push(React.createElement(Button, {
                            key: 'ai', icon: React.createElement(RobotOutlined, null), size: 'small',
                            type: 'primary', ghost: true, style: { marginLeft: 4 },
                            onClick: function() {
                                self.setState({ selectedFile: record, analysisResult: '', analysisModalVisible: true });
                            }
                        }, 'Analyze'));
                    }
                    btns.push(React.createElement(Popconfirm, {
                        key: 'del', title: 'Delete this ' + record.type + '?',
                        onConfirm: function() { self.deleteItem(record.path); },
                        okText: 'Yes', cancelText: 'No',
                    }, React.createElement(Button, {
                        icon: React.createElement(DeleteOutlined, null), danger: true, size: 'small',
                        style: { marginLeft: 4 }
                    })));
                    return React.createElement(Space, null, btns);
                }
            }
        ];

        // Cost table columns
        var costColumns = [
            { title: 'Vendor', dataIndex: 'vendor', key: 'vendor',
                filters: [].concat.apply([], (function() {
                    var seen = {};
                    return self.state.costs.filter(function(c) {
                        if (seen[c.vendor]) return false;
                        seen[c.vendor] = true; return true;
                    }).map(function(c) { return { text: c.vendor, value: c.vendor }; });
                })()),
                onFilter: function(v, r) { return r.vendor === v; },
                render: function(text) { return React.createElement(Tag, { color: 'blue' }, text); }
            },
            { title: 'Feature', dataIndex: 'feature', key: 'feature', sorter: function(a, b) { return a.feature.localeCompare(b.feature); } },
            { title: 'Cost/License', dataIndex: 'cost_per_license', key: 'cost', align: 'right',
                sorter: function(a, b) { return a.cost_per_license - b.cost_per_license; },
                render: function(val, r) { return React.createElement('span', { style: { fontWeight: 600 } }, r.currency + ' ' + val.toLocaleString()); }
            },
            { title: 'Period', dataIndex: 'billing_period', key: 'period',
                render: function(p) {
                    var colors = { annual: 'green', monthly: 'cyan', perpetual: 'purple' };
                    return React.createElement(Tag, { color: colors[p] || 'default' }, (p || '').charAt(0).toUpperCase() + (p || '').slice(1));
                }
            },
            { title: 'Notes', dataIndex: 'notes', key: 'notes', ellipsis: true },
            { title: 'Actions', key: 'actions', width: 120,
                render: function(_, record) {
                    return React.createElement(Space, null,
                        React.createElement(Button, {
                            icon: React.createElement(EditOutlined, null), size: 'small',
                            onClick: function() { self.setState({ editingCost: record, costModalVisible: true }); }
                        }),
                        React.createElement(Popconfirm, {
                            title: 'Delete this cost entry?',
                            onConfirm: function() { self.deleteCost(record.id); },
                            okText: 'Yes', cancelText: 'No',
                        }, React.createElement(Button, {
                            icon: React.createElement(DeleteOutlined, null), danger: true, size: 'small'
                        }))
                    );
                }
            }
        ];

        return React.createElement('div', { style: { padding: 24 } },
            // Horizontal split: Documents on left, License Costs on right
            React.createElement(Row, { gutter: 16 },
                // Left: Documents
                React.createElement(Col, { span: 12 },
                    React.createElement(Card, {
                        title: React.createElement('span', null, React.createElement(FolderOutlined, { style: { marginRight: 8 } }), 'Documents'),
                        style: { borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', minHeight: '80vh' },
                        extra: React.createElement(Space, null,
                            React.createElement(Upload, {
                                showUploadList: false,
                                customRequest: this.handleUpload,
                                accept: '.txt,.csv,.pdf',
                            }, React.createElement(Button, { icon: React.createElement(UploadOutlined, null), type: 'primary', size: 'small' }, 'Upload')),
                            React.createElement(Button, {
                                icon: React.createElement(FolderAddOutlined, null),
                                size: 'small',
                                onClick: function() { self.setState({ newFolderModalVisible: true, newFolderName: '' }); }
                            }, 'New Folder'),
                            this.state.currentPath ? React.createElement(Button, {
                                icon: React.createElement(ArrowLeftOutlined, null),
                                size: 'small',
                                onClick: function() { self.navigateUp(); }
                            }, 'Back') : null,
                            React.createElement(Button, {
                                icon: React.createElement(ReloadOutlined, null),
                                size: 'small',
                                onClick: this.fetchFiles
                            })
                        )
                    },
                        React.createElement(Breadcrumb, { style: { marginBottom: 12 } }, breadcrumbItems),
                        React.createElement(Table, {
                            columns: fileColumns,
                            dataSource: this.state.files,
                            loading: this.state.filesLoading,
                            rowKey: 'path',
                            pagination: false,
                            locale: { emptyText: React.createElement(Empty, { description: 'No files yet. Upload documents or create a folder.' }) },
                            size: 'small',
                        })
                    )
                ),
                // Right: License Costs
                React.createElement(Col, { span: 12 },
                    // Summary cards
                    React.createElement(Row, { gutter: [8, 8], style: { marginBottom: 12 } },
                        React.createElement(Col, { span: 8 },
                            React.createElement(Card, { bodyStyle: { padding: 12 } },
                                React.createElement(Statistic, {
                                    title: 'Total Annual Cost',
                                    value: this.state.costSummary.grand_total,
                                    prefix: '$',
                                    precision: 0,
                                    valueStyle: { color: '#1e3a5f', fontSize: 18 },
                                })
                            )
                        ),
                        this.state.costSummary.vendors.map(function(v) {
                            return React.createElement(Col, { span: 8, key: v.vendor },
                                React.createElement(Card, { bodyStyle: { padding: 12 } },
                                    React.createElement(Statistic, {
                                        title: v.vendor,
                                        value: v.total,
                                        prefix: '$',
                                        precision: 0,
                                        valueStyle: { fontSize: 16 },
                                        suffix: React.createElement('span', { style: { fontSize: 11, color: '#999' } }, ' (' + v.count + ')'),
                                    })
                                )
                            );
                        })
                    ),
                    React.createElement(Card, {
                        title: React.createElement('span', null, React.createElement(DollarOutlined, { style: { marginRight: 8 } }), 'License Costs'),
                        style: { borderRadius: 12 },
                        extra: React.createElement(Space, null,
                            React.createElement(Button, {
                                type: 'primary',
                                icon: React.createElement(PlusOutlined, null),
                                size: 'small',
                                onClick: function() { self.setState({ editingCost: null, costModalVisible: true }); }
                            }, 'Add Cost'),
                            React.createElement(Button, {
                                icon: React.createElement(ReloadOutlined, null),
                                size: 'small',
                                onClick: function() { self.fetchCosts(); self.fetchCostSummary(); }
                            })
                        )
                    },
                        React.createElement(Table, {
                            columns: costColumns,
                            dataSource: this.state.costs,
                            loading: this.state.costsLoading,
                            rowKey: 'id',
                            pagination: { pageSize: 10, showSizeChanger: true },
                            size: 'small',
                        })
                    )
                )
            ),

            // New Folder Modal
            React.createElement(Modal, {
                title: 'Create New Folder',
                visible: this.state.newFolderModalVisible,
                onOk: this.createFolder,
                onCancel: function() { self.setState({ newFolderModalVisible: false }); },
                okText: 'Create',
            },
                React.createElement(Input, {
                    placeholder: 'Folder name',
                    value: this.state.newFolderName,
                    onChange: function(e) { self.setState({ newFolderName: e.target.value }); },
                    onPressEnter: this.createFolder,
                })
            ),

            // AI Analysis Modal
            React.createElement(Modal, {
                title: React.createElement('span', null,
                    React.createElement(RobotOutlined, null),
                    ' AI Document Analysis',
                    this.state.selectedFile ? ' - ' + this.state.selectedFile.name : ''
                ),
                visible: this.state.analysisModalVisible,
                onCancel: function() { self.setState({ analysisModalVisible: false, needsKey: false }); },
                footer: null,
                width: 800,
            },
                // API Key prompt - shown when no key is configured
                this.state.needsKey ? React.createElement(Card, {
                    style: { marginBottom: 16, background: '#fffbe6', border: '1px solid #ffe58f', borderRadius: 8 },
                },
                    React.createElement('div', { style: { marginBottom: 8, fontWeight: 500, color: '#ad6800' } },
                        'No OpenAI API key configured. Enter one below to proceed, or set it in Admin \u2192 AI / Models.'
                    ),
                    React.createElement(Input.Password, {
                        placeholder: 'sk-... (your OpenAI API key)',
                        value: this.state.inlineApiKey,
                        onChange: function(e) { self.setState({ inlineApiKey: e.target.value }); },
                        style: { marginBottom: 8 },
                        size: 'large',
                    }),
                    React.createElement('div', { style: { fontSize: 12, color: '#8c8c8c' } },
                        'This key is used for this session only and is not stored.'
                    )
                ) : null,
                React.createElement('div', { style: { marginBottom: 12 } },
                    React.createElement('label', { style: { fontWeight: 500, display: 'block', marginBottom: 4 } }, 'Prompt:'),
                    React.createElement(TextArea, {
                        rows: 3,
                        value: this.state.analysisPrompt,
                        onChange: function(e) { self.setState({ analysisPrompt: e.target.value }); },
                    })
                ),
                React.createElement(Button, {
                    type: 'primary',
                    icon: React.createElement(SendOutlined, null),
                    loading: this.state.analyzing,
                    onClick: this.analyzeFile,
                    disabled: this.state.needsKey && !this.state.inlineApiKey.trim(),
                    style: { marginBottom: 16 },
                }, this.state.needsKey ? 'Send with API Key' : 'Send to AI'),
                this.state.analyzing ? React.createElement(Spin, { tip: 'Analyzing document...', style: { display: 'block', margin: '20px auto' } }) : null,
                this.state.analysisResult ? React.createElement(Card, {
                    title: 'AI Response',
                    style: { background: '#f9fafb', maxHeight: 400, overflow: 'auto' },
                },
                    React.createElement('pre', { style: { whiteSpace: 'pre-wrap', fontSize: 13, margin: 0 } }, this.state.analysisResult)
                ) : null
            ),

            // Cost Add/Edit Modal
            React.createElement(CostModal, {
                visible: this.state.costModalVisible,
                editingCost: this.state.editingCost,
                onSave: this.saveCost,
                onCancel: function() { self.setState({ costModalVisible: false, editingCost: null }); },
            })
        );
    }
}


// Separate cost modal component (class-based for webpack 4 compat)
class CostModal extends React.Component {
    constructor(props) {
        super(props);
        this.formRef = React.createRef();
    }

    componentDidUpdate(prevProps) {
        if (this.props.visible && !prevProps.visible && this.formRef.current) {
            if (this.props.editingCost) {
                this.formRef.current.setFieldsValue(this.props.editingCost);
            } else {
                this.formRef.current.resetFields();
            }
        }
    }

    render() {
        var self = this;
        return React.createElement(Modal, {
            title: this.props.editingCost ? 'Edit License Cost' : 'Add License Cost',
            visible: this.props.visible,
            onCancel: this.props.onCancel,
            footer: null,
            width: 600,
        },
            React.createElement(Form, {
                ref: this.formRef,
                layout: 'vertical',
                onFinish: this.props.onSave,
                initialValues: this.props.editingCost || { currency: 'USD', billing_period: 'annual' },
            },
                React.createElement(Row, { gutter: 16 },
                    React.createElement(Col, { span: 12 },
                        React.createElement(Form.Item, { name: 'vendor', label: 'Vendor', rules: [{ required: true }] },
                            React.createElement(Select, { placeholder: 'Select or type vendor', showSearch: true, allowClear: true },
                                React.createElement(Option, { value: 'Altair' }, 'Altair'),
                                React.createElement(Option, { value: 'MSC' }, 'MSC'),
                                React.createElement(Option, { value: 'Particleworks' }, 'Particleworks'),
                                React.createElement(Option, { value: 'RLM' }, 'RLM'),
                                React.createElement(Option, { value: 'Ricardo' }, 'Ricardo')
                            )
                        )
                    ),
                    React.createElement(Col, { span: 12 },
                        React.createElement(Form.Item, { name: 'feature', label: 'Feature', rules: [{ required: true }] },
                            React.createElement(Input, { placeholder: 'e.g. Nastran, HyperMesh' })
                        )
                    )
                ),
                React.createElement(Row, { gutter: 16 },
                    React.createElement(Col, { span: 8 },
                        React.createElement(Form.Item, { name: 'cost_per_license', label: 'Cost per License', rules: [{ required: true }] },
                            React.createElement(Input, { type: 'number', placeholder: '0.00' })
                        )
                    ),
                    React.createElement(Col, { span: 8 },
                        React.createElement(Form.Item, { name: 'currency', label: 'Currency' },
                            React.createElement(Select, null,
                                React.createElement(Option, { value: 'USD' }, 'USD'),
                                React.createElement(Option, { value: 'EUR' }, 'EUR'),
                                React.createElement(Option, { value: 'GBP' }, 'GBP'),
                                React.createElement(Option, { value: 'JPY' }, 'JPY')
                            )
                        )
                    ),
                    React.createElement(Col, { span: 8 },
                        React.createElement(Form.Item, { name: 'billing_period', label: 'Billing Period' },
                            React.createElement(Select, null,
                                React.createElement(Option, { value: 'annual' }, 'Annual'),
                                React.createElement(Option, { value: 'monthly' }, 'Monthly'),
                                React.createElement(Option, { value: 'perpetual' }, 'Perpetual')
                            )
                        )
                    )
                ),
                React.createElement(Form.Item, { name: 'notes', label: 'Notes' },
                    React.createElement(TextArea, { rows: 2, placeholder: 'Optional notes' })
                ),
                React.createElement(Form.Item, null,
                    React.createElement(Space, null,
                        React.createElement(Button, { type: 'primary', htmlType: 'submit' },
                            self.props.editingCost ? 'Update' : 'Create'
                        ),
                        React.createElement(Button, { onClick: self.props.onCancel }, 'Cancel')
                    )
                )
            )
        );
    }
}

import React from 'react';
import { Row, Col, Popover, Avatar, Layout} from 'antd';

/*
 * Footer for the website.
*/
export class GenericFooter extends React.Component {
    render(){
        const { Footer } = Layout;
        return (
            <Footer
                style={{ paddingTop: 10, marginTop: 0, color:'#E3E3E3' , backgroundColor: '#202c44',  bottom: 0, height: '6%', width: '100%', textAlign: 'center', position: "fixed" }}>
                <Row style={{ paddingLeft: 0, paddingTop: 0 }}>
                    <Col span={18} align='middle'>
                        <p style={{ fontSize: "0.7rem" }}>
                            <b><i>{this.props.name}</i></b><br />
                            Please use the project issue tracker for assistance and requests regarding
                            the user interface.
                            </p>
                    </Col>
                </Row>
            </Footer>
        )
    }
}

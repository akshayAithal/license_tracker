import React from 'react';
import ReactDOM from 'react-dom';
import { Table } from 'antd';

const License_Table = ({onClickKill, Username, DataSource, Application,region,hostname,software}) => {
        
    const columnsWithKill = [
      { title: "User", data: "NAME" , key : "NAME",
        render: (text, record) => (
        <span>
          <p>{record["NAME"]}</p>
        </span>
        ),},
      { title: "Host", data: "HOST", key: "HOST",
      render: (text, record) => (
      <span>
        <p>{record["HOST"]}</p>
      </span>
      ),},
      { title: "Region", data: "SITE", key: "SITE",
        render: (text, record) => (
        <span>
          <p>{record["SITE"]}</p>
        </span>
        ),},
      { title: "Feature", data: "FEATURE", key: "FEATURE",
        render: (text, record) => (
        <span>
          <p>{record["FEATURE"]}</p>
        </span>
        ),},
      { title: "Version", data: "VERSION", key: "VERSION",
        render: (text, record) => (
        <span>
          <p>{record["VERSION"]}</p>
        </span>
        ),},
      { title: "Server", data: "SERVER", key: "SERVER",
        render: (text, record) => (
        <span>
          <p>{record["SERVER"]}</p>
        </span>
        ),},
      { title: "Unique Key", data: "KEY", key: "KEY",
        render: (text, record) => (
        <span>
          <p>{record["KEY"]}</p>
        </span>
        ),},
      { title: "Date", data: "DATE", key: "DATE",
        render: (text, record) => (
        <span>
          <p>{record["DATE"]}</p>
        </span>
        ),},
      { title: "Time", data: "TIME", key: "TIME",
          render: (text, record) => (
          <span>
            <p>{record["TIME"]}</p>
          </span>
          ),},
      { title: "License Used", data: "USED", key: "USED",
        render: (text, record) => (
        <span>
          <p>{record["USED"]}</p>
        </span>
        ),},
      { title: "Action", data: "", key: "KILL",
        render: (record) => ( 
          record.NAME.toLowerCase() == Username?
          <a onClick={() => onClickKill(record, software, Application, region, hostname)} >
            Kill
          </a>
          : ""
      ),
      },
      // Application == "pw"?
      // { 
      //   title: "SERVER HOST", data: "SERVER_HOST", key: "SERVER_HOST",
      //  }
      //  : "",
    ];

    const columns = [
      { title: "User", data: "NAME" , key : "NAME",
        render: (text, record) => (
        <span>
          <p>{record["NAME"]}</p>
        </span>
        ),},
      { title: "Host", data: "HOST", key: "HOST",
        render: (text, record) => (
        <span>
          <p>{record["HOST"]}</p>
        </span>
        ),},
      { title: "Region", data: "SITE", key: "SITE",
      render: (text, record) => (
      <span>
        <p>{record["SITE"]}</p>
      </span>
      ),},
      { title: "Feature", data: "FEATURE", key: "FEATURE",
        render: (text, record) => (
        <span>
          <p>{record["FEATURE"]}</p>
        </span>
        ),},
      { title: "Version", data: "VERSION", key: "VERSION",
        render: (text, record) => (
        <span>
          <p>{record["VERSION"]}</p>
        </span>
        ),},
      { title: "Server", data: "SERVER", key: "SERVER",
        render: (text, record) => (
        <span>
          <p>{record["SERVER"]}</p>
        </span>
        ),},
      { title: "Unique Key", data: "KEY", key: "KEY",
        render: (text, record) => (
        <span>
          <p>{record["KEY"]}</p>
        </span>
        ),},
      { title: "Date", data: "DATE", key: "DATE",
        render: (text, record) => (
        <span>
          <p>{record["DATE"]}</p>
        </span>
        ),},
      { title: "Time", data: "TIME", key: "TIME",
          render: (text, record) => (
          <span>
            <p>{record["TIME"]}</p>
          </span>
          ),},
      { title: "License Used", data: "USED", key: "USED",
        render: (text, record) => (
        <span>
          <p>{record["USED"]}</p>
        </span>
        ),},
      
    ];

    return (
      <div>
          <Table
            columns={(Username != "" && ( Application == "msc" || Application == "pw"))?columnsWithKill:columns }
            dataSource={DataSource}
            pagination={false}
            scroll={{ y: 400 }}
          />
        </div>
    );
};


export default License_Table;
import Chart from 'react-apexcharts'
import React from 'react';
import ReactDOM from 'react-dom';

const ChartItem = ({Labels,Series}) => {
  let new_labels  = []
  { Labels.map(label=>
    new_labels.push(label.split(":")[0])
  )
  }
    let series = Series;
    let options = {
        chart: {
          width: "70%",
          type: 'donut',
          dropShadow: {
            enabled: true,
            color: '#111',
            top: -1,
            left: 3,
            blur: 3,
            opacity: 0.2
          }
        },
        stroke: {
          width: 0,
        },
        labels: new_labels,
        states: {
          hover: {
            filter: 'none'
          }
        },
        theme: {
          mode: 'light', 
          palette: 'palette1', 
          monochrome: {
              enabled: false,
              color: '#255aee',
              shadeTo: 'light',
              shadeIntensity: 0.65
          },
        },
        responsive: [{
          breakpoint: "70%",
          options: {
            chart: {
              width: "70%"
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      };
    return (
        <div style={{width: '100%', height: '100%', marginTop:"14px", background:'rgb(0 0 0 / 0%)' }} >
            <Chart style={{background: "rgb(0 0 0 / 0%) !important"}}  options={options} series={series} type="donut" width={"100%"} height={"85%"}/> 
       </div>
    );
};


export default ChartItem; 
import Chart from 'react-apexcharts'
import React from 'react';
import ReactDOM from 'react-dom';

const LineChart = ({Labels,Series}) => {
 
    let series = [ ];
    let options =  {
      chart: {
        height: 350,
        type: 'line',
        zoom: {
          enabled: false
        },
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        // width: [5,5,4],
        curve: 'smooth',
        // dashArray: [0, 8, 5]
      },
      title: {
        text: 'License Usage',
        align: 'left'
      },
      legend: {
        tooltipHoverFormatter: function(val, opts) {
          return val + ' - <strong>' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + '</strong>'
        }
      },
      markers: {
        size: 0,
        hover: {
          sizeOffset: 6
        }
      },
      xaxis: {
        categories: Labels
      },
      tooltip: {
        y: [
          {
            title: {
              formatter: function (val) {
                return val + " (mins)"
              }
            }
          },
          {
            title: {
              formatter: function (val) {
                return val + " per session"
              }
            }
          },
          {
            title: {
              formatter: function (val) {
                return val;
              }
            }
          }
        ]
      },
      grid: {
        borderColor: '#f1f1f1',
      }
    };
  
    return (
      <div>
          <div style={{width: '95%', height: '75vh' }} >
              <Chart options={options} series={Series} type="line" width={"100%"} height={"100%"}/> 
        </div>
       </div>
    );
};


export default LineChart;
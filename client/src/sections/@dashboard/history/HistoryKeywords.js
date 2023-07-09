import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

import { Card, CardHeader } from '@mui/material';

// ----------------------------------------------------------------------

HistoryKeywords.propTypes = {
  title: PropTypes.string,
  subheader: PropTypes.string,
  chartColors: PropTypes.arrayOf(PropTypes.string),
  chartData: PropTypes.object,
  top: PropTypes.number
};

export default function HistoryKeywords({ title, subheader, top, chartColors, chartData }) {
  
  const chartSeries = [{
    name: 'Frequency',
    data: chartData? Object.values(chartData).slice(0, top) : []
  }]
  const chartLabels = chartData? Object.keys(chartData).slice(0, top) : []

  const chartOptions = {
    plotOptions: {
      bar: {
        borderRadius: 2,
        horizontal: true,
        width: 20
      }
    },
    dataLabels: {
      enabled: false
    },
    xaxis: {
      categories: chartLabels,
    },
    colors: chartColors
  }

  return (
    <Card sx={{
      p: 3
    }}>
      <CardHeader title={`${title} (Top ${top})`} subheader={subheader} />

      <ReactApexChart 
        type='bar' 
        series={chartSeries} 
        options={chartOptions} 
        height={chartLabels.length * 25 + 100} />
    </Card>
  );
}

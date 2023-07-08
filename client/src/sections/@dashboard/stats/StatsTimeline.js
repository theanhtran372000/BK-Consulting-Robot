import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

// @mui
import { Card, CardHeader, Box } from '@mui/material';

// components
import { useChart } from '../../../components/chart';

// ----------------------------------------------------------------------

StatsTimeline.propTypes = {
  title: PropTypes.string,
  metric: PropTypes.string,
  subheader: PropTypes.string,
  chartData: PropTypes.array.isRequired,
  chartLabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  chartColors: PropTypes.array
};

export default function StatsTimeline({ title, metric, subheader, chartColors, chartLabels, chartData, ...other }) {

  const chartOptions = useChart({
    plotOptions: { bar: { columnWidth: '16%' } },
    colors: chartColors,
    fill: { 
      type: chartData.map((i) => i.fill),
    },
    labels: chartLabels,
    xaxis: { 
      type: 'datetime',
      labels: {
        format: 'MMM dd'
      }
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        format: 'hh:mm:ss'
      },
      y: {
        formatter: (y) => {
          if (typeof y !== 'undefined') {
            return `${y.toFixed(0)} ${metric}`;
          }
          return y;
        },
      },
    },
  });

  return (
    <Card {...other}>
      <CardHeader title={title} subheader={subheader} />

      <Box sx={{ p: 3, pb: 1, mt: -5.5 }} dir="ltr">
        <ReactApexChart type="line" series={chartData} options={chartOptions} height={260} />
      </Box>
    </Card>
  );
}

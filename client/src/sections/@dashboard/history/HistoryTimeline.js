import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

// @mui
import { Card, CardHeader, Box } from '@mui/material';

// components
import { useChart } from '../../../components/chart';

// ----------------------------------------------------------------------

HistoryTimeline.propTypes = {
  title: PropTypes.string,
  metric: PropTypes.string,
  subheader: PropTypes.string,
  chartData: PropTypes.array.isRequired,
  chartLabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  chartColors: PropTypes.array
};

export default function HistoryTimeline({ title, metric, subheader, chartColors, chartLabels, chartData, ...other }) {

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
        formatter: (epoch) => {
          const date = new Date(epoch)
          const dateString = date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          })
          return dateString
        }
      }
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        formatter: (epoch) => {
          const date = new Date(epoch)
          const dateString = date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            hour12: false,
          })
          return dateString
        }
      },
      y: {
        formatter: (y) => `${y} ${metric}`,
      },
    },
  });

  return (
    <Card {...other}>
      <CardHeader title={title} subheader={subheader} />

      <Box sx={{ p: 3, pb: 1, mt: -5 }} dir="ltr">
        <ReactApexChart type="line" series={chartData} options={chartOptions} height={260} />
      </Box>
    </Card>
  );
}

import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

// @mui
import { Card, CardHeader, Box } from '@mui/material';

// ----------------------------------------------------------------------

HistoryDistribution.propTypes = {
  title: PropTypes.string,
  metric: PropTypes.string,
  subheader: PropTypes.string,
  chartData: PropTypes.array.isRequired,
  chartLabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  chartColors: PropTypes.array
};

export default function HistoryDistribution({ title, metric, subheader, chartColors, chartLabels, chartData, ...other }) {

  const chartOptions = {
    chart: {
      type: 'bar',
      height: 350
    },
    colors: chartColors,
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
        endingShape: 'rounded'
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    xaxis: {
      labels: {
        rotate: -45
      },
      tickPlacement: 'on',
      categories: chartLabels,
    },
    yaxis: {
      title: {
        text: `${metric}`
      }
    },
    fill: {
      opacity: 1
    },
    tooltip: {
      y: {
        formatter (val) {
          return `${val} ${metric}`
        }
      }
    }
  }

  return (
    <Card {...other}>
      <CardHeader title={title} subheader={subheader} />

      <Box sx={{ p: 3, pb: 1, mt: -5 }} dir="ltr">
        <ReactApexChart options={chartOptions} series={chartData} type="bar" height={350} />
      </Box>
    </Card>
  );
}

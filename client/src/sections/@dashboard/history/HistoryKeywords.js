import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

import { Card, CardHeader, Box, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles'

// ----------------------------------------------------------------------

HistoryKeywords.propTypes = {
  title: PropTypes.string,
  subheader: PropTypes.string,
  chartColors: PropTypes.arrayOf(PropTypes.string),
  chartData: PropTypes.object,
  top: PropTypes.number
};

export default function HistoryKeywords({ title, subheader, top, chartColors, chartData }) {
  
  const theme = useTheme()
  
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
    <Card>
      <CardHeader title={`${title} (Top ${top})`} subheader={subheader} />

      <Box sx={{ p: 3, pb: 3 }} dir="ltr">
        {chartLabels.length > 0 ? 
          <ReactApexChart 
            type='bar' 
            series={chartSeries} 
            options={chartOptions} 
            height={385} /> :
          <Typography
            variant='body2' 
            color={theme.palette.grey[600]}
          >
            There's no data to display!
          </Typography>
        }
      </Box>
    </Card>
  );
}

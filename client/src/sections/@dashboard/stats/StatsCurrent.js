import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';

// @mui
import { useTheme } from '@mui/material/styles';
import { Card, CardHeader } from '@mui/material';

// ----------------------------------------------------------------------

StatsCurrent.propTypes = {
  title: PropTypes.string,
  subheader: PropTypes.string,
  chartTitleColor: PropTypes.string,
  chartLabels: PropTypes.arrayOf(PropTypes.string),
  chartData: PropTypes.array,
  chartColors: PropTypes.arrayOf(PropTypes.string),
};

export default function StatsCurrent({
  title, subheader, chartTitleColor, 
  chartData, chartLabels, chartColors
}) {

  const theme = useTheme()
     
  const chartOptions = {
    chart: {
      height: 350,
      type: 'radialBar',
      offsetY: -10
    },
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        dataLabels: {
          name: {
            fontSize: '16px',
            color: chartTitleColor,
            offsetY: 120
          },
          value: {
            offsetY: 76,
            fontSize: '22px',
            color: theme.palette.grey[600],
            formatter (val) {
              return `${ val }%`;
            }
          }
        }
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
          shade: 'dark',
          shadeIntensity: 0.15,
          inverseColors: false,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 50, 65, 91]
      },
      colors: chartColors
    },
    stroke: {
      dashArray: 4
    },
    labels: chartLabels,
  }

  return (
    <Card>
      <CardHeader title={title} subheader={subheader} />
      <ReactApexChart options={chartOptions} series={chartData} type="radialBar" height={308} />
    </Card>
  );
}

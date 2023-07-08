import { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useOutletContext } from 'react-router-dom';

// @mui
import { 
  Grid, 
  Container, 
  Typography 
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

// components
import {
  StatsCurrent,
  StatsTimeline,
} from '../sections/@dashboard/stats'

// utils
import { 
  fromDayJSToEpochSecTime, 
  fromUnixTimeToDateString 
} from '../utils/time';
import { 
  roundNumber, 
} from '../utils/number';

// services
import { listStatsLog } from '../services/log';

// ----------------------------------------------------------------------

export default function StatsPage() {

  const theme = useTheme()

  const SAFE_CPU_THRESH = 95 // %
  const SAFE_RAM_THRESH = 95 // %

  const { 
    selectedIndex, systemList, 
    from, to
  } = useOutletContext()

  const [statsLogList, setStatsLogList] = useState([])

  useEffect(() => {
    const updateStatsLog = async () => {

      // Prepare data
      const systemId = systemList.length > 0 ? systemList[selectedIndex].system_id : 0
      const fromEpoch = fromDayJSToEpochSecTime(from)
      const toEpoch = fromDayJSToEpochSecTime(to)
      console.log(`New configs: \n- System: ${systemId}\n- From: ${from} ~ ${fromEpoch}\n- To: ${to} ~ ${toEpoch}`)
      
      // Load data here
      const response = await listStatsLog(systemId, fromEpoch, toEpoch)

      const content = await response.json()
      if (!content.success) {
        console.log('Cant load track log data!')
        setStatsLogList([])
      }
      else {
        setStatsLogList(content.data)
      }
    }
    
    updateStatsLog()
  }, [
    from, to,
    selectedIndex, systemList
  ])

  return (
    <>
      <Helmet>
        <title> Dashboard </title>
      </Helmet>

      <Container maxWidth="xl">

        {/* CPU logs */}
        <Typography variant="h4" sx={{ mb: 5 }}>
          CPU Usage
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={8}>

            {/* Timeline */}
            <StatsTimeline
              title="CPU in Percent"
              metric='%'
              subheader="(%)"
              chartLabels={
                statsLogList.map((log) => fromUnixTimeToDateString(Math.round(log.at)))
              }
              chartData={[
                {
                  name: 'CPU Usage',
                  type: 'line',
                  fill: 'solid',
                  data: statsLogList.map((log) => roundNumber(log.cpu_percent, 1))
                },
                {
                  name: 'Safe Usage',
                  type: 'area',
                  fill: 'gradient',
                  data: statsLogList.map(() => roundNumber(SAFE_CPU_THRESH))
                },
              ]}
              chartColors={[
                theme.palette.warning.main,
                theme.palette.success.main
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <StatsCurrent
              title="Current CPU Usage"
              chartData={[statsLogList.length > 0 ? statsLogList[statsLogList.length - 1].cpu_percent : 0]}
              chartLabels={['Current CPU Usage']}
              chartTitleColor={theme.palette.info.main}
              chartColors={[theme.palette.info.main]}
            />
          </Grid>
        
        </Grid>

        {/* RAM logs */}
        <Typography variant="h4" sx={{ mb: 5, mt: 8 }}>
          RAM Usage
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={8}>

            {/* Timeline */}
            <StatsTimeline
              title="RAM in Percent"
              metric='%'
              subheader="(%)"
              chartLabels={
                statsLogList.map((log) => fromUnixTimeToDateString(Math.round(log.at)))
              }
              chartData={[
                {
                  name: 'RAM Usage',
                  type: 'line',
                  fill: 'solid',
                  data: statsLogList.map((log) => roundNumber(log.ram_percent, 1))
                },
                {
                  name: 'Safe Usage',
                  type: 'area',
                  fill: 'gradient',
                  data: statsLogList.map(() => roundNumber(SAFE_RAM_THRESH))
                },
              ]}
              chartColors={[
                theme.palette.warning.main,
                theme.palette.success.main
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <StatsCurrent
              title="Current RAM Usage"
              chartData={[statsLogList.length > 0 ? statsLogList[statsLogList.length - 1].ram_percent : 0]}
              chartLabels={['Current RAM Usage']}
              chartTitleColor={theme.palette.warning.main}
              chartColors={[theme.palette.warning.main]}
            />
          </Grid>

          <Grid item xs={12} md={12} lg={12}>

            {/* Timeline */}
            <StatsTimeline
              title="RAM in GB"
              metric='GB'
              subheader="(GB)"
              chartLabels={
                statsLogList.map((log) => fromUnixTimeToDateString(Math.round(log.at)))
              }
              chartData={[
                {
                  name: 'RAM Usage',
                  type: 'area',
                  fill: 'gradient',
                  data: statsLogList.map((log) => roundNumber(log.ram_used, 2))
                },
                {
                  name: 'Safe Usage',
                  type: 'area',
                  fill: 'gradient',
                  data: statsLogList.map((log) => roundNumber(SAFE_RAM_THRESH * log.ram_total / 100, 2))
                },
                {
                  name: 'RAM Total',
                  type: 'area',
                  fill: 'gradient',
                  data: statsLogList.map((log) => roundNumber(log.ram_total, 2))
                },
              ]}
              chartColors={[
                theme.palette.warning.main,
                theme.palette.success.main,
                theme.palette.primary.main
              ]}
            />
          </Grid>
        
        </Grid>

      </Container>
    </>
  );
}

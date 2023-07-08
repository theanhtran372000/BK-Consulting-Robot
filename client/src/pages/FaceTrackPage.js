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
  FaceTrackSummary,
  FaceTrackTimeline,
  FaceTrackCurrent
} from '../sections/@dashboard/track'

// utils
import { fromDayJSToEpochSecTime, fromUnixTimeToDateString } from '../utils/time';
import { roundNumber, listAverage, listMedian } from '../utils/number';

// services
import { listFaceTrackLog } from '../services/log';

// ----------------------------------------------------------------------

export default function FaceTrackPage() {

  const REALTIME_FPS = 30

  const theme = useTheme()

  const [currentFpsRatio, setCurrentFpsRatio] = useState([0])
  const [currentLatencyRatio, setCurrentLatencyRatio] = useState([0])

  const { 
    selectedIndex, systemList, 
    from, to
  } = useOutletContext()

  const [trackLogList, setTrackLogList] = useState([])

  useEffect(() => {
    const updateTrackLog = async () => {

      // Prepare data
      const systemId = systemList.length > 0 ? systemList[selectedIndex].system_id : 0
      const fromEpoch = fromDayJSToEpochSecTime(from)
      const toEpoch = fromDayJSToEpochSecTime(to)
      console.log(`New configs: \n- System: ${systemId}\n- From: ${from} ~ ${fromEpoch}\n- To: ${to} ~ ${toEpoch}`)
      
      // Load data here
      const response = await listFaceTrackLog(systemId, fromEpoch, toEpoch)

      const content = await response.json()
      if (!content.success) {
        console.log('Cant load track log data!')
        setTrackLogList([])
      }
      else {
        setTrackLogList(content.data)
        setCurrentFpsRatio(
          content.data.length > 0 ? 
          [roundNumber(content.data[content.data.length - 1].fps / Math.max(...content.data.map((log) => log.fps)), 1) * 100] : 
          [0]
        )
        setCurrentLatencyRatio(
          content.data.length > 0 ? 
          [roundNumber(content.data[content.data.length - 1].elapsed_time / Math.max(...content.data.map((log) => log.elapsed_time)), 1) * 100] : 
          [0]
        )
      }
    }
    
    updateTrackLog()
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

        {/* FPS logs */}
        <Typography variant="h4" sx={{ mb: 5 }}>
          Frame per second
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={8}>

            {/* Timeline */}
            <FaceTrackTimeline
              title="FPS Logs"
              metric='FPS'
              subheader="(FPS)"
              chartLabels={
                trackLogList.map((log) => fromUnixTimeToDateString(Math.round(log.at)))
              }
              chartData={[
                {
                  name: 'Speed',
                  type: 'line',
                  fill: 'solid',
                  data: trackLogList.map((log) => roundNumber(log.fps, 1))
                },
                {
                  name: 'Realtime',
                  type: 'area',
                  fill: 'gradient',
                  data: trackLogList.map(() => REALTIME_FPS) ,
                },
              ]}
              chartColors={[
                theme.palette.success.main,
                theme.palette.error.main
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <FaceTrackCurrent
              title="Current/Max FPS"
              chartData={currentFpsRatio}
              chartTitleColor={theme.palette.success.main}
              chartLabels={['Current/Max FPS']}
              chartColors={[theme.palette.success.main]}
            />
          </Grid>
          
          {/* System stats */}
          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Max FPS" 
            subtitle='FPS' 
            value={
              trackLogList.length > 0 ? Math.max(...trackLogList.map((log) => log.fps)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Avg FPS" 
            subtitle='FPS' 
            color='info'
            value={
              trackLogList.length > 0 ? listAverage(trackLogList.map((log) => log.fps)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Med FPS" 
            subtitle='FPS'
            color='warning'
            value={
              trackLogList.length > 0 ? listMedian(trackLogList.map((log) => log.fps)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Min FPS" 
            subtitle='FPS'
            color='error'
            value={
              trackLogList.length > 0 ? Math.min(...trackLogList.map((log) => log.fps)) : '-'
            } 
            />
          </Grid>
        
        </Grid>

        {/* Latency logs */}
        <Typography variant="h4" sx={{ mb: 5, mt: 12 }}>
          Latency
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={8}>

            {/* Timeline */}
            <FaceTrackTimeline
              title="Latency"
              metric='ms'
              subheader="(miliseconds)"
              chartLabels={
                trackLogList.map((log) => fromUnixTimeToDateString(Math.round(log.at)))
              }
              chartData={[
                {
                  name: 'Latency',
                  type: 'line',
                  fill: 'solid',
                  data: trackLogList.map((log) => roundNumber(log.elapsed_time))
                },
                {
                  name: 'Realtime',
                  type: 'area',
                  fill: 'gradient',
                  data: trackLogList.map(() => roundNumber(1000 / REALTIME_FPS)) ,
                },
              ]}
              chartColors={[
                theme.palette.error.main,
                theme.palette.success.main
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <FaceTrackCurrent
              title="Current/Max latency"
              chartData={currentLatencyRatio}
              chartLabels={['Current/Max latency']}
              chartTitleColor={theme.palette.error.main}
              chartColors={[theme.palette.error.main]}
            />
          </Grid>
          
          {/* Response time */}
          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Max latency" 
            subtitle='ms' 
            color='error'
            value={
              trackLogList.length > 0 ? Math.max(...trackLogList.map((log) => log.elapsed_time)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Avg latency" 
            subtitle='ms' 
            color='warning'
            value={
              trackLogList.length > 0 ? listAverage(trackLogList.map((log) => log.elapsed_time)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Med latency" 
            subtitle='ms' 
            color='info'
            value={
              trackLogList.length > 0 ? listMedian(trackLogList.map((log) => log.elapsed_time)) : '-'
            } 
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FaceTrackSummary 
            title="Min latency" 
            subtitle='ms'
            value={
              trackLogList.length > 0 ? Math.min(...trackLogList.map((log) => log.elapsed_time)) : '-'
            } 
            />
          </Grid>
        </Grid>

      </Container>
    </>
  );
}

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
  HistoryDistribution,
  HistoryPieChart,
  HistoryTimeline,
  HistoryConversationList,
  HistoryKeywords
} from '../sections/@dashboard/history'

// utils
import { 
  fromDayJSToEpochSecTime, 
  fromUnixTimeToDate,
  fromUnixTimeToDateString
} from '../utils/time';
import { 
  listSum, 
  roundNumber
} from '../utils/number';

// services
import { listHistoryLog } from '../services/log';
import { extractKeywords } from '../services/answer';

// ----------------------------------------------------------------------

export default function HistoryPage() {

  const TOP_KEYWORDS = 10

  const theme = useTheme()

  const { 
    selectedIndex, systemList, 
    from, to
  } = useOutletContext()

  const [historyLogList, setHistoryLogList] = useState([])
  const [keywordFrequencies, setKeywordFrequencies] = useState(null)

  const getHistoryDistribution = () => {
    const distribute = [
      {
        name: 'AM',
        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      },
      {
        name: 'PM',
        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      }
    ]

    historyLogList.map((log) => {
      const h = fromUnixTimeToDate(log.start).getHours()

      if (h >= 12) {
        distribute[1].data[h - 12] += 1
      }
      else {
        distribute[0].data[h] += 1
      }

      return h
    })

    return distribute
  }

  const getDayNightRatio = () => {
    const distribute = getHistoryDistribution()
    return distribute.map((dis) => ({
        label: dis.name,
        value: listSum(dis.data)
      })
    )
  }

  useEffect(() => {
    const updateHistoryLog = async () => {

      // Prepare data
      const systemId = systemList.length > 0 ? systemList[selectedIndex].system_id : 0
      const fromEpoch = fromDayJSToEpochSecTime(from)
      const toEpoch = fromDayJSToEpochSecTime(to)
      console.log(`New configs: \n- System: ${systemId}\n- From: ${from} ~ ${fromEpoch}\n- To: ${to} ~ ${toEpoch}`)
      
      // Load data here
      const response = await listHistoryLog(systemId, fromEpoch, toEpoch)

      const content = await response.json()
      if (!content.success) {
        console.log('Cant load track log data!')
        setHistoryLogList([])
        setKeywordFrequencies(null)
      }
      else {
        setHistoryLogList(content.data)

        const questions = content.data.map((sample) => sample.question)
        const inputData = questions.join(' | ')

        const response = await extractKeywords(inputData)
        const keywordContent = await response.json()

        if (!keywordContent.success) {
          console.log('Cant extract keywords!')
          setKeywordFrequencies(null)
        }
        else {
          const keywords = JSON.parse(keywordContent.data.result)

          // Sort keywords from high to low
          const sortedKeywords = Object.fromEntries(
            Object.entries(keywords).sort(([, a], [, b]) => b - a)
          );
          
          setKeywordFrequencies(sortedKeywords)
        }
      }
    }
    
    updateHistoryLog()
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

        {/* Distribution */}
        <Typography variant="h4" sx={{ mb: 5 }}>
          Distribution
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={8}>

            {/* Timeline */}
            <HistoryDistribution
              title="Conversation distribution by time"
              metric='conversations'
              subheader="(conversations)"
              chartLabels={
                [...Array(12).keys()].map((h) => `${h}h - ${h + 1}h`)
              }
              chartData={getHistoryDistribution()}
              chartColors={[
                theme.palette.warning.main,
                theme.palette.info.main,
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <HistoryPieChart
              title="Day-Night Ratio"
              chartData={getDayNightRatio()}
              chartColors={[
                theme.palette.warning.main,
                theme.palette.info.main,
              ]}
            />
          </Grid>
        
        </Grid>

        {/* Duration */}
        <Typography variant="h4" sx={{ mb: 5, mt: 8 }}>
          Reponse Time
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={12} lg={12}>

            {/* Timeline */}
            <HistoryTimeline
              title="Response time"
              metric='seconds'
              subheader="(seconds)"
              chartLabels={
                historyLogList.map((log) => fromUnixTimeToDateString(roundNumber(log.start)))
              }
              chartData={[
                {
                  name: 'Response time',
                  type: 'area',
                  fill: 'gradient',
                  data: historyLogList.map((log) => roundNumber(log.end - log.start, 1))
                }
              ]}
              chartColors={[
                theme.palette.success.main
              ]}
            />
          </Grid>
        
        </Grid>


        {/* Conversations */}
        <Typography variant="h4" sx={{ mb: 5, mt: 8 }}>
          Conversations
        </Typography>

        <Grid container spacing={3}>

          <Grid item xs={12} md={6} lg={7}>
            <HistoryConversationList
              title="History"
              list={historyLogList}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={5}>
            <HistoryKeywords
              title='Keywords'
              chartData={keywordFrequencies}
              chartColors={[
                theme.palette.error.main
              ]}
              top={TOP_KEYWORDS}
            />
          </Grid>
        
        </Grid>

      </Container>
    </>
  );
}

import PropTypes from 'prop-types';
import { useState } from 'react'

// @mui
import { 
  Stack, Box,
  Card, CardHeader,
  Typography,
  Pagination
} from '@mui/material';
import { useTheme } from '@mui/material/styles'

// components
import Scrollbar from '../../../components/scrollbar';
import HistoryConversation from './HistoryConversation'

// ----------------------------------------------------------------------

HistoryConversationList.propTypes = {
  title: PropTypes.string,
  subheader: PropTypes.string,
  list: PropTypes.array.isRequired,
};

export default function HistoryConversationList({ title, subheader, list }) {

  const CONV_PER_PAGE = 5

  const [currentPage, setCurrentPage] = useState(1)
  const theme = useTheme()

  return (
    <Card sx={{
      height: '501px',
    }}>
      <CardHeader title={title} subheader={subheader} />

      <Scrollbar>
        <Stack height='500px' spacing={0} sx={{ p: 3, pr: 0, pl: 0 }}>
          {list.length > 0 ? 
            list.slice().reverse() // Reverse list
            .slice((currentPage - 1) * CONV_PER_PAGE, currentPage * CONV_PER_PAGE)
            .map((conv) => (
              <HistoryConversation key={conv._id} conversation={conv} />
            )) :
            <Typography
              sx={{
                px: 3
              }}
              variant='body2' 
              color={theme.palette.grey[600]}
            >
              History empty!
            </Typography>
          }
          
          {/* Pagination */}
          <Box sx={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mt: 1,
          }}>
            <Pagination 
              count={Math.ceil(list.length / CONV_PER_PAGE)} 
              shape="rounded" 
              onChange={(event, page) => {
                console.log(`Change to page ${ page }`)
                setCurrentPage(page)
              }}
            />
          </Box>
          
        </Stack>
      </Scrollbar>
    </Card>
  );
}
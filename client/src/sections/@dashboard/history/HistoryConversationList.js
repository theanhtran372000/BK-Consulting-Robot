import PropTypes from 'prop-types';

// @mui
import { 
  Stack, Card, CardHeader,Typography
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

  const theme = useTheme()

  return (
    <Card>
      <CardHeader title={title} subheader={subheader} />

      <Scrollbar>
        <Stack spacing={0} sx={{ p: 3, pr: 0, pl: 0 }}>
          {list.length > 0 ? 
            list.slice().reverse().map((conv) => (
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
        </Stack>
      </Scrollbar>
    </Card>
  );
}
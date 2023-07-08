import PropTypes from 'prop-types';

// @mui
import { 
  Stack, Card, CardHeader 
} from '@mui/material';

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

  return (
    <Card>
      <CardHeader title={title} subheader={subheader} />

      <Scrollbar>
        <Stack spacing={0} sx={{ p: 3, pr: 0, pl: 0 }}>
          {list.slice().reverse().map((conv) => (
            <HistoryConversation key={conv._id} conversation={conv} />
          ))}
        </Stack>
      </Scrollbar>
    </Card>
  );
}
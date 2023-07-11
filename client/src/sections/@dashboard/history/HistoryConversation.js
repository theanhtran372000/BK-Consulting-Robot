import { useState } from 'react'
import { useTheme } from '@mui/material/styles'
import PropTypes from 'prop-types';

// @mui
import { 
  Box, Stack, Typography,  
} from '@mui/material';

// utils
import { roundNumber } from '../../../utils/number';
import { fromUnixTimeToDate } from '../../../utils/time';
import { fToNow } from '../../../utils/formatTime';

// ----------------------------------------------------------------------

Conversation.propTypes = {
  conversation: PropTypes.object,
};

export default function Conversation({ conversation }) {

  const theme = useTheme()

  const [shrink, ] = useState(true)

  const { 
    question, answer,
    start, end,
    face
  } = conversation;

  return (
    <Stack 
      direction="row" 
      alignItems="center" 
      spacing={2}
      sx={{
        borderRadius: 1,
        px: 3,
        py: 1.5,
        '&:hover': {
          backgroundColor: theme.palette.grey[200]
        }
      }}
    >
      
      <Box 
        component="img" 
        src={`data:image/jpeg;base64,${face}`} 
        sx={{ 
          width: 48, 
          height: 48, 
          borderRadius: 1.5, 
          flexShrink: 0 
        }}
      />

      <Box sx={{ minWidth: 160, flexGrow: 1 }}>
        <Typography 
          color="inherit" 
          variant="subtitle2" 
          noWrap={shrink}
        >
          {`${question}`}
        </Typography>

        <Typography 
          variant="body2" 
          sx={{ color: 'text.secondary' }} 
          noWrap={shrink}
        >
          {`(${roundNumber(end - start, 1)}s) ${answer}`}
        </Typography>
      </Box>

      <Typography variant="caption" sx={{ pr: 3, flexShrink: 0, color: 'text.secondary' }}>
        {`${fToNow(fromUnixTimeToDate(start))}`}
      </Typography>
    </Stack>
  );
}

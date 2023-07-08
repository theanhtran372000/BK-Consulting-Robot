// React
import PropType from 'prop-types'

// Mui
import {
  Typography,
  Stack
} from '@mui/material'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'

// ----------------------------------------------------------

DateTimeSelect.propTypes = {
  title: PropType.string,
  bindTime: PropType.object,
  onChangeTime: PropType.func
}

export default function DateTimeSelect({ title, bindTime, onChangeTime }) {
  return (
    <Stack sx={{
      mt: 2.5,
      mx: 1.5
    }}>
      <Typography sx={{ mb: 0.8 }} variant='caption'>
        {title}
      </Typography>

      <DateTimePicker 
        label={title}
        value={bindTime}
        onChange={onChangeTime}
      />
    </Stack>
  )
}
// React
import PropType from 'prop-types'

// Mui
import {
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
      mt: 1.5,
      mx: 1.5
    }}>

      <DateTimePicker 
        sx={{
          mt: 0.5
        }}
        label={title}
        value={bindTime}
        onChange={onChangeTime}
      />
    </Stack>
  )
}
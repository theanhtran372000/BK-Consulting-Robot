import { PropTypes } from 'prop-types';

// @mui
import { 
  MenuItem, 
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';

// ----------------------------------------------------------------------

SystemSelect.propTypes = {
  systemList: PropTypes.array,
  handleChangeSystem: PropTypes.func,
  selectedIndex: PropTypes.number
}

export default function SystemSelect({ systemList, selectedIndex, handleChangeSystem }) {

  return (
    <>
      <FormControl sx={{
        mt: 2.5,
        mx: 1.5,
        minWidth: '256px'
      }}>
        
        <InputLabel id="demo-simple-select-label">System ID</InputLabel>
        <Select
          sx={{
            px: 1,
            py: 0.5,
            borderColor: 'gray',
            '&:hover': {
              borderColor: 'blue'
            },
          }}
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={systemList.length > 0 ? selectedIndex : 0}
          label="System ID"
          onChange={(e) => {
            const newIndex = e.target.value
            handleChangeSystem(newIndex)
          }}
        >
          
          {
            systemList.length > 0 ?
            systemList.map((system, index) => (
              <MenuItem 
                key={system._id} 
                value={index}
                selected={index === selectedIndex}
              >
                  {system.system_id}
              </MenuItem>
            )) :
            <MenuItem 
              key='0' 
              value='0'
              selected
            >
              No system found!
            </MenuItem>
          }

        </Select>
      </FormControl>
    </>
  );
}

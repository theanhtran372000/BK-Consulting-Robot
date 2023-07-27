import { useState } from 'react';
import { PropTypes } from 'prop-types'

// @mui
import { styled } from '@mui/material/styles';
import { 
  Input, 
  Slide, 
  Button, 
  IconButton, 
  InputAdornment, 
  ClickAwayListener,
  Typography
} from '@mui/material';

// utils
import { bgBlur } from '../../../utils/cssStyles';

// component
import Iconify from '../../../components/iconify';

// Service
import { addSystem } from '../../../services/system';

// ----------------------------------------------------------------------

const HEADER_MOBILE = 64;
const HEADER_DESKTOP = 92;

const StyledSearchbar = styled('div')(({ theme }) => ({
  ...bgBlur({ color: theme.palette.background.default }),
  top: 0,
  left: 0,
  zIndex: 99,
  width: '100%',
  display: 'flex',
  position: 'absolute',
  alignItems: 'center',
  height: HEADER_MOBILE,
  padding: theme.spacing(0, 3),
  boxShadow: theme.customShadows.z8,
  [theme.breakpoints.up('md')]: {
    height: HEADER_DESKTOP,
    padding: theme.spacing(0, 5),
  },
}));

// ----------------------------------------------------------------------

AddBar.propTypes = {
  systemList: PropTypes.array,
  setSystemList: PropTypes.func
}

export default function AddBar({ systemList, setSystemList }) {
  const [open, setOpen] = useState(false);

  const [systemId, setSystemId] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState(false)

  const handleOpen = () => {
    setOpen(!open);
    setSystemId('')
  };

  const handleClose = () => {
    setOpen(false);
  }

  const handleClick = async () => {
    handleClose()
    
    if(!systemId) {
      setError(true)
      setMessage('System Id is empty!')
      setTimeout(() => {
        setMessage('')
        setError(false)
      }, 5000)
      return
    }

    // Add new system
    const response = await addSystem(systemId)
    const content = await response.json()

    if(!content.success) {
      setError(true)
      setMessage(content.message)
      setTimeout(() => {
        setMessage('')
        setError(false)
      }, 5000)
    }
    else {
      setError(false)
      setSystemList([...systemList, {
        '_id': content.data._id,
        'system_id': systemId
      }])
      setMessage('Success!')
      setTimeout(() => {
        setMessage('')
      }, 5000)
    }
  };

  return (
    <ClickAwayListener onClickAway={handleClose}>
      <div>
        {!open && (
          <>
            <IconButton
              sx={{
                borderRadius: 1,
              }}
              onClick={handleOpen}
            >
              <Iconify sx={{ color: message ? (error? 'red' : 'green') : 'primary' }} icon="gridicons:add-outline" />
              <Typography 
                sx={{
                  marginLeft: 1,
                  color: message ? (error? 'red' : 'green') : 'primary'
                }}
                variant='body1'
              >
                { message || 'Add new system' }
              </Typography>
            </IconButton>

          </>
        )}

        <Slide direction="down" in={open} mountOnEnter unmountOnExit>
          <StyledSearchbar>
            <Input
              autoFocus
              fullWidth
              disableUnderline
              placeholder="System ID..."
              value={systemId}
              onChange={(e) => setSystemId(e.target.value)}
              startAdornment={
                <InputAdornment position="start">
                  <Iconify icon="pepicons-pop:gear" sx={{ color: 'text.disabled', width: 20, height: 20 }} />
                </InputAdornment>
              }
              sx={{ mr: 1, fontWeight: 'fontWeightLight' }}
            />
            <Button variant="contained" onClick={handleClick}>
              Add
            </Button>
          </StyledSearchbar>
        </Slide>
      </div>
    </ClickAwayListener>
  );
}

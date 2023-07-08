import { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

// @mui
import { styled } from '@mui/material/styles';

// Components
import Header from './header';
import Nav from './nav';

// Services
import { checkAuth } from '../../services/auth';
import { listSystem } from '../../services/system';

// Utils
import { deleteToken } from '../../utils/auth';
import { 
  getStartOfToday, 
  getEndOfToday, 
  fromDateToDayJS
} from '../../utils/time';

// ----------------------------------------------------------------------

const APP_BAR_MOBILE = 64;
const APP_BAR_DESKTOP = 92;

const StyledRoot = styled('div')({
  display: 'flex',
  minHeight: '100%',
  overflow: 'hidden',
});

const Main = styled('div')(({ theme }) => ({
  flexGrow: 1,
  overflow: 'auto',
  minHeight: '100%',
  paddingTop: APP_BAR_MOBILE + 24,
  paddingBottom: theme.spacing(10),
  [theme.breakpoints.up('lg')]: {
    paddingTop: APP_BAR_DESKTOP + 24,
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
  },
}));

// ----------------------------------------------------------------------

export default function DashboardLayout() {
  const navigate = useNavigate()

  const [open, setOpen] = useState(false)
  const [user, setUser] = useState(null)
  
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [systemList, setSystemList] = useState([])

  const [from, setFrom] = useState(fromDateToDayJS(getStartOfToday()))
  const [to, setTo] = useState(fromDateToDayJS(getEndOfToday()))

  // Handle time change
  const handleFromChange = (newFrom) => {
    setFrom(newFrom)
  }

  const handleToChange = (newTo) => {
    setTo(newTo)
  }

  // Handle system change
  const handleChangeSystem = (newIndex) => {
    setSelectedIndex(newIndex)
  }

  // Check auth here
  useEffect(() => {
    const getAuth = async () => {
      const result = await checkAuth()

      if (!result.success) {
        console.log(`Authentication failed: ${ result.message }`)
        deleteToken()
        return navigate('/')
      }
      console.log('User authenticated!')
      setUser(result.data)
      return null
    }

    const listMySystem = async () => {
      const response = await listSystem()
      const content = await response.json()

      if (content.success) {
        setSystemList(content.data)
      }
    }

    getAuth()
    listMySystem()

  }, [navigate])

  return (
    <StyledRoot>
      <Header 
        user={user} 
        onOpenNav={() => setOpen(true)} 
        systemList={systemList}
        setSystemList={setSystemList}
      />

      <Nav 
        user={user} 
        from={from}
        to={to}
        openNav={open} 
        onCloseNav={() => setOpen(false)} 
        systemList={systemList}
        selectedIndex={selectedIndex}
        handleChangeSystem={handleChangeSystem} 
        handleFromChange={handleFromChange}
        handleToChange={handleToChange}
      />

      <Main>
        <Outlet context={{
          selectedIndex,
          systemList,
          from, to
        }}/>
      </Main>
    </StyledRoot>
  );
}

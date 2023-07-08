// component
import SvgColor from '../../../components/svg-color';

// ----------------------------------------------------------------------

const icon = (name) => <SvgColor src={`/assets/icons/navbar/${name}.svg`} sx={{ width: 1, height: 1 }} />;

const navConfig = [
  {
    title: 'Face Track Log',
    path: '/dashboard/track',
    icon: icon('ic_track'),
  },
  {
    title: 'System Stats Log',
    path: '/dashboard/stats',
    icon: icon('ic_stats'),
  },
  {
    title: 'History Log',
    path: '/dashboard/history',
    icon: icon('ic_history'),
  }
];

export default navConfig;

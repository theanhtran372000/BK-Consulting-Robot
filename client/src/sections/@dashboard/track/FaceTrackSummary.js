// @mui
import PropTypes from 'prop-types';
import { Card, Typography } from '@mui/material';
import { roundNumber } from '../../../utils/number';

// ----------------------------------------------------------------------

FaceTrackSummary.propTypes = {
  color: PropTypes.string,
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  value: PropTypes.any,
  sx: PropTypes.object,
};

export default function FaceTrackSummary({ title, subtitle, value, color = 'primary', sx, ...other }) {
  return (
    <Card
      sx={{
        py: 3,
        boxShadow: 2,
        textAlign: 'center',
        color: (theme) => theme.palette[color].darker,
        bgcolor: (theme) => theme.palette[color].lighter,
        ...sx,
      }}
      {...other}
    >
      <Typography variant="subtitle2" sx={{ opacity: 0.8, fontSize: 16 }}>
        {title}
      </Typography>

      <Typography variant="h4">{typeof(value) === 'string' ? value : roundNumber(value, 1)}</Typography>

      <Typography variant="subtitle2" sx={{ opacity: 0.5, fontSize: 14 }}>
        {subtitle}
      </Typography>
    </Card>
  );
}

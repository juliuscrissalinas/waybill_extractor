import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Box, 
  Button, 
  Container,
  useScrollTrigger,
  Slide,
  IconButton,
  useMediaQuery,
  useTheme,
  Tooltip,
  Fade
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import GitHubIcon from '@mui/icons-material/GitHub';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ThemeToggle from './ThemeToggle';

// Hide AppBar on scroll down
function HideOnScroll(props) {
  const { children } = props;
  const trigger = useScrollTrigger();

  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

const Header = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isDarkMode = theme.palette.mode === 'dark';

  return (
    <HideOnScroll>
      <AppBar 
        position="sticky" 
        color="default" 
        elevation={0}
        sx={{ 
          backgroundColor: isDarkMode 
            ? 'rgba(30, 30, 30, 0.8)' 
            : 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(8px)',
          borderBottom: '1px solid',
          borderColor: 'divider',
          transition: 'background-color 0.5s ease',
        }}
      >
        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ py: 1 }}>
            <Fade in={true} timeout={1000}>
              <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                <DescriptionIcon 
                  sx={{ 
                    mr: 1.5, 
                    color: 'primary.main',
                    fontSize: 28,
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1) rotate(5deg)',
                    }
                  }} 
                />
                <Typography 
                  variant="h6" 
                  component="div" 
                  sx={{ 
                    fontWeight: 700,
                    background: isDarkMode
                      ? 'linear-gradient(90deg, #90CAF9 0%, #CE93D8 100%)'
                      : 'linear-gradient(90deg, #2196F3 0%, #673AB7 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-0.5px'
                  }}
                >
                  Waybill Extractor
                </Typography>
              </Box>
            </Fade>

            {isMobile ? (
              <Box>
                <ThemeToggle />
                <Tooltip title="Help">
                  <IconButton color="primary" size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="GitHub">
                  <IconButton color="primary" size="small" sx={{ ml: 1 }}>
                    <GitHubIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            ) : (
              <Fade in={true} timeout={1200}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ThemeToggle />
                  <Button 
                    variant="text" 
                    color="primary"
                    startIcon={<HelpOutlineIcon />}
                    sx={{ 
                      mr: 2,
                      transition: 'transform 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                      }
                    }}
                  >
                    Help
                  </Button>
                  <Button 
                    variant="outlined" 
                    color="primary"
                    startIcon={<GitHubIcon />}
                    href="https://github.com/yourusername/waybill-extractor"
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ 
                      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: theme.palette.mode === 'dark' 
                          ? '0 4px 12px rgba(144, 202, 249, 0.2)' 
                          : '0 4px 12px rgba(33, 150, 243, 0.2)',
                      }
                    }}
                  >
                    GitHub
                  </Button>
                </Box>
              </Fade>
            )}
          </Toolbar>
        </Container>
      </AppBar>
    </HideOnScroll>
  );
};

export default Header; 
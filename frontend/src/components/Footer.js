import React from 'react';
import { Box, Container, Typography, Link, Divider, IconButton, Tooltip, useTheme, Fade } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: 'background.paper',
        borderTop: '1px solid',
        borderColor: 'divider',
        transition: 'background-color 0.5s ease',
      }}
    >
      <Container maxWidth="lg">
        <Fade in={true} timeout={800}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Box sx={{ mb: { xs: 2, sm: 0 } }}>
              <Typography variant="body2" color="text.secondary" align="center">
                © {currentYear} Waybill Extractor. All rights reserved.
              </Typography>
              <Typography variant="caption" color="text.secondary" align="center" display="block">
                Built with React, Material-UI, and Django
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ display: 'flex', mr: 2 }}>
                <Link 
                  href="#" 
                  color="inherit" 
                  sx={{ 
                    mx: 1,
                    transition: 'color 0.2s ease',
                    '&:hover': {
                      color: 'primary.main',
                    }
                  }}
                >
                  <Typography variant="body2">Privacy</Typography>
                </Link>
                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
                <Link 
                  href="#" 
                  color="inherit" 
                  sx={{ 
                    mx: 1,
                    transition: 'color 0.2s ease',
                    '&:hover': {
                      color: 'primary.main',
                    }
                  }}
                >
                  <Typography variant="body2">Terms</Typography>
                </Link>
                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
                <Link 
                  href="#" 
                  color="inherit" 
                  sx={{ 
                    mx: 1,
                    transition: 'color 0.2s ease',
                    '&:hover': {
                      color: 'primary.main',
                    }
                  }}
                >
                  <Typography variant="body2">Contact</Typography>
                </Link>
              </Box>
              
              <Box>
                <Tooltip title="GitHub">
                  <IconButton 
                    size="small" 
                    color="inherit"
                    sx={{
                      transition: 'transform 0.2s ease, color 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: isDarkMode ? '#90CAF9' : '#2196F3',
                      }
                    }}
                  >
                    <GitHubIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="LinkedIn">
                  <IconButton 
                    size="small" 
                    color="inherit"
                    sx={{
                      transition: 'transform 0.2s ease, color 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: isDarkMode ? '#90CAF9' : '#2196F3',
                      }
                    }}
                  >
                    <LinkedInIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Twitter">
                  <IconButton 
                    size="small" 
                    color="inherit"
                    sx={{
                      transition: 'transform 0.2s ease, color 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: isDarkMode ? '#90CAF9' : '#2196F3',
                      }
                    }}
                  >
                    <TwitterIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default Footer; 
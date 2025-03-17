import React, { useMemo } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import WaybillUploader from './components/WaybillUploader';
import Header from './components/Header';
import Footer from './components/Footer';
import { ColorModeProvider, useColorMode } from './context/ColorModeContext';

// App with theme
const AppWithTheme = () => {
  const { mode } = useColorMode();

  // Create theme based on color mode
  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      ...(mode === 'light' 
        ? {
            // Light mode colors
            primary: {
              main: '#2196F3',
              light: '#64B5F6',
              dark: '#1976D2',
              contrastText: '#fff',
            },
            secondary: {
              main: '#673AB7',
              light: '#9575CD',
              dark: '#512DA8',
              contrastText: '#fff',
            },
            background: {
              default: '#f8f9fa',
              paper: '#ffffff',
            },
            text: {
              primary: '#2c3e50',
              secondary: '#7f8c8d',
            },
            divider: '#e0e0e0',
          }
        : {
            // Dark mode colors
            primary: {
              main: '#90CAF9',
              light: '#BBDEFB',
              dark: '#42A5F5',
              contrastText: '#000',
            },
            secondary: {
              main: '#CE93D8',
              light: '#E1BEE7',
              dark: '#AB47BC',
              contrastText: '#000',
            },
            background: {
              default: '#121212',
              paper: '#1E1E1E',
            },
            text: {
              primary: '#E0E0E0',
              secondary: '#AAAAAA',
            },
            divider: '#424242',
          }),
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 700,
        letterSpacing: '-0.5px',
      },
      h2: {
        fontWeight: 700,
        letterSpacing: '-0.5px',
      },
      h3: {
        fontWeight: 700,
        letterSpacing: '-0.5px',
      },
      h4: {
        fontWeight: 600,
        letterSpacing: '-0.25px',
      },
      h5: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 600,
      },
      button: {
        fontWeight: 600,
        textTransform: 'none',
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            },
          },
          contained: {
            '&:hover': {
              boxShadow: '0 6px 16px rgba(0,0,0,0.12)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 12,
          },
          elevation1: {
            boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
          },
          elevation4: {
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
            },
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 6,
          },
        },
      },
    },
  }), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          minHeight: '100vh',
          bgcolor: 'background.default',
          transition: 'background-color 0.5s ease',
        }}
      >
        <Header />
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column' 
          }}
        >
          <WaybillUploader />
        </Box>
        <Footer />
      </Box>
    </ThemeProvider>
  );
};

// Main App component with ColorModeProvider
function App() {
  return (
    <ColorModeProvider>
      <AppWithTheme />
    </ColorModeProvider>
  );
}

export default App; 
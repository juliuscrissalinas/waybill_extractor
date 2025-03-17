import React, { createContext, useState, useContext, useMemo, useEffect } from 'react';

// Create context
export const ColorModeContext = createContext({
  toggleColorMode: () => {},
  mode: 'light',
});

// Custom hook to use the color mode context
export const useColorMode = () => useContext(ColorModeContext);

// Provider component
export const ColorModeProvider = ({ children }) => {
  // Check if user has a preference stored in localStorage
  const storedMode = localStorage.getItem('colorMode');
  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Initialize state with stored preference, system preference, or default to light
  const [mode, setMode] = useState(storedMode || (prefersDarkMode ? 'dark' : 'light'));

  // Update localStorage when mode changes
  useEffect(() => {
    localStorage.setItem('colorMode', mode);
  }, [mode]);

  // Toggle function
  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  // Memoize the context value
  const contextValue = useMemo(
    () => ({
      toggleColorMode,
      mode,
    }),
    [mode]
  );

  return (
    <ColorModeContext.Provider value={contextValue}>
      {children}
    </ColorModeContext.Provider>
  );
};

export default ColorModeProvider; 
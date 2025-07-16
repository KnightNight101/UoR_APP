import { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Vite + React + Material UI
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
          <Typography variant="h4" gutterBottom>
            Welcome!
          </Typography>
          <Button variant="contained" onClick={() => setCount((count) => count + 1)}>
            Count is {count}
          </Button>
          <Typography variant="body1">
            Edit <code>src/App.jsx</code> and save to test HMR.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click on the Vite and React logos to learn more.
          </Typography>
        </Box>
      </Container>
    </>
  );
}

export default App;

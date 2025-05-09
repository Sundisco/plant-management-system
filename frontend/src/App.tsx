import { Garden } from './components/Garden';
import { Container, Typography } from '@mui/material';

// Default user ID for the supervisor
const DEFAULT_USER_ID = 1;

function App() {
  return (
    <Container>
      <Typography variant="h3" component="h1" gutterBottom>
        Plant Management System
      </Typography>
      <Garden userId={DEFAULT_USER_ID} />
    </Container>
  );
}

export default App; 
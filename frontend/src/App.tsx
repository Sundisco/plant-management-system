import { Garden } from './components/Garden';
import { Container, Typography } from '@mui/material';

function App() {
  return (
    <Container>
      <Typography variant="h3" component="h1" gutterBottom>
        Plant Search
      </Typography>
      <Garden />
    </Container>
  );
}

export default App; 
import { ThemeProvider } from './contexts/ThemeContext';
import { ChatProvider } from './contexts/ChatContext';
import { AppShell } from './components/AppShell';

function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <AppShell />
      </ChatProvider>
    </ThemeProvider>
  );
}

export default App;

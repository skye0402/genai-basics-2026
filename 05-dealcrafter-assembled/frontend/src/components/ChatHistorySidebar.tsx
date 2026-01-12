import { useCallback, useMemo, useState } from 'react';
import {
  Button,
  FlexBox,
  Input,
  SideNavigation,
  SideNavigationItem,
  SideNavigationSubItem,
  Text,
  Title,
  type SideNavigationPropTypes,
  type InputPropTypes,
} from '@ui5/webcomponents-react';
import '@ui5/webcomponents-icons/dist/add.js';
import '@ui5/webcomponents-icons/dist/delete.js';
import '@ui5/webcomponents-icons/dist/customer-history.js';
import '@ui5/webcomponents-icons/dist/refresh.js';
import '@ui5/webcomponents-icons/dist/menu.js';
import { useChat } from '../contexts/ChatContext';

function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date);
}

interface ChatHistorySidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export function ChatHistorySidebar({ collapsed, onToggleCollapse }: ChatHistorySidebarProps) {
  const {
    sessions,
    activeSessionId,
    loadSession,
    createSession,
    deleteSession,
    refreshSessions,
  } = useChat();
  const [search, setSearch] = useState('');

  const filteredSessions = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) {
      return sessions;
    }
    return sessions.filter((session) =>
      session.title.toLowerCase().includes(term) || session.last_message.toLowerCase().includes(term)
    );
  }, [search, sessions]);

  const handleSelectionChange: SideNavigationPropTypes['onSelectionChange'] = (event) => {
    const sessionId = event.detail.item.dataset.sessionId;
    if (sessionId) {
      void loadSession(sessionId);
    }
  };

  const handleSearchInput = useCallback<NonNullable<InputPropTypes['onInput']>>((event) => {
    const value = event.target.value ?? '';
    setSearch(value);
  }, []);

  const handleCreateSession = async () => {
    await createSession();
  };

  const handleDelete = async () => {
    if (activeSessionId) {
      await deleteSession(activeSessionId);
    }
  };

  return (
    <FlexBox
      direction="Column"
      style={{
        width: collapsed ? '3rem' : '260px',
        maxWidth: collapsed ? '3rem' : '260px',
        minWidth: collapsed ? '3rem' : '220px',
        borderRight: '1px solid var(--sapList_BorderColor)',
        backgroundColor: 'var(--sapShellColor)',
        padding: '0.75rem',
        gap: '0.75rem',
        flexShrink: 0,
        transition: 'width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease',
      }}
    >
      <FlexBox justifyContent="SpaceBetween" alignItems="Center">
        {collapsed ? (
          <Button 
            icon="menu" 
            design="Transparent" 
            tooltip="Expand Sidebar" 
            onClick={onToggleCollapse}
            style={{ width: '100%' }}
          />
        ) : (
          <>
            <Title level="H5">Chat History</Title>
            <FlexBox style={{ gap: '0.25rem' }}>
              <Button icon="menu" design="Transparent" tooltip="Collapse Sidebar" onClick={onToggleCollapse} />
              <Button icon="refresh" design="Transparent" tooltip="Refresh" onClick={() => void refreshSessions()} />
              <Button icon="add" design="Emphasized" tooltip="New Chat" onClick={handleCreateSession} />
            </FlexBox>
          </>
        )}
      </FlexBox>

      {!collapsed && (
        <>
          <Input value={search} onInput={handleSearchInput} placeholder="Search conversations..." showClearIcon />

          <FlexBox direction="Column" style={{ gap: '0.5rem' }}>
            <Button
              icon="delete"
              design="Transparent"
              disabled={!activeSessionId}
              onClick={handleDelete}
            >
              Delete Current
            </Button>
          </FlexBox>

          <div style={{ flex: 1, minHeight: 0 }}>
            {filteredSessions.length === 0 ? (
              <FlexBox
                direction="Column"
                alignItems="Center"
                justifyContent="Center"
                style={{ padding: '1rem', gap: '0.5rem', textAlign: 'center' }}
              >
                <Text>No conversations yet.</Text>
                <Text style={{ fontSize: '0.875rem' }}>Create a new chat to get started.</Text>
              </FlexBox>
            ) : (
              <SideNavigation
                onSelectionChange={handleSelectionChange}
                style={{
                  flex: 1,
                  minHeight: 0,
                }}
              >
                {filteredSessions.map((session) => (
                  <SideNavigationItem
                    key={session.session_id}
                    text={session.title || 'Untitled chat'}
                    icon="customer-history"
                    selected={session.session_id === activeSessionId}
                    data-session-id={session.session_id}
                  >
                    <SideNavigationSubItem text={`Updated ${formatTimestamp(session.timestamp)}`} />
                    <SideNavigationSubItem text={`${session.message_count} messages`} />
                  </SideNavigationItem>
                ))}
              </SideNavigation>
            )}
          </div>
        </>
      )}
    </FlexBox>
  );
}

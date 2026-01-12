/**
 * Main application shell with ShellBar and layout.
 */
import { ShellBar, Avatar, FlexBox, Menu, MenuItem, Icon } from '@ui5/webcomponents-react';
import '@ui5/webcomponents-icons/dist/palette.js';
import '@ui5/webcomponents-icons/dist/document.js';
import '@ui5/webcomponents-icons/dist/discussion.js';
import '@ui5/webcomponents-icons/dist/slim-arrow-down.js';
import { ThemeSelector } from './ThemeSelector';
import { ChatInterface } from './ChatInterface';
import { DocumentManagement } from './DocumentManagement';
import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { ChatHistorySidebar } from './ChatHistorySidebar';

type ViewMode = 'chat' | 'documents';

export function AppShell() {
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('chat');
  const [showViewMenu, setShowViewMenu] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!showThemeSelector) {
      return;
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setShowThemeSelector(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showThemeSelector]);

  return (
    <FlexBox
      direction="Column"
      style={{
        height: '100%',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Shell Bar with clickable logo/title */}
      <ShellBar
        primaryTitle="Fiori AI Chat"
        secondaryTitle={viewMode === 'chat' ? 'Financial Data Assistant' : 'Document Management'}
        logo={
          <div
            id="logoMenuButton"
            role="button"
            tabIndex={0}
            aria-haspopup="menu"
            aria-expanded={showViewMenu}
            onClick={() => setShowViewMenu(!showViewMenu)}
            onKeyDown={(event: KeyboardEvent<HTMLDivElement>) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                setShowViewMenu(!showViewMenu);
              }
            }}
            style={{
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.375rem',
              background: showViewMenu ? 'var(--sapShellColor)' : 'transparent',
            }}
          >
            <img src="/sap-logo.svg" alt="SAP Logo" style={{ height: '2rem' }} />
            <Icon name="slim-arrow-down" style={{ color: 'var(--sapShell_TextColor)' }} />
          </div>
        }
        profile={
          <Avatar
            initials="U"
            colorScheme="Accent1"
            onClick={() => setShowThemeSelector(!showThemeSelector)}
            style={{ cursor: 'pointer' }}
          />
        }
      />

      {/* View Selection Menu */}
      <Menu
        open={showViewMenu}
        opener="logoMenuButton"
        onClose={() => setShowViewMenu(false)}
        onItemClick={(e) => {
          const text = e.detail.text;
          if (text === 'Chat') {
            setViewMode('chat');
          } else if (text === 'Document Management') {
            setViewMode('documents');
          }
          setShowViewMenu(false);
        }}
      >
        <MenuItem icon="discussion" text="Chat" />
        <MenuItem icon="document" text="Document Management" />
      </Menu>

      {/* Theme Selector Popover */}
      {showThemeSelector && (
        <div
          ref={popoverRef}
          style={{
            position: 'absolute',
            top: '3rem',
            right: '1rem',
            zIndex: 1000,
          }}
        >
          <ThemeSelector onClose={() => setShowThemeSelector(false)} />
        </div>
      )}

      {/* Main Content */}
      <FlexBox
        direction="Row"
        style={{
          flex: 1,
          overflow: 'hidden',
          backgroundColor: 'var(--sapBackgroundColor)',
        }}
      >
        {/* Show sidebar only in chat mode */}
        {viewMode === 'chat' && (
          <ChatHistorySidebar 
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          />
        )}
        
        <FlexBox
          direction="Column"
          style={{
            flex: 1,
            overflow: 'hidden',
            minWidth: 0,
          }}
        >
          {viewMode === 'chat' ? <ChatInterface /> : <DocumentManagement />}
        </FlexBox>
      </FlexBox>
    </FlexBox>
  );
}

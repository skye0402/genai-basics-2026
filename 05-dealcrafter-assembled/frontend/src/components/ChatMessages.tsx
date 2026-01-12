/**
 * Chat messages display component.
 */
import { useEffect, useRef, useState } from 'react';
import { FlexBox, BusyIndicator, Text, Button, Toast } from '@ui5/webcomponents-react';
import '@ui5/webcomponents-icons/dist/copy.js';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { useChat } from '../contexts/ChatContext';
import { MessageBubble } from './MessageBubble';
import { TableDisplay } from './TableDisplay';
import './markdown.css';

export function ChatMessages() {
  const { messages, currentResponse, isStreaming } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const handleCopyStreaming = async () => {
    try {
      const textContent = currentResponse
        .filter(c => c.type === 'text')
        .map(c => c.content)
        .join('');
      await navigator.clipboard.writeText(textContent);
      setToastMessage('Message copied to clipboard');
      setToastOpen(true);
    } catch (err) {
      setToastMessage('Failed to copy message');
      setToastOpen(true);
    }
  };

  // Auto-scroll to bottom when new messages arrive
  // Use setTimeout to ensure tables are fully rendered before scrolling
  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
    return () => clearTimeout(timer);
  }, [messages, currentResponse]);

  return (
    <FlexBox
      direction="Column"
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem',
        gap: '1rem',
      }}
    >
      {/* Display chat history */}
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}

      {/* Display streaming response - only show while streaming AND has content */}
      {currentResponse.length > 0 && (
        <FlexBox direction="Column" style={{ gap: '0.5rem' }}>
          {/* Show accumulated text content */}
          {currentResponse.some(c => c.type === 'text') && (
            <FlexBox justifyContent="Start">
              <FlexBox direction="Column" style={{ position: 'relative', maxWidth: '70%' }}>
                <div
                  style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--sapList_Background)',
                    border: '1px solid var(--sapList_BorderColor)',
                    color: 'var(--sapTextColor)',
                  }}
                >
                  <div className="chat-markdown">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                    >
                      {currentResponse
                        .filter(c => c.type === 'text')
                        .map(c => c.content)
                        .join('')}
                    </ReactMarkdown>
                  </div>
                </div>
                <Button
                  icon="copy"
                  design="Transparent"
                  onClick={handleCopyStreaming}
                  tooltip="Copy message"
                  style={{
                    position: 'absolute',
                    bottom: '0.25rem',
                    right: '0.25rem',
                    opacity: 0.6,
                    minWidth: '2rem',
                    height: '2rem',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '1';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '0.6';
                  }}
                />
              </FlexBox>
            </FlexBox>
          )}
          
          {/* Show tables */}
          {currentResponse
            .filter(c => c.type === 'table' && c.tableData)
            .map((content) => (
              <TableDisplay key={content.id} data={content.tableData!} />
            ))}
        </FlexBox>
      )}

      {/* Streaming indicator */}
      {isStreaming && (
        <FlexBox justifyContent="Start">
          <BusyIndicator active size="S" style={{ padding: '0.5rem' }} />
        </FlexBox>
      )}

      {/* Empty state */}
      {messages.length === 0 && currentResponse.length === 0 && !isStreaming && (
        <FlexBox
          direction="Column"
          alignItems="Center"
          justifyContent="Center"
          style={{ flex: 1, gap: '1rem' }}
        >
          <Text
            style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: 'var(--sapContent_LabelColor)',
            }}
          >
            Welcome to Fiori AI Chat
          </Text>
          <Text style={{ color: 'var(--sapContent_LabelColor)' }}>
            Ask me about products, sales data, or financial reports
          </Text>
        </FlexBox>
      )}

      <div ref={messagesEndRef} />

      {/* Toast for copy feedback */}
      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
      >
        {toastMessage}
      </Toast>
    </FlexBox>
  );
}

/**
 * Individual message bubble component.
 */
import { useState } from 'react';
import { FlexBox, Text, Avatar, Button, Toast } from '@ui5/webcomponents-react';
import '@ui5/webcomponents-icons/dist/copy.js';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import type { ChatMessage, TableData } from '../types/index';
import { TableDisplay } from './TableDisplay';
import './markdown.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content || '');
      setToastMessage('Message copied to clipboard');
      setToastOpen(true);
    } catch (err) {
      setToastMessage('Failed to copy message');
      setToastOpen(true);
    }
  };

  return (
    <FlexBox
      direction="Column"
      alignItems={isUser ? 'End' : 'Start'}
      style={{ gap: '0.5rem' }}
    >
      <FlexBox
        justifyContent={isUser ? 'End' : 'Start'}
        alignItems="Start"
        style={{ gap: '0.5rem' }}
      >
        {!isUser && (
          <Avatar
            size="XS"
            initials="AI"
            colorScheme="Accent6"
            style={{ flexShrink: 0 }}
          />
        )}

        <FlexBox 
          direction="Column" 
          style={{ 
            position: 'relative', 
            maxWidth: '70%', 
            minWidth: message.attachments && message.attachments.length > 0 ? '220px' : 'auto',
          }}
        >
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '0.5rem',
              backgroundColor: isUser
                ? 'var(--sapButton_Emphasized_Background)'
                : 'var(--sapList_Background)',
              color: isUser
                ? 'var(--sapButton_Emphasized_TextColor)'
                : 'var(--sapTextColor)',
              border: isUser ? 'none' : '1px solid var(--sapList_BorderColor)',
            }}
          >
            {message.content && (
              <div className="chat-markdown">
                {isUser ? (
                  <Text style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem' }}>{message.content}</Text>
                ) : (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeRaw]}
                  >
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
            )}
            <Text
              style={{
                fontSize: '0.75rem',
                marginTop: '0.25rem',
                opacity: 0.7,
              }}
            >
              {new Date(message.timestamp).toLocaleTimeString()}
            </Text>
            
            {/* Display image attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <FlexBox
                wrap="Wrap"
                style={{
                  gap: '0.5rem',
                  marginTop: message.content ? '0.5rem' : '0',
                  maxWidth: '100%',
                }}
              >
                {message.attachments.map((attachment) => (
                  <img
                    key={attachment.id}
                    src={attachment.previewUrl}
                    alt={attachment.name}
                    loading="eager"
                    onLoad={() => {
                      setLoadedImages(prev => new Set(prev).add(attachment.id));
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      setPreviewImage(attachment.previewUrl);
                    }}
                    style={{
                      maxWidth: '200px',
                      maxHeight: '200px',
                      width: 'auto',
                      height: 'auto',
                      borderRadius: '0.25rem',
                      objectFit: 'contain',
                      cursor: 'pointer',
                      transition: 'opacity 0.3s ease-in',
                      border: '1px solid var(--sapList_BorderColor)',
                      opacity: loadedImages.has(attachment.id) ? 1 : 0,
                      minHeight: loadedImages.has(attachment.id) ? 'auto' : '100px',
                    }}
                    onMouseEnter={(e) => {
                      if (loadedImages.has(attachment.id)) {
                        e.currentTarget.style.opacity = '0.85';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (loadedImages.has(attachment.id)) {
                        e.currentTarget.style.opacity = '1';
                      }
                    }}
                  />
                ))}
              </FlexBox>
            )}
          </div>
          <Button
            icon="copy"
            design="Transparent"
            onClick={handleCopy}
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

        {isUser && (
          <Avatar
            size="XS"
            initials="ME"
            colorScheme="Accent1"
            style={{ flexShrink: 0 }}
          />
        )}
      </FlexBox>

      {/* Display tables if present */}
      {message.tables?.map((table: TableData, idx: number) => (
        <TableDisplay key={`table-${idx}`} data={table} />
      ))}

      {previewImage && (
        <div
          role="button"
          tabIndex={-1}
          onClick={() => setPreviewImage(null)}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              setPreviewImage(null);
            }
          }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            cursor: 'zoom-out',
          }}
        >
          <img
            src={previewImage}
            alt="Full size preview"
            onClick={(e) => {
              e.stopPropagation();
              setPreviewImage(null);
            }}
            style={{
              maxWidth: '90vw',
              maxHeight: '90vh',
              borderRadius: '0.5rem',
              boxShadow: '0 0 20px rgba(0, 0, 0, 0.5)',
            }}
          />
        </div>
      )}

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

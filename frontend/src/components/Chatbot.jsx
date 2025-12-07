import { useState, useEffect, useRef } from 'react';
import { chatAPI, alumniAPI } from '../utils/api';
import '../styles/chatbot.css';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [memberCards, setMemberCards] = useState([]);
  const [expandedCard, setExpandedCard] = useState(null);
  const [generatingEmailFor, setGeneratingEmailFor] = useState(null);
  const [generatedEmail, setGeneratedEmail] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Load chat history when component mounts or chat opens
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadChatHistory();
    }
  }, [isOpen]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, memberCards]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await chatAPI.getHistory();
      if (response.success && response.messages) {
        setMessages(response.messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })));
        if (response.session_id) {
          setSessionId(response.session_id);
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    // Don't clear member cards here - keep them visible until new ones are returned

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(userMessage, sessionId);

      if (response.success) {
        // Add AI response with member cards attached to the message
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.response,
          memberCards: response.member_cards || null
        }]);

        // Update session ID if new
        if (response.session_id) {
          setSessionId(response.session_id);
        }

        // Also update the current memberCards state for expanded card functionality
        if (response.member_cards && response.member_cards.length > 0) {
          setMemberCards(response.member_cards);
        }
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I had trouble processing your request. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const response = await chatAPI.newSession();
      if (response.success) {
        setSessionId(response.session_id);
        setMessages([]);
        setMemberCards([]);
        setExpandedCard(null);
      }
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle AI email generation for a member
  const handleGenerateEmail = async (member) => {
    const memberId = member.csv_row_id || member.name;
    if (generatingEmailFor === memberId) return;

    setGeneratingEmailFor(memberId);
    setGeneratedEmail(null);

    try {
      const response = await alumniAPI.generateEmail(member);
      if (response.success && response.email) {
        setGeneratedEmail({
          memberId,
          email: response.email,
          subject: response.subject || 'Connecting from Purdue THINK'
        });
      } else {
        console.error('Failed to generate email:', response.error);
      }
    } catch (error) {
      console.error('Error generating email:', error);
    } finally {
      setGeneratingEmailFor(null);
    }
  };

  // Copy generated email to clipboard
  const handleCopyGeneratedEmail = async () => {
    if (!generatedEmail) return;
    try {
      const fullText = `Subject: ${generatedEmail.subject}\n\n${generatedEmail.email}`;
      await navigator.clipboard.writeText(fullText);
      alert('Email copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const fallbackLogo = '/assets/Copy of P Logo for dark background (1).png';

  const renderMemberCard = (member) => {
    const profileImage = member.profile_image_url || '';
    const isValidUrl = profileImage && String(profileImage).startsWith('http');
    const imageUrl = isValidUrl ? profileImage : fallbackLogo;
    const cardId = member.csv_row_id || member.name;
    const isExpanded = expandedCard === cardId;

    const roleDisplay = member.roles_list?.length > 0
      ? member.roles_list.slice(0, 2).join(' / ')
      : member.role_title || 'N/A';

    const companyDisplay = member.companies_list?.length > 0
      ? member.companies_list.slice(0, 2).join(', ')
      : member.company || 'N/A';

    // Full details for expanded view
    const allRoles = member.roles_list?.length > 0
      ? [...new Set(member.roles_list)].filter(r => r && r !== 'null')
      : [];
    const allCompanies = member.companies_list?.length > 0
      ? [...new Set(member.companies_list)].filter(c => c && c !== 'null')
      : [];

    const infoItems = [];
    if (member.major) infoItems.push(member.major);
    if (member.grad_year) infoItems.push(`Class of ${String(member.grad_year).replace('.0', '')}`);
    if (member.location) infoItems.push(member.location);

    return (
      <div key={cardId} className={`chat-member-card ${isExpanded ? 'expanded' : ''}`}>
        <div
          className="chat-member-card-header"
          onClick={() => setExpandedCard(isExpanded ? null : cardId)}
        >
          <div className="chat-member-image">
            {isValidUrl ? (
              <img
                src={imageUrl}
                alt={member.name}
                onError={(e) => {
                  e.target.src = fallbackLogo;
                }}
              />
            ) : (
              <img src={fallbackLogo} alt="THINK Logo" />
            )}
          </div>
          <div className="chat-member-info">
            <h4>{member.name}</h4>
            <p className="chat-member-role">{roleDisplay}</p>
            <p className="chat-member-company">{companyDisplay}</p>
          </div>
          <div className="chat-member-expand">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>

        {isExpanded && (
          <div className="chat-member-expanded">
            {/* Profile Image - Larger */}
            <div className="chat-member-expanded-image">
              <img
                src={imageUrl}
                alt={member.name}
                onError={(e) => {
                  e.target.src = fallbackLogo;
                }}
              />
            </div>

            {/* Full Name and Title */}
            <h3 className="chat-member-expanded-name">{member.name}</h3>
            {member.headline && (
              <p className="chat-member-expanded-headline">{member.headline}</p>
            )}

            {/* Info Items */}
            {infoItems.length > 0 && (
              <p className="chat-member-expanded-info">{infoItems.join(' • ')}</p>
            )}

            {/* All Roles */}
            {allRoles.length > 0 && (
              <div className="chat-member-expanded-section">
                <span className="chat-member-expanded-label">Roles:</span>
                <span>{allRoles.join(' → ')}</span>
              </div>
            )}

            {/* All Companies */}
            {allCompanies.length > 0 && (
              <div className="chat-member-expanded-section">
                <span className="chat-member-expanded-label">Companies:</span>
                <span>{allCompanies.join(', ')}</span>
              </div>
            )}

            {/* Actions */}
            <div className="chat-member-expanded-actions">
              {member.linkedin && (
                <a
                  href={member.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="chat-member-action-btn linkedin"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  LinkedIn
                </a>
              )}
              {member.email && (
                <a
                  href={`mailto:${member.email}`}
                  className="chat-member-action-btn email"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                  Email
                </a>
              )}
              <button
                className={`chat-member-action-btn ai-email ${generatingEmailFor === cardId ? 'loading' : ''}`}
                onClick={() => handleGenerateEmail(member)}
                disabled={generatingEmailFor === cardId}
              >
                {generatingEmailFor === cardId ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" className="spinning">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="31.4" strokeDashoffset="10" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                )}
                AI Email
              </button>
            </div>

            {/* Generated Email Display */}
            {generatedEmail && generatedEmail.memberId === cardId && (
              <div className="chat-member-generated-email">
                <div className="chat-email-header">
                  <span>Generated Email</span>
                  <button onClick={() => setGeneratedEmail(null)} className="chat-email-close">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
                <div className="chat-email-subject">
                  <strong>Subject:</strong> {generatedEmail.subject}
                </div>
                <div className="chat-email-body">{generatedEmail.email}</div>
                <button className="chat-email-copy" onClick={handleCopyGeneratedEmail}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  Copy to Clipboard
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        className={`chatbot-toggle ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          <img
            src="/assets/Copy of P Logo for dark background (1).png"
            alt="The THINKer"
            style={{ width: '40px', height: '40px', objectFit: 'contain' }}
          />
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="chatbot-panel">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-title">
              <img
                src="/assets/Copy of P Logo for dark background (1).png"
                alt="THINK Logo"
                className="chatbot-header-logo"
              />
              <span>The THINKer</span>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button className="chatbot-reset-chat" onClick={handleNewChat} title="Reset conversation">
                Reset chat
              </button>
              <button className="chatbot-header-close" onClick={() => setIsOpen(false)} title="Close chat">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <div className="chatbot-welcome">
                <div className="chatbot-welcome-icon">
                  <img
                    src="/assets/Copy of P Logo for dark background (1).png"
                    alt="THINK Logo"
                    className="chatbot-welcome-logo"
                  />
                </div>
                <h3>The THINKer</h3>
                <p>I can help you with networking advice, finding THINK members, and using the platform.</p>
                <div className="chatbot-suggestions">
                  <button onClick={() => setInputValue('How do I write a good networking email?')}>
                    How to write a networking email?
                  </button>
                  <button onClick={() => setInputValue('Find members who work in consulting')}>
                    Find consulting members
                  </button>
                  <button onClick={() => setInputValue('What are the best networking practices?')}>
                    Networking best practices
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg, index) => (
              <div key={index} className="chatbot-message-group">
                <div className={`chatbot-message ${msg.role}`}>
                  {msg.role === 'assistant' && (
                    <div className="chatbot-message-avatar">
                      <img
                        src="/assets/Copy of P Logo for dark background (1).png"
                        alt="THINK"
                        className="chatbot-avatar-img"
                      />
                    </div>
                  )}
                  <div className="chatbot-message-content">
                    {msg.content}
                  </div>
                </div>
                {/* Member Cards inline with the message that generated them */}
                {msg.memberCards && msg.memberCards.length > 0 && (
                  <div className="chatbot-member-cards">
                    <div className="chatbot-member-cards-label">Found these members:</div>
                    {msg.memberCards.map(renderMemberCard)}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chatbot-message assistant">
                <div className="chatbot-message-avatar">
                  <img
                    src="/assets/Copy of P Logo for dark background (1).png"
                    alt="THINK"
                    className="chatbot-avatar-img"
                  />
                </div>
                <div className="chatbot-message-content">
                  <div className="chatbot-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form className="chatbot-input-form" onSubmit={handleSendMessage}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about networking..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !inputValue.trim()}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default Chatbot;

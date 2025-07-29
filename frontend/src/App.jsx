import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [clarification, setClarification] = useState('');
  const [followUp, setFollowUp] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false);
  const [isShowingAnswer, setIsShowingAnswer] = useState(false);
  
  const scrollContainerRef = useRef(null);
  const isUserScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef(null);

  // Custom components for ReactMarkdown
  const markdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={tomorrow}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    table({ children }) {
      return (
        <div className="table-container">
          <table className="trace-table">{children}</table>
        </div>
      );
    },
    th({ children }) {
      return <th className="table-header">{children}</th>;
    },
    td({ children }) {
      return <td className="table-cell">{children}</td>;
    }
  };

  // Track user scrolling to prevent auto-scroll interference
  const handleScroll = () => {
    isUserScrollingRef.current = true;
    
    // Clear existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    // Reset scroll flag after user stops scrolling
    scrollTimeoutRef.current = setTimeout(() => {
      isUserScrollingRef.current = false;
    }, 1000);
  };

  // Smart auto-scroll only when appropriate
  const conditionalAutoScroll = () => {
    if (!scrollContainerRef.current || isUserScrollingRef.current) return;
    
    const container = scrollContainerRef.current;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const isNearBottom = scrollTop + clientHeight >= scrollHeight - 50;
    
    // Only auto-scroll if user is already near the bottom
    if (isNearBottom) {
      setTimeout(() => {
        if (!isUserScrollingRef.current) {
          container.scrollTo({
            top: scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 300);
    }
  };


  const BASE_URL = import.meta.env.VITE_API_URL;
  const generateQuestion = async () => {
    setIsGeneratingQuestion(true);
    try {
      const res = await axios.post(`${BASE_URL}/predict`, {
        paper_code: 'MATH101'
      });
      
      const newQuestion = res.data.question;
      setQuestion(newQuestion);
      setAnswer(''); // Reset current answer state
      
      // APPEND to chat history - don't replace
      setChatHistory(prev => [
        ...prev,
        { role: 'system', content: newQuestion, type: 'question', id: Date.now() }
      ]);
      
      conditionalAutoScroll();
    } catch (err) {
      console.error('Error generating question:', err);
    } finally {
      setIsGeneratingQuestion(false);
    }
  };

  const showAnswer = async () => {
    setIsShowingAnswer(true);
    try {
      const res = await axios.post(`${BASE_URL}/answer`);
      const newAnswer = res.data.answer;
      setAnswer(newAnswer);
      
      // APPEND to chat history
      setChatHistory(prev => [
        ...prev,
        { role: 'system', content: newAnswer, type: 'answer', id: Date.now() }
      ]);
      
      conditionalAutoScroll();
    } catch (err) {
      console.error('Error showing answer:', err);
    } finally {
      setIsShowingAnswer(false);
    }
  };

  const askClarification = async () => {
    if (!followUp.trim()) return;
    
    try {
      // Add user question to chat
      setChatHistory(prev => [
        ...prev,
        { role: 'user', content: followUp, type: 'clarification-question', id: Date.now() }
      ]);
      
      const res = await axios.post(`${BASE_URL}/clarify`, {
        follow_up: followUp
      });
      
      const newClarification = res.data.clarification;
      setClarification(newClarification);
      
      // Add system response to chat
      setChatHistory(prev => [
        ...prev,
        { role: 'system', content: newClarification, type: 'clarification', id: Date.now() }
      ]);
      
      setFollowUp('');
      conditionalAutoScroll();
    } catch (err) {
      console.error('Clarification failed:', err);
    }
  };

  const clearHistory = () => {
    setChatHistory([]);
    setQuestion('');
    setAnswer('');
    setClarification('');
    setFollowUp('');
  };

  const goBackToHome = () => {
    setQuestion('');
    setAnswer('');
    setClarification('');
    setFollowUp('');
    setChatHistory([]);
  };

  // Check if current question has an answer
  const currentQuestionHasAnswer = () => {
    if (!question) return false;
    
    // Find the current question in chat history
    const questions = chatHistory.filter(msg => msg.type === 'question');
    const currentQuestionEntry = questions[questions.length - 1];
    
    if (!currentQuestionEntry) return false;
    
    // Check if there's an answer after this question
    const currentQuestionIndex = chatHistory.findIndex(msg => msg.id === currentQuestionEntry.id);
    const hasAnswerAfter = chatHistory.slice(currentQuestionIndex + 1).some(msg => msg.type === 'answer');
    
    return hasAnswerAfter;
  };

  return (
    <div className="App">
      {/* Background decorative elements */}
      <div className="bg-decorations">
        <div className="bg-glow bg-glow-1"></div>
        <div className="bg-glow bg-glow-2"></div>
        <div className="bg-glow bg-glow-3"></div>
        <div className="bg-grid"></div>
      </div>

      {/* Header */}
      <header className="app-header">
        <div className="header-container">
          <div className="brand-section" onClick={goBackToHome}>
            <div className="logo-icon">
              <div className="logo-inner">
                <span className="logo-text">AI</span>
              </div>
            </div>
            <div className="brand-text">
              <h1 className="brand-title">Askara AI</h1>
              <p className="brand-subtitle">Smart AI Exam Prediction Tool</p>
            </div>
          </div>
          <div className="header-actions">
            {question && (
              <>
                <button className="btn btn-outline" onClick={goBackToHome}>
                  <span className="btn-text">New Session</span>
                </button>
                {chatHistory.length > 0 && (
                  <button className="btn btn-secondary" onClick={clearHistory}>
                    <span className="btn-text">Clear History</span>
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {!question ? (
          // Hero Section - Landing Page
          <div className="hero-section">
            <div className="hero-content">
              <div className="hero-text">
                <h2 className="hero-title">Ready to practice?</h2>
                <p className="hero-description">
                  Click generate question to start your AI-powered exam practice session. 
                  Get instant answers, clarification, and detailed explanations.
                </p>
              </div>
              <div className="hero-action">
                <button 
                  className="btn btn-hero" 
                  onClick={generateQuestion}
                  disabled={isGeneratingQuestion}
                >
                  <span className="btn-text">
                    {isGeneratingQuestion ? 'Generating...' : 'Generate Question'}
                  </span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          // Study Session Layout
          <div className="study-layout">
            <div className="study-grid">
              {/* Left Column - Scrollable Questions & Answers */}
              <div className="main-study-content" ref={scrollContainerRef} onScroll={handleScroll}>
                <div className="study-content-inner">
                  {/* Current Question */}
                  <section className="content-card question-section">
                    <div className="section-header">
                      <div className="section-icon">📘</div>
                      <h2 className="section-title">
                        Question {chatHistory.filter(msg => msg.type === 'question').length}
                      </h2>
                    </div>
                    <div className="section-content">
                      <ReactMarkdown 
                        components={markdownComponents}
                        remarkPlugins={[remarkGfm]}
                      >
                        {question}
                      </ReactMarkdown>
                    </div>
                  </section>
                  
                  {/* Action Buttons - BOTH SHOW WHEN QUESTION EXISTS */}
                  <div className="action-section">
                    <div className="action-buttons">
                      {/* Show Answer Button - Always visible when there's a question without answer */}
                      {!currentQuestionHasAnswer() && (
                        <button 
                          className="btn btn-action" 
                          onClick={showAnswer}
                          disabled={isShowingAnswer}
                        >
                          <span className="btn-text">
                            {isShowingAnswer ? 'Loading Answer...' : 'Show Answer'}
                          </span>
                        </button>
                      )}
                      
                      {/* Next Question Button - ALWAYS visible when there's a question */}
                      <button 
                        className="btn btn-next" 
                        onClick={generateQuestion}
                        disabled={isGeneratingQuestion}
                      >
                        <span className="btn-text">
                          {isGeneratingQuestion ? 'Generating...' : 'Next Question'}
                        </span>
                      </button>
                    </div>
                  </div>
                  
                  {/* Current Answer (if shown) */}
                  {answer && (
                    <section className="content-card answer-section">
                      <div className="section-header">
                        <div className="section-icon">📝</div>
                        <h2 className="section-title">
                          Answer {chatHistory.filter(msg => msg.type === 'answer').length}
                        </h2>
                      </div>
                      <div className="section-content">
                        <ReactMarkdown 
                          components={markdownComponents}
                          remarkPlugins={[remarkGfm]}
                        >
                          {answer}
                        </ReactMarkdown>
                      </div>
                    </section>
                  )}

                  {/* Previous Q&A History */}
                  {chatHistory.length > 2 && (
                    <div className="history-section">
                      <h3 className="history-title">Previous Questions & Answers</h3>
                      {chatHistory
                        .filter(msg => msg.type === 'question' || msg.type === 'answer')
                        .slice(0, -2) // Exclude current Q&A
                        .reduce((acc, msg, index, arr) => {
                          if (msg.type === 'question') {
                            const nextAnswer = arr[index + 1];
                            if (nextAnswer && nextAnswer.type === 'answer') {
                              acc.push({ question: msg, answer: nextAnswer });
                            }
                          }
                          return acc;
                        }, [])
                        .map((qa, qaIndex) => (
                          <div key={qa.question.id} className="qa-pair">
                            <section className="content-card question-section">
                              <div className="section-header">
                                <div className="section-icon">📘</div>
                                <h3 className="section-title">Question {qaIndex + 1}</h3>
                              </div>
                              <div className="section-content">
                                <ReactMarkdown 
                                  components={markdownComponents}
                                  remarkPlugins={[remarkGfm]}
                                >
                                  {qa.question.content}
                                </ReactMarkdown>
                              </div>
                            </section>
                            
                            <section className="content-card answer-section">
                              <div className="section-header">
                                <div className="section-icon">📝</div>
                                <h3 className="section-title">Answer {qaIndex + 1}</h3>
                              </div>
                              <div className="section-content">
                                <ReactMarkdown 
                                  components={markdownComponents}
                                  remarkPlugins={[remarkGfm]}
                                >
                                  {qa.answer.content}
                                </ReactMarkdown>
                              </div>
                            </section>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column - Clarifications */}
              <div className="sidebar-content">
                <section className="content-card clarification-section">
                  <div className="section-header">
                    <div className="section-icon">💡</div>
                    <h3 className="section-title">Ask Questions</h3>
                  </div>

                  {/* Input Section */}
                  <div className="clarification-input">
                    <div className="input-group">
                      <textarea
                        value={followUp}
                        onChange={(e) => setFollowUp(e.target.value)}
                        placeholder="Ask for clarification on any part..."
                        className="clarify-input"
                        rows={3}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            askClarification();
                          }
                        }}
                      />
                      <button className="btn btn-clarify" onClick={askClarification}>
                        <span className="btn-text">Ask</span>
                      </button>
                    </div>
                  </div>

                  {/* Display clarification history */}
                  <div className="clarification-history">
                    {(() => {
                      const clarifications = chatHistory.filter(msg => 
                        msg.type === 'clarification-question' || msg.type === 'clarification'
                      );
                      const lastFew = clarifications.slice(-8);
                      return lastFew.length > 0 ? (
                        <>
                          <div className="history-header">
                            <h4>Recent Clarifications</h4>
                          </div>
                          {lastFew.map((message) => (
                            <div key={message.id} className={`clarification-message ${message.role}`}>
                              <div className="message-header">
                                <span className="message-role">
                                  {message.role === 'user' ? '👤 You asked:' : '💡 Answer:'}
                                </span>
                              </div>
                              <div className="message-content">
                                <ReactMarkdown 
                                  components={markdownComponents}
                                  remarkPlugins={[remarkGfm]}
                                >
                                  {message.content}
                                </ReactMarkdown>
                              </div>
                            </div>
                          ))}
                        </>
                      ) : (
                        <div className="empty-state">
                          <div className="empty-icon">🤔</div>
                          <p>No questions yet. Ask your first clarification above!</p>
                        </div>
                      );
                    })()}
                  </div>
                </section>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
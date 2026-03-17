import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, AlertCircle, Shield, CheckCircle2, Users, MessageSquare, FileText, Mic, MicOff } from 'lucide-react';
import PhaseIndicator from '@/components/PhaseIndicator';
import MessageCard, { type AgentMessage } from '@/components/MessageCard';
import HumanInputPanel from '@/components/HumanInputPanel';
import TypingIndicator from '@/components/TypingIndicator';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';

const API_BASE = 'http://localhost:8000';

const PHASE_MAP: Record<string, number> = {
  research: 0,
  debate_round1: 1,
  hitl: 2,
  debate_round2: 3,
  debate_round3: 4,
  synthesis: 5,
};

const EXAMPLE_QUESTIONS = [
  "Should Spotify acquire a podcast analytics company?",
  "Should we expand our SaaS product to the European market?",
  "Should we pivot from B2C to B2B?",
];

const Index = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [context, setContext] = useState(''); 
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);

  const voiceQuestion = useSpeechRecognition(
    useCallback((text: string) => setQuestion((prev) => prev + (prev ? ' ' : '') + text), [])
  );

  const scrollRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [boardType, setBoardType] = useState('tech');
  const [user, setUser] = useState<any>(null);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [authError, setAuthError] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [compareSession, setCompareSession] = useState<any>(null);
  const [compareWith, setCompareWith] = useState<any>(null);

  const scrollToBottom = useCallback(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isPaused, scrollToBottom]);

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  const initSSE = useCallback((sid: string) => {
    const es = new EventSource(`${API_BASE}/api/${sid}/agents_research`);
    eventSourceRef.current = es;
    setIsThinking(true);

    es.addEventListener('phase', (e) => {
      try {
        const data = JSON.parse(e.data);
        
        if (data.phase === 'research') {
            setCurrentPhase(0);
        } else if (data.phase === 'debate' && data.round === 1) {
            setCurrentPhase(1);
        } else if (data.phase === 'debate' && data.round === 2) {
            setCurrentPhase(3);
        } else if (data.phase === 'debate' && data.round === 3) {
            setCurrentPhase(4);
        } else if (data.phase === 'synthesis') {
            setCurrentPhase(5);
        }
        
        setIsThinking(true);
      } catch { /* ignore */ }
    });
    es.addEventListener('agent_start', (e) => {
    try {
        const data = JSON.parse(e.data);
        setThinkingAgent(`${data.agent} is ${data.action}...`);
        setIsThinking(true);
    } catch { /* ignore */ }
});

    es.addEventListener('agent_message', (e) => {
      try {
        const data = JSON.parse(e.data) as AgentMessage;
        setMessages((prev) => [...prev, data]);
        setIsThinking(false);
        setThinkingAgent(null);
        // Brief pause then show thinking again for next message
        setTimeout(() => setIsThinking(true), 800);
      } catch { /* ignore */ }
    });

    es.addEventListener('pause', (e) => {
      try { JSON.parse(e.data); } catch { /* ignore */ }
      setIsPaused(true);
      setIsThinking(false);
      setCurrentPhase(2); // HITL phase
    });

    es.addEventListener('heartbeat', () => {
      // Keep connection alive while waiting for human input
    });

    es.addEventListener('brief_ready', (e) => {
      try { JSON.parse(e.data); } catch { /* ignore */ }
    });

    es.addEventListener('resume', () => {
      setIsPaused(false);
      setIsThinking(true);
    });

    es.addEventListener('error', (e) => {
      try {
        const data = JSON.parse((e as MessageEvent).data);
        setError(data.message || 'Pipeline error occurred.');
      } catch { /* ignore */ }
    });

    es.addEventListener('complete', () => {
      setIsComplete(true);
      setIsThinking(false);
      es.close();
    });

    es.onerror = () => {
      // Only show error if stream wasn't intentionally closed
      if (es.readyState !== EventSource.CLOSED) {
        setError('Connection to Board lost. Attempting to reconnect...');
      }
    };
  }, []);

  const startDebate = async () => {
    if (!question.trim()) return;
    setIsStarting(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/session/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, context, board_type: boardType,user_id: user?.user_id || '' }),
      });
      const data = await res.json();
      setSessionId(data.session);

      // Upload file if one was selected
      if (uploadedFile) {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        await fetch(`${API_BASE}/api/${data.session}/upload`, {
          method: 'POST',
          body: formData,
        });
      }

      initSSE(data.session);
    } catch {
      setError('Failed to initialize session. Ensure backend is running.');
      setIsStarting(false);
    }
  };


  const submitHumanInput = async (text: string, targetAgent: string = 'all') => {
    if (!sessionId) return;
    try {
      const response = await fetch(`${API_BASE}/api/${sessionId}/human_input`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ human_ip: text, target_agent: targetAgent }),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      // Only update state after backend confirms receipt
      setIsPaused(false);
      setIsThinking(true);
    } catch {
      setError('Failed to send input. Please try again.');
    }
  };
  const handleLogin = async () => {
    setAuthError('');
    try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: authEmail, password: authPassword }),
        });
        const data = await res.json();
        if (data.status === 'success') {
            setUser(data.user);
        } else {
            setAuthError(data.message);
        }
    } catch {
        setAuthError('Connection failed');
    }
};

  const handleSignup = async () => {
      setAuthError('');
      try {
          const res = await fetch(`${API_BASE}/api/auth/signup`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email: authEmail, password: authPassword, name: authName }),
          });
          const data = await res.json();
          if (data.status === 'success') {
              setUser(data.user);
          } else {
              setAuthError(data.message);
          }
      } catch {
          setAuthError('Connection failed');
      }
  };

  const loadHistory = async () => {
      if (!user) return;
      try {
          const res = await fetch(`${API_BASE}/api/sessions/history/${user.user_id}`);
          const data = await res.json();
          setHistory(data.sessions);
          setShowHistory(true);
      } catch {
          setError('Failed to load history');
      }
  };
  // Auth screen
if (!user) {
    return (
        <div className="min-h-svh flex flex-col bg-grid-pattern">
            <div className="flex-1 flex flex-col items-center justify-center px-6">
                <motion.div
                    initial={{ opacity: 0, y: 24 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-8"
                >
                    <h1 className="text-5xl md:text-7xl font-serif font-bold tracking-tight mb-4 gold-gradient-text">
                        SHADOW BOARD
                    </h1>
                    <p className="text-muted-foreground text-sm">
                        AI-Powered Executive Decision Simulation
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="w-full max-w-md"
                >
                    <div className="glass-card-strong rounded-xl p-6 md:p-8">
                        <div className="flex gap-4 mb-6">
                            <button
                                onClick={() => setAuthMode('login')}
                                className={`flex-1 py-2 text-sm font-semibold uppercase tracking-wider rounded-lg transition-all ${
                                    authMode === 'login'
                                        ? 'gold-gradient text-primary-foreground'
                                        : 'text-muted-foreground hover:text-foreground'
                                }`}
                            >
                                Login
                            </button>
                            <button
                                onClick={() => setAuthMode('signup')}
                                className={`flex-1 py-2 text-sm font-semibold uppercase tracking-wider rounded-lg transition-all ${
                                    authMode === 'signup'
                                        ? 'gold-gradient text-primary-foreground'
                                        : 'text-muted-foreground hover:text-foreground'
                                }`}
                            >
                                Sign Up
                            </button>
                        </div>

                        {authMode === 'signup' && (
                            <input
                                value={authName}
                                onChange={(e) => setAuthName(e.target.value)}
                                placeholder="Your name"
                                className="w-full bg-secondary/40 border border-border rounded-lg p-3 text-sm text-foreground focus:outline-none focus:border-primary/40 transition-colors mb-3 placeholder:text-muted-foreground/50"
                            />
                        )}

                        <input
                            value={authEmail}
                            onChange={(e) => setAuthEmail(e.target.value)}
                            placeholder="Email"
                            type="email"
                            className="w-full bg-secondary/40 border border-border rounded-lg p-3 text-sm text-foreground focus:outline-none focus:border-primary/40 transition-colors mb-3 placeholder:text-muted-foreground/50"
                        />

                        <input
                            value={authPassword}
                            onChange={(e) => setAuthPassword(e.target.value)}
                            placeholder="Password"
                            type="password"
                            onKeyDown={(e) => e.key === 'Enter' && (authMode === 'login' ? handleLogin() : handleSignup())}
                            className="w-full bg-secondary/40 border border-border rounded-lg p-3 text-sm text-foreground focus:outline-none focus:border-primary/40 transition-colors mb-4 placeholder:text-muted-foreground/50"
                        />

                        {authError && (
                            <p className="text-destructive text-xs mb-3">{authError}</p>
                        )}

                        <button
                            onClick={authMode === 'login' ? handleLogin : handleSignup}
                            className="w-full py-3 rounded-lg gold-gradient text-primary-foreground font-bold uppercase tracking-wider text-sm hover:opacity-90 transition-all"
                        >
                            {authMode === 'login' ? 'Login' : 'Create Account'}
                        </button>
                    </div>
                </motion.div>
            </div>
            <AppFooter />
        </div>
    );
}
  const agentCount = new Set(messages.map(m => m.agent)).size;
  const roundCount = new Set(messages.filter(m => m.round).map(m => m.round)).size;

  // Landing page
  if (!sessionId) {
    return (
      <div className="min-h-svh flex flex-col bg-grid-pattern">
        {/* Top bar */}
        <div className="flex justify-end p-4 md:p-6 gap-3">
        <span className="flex items-center gap-2 glass-card rounded-full px-4 py-2 text-[10px] font-mono text-muted-foreground">
            Welcome, {user.name}
        </span>
        <button
            onClick={loadHistory}
            className="flex items-center gap-2 glass-card rounded-full px-4 py-2 hover:bg-primary/10 transition-colors"
        >
            <FileText size={14} className="text-primary" />
            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Past Sessions</span>
        </button>
        <button
            onClick={() => setUser(null)}
            className="flex items-center gap-2 glass-card rounded-full px-4 py-2 hover:bg-destructive/10 transition-colors"
        >
            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Logout</span>
        </button>
        <div className="flex items-center gap-2 glass-card rounded-full px-4 py-2">
            <Shield size={14} className="text-primary" />
            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Powered by AIRIA</span>
        </div>
        </div>

      {showHistory && (
    <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto px-6 mb-8">
        <div className="glass-card-strong rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="font-serif text-xl font-bold gold-gradient-text">Past Sessions</h2>
                <button
                    onClick={() => setShowHistory(false)}
                    className="text-xs text-muted-foreground hover:text-foreground"
                >
                    ✕ Close
                </button>
            </div>
            {history.length === 0 ? (
                <p className="text-muted-foreground text-sm">No past sessions yet.</p>
            ) : (
                <div className="space-y-3">
                    {history.map((s: any) => (
                  <div
                      key={s.session_id}
                      className="glass-card rounded-lg p-4 hover:bg-primary/5 transition-colors"
                  >
                      <div className="flex justify-between items-start mb-2">
                          <p className="text-sm font-medium text-foreground flex-1">{s.question}</p>
                          <span className="text-[10px] font-mono text-muted-foreground ml-2">
                              {new Date(s.created_at).toLocaleDateString()}
                          </span>
                      </div>
                      <div className="flex gap-2 text-xs mb-3 flex-wrap">
                          <span className="uppercase font-mono text-muted-foreground px-2 py-0.5 rounded-full bg-muted/50">
                              {s.board_type}
                          </span>
                          {Object.entries(s.votes || {}).map(([agent, vote]: [string, any]) => (
                              <span key={agent} className={`px-2 py-0.5 rounded-full ${
                                  vote === 'GO' ? 'bg-cmo/10 text-cmo' :
                                  vote === 'NO-GO' ? 'bg-devil/10 text-devil' : 'bg-legal/10 text-legal'
                              }`}>
                                  {agent}: {vote}
                              </span>
                          ))}
                      </div>
                      {s.moderator_summary && (
                          <details className="text-xs text-muted-foreground">
                              <summary className="cursor-pointer hover:text-foreground transition-colors font-mono uppercase tracking-wider mb-2">
                                  View Strategy Brief
                              </summary>
                              <div className="bg-secondary/30 rounded-lg p-3 mt-1 text-foreground/70 whitespace-pre-wrap max-h-48 overflow-y-auto">
                                  {s.moderator_summary}
                              </div>
                          </details>
                      )}
                      <div className="flex gap-2 mt-3">
                          <button
                              onClick={() => {
                                  setQuestion(s.question);
                                  setContext(s.context || '');
                                  setBoardType(s.board_type || 'tech');
                                  setShowHistory(false);
                              }}
                              className="text-[10px] font-mono uppercase tracking-wider px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:border-primary/40 transition-all"
                          >
                              Re-run this question
                          </button>
                          <button
                              onClick={() => {
                                  if (compareSession && compareSession.session_id !== s.session_id) {
                                      setCompareWith(s);
                                  } else {
                                      setCompareSession(s);
                                  }
                              }}
                              className="text-[10px] font-mono uppercase tracking-wider px-3 py-1.5 rounded-lg border border-primary/30 text-primary hover:bg-primary/10 transition-all"
                          >
                              {compareSession?.session_id === s.session_id ? '✓ Selected' : 'Compare'}
                          </button>
                      </div>
                  </div>
              ))}
                </div>
            )}
            {compareSession && compareWith && (
    <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-6 border-t border-border/30 pt-6"
    >
        <div className="flex justify-between items-center mb-4">
            <h3 className="font-serif text-lg font-bold gold-gradient-text">
                Session Comparison
            </h3>
            <button
                onClick={() => { setCompareSession(null); setCompareWith(null); }}
                className="text-xs text-muted-foreground hover:text-foreground"
            >
                ✕ Clear comparison
            </button>
        </div>
        <div className="grid grid-cols-2 gap-4">
            {[compareSession, compareWith].map((s: any, idx: number) => (
                <div key={idx} className="glass-card rounded-lg p-4">
                    <p className="text-sm font-medium text-foreground mb-3">
                        {s.question}
                    </p>
                    <div className="flex flex-wrap gap-1 mb-3">
                        {Object.entries(s.votes || {}).map(([agent, vote]: [string, any]) => (
                            <span key={agent} className={`text-[10px] px-2 py-0.5 rounded-full ${
                                vote === 'GO' ? 'bg-cmo/10 text-cmo' :
                                vote === 'NO-GO' ? 'bg-devil/10 text-devil' : 'bg-legal/10 text-legal'
                            }`}>
                                {agent}: {vote}
                            </span>
                        ))}
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-pre-wrap max-h-64 overflow-y-auto bg-secondary/30 rounded-lg p-3">
                        {s.moderator_summary || 'No summary available'}
                    </div>
                </div>
            ))}
        </div>
        </motion.div>)}
        </div>
    </motion.div>
)}

        {/* Hero */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 pb-20">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl md:text-8xl font-serif font-bold tracking-tight mb-4 gold-gradient-text animate-title-glow">
              SHADOW BOARD
            </h1>
            <p className="text-muted-foreground text-sm md:text-base tracking-wide">
              AI-Powered Executive Decision Simulation
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="w-full max-w-2xl"
          >
            <div className="glass-card-strong rounded-xl p-6 md:p-8">
              <div className="relative">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder={voiceQuestion.isListening ? 'Listening... speak your strategic question' : 'What strategic decision should the board analyze?'}
                  className={`w-full bg-secondary/40 border rounded-lg p-4 pr-12 text-sm md:text-base text-foreground focus:outline-none transition-colors resize-none h-32 placeholder:text-muted-foreground/50 ${
                    voiceQuestion.isListening ? 'border-primary/60 bg-primary/5' : 'border-border focus:border-primary/40'
                  }`}
                />
                {voiceQuestion.supported && (
                  <button
                    type="button"
                    onClick={voiceQuestion.toggle}
                    className={`absolute right-3 top-3 p-1.5 rounded-full transition-all ${
                      voiceQuestion.isListening
                        ? 'text-primary bg-primary/10 animate-pulse'
                        : 'text-muted-foreground/40 hover:text-muted-foreground hover:bg-secondary/50'
                    }`}
                    title={voiceQuestion.isListening ? 'Stop listening' : 'Speak your question'}
                  >
                    {voiceQuestion.isListening ? <MicOff size={18} /> : <Mic size={18} />}
                  </button>
                )}
                {voiceQuestion.isListening && (
                  <div className="absolute bottom-2 left-4 flex items-center gap-2 text-xs text-primary">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
                    </span>
                    Listening...
                  </div>
                )}
              </div>

              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Company context (optional): e.g. We are Spotify. Revenue: $15B. Cash: $4.2B. 500M monthly active users."
                className="w-full bg-secondary/40 border border-border rounded-lg p-4 text-sm md:text-base text-foreground focus:outline-none focus:border-primary/40 transition-colors resize-none h-20 placeholder:text-muted-foreground/50 mt-3"
              />
              <div className="flex items-center gap-2 mt-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => {
                  if (e.target.files?.[0]) setUploadedFile(e.target.files[0]);
                }}
                accept=".pdf,.txt,.docx"
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-primary/40 hover:bg-primary/5 transition-all text-xs"
              >
                <FileText size={14} />
                {uploadedFile ? uploadedFile.name : 'Attach document (optional)'}
              </button>
              {uploadedFile && (
                <button
                  onClick={() => setUploadedFile(null)}
                  className="text-xs text-destructive hover:text-destructive/80"
                >
                  ✕ Remove
                </button>
              )}
            </div>
            <div className="mt-4 mb-2">
              <label className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-2 block">
                Board Expertise
              </label>
              <div className="flex gap-2 flex-wrap">
                {[
                  { id: 'tech', label: '💻 Tech' },
                  { id: 'healthcare', label: '🏥 Healthcare' },
                  { id: 'finance', label: '🏦 Finance' },
                  { id: 'retail', label: '🛒 Retail' },
                ].map((b) => (
                  <button
                    key={b.id}
                    onClick={() => setBoardType(b.id)}
                    className={`px-4 py-2 rounded-lg border text-xs transition-all ${
                      boardType === b.id
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border text-muted-foreground hover:border-primary/40'
                    }`}
                  >
                    {b.label}
                  </button>
                ))}
              </div>
            </div>
              {/* Example chips */}

              {/* Example chips */}
              <div className="flex flex-wrap gap-2 mt-4 mb-6">
                {EXAMPLE_QUESTIONS.map((eq) => (
                  <button
                    key={eq}
                    onClick={() => setQuestion(eq)}
                    className="text-xs px-3 py-1.5 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-primary/40 hover:bg-primary/5 transition-all"
                  >
                    {eq}
                  </button>
                ))}
              </div>

              <button
                onClick={startDebate}
                disabled={!question.trim() || isStarting}
                className="w-full py-4 rounded-lg gold-gradient text-primary-foreground font-bold uppercase tracking-wider text-sm hover:opacity-90 transition-all disabled:opacity-40 disabled:cursor-not-allowed group flex items-center justify-center gap-2 gold-glow"
              >
                {isStarting ? 'Convening the Board...' : 'Convene the Board'}
                <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </motion.div>
        </div>

        <AppFooter />
        <ErrorBanner error={error} onDismiss={() => setError(null)} />
      </div>
    );
  }

  // Debate Arena
  return (
    <div className="min-h-svh flex flex-col bg-grid-pattern">
      <PhaseIndicator currentPhase={currentPhase} />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 md:py-12 space-y-4">
        <AnimatePresence mode="popLayout">
          {messages.map((msg, i) => (
            <MessageCard key={i} message={msg} index={i} sessionId={sessionId} />
          ))}
        </AnimatePresence>

        <AnimatePresence>
          {isThinking && !isPaused && !isComplete && (
            <TypingIndicator
              agentName={thinkingAgent}
              phase={currentPhase === 0 ? 'research' : 'debate'}
            />
          )}
        </AnimatePresence>

        {isPaused && (
          <HumanInputPanel
            onSubmit={(text,targetAgent) => submitHumanInput(text,targetAgent)}
            onSkip={() => submitHumanInput('', 'all')}
          />
        )}

        {isComplete && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="rounded-xl overflow-hidden gold-glow"
            style={{
              background: 'linear-gradient(135deg, hsla(40, 52%, 30%, 0.3), hsla(40, 52%, 20%, 0.5))',
              border: '1px solid hsla(40, 52%, 58%, 0.3)',
            }}
          >
            <div className="p-8 md:p-10 text-center">
              <CheckCircle2 className="mx-auto mb-4 text-primary" size={48} />
              <h2 className="text-3xl md:text-4xl font-serif font-bold mb-2 gold-gradient-text">
                Shadow Board Session Complete
              </h2>
              <p className="text-muted-foreground text-sm mb-6">
                The board has reached its conclusions
              </p>
              <div className="flex items-center justify-center gap-6 text-xs font-mono text-muted-foreground uppercase tracking-wider">
                <span className="flex items-center gap-1.5">
                  <Users size={14} className="text-primary" />
                  {agentCount} agents
                </span>
                <span className="flex items-center gap-1.5">
                  <MessageSquare size={14} className="text-primary" />
                  {roundCount} rounds
                </span>
                <span className="flex items-center gap-1.5">
                  <FileText size={14} className="text-primary" />
                  1 synthesis
                </span>
              </div>
              <button
                onClick={() => {
                setSessionId(null);
                setMessages([]);
                setCurrentPhase(0);
                setIsPaused(false);
                setIsComplete(false);
                setIsStarting(false);
                setIsThinking(false);
                setQuestion('');
                setContext('');
                setBoardType('tech');
                setUploadedFile(null);    
                setError(null);
                setCompareSession(null);
                setShowHistory(false)
                setCompareWith(null);
                eventSourceRef.current?.close();
            }}
              className="mt-6 px-6 py-3 rounded-lg border border-primary/30 text-primary font-semibold uppercase tracking-wider text-sm hover:bg-primary/10 transition-all">
            Start New Session
            </button>
            </div>
          </motion.div>
        )}

        <div ref={scrollRef} className="h-20" />
      </main>

      <AppFooter />
      <ErrorBanner error={error} onDismiss={() => setError(null)} />
    </div>
  );
};

const AppFooter = () => (
  <footer className="py-6 text-center border-t border-border/30">
    <p className="text-xs text-muted-foreground/60 font-mono">
      Shadow Board by Agent Quorum · Powered by AIRIA
    </p>
    <p className="text-[10px] text-muted-foreground/30 mt-1">
      Built for the AIRIA AI Agent Challenge 2026
    </p>
  </footer>
);

const ErrorBanner = ({ error, onDismiss }: { error: string | null; onDismiss: () => void }) => {
  if (!error) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-8 right-8 glass-card-strong text-foreground px-6 py-4 rounded-lg flex items-center gap-3 shadow-2xl z-50 text-xs cursor-pointer border border-destructive/30"
      onClick={onDismiss}
    >
      <AlertCircle size={16} className="text-destructive" /> {error}
    </motion.div>
  );
};

export default Index;

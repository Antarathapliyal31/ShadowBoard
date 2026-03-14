import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, SkipForward, Mic } from 'lucide-react';

interface HumanInputPanelProps {
  onSubmit: (text: string) => void;
  onSkip: () => void;
}

const HumanInputPanel: React.FC<HumanInputPanelProps> = ({ onSubmit, onSkip }) => {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    onSubmit(input);
    setInput('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="rounded-lg p-6 md:p-8 pulse-gold"
      style={{
        background: 'hsla(222, 47%, 16%, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '2px solid hsla(40, 52%, 58%, 0.4)',
      }}
    >
      <div className="flex items-center gap-2 mb-4">
        <MessageSquare size={18} className="text-primary" />
        <h2 className="font-serif text-xl font-semibold text-primary">
          The Board Awaits Your Input
        </h2>
      </div>
      <p className="text-muted-foreground text-sm mb-5">
        Ask the board a question or challenge their reasoning to shape the next round of deliberation.
      </p>
      <div className="relative mb-5">
        <input
          autoFocus
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Ask the board a question or challenge their reasoning..."
          className="w-full bg-secondary/50 border border-border rounded-lg px-4 py-4 pr-12 text-sm text-foreground focus:outline-none focus:border-primary/50 transition-colors placeholder:text-muted-foreground/50"
        />
        <button className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground/40 hover:text-muted-foreground transition-colors" title="Voice input (coming soon)">
          <Mic size={18} />
        </button>
      </div>
      <div className="flex gap-3">
        <button
          onClick={handleSubmit}
          className="flex-1 gold-gradient text-primary-foreground py-3 rounded-lg font-semibold text-sm uppercase tracking-wider hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          <Send size={14} />
          Send to Board
        </button>
        <button
          onClick={onSkip}
          className="px-6 border border-border rounded-lg text-muted-foreground font-semibold text-sm uppercase tracking-wider hover:bg-secondary/50 transition-colors flex items-center gap-2"
        >
          <SkipForward size={14} />
          Skip
        </button>
      </div>
    </motion.div>
  );
};

export default HumanInputPanel;

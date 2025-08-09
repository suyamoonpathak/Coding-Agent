import React from 'react';
import Button from './ui/Button';
import TextArea from './ui/TextArea';

export default function Composer({ value, onChange, onSend, loading }) {
  const onKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) return; // allow newline with Shift+Enter
      e.preventDefault();
      onSend();
    }
  };
  return (
    <div className="composer">
      <div className="composerInner">
        <TextArea className="input" rows={5} placeholder="Message Coding Agent…" value={value} onChange={(e)=>onChange(e.target.value)} onKeyDown={onKeyDown} />
        <div className="actions"><Button size="lg" style={{ alignSelf: 'stretch' }} onClick={onSend} disabled={loading}>{loading ? 'Generating…' : 'Send'}</Button></div>
      </div>
    </div>
  );
}



import React, { useEffect, useRef, useState } from 'react';
import Composer from './Composer';
import MessageList from './MessageList';
import { useSelector } from 'react-redux';
import { streamText } from '../services/api';

export default function Chat({ modelBase }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const base = useSelector((s) => s.settings.modelBase) || modelBase;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages((m) => [...m, userMsg, { role: 'assistant', content: '' }]);
    setInput('');
    setLoading(true);
    try {
      let acc = '';
      for await (const chunk of await streamText(base + '/generate_code_stream', { prompt: userMsg.content })) {
        acc += chunk;
        setMessages((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: 'assistant', content: acc };
          return copy;
        });
      }
    } catch (e) {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: 'assistant', content: 'Error: ' + e.message };
        return copy;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatRoot">
      <MessageList messages={messages} />
      <div ref={bottomRef} />
      <Composer value={input} onChange={setInput} onSend={send} loading={loading} />
    </div>
  );
}



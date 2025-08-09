import React, { useState } from 'react';
import Button from './ui/Button';
import Editor from '@monaco-editor/react';
import { useSelector } from 'react-redux';
import { streamText } from '../services/api';

export default function Executor({ execBase }) {
  const [code, setCode] = useState('print("Hello from sandbox")');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const base = useSelector((s) => s.settings.execBase) || execBase;

  const run = async () => {
    setLoading(true);
    setOutput('');
    try {
      for await (const chunk of await streamText(base + '/execute_code_stream', { code })) {
        setOutput((prev) => prev + chunk);
      }
    } catch (e) {
      setOutput('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="execRoot">
      <div className="execTop">
        <div className="label">Python</div>
      </div>
      <div className="execBody">
        <div style={{ height: 280 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(val)=>setCode(val || '')}
            options={{ fontSize: 15, minimap: { enabled: false } }}
          />
        </div>
        <div className="execActions"><Button size="lg" onClick={run} disabled={loading}>{loading ? 'Running…' : 'Run'}</Button></div>
        <div className="execOutput">
          {output || <span className="tiny">Program output will appear here…</span>}
        </div>
      </div>
    </div>
  );
}



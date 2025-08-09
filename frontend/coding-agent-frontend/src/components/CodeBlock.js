import React, { useMemo, useState } from 'react';
import copy from 'copy-to-clipboard';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import javascript from 'highlight.js/lib/languages/javascript';
import bash from 'highlight.js/lib/languages/bash';
import 'highlight.js/styles/github-dark.css';

// Register a few common languages; others will fall back to auto
hljs.registerLanguage('python', python);
hljs.registerLanguage('py', python);
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('js', javascript);
hljs.registerLanguage('bash', bash);
hljs.registerLanguage('sh', bash);

export default function CodeBlock({ language = '', value = '' }) {
  const [copied, setCopied] = useState(false);
  const highlighted = useMemo(() => {
    try {
      if (language && hljs.getLanguage(language)) {
        return hljs.highlight(value, { language }).value;
      }
      return hljs.highlightAuto(value).value;
    } catch {
      return value;
    }
  }, [language, value]);

  const onCopy = () => {
    copy(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="button secondary"
        style={{ position: 'absolute', right: 8, top: 8, transition: 'opacity .2s ease' }}
        onClick={onCopy}
      >
        <span style={{ marginRight: 8, display: 'inline-block', opacity: copied ? 0 : 1, transition: 'opacity .2s ease' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="9" width="11" height="11" rx="2" stroke="currentColor" strokeWidth="1.6"/>
            <rect x="4" y="4" width="11" height="11" rx="2" stroke="currentColor" strokeWidth="1.6"/>
          </svg>
        </span>
        <span style={{ transition: 'opacity .2s ease' }}>{copied ? 'Copied!' : 'Copy'}</span>
      </button>
      <pre className="hljs" style={{ overflow: 'auto' }}>
        <code className={`language-${language}`} dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  );
}



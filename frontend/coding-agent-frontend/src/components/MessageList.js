import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';

export default function MessageList({ messages }) {
  
  return (
    <div className="messages">
      {messages.map((m, i) => (
        <div key={i} className="message">
          <div className="role">{m.role.toUpperCase()}</div>
          <div className={`bubble ${m.role}`}>
            <div className="markdown">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const content = Array.isArray(children) ? children.join('') : String(children || '');
                    if (!inline) {
                      return <CodeBlock language={match?.[1] || ''} value={content.replace(/\n$/, '')} />;
                    }
                    return <code className={className} {...props}>{content}</code>;
                  }
                }}
              >
                {m.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}



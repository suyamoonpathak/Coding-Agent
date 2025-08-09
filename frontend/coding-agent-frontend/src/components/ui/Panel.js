import React from 'react';

export default function Panel({ children, className = '', ...props }) {
  return (
    <div className={["panel", className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}



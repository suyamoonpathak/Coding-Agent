import React from 'react';

export default function TextArea({ mono = false, className = '', ...props }) {
  const classes = ['textarea', mono ? 'mono' : null, className].filter(Boolean).join(' ');
  return <textarea className={classes} {...props} />;
}



import React from 'react';

export default function Button({ children, variant = 'primary', size = 'md', className = '', loading = false, ...props }) {
  const classes = [
    'button',
    variant === 'secondary' ? 'secondary' : null,
    size === 'lg' ? 'large' : null,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} {...props} disabled={props.disabled || loading}>
      {loading ? (
        <span className="spinner" style={{ display: 'inline-block', width: 16, height: 16, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%', marginRight: 8, animation: 'spin .9s linear infinite' }} />
      ) : null}
      <span>{children}</span>
    </button>
  );
}



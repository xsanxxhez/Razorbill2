import React, { useEffect } from 'react';
import './Notification.css';

const Notification = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return (
    <div className={`notification ${type}`}>
      <div className="notification-content">
        <span className="notification-icon">
          {type === 'success' ? '✓' : type === 'error' ? '✕' : 'i'}
        </span>
        <span className="notification-text">{message}</span>
      </div>
      <button className="notification-close" onClick={onClose}>×</button>
    </div>
  );
};

export default Notification;

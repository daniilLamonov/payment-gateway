import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import './PaymentError.css';

const PaymentError = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const type = searchParams.get('type') || 'error';
  const message = searchParams.get('message') || '';

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getErrorContent = () => {
    switch (type) {
      case 'closed':
        return {
          icon: '⏰',
          title: 'Платежная система закрыта',
          description: decodeURIComponent(message),
          gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          showTime: true,
          buttons: [
            {
              text: '↻ Обновить',
              action: () => navigate('/'),
              primary: false
            }
          ]
        };

      case 'maintenance':
        return {
          icon: '🔧',
          title: 'Система на техническом обслуживании',
          description: 'Платежная система временно недоступна. Администратор ещё не добавил актуальные реквизиты. Пожалуйста, попробуйте позже.',
          gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          showTime: false,
          buttons: [
            {
              text: '↻ Обновить',
              action: () => window.history.back(),
              primary: false
            }
          ]
        };

      case 'error':
        return {
          icon: '❌',
          title: 'Произошла ошибка',
          description: decodeURIComponent(message) || 'Неизвестная ошибка. Пожалуйста, попробуйте позже.',
          gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          showTime: false,
          buttons: [
            {
              text: '↻ Обновить',
              action: () => navigate('/'),
              primary: false
            }
          ]
        };

      default:
        return {
          icon: '⚠️',
          title: 'Что-то пошло не так',
          description: 'Неизвестная ошибка',
          gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          showTime: false,
          buttons: [
            {
              text: '↻ Обновить',
              action: () => navigate('/'),
              primary: true
            }
          ]
        };
    }
  };

  const content = getErrorContent();

  return (
    <div className="payment-error-page">
      <div className="error-container">
        <div className="error-icon">{content.icon}</div>

        <h1 className="error-title">{content.title}</h1>

        <div className="error-description">
          {content.description}
        </div>

        {content.showTime && (
          <div className="info-box">
            <strong>Текущее время (МСК):</strong>
            <p className="current-time">
              {currentTime.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZone: 'Europe/Moscow'
              })}
            </p>
          </div>
        )}

        <div className="error-buttons">
          {content.buttons.map((button, idx) => (
            <button
              key={idx}
              className={`error-button ${button.primary ? 'primary' : 'secondary'}`}
              onClick={button.action}
            >
              {button.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PaymentError;

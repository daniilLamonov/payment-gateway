import React, { useState, useEffect, useCallback } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { generateQR, getPaymentLink } from '../api';
import './PaymentPage.css';
import sbpIcon from '../assets/SBP.png';

const PaymentPage = () => {
  const SESSION_DURATION = 5 * 60; // 300 секунд

  const [qrData, setQrData] = useState(null);
  const [paymentLink, setPaymentLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [qrTimeLeft, setQrTimeLeft] = useState(null);
  const [linkTimeLeft, setLinkTimeLeft] = useState(null);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const autoRefreshQR = useCallback(async () => {
    console.log('🔄 Автообновление QR-кода...');
    try {
      const data = await generateQR();
      if (data.success) {
        setQrData(data.qr_code);
        setQrTimeLeft(SESSION_DURATION);
      }
    } catch (err) {
      console.error('Ошибка автообновления QR:', err);
    }
  }, [SESSION_DURATION]);

  const autoRefreshLink = useCallback(async () => {
    console.log('🔄 Автообновление ссылки...');
    try {
      const data = await getPaymentLink();
      if (data.success) {
        setPaymentLink(data);
        setLinkTimeLeft(SESSION_DURATION);
      }
    } catch (err) {
      console.error('Ошибка автообновления ссылки:', err);
    }
  }, [SESSION_DURATION]);

  useEffect(() => {
    const fetchPaymentLink = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPaymentLink();
        if (data.success) {
          setPaymentLink(data);
          setLinkTimeLeft(SESSION_DURATION);
        } else {
          setError('Ошибка при создании ссылки');
        }
      } catch (err) {
        setError('Ошибка при создании ссылки');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPaymentLink();
  }, [SESSION_DURATION]);

  const handleOpenPayment = () => {
    if (paymentLink?.link) {
      window.open(paymentLink.link, '_blank');
    }
  };

  useEffect(() => {
    if (qrTimeLeft === null || qrTimeLeft < 0) return;

    if (qrTimeLeft === 0) {
      autoRefreshQR();
      return;
    }

    const timer = setInterval(() => {
      setQrTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [qrTimeLeft, autoRefreshQR]);

  useEffect(() => {
    if (linkTimeLeft === null || linkTimeLeft < 0) return;

    if (linkTimeLeft === 0) {
      autoRefreshLink();
      return;
    }

    const timer = setInterval(() => {
      setLinkTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [linkTimeLeft, autoRefreshLink]);

  const handleGenerateQR = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateQR();
      if (data.success) {
        setQrData(data.qr_code);
        setQrTimeLeft(SESSION_DURATION);
      } else {
        setError('Ошибка при генерации QR-кода');
      }
    } catch (err) {
      setError('Ошибка при генерации QR-кода');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-page">
      <div className="payment-container">
        <div className="header">
          <h1>💳 Оплата через СБП</h1>
          <p className="subtitle">Система быстрых платежей</p>
        </div>

        {/* ПРЕДУПРЕЖДЕНИЕ */}
        <div className="warning-section">
          <div className="warning-box">
            <div className="warning-icon">⚠️</div>
            <div className="warning-content">
              <h3>ВАЖНО!</h3>
              <p>
                <strong>QR-код СБП действителен 5 минут, после придется сгенерировать новый QR-код на оплату по СБП</strong>.
              </p>
            </div>
          </div>
        </div>

        {/* ВАРИАНТЫ ОПЛАТЫ */}
        <div className="payment-options">
          {/* ВАРИАНТ 1: QR КОД */}
          <div className="option qr-option">
            <div className="option-header">
              <h2>Способ 1️⃣</h2>
              <p className="option-subtitle">Отсканировать QR-код</p>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleGenerateQR}
              disabled={loading}
            >
              {loading ? (
                'Генерирую QR-код...'
              ) : (
                <>
                  <img src={sbpIcon} alt="" style={{ width: '16px', height: '16px', marginRight: '8px' }} />
                  QR-код СБП
                </>
              )}
            </button>

            {qrData && (
              <div className="qr-display">
                {qrTimeLeft !== null && (
                  <div className={`timer-display ${qrTimeLeft < 60 ? 'timer-warning' : ''}`}>
                    <div className="timer-content">
                      <div className="timer-label">Обновление через:</div>
                      <div className="timer-value">{formatTime(qrTimeLeft)}</div>
                      {qrTimeLeft < 60 && (
                        <div className="timer-warning-text">
                          ⚠️ QR-код скоро обновится!
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="qr-content">
                  <QRCodeSVG
                    value={qrData.url}
                    size={280}
                    level="H"
                    includeMargin={true}
                  />
                  <p className="qr-url">
                    <code>{qrData.url}</code>
                  </p>
                </div>

                <p className="qr-instruction">
                  👆 Откройте камеру телефона и отсканируйте этот QR-код
                </p>
              </div>
            )}
          </div>

          {/* РАЗДЕЛИТЕЛЬ */}
          <div className="divider">или</div>

          {/* ВАРИАНТ 2: ССЫЛКА */}
          <div className="option link-option">
            <div className="option-header">
              <h2>Способ 2️⃣</h2>
              <p className="option-subtitle">Оплатить в приложении банка</p>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleOpenPayment}
              disabled={loading || !paymentLink}
            >
              {loading ? '⏳ Загрузка...' : '→ Перейти к оплате'}
            </button>
          </div>
        </div>

        {/* ОШИБКА */}
        {error && (
          <div className="error-section">
            <div className="error-box">
              <span className="error-icon">❌</span>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* FAQ */}
        <div className="faq-section">
          <h3>❓ Частые вопросы</h3>
          <details className="faq-item">
            <summary>Зачем автоматически обновляется QR-код?</summary>
            <p>Для безопасности система генерирует новый уникальный идентификатор каждые 5 минут. Это защищает ваши платежи.</p>
          </details>
          <details className="faq-item">
            <summary>Что будет, если время истекло во время оплаты?</summary>
            <p>Не переживайте! Система автоматически сгенерирует новый QR-код. Просто повторите попытку оплаты.</p>
          </details>
          <details className="faq-item">
            <summary>В какие часы принимаются платежи?</summary>
            <p>Платежи принимаются ежедневно с 10:00 до 21:00 по московскому времени.</p>
          </details>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;

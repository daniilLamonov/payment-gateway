import React, { useState, useEffect, useCallback } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { generateQR, getPaymentLink } from '../api';
import './PaymentPage.css';
import sbpIcon from '../assets/SBP.png';

const PaymentPage = () => {
  const SESSION_DURATION = 5 * 60;
  const PAGE_SESSION_DURATION = 5 * 60;

  const [sessionId] = useState(() => {
    return Math.floor(Math.random() * 90000000000000) + 10000000000000;
  });

  const [pageTimeLeft, setPageTimeLeft] = useState(PAGE_SESSION_DURATION);
  const [qrData, setQrData] = useState(null);
  const [paymentLink, setPaymentLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [qrTimeLeft, setQrTimeLeft] = useState(null);
  const [linkTimeLeft, setLinkTimeLeft] = useState(null);
  const [showQR, setShowQR] = useState(false);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    if (pageTimeLeft === 0) {
      window.location.reload();
      return;
    }
    const timer = setInterval(() => {
      setPageTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [pageTimeLeft]);

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
        setShowQR(true);
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
          <h1>Оплата через СБП</h1>
          <p className="subtitle">Сессия: {sessionId}</p>
          <p className="subtitle">Завершите платеж в течении: {formatTime(pageTimeLeft)}</p>
        </div>

        {/* ОСНОВНОЙ СПОСОБ ОПЛАТЫ - ПО ЦЕНТРУ */}
        <div className="primary-payment">
          <div className="primary-header">
            <h2>Оплатить в приложении банка</h2>
            <p className="primary-subtitle">Быстрый и удобный способ</p>
          </div>

          <button
            className="btn btn-primary btn-large btn-featured"
            onClick={handleOpenPayment}
            disabled={loading || !paymentLink}
          >
            {loading ? '⏳ Загрузка...' : (
              <>
                <img src={sbpIcon} alt="" className="btn-icon" />
                Выбрать банк
              </>
            )}
          </button>
        </div>

        {/* РАЗДЕЛИТЕЛЬ */}
        <div className="divider">или</div>

        {/* АЛЬТЕРНАТИВНЫЙ СПОСОБ - QR КОД */}
        <div className="secondary-payment">
          <button
            className="btn btn-secondary btn-small"
            onClick={handleGenerateQR}
            disabled={loading}
          >
            {showQR ? 'Обновить QR-код' : 'Показать QR-код для сканирования'}
          </button>

          {qrData && showQR && (
            <div className="qr-display">
              <div className="qr-content">
                <QRCodeSVG
                  value={qrData.url}
                  size={200}
                  level="H"
                  includeMargin={true}
                />
                <p className="qr-instruction">
                  Отсканируйте камерой телефона
                </p>
                {/* ПРЕДУПРЕЖДЕНИЕ */}
                <div className="warning-section">
                    <div className="warning-box">
                        <div className="warning-icon">⚠️</div>
                        <div className="warning-content">
                            <h3>ВАЖНО!</h3>
                            <p>
                                <strong>Реквизиты действительны 5 минут. Оплата по истёкшим реквизитам приводит к потере средств.</strong>.
                            </p>
                        </div>
                    </div>
                </div>
              </div>
            </div>
          )}
        </div>


        {/* ОШИБКА */}
        {error && (
          <div className="error-section">
            <div className="error-box">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* FAQ */}
        <div className="faq-section">
          <h3>Частые вопросы</h3>
          <details className="faq-item">
            <summary>Как оплатить через приложение банка?</summary>
            <p>Нажмите "Выбрать банк", система откроет список доступных банков для оплаты через СБП.</p>
          </details>
          <details className="faq-item">
            <summary>Зачем нужен QR-код?</summary>
            <p>QR-код — альтернативный способ оплаты. Отсканируйте его камерой телефона, если не хотите использовать кнопку выбора банка.</p>
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

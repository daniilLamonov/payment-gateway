import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { generateQR, getPaymentLink } from '../api';
import './PaymentPage.css';

const PaymentPage = () => {
  const [qrData, setQrData] = useState(null);
  const [paymentLink, setPaymentLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateQR = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateQR();
      if (data.success) {
        setQrData(data.qr_code);
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

  const handleGetPaymentLink = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPaymentLink();
      if (data.success) {
        setPaymentLink(data);
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

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Ссылка скопирована в буфер обмена');
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
                QR-код и ссылка на оплату содержат <strong>уникальный идентификатор сессии</strong>.
              </p>
              <p>
                После успешной оплаты <strong>вернитесь на эту страницу</strong> и сгенерируйте
                новый QR-код или ссылку для следующего платежа.
              </p>
              <p>
                ⚠️ Не используйте повторно старые QR-коды и ссылки!
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
              {loading ? '⏳ Генерирую QR-код...' : '📱 Сгенерировать QR-код'}
            </button>

            {qrData && (
              <div className="qr-display">
                <div className="qr-content">
                  <QRCodeSVG
                    value={qrData.url}
                    size={280}
                    level="H"
                    includeMargin={true}
                  />
                  <p className="qr-session">
                    ID сессии: <code>{qrData.session_id.substring(0, 8)}...</code>
                  </p>
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
              <p className="option-subtitle">Использовать ссылку для оплаты</p>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleGetPaymentLink}
              disabled={loading}
            >
              {loading ? '⏳ Создаю ссылку...' : '🔗 Получить ссылку на оплату'}
            </button>

            {paymentLink && (
              <div className="link-display">
                <div className="link-input-group">
                  <input
                    type="text"
                    value={paymentLink.link}
                    readOnly
                    className="link-input"
                    onClick={(e) => e.target.select()}
                  />
                  <button
                    className="btn btn-secondary"
                    onClick={() => copyToClipboard(paymentLink.link)}
                    title="Скопировать ссылку"
                  >
                    📋 Копировать
                  </button>
                </div>

                <button
                  className="btn btn-success btn-large"
                  onClick={() => window.open(paymentLink.link, '_blank')}
                >
                  → Перейти к оплате
                </button>

                <p className="link-session">
                  ID сессии: <code>{paymentLink.session_id.substring(0, 8)}...</code>
                </p>
              </div>
            )}
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
            <summary>Как долго действует QR-код?</summary>
            <p>Каждый QR-код содержит уникальный идентификатор сессии для отслеживания платежа. Рекомендуется генерировать новый QR-код для каждого платежа.</p>
          </details>
          <details className="faq-item">
            <summary>Что будет, если я использую старый QR-код?</summary>
            <p>Старый QR-код продолжит работать, но может привести к путанице при отслеживании платежей. Всегда генерируйте новый QR-код перед оплатой.</p>
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

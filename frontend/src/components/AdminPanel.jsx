import React, { useState, useEffect } from 'react';
import {
  updateDynamicRedirect,
  getAllRedirects,
  getCurrentRedirect,
  updateWorkingHours,
  getAllWorkingHours,
  logout
} from '../api';
import './AdminPanel.css';

const AdminPanel = () => {
  const [redirects, setRedirects] = useState([]);
  const [currentRedirect, setCurrentRedirect] = useState(null);
  const [workingHours, setWorkingHours] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('current'); // current, redirects, hours

  const [newRedirect, setNewRedirect] = useState({
    target_url: '',
    valid_from: new Date().toISOString().slice(0, 16),
    valid_until: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    notes: ''
  });
  const handleLogout = async () => {
  try {
    await logout();
    window.location.href = '/login';
  } catch (err) {
    console.error('Logout error:', err);
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    window.location.href = '/login';
  }
};

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [currentData, redirectsData, hoursData, logsData, sessionsData] = await Promise.all([
        getCurrentRedirect(),
        getAllRedirects(),
        getAllWorkingHours(),
      ]);

      if (currentData.success) {
        setCurrentRedirect(currentData.redirect);
      }

      setRedirects(redirectsData);

      // Преобразуем рабочие часы в объект
      const hoursObj = {};
      hoursData.forEach(hour => {
        hoursObj[hour.day_of_week] = {
          work_start: hour.work_start,
          work_end: hour.work_end,
          is_enabled: hour.is_enabled
        };
      });
      setWorkingHours(hoursObj);

      // Инициализируем недостающие дни
      for (let i = 0; i < 7; i++) {
        if (!hoursObj[i]) {
          hoursObj[i] = {
            work_start: '10:00',
            work_end: '21:00',
            is_enabled: true
          };
        }
      }
      setWorkingHours(hoursObj);

    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Ошибка при загрузке данных');
    }
  };

  const handleAddRedirect = async () => {
    if (!newRedirect.target_url.trim()) {
      setError('Введите ссылку на оплату');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const data = await updateDynamicRedirect({
        target_url: newRedirect.target_url,
        valid_from: new Date(newRedirect.valid_from).toISOString(),
        valid_until: new Date(newRedirect.valid_until).toISOString(),
        notes: newRedirect.notes
      });

      if (data.success) {
        setSuccess(data.message);
        setNewRedirect({
          target_url: '',
          valid_from: new Date().toISOString().slice(0, 16),
          valid_until: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
          notes: ''
        });
        fetchData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при добавлении ссылки');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateWorkingHours = async (dayOfWeek) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const data = await updateWorkingHours({
        day_of_week: dayOfWeek,
        work_start: workingHours[dayOfWeek].work_start,
        work_end: workingHours[dayOfWeek].work_end,
        is_enabled: workingHours[dayOfWeek].is_enabled
      });

      if (data.success) {
        setSuccess(data.message);
        fetchData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении рабочего времени');
    } finally {
      setLoading(false);
    }
  };

  const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const daysLong = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'];

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="admin-panel">
      <div className="admin-container">
        <div className="admin-header">
          <div className="admin-header-top">
            <div>
              <h1>📊 Админ-панель платежной системы</h1>
              <p className="admin-subtitle">Управление платёжным шлюзом</p>
            </div>
            <button onClick={handleLogout} className="btn-logout">
              🚪 Выйти
            </button>
          </div>
        </div>

        {/* УВЕДОМЛЕНИЯ */}
        {error && (
          <div className="notification error-notification">
            <span className="notification-icon">❌</span>
            <span>{error}</span>
            <button className="notification-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {success && (
          <div className="notification success-notification">
            <span className="notification-icon">✅</span>
            <span>{success}</span>
            <button className="notification-close" onClick={() => setSuccess(null)}>×</button>
          </div>
        )}

        {/* ТАБЫ */}
        <div className="admin-tabs">
          <button
            className={`admin-tab ${activeTab === 'current' ? 'active' : ''}`}
            onClick={() => setActiveTab('current')}
          >
            🟢 Текущая ссылка
          </button>
          <button
            className={`admin-tab ${activeTab === 'redirects' ? 'active' : ''}`}
            onClick={() => setActiveTab('redirects')}
          >
            🔗 Все ссылки
          </button>
          <button
            className={`admin-tab ${activeTab === 'hours' ? 'active' : ''}`}
            onClick={() => setActiveTab('hours')}
          >
            ⏰ Рабочее время
          </button>
        </div>

        {/* КОНТЕНТ ТАБОВ */}
        <div className="admin-content">

          {/* ТАБ: ТЕКУЩАЯ ССЫЛКА */}
          {activeTab === 'current' && (
            <div className="tab-content">
              <h2>🟢 Текущая активная ссылка</h2>

              {currentRedirect ? (
                <div className="current-redirect-box">
                  <div className="info-row">
                    <span className="info-label">Шлюз (ваша ссылка):</span>
                    <div className="info-value">
                      <code className="url-code">{currentRedirect.gateway_url}</code>
                      <button
                        className="btn-copy"
                        onClick={() => {
                          navigator.clipboard.writeText(currentRedirect.gateway_url);
                          setSuccess('Ссылка скопирована');
                        }}
                      >
                        📋 Копировать
                      </button>
                    </div>
                  </div>

                  <div className="info-row">
                    <span className="info-label">Редиректит на (СБП):</span>
                    <div className="info-value">
                      <code className="url-code small">{currentRedirect.target_url}</code>
                    </div>
                  </div>

                  <div className="info-row">
                    <span className="info-label">Действительна:</span>
                    <span className="info-value">
                      {formatDate(currentRedirect.valid_from)} — {formatDate(currentRedirect.valid_until)}
                    </span>
                  </div>

                  {currentRedirect.notes && (
                    <div className="info-row">
                      <span className="info-label">Примечание:</span>
                      <span className="info-value">{currentRedirect.notes}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-data">
                  <p>❌ Нет активной ссылки</p>
                  <p>Добавьте новую ссылку ниже</p>
                </div>
              )}

              <div className="section add-redirect-section">
                <h3>➕ Добавить новую ссылку на оплату</h3>
                <p className="section-description">
                  Когда вы добавляете новую ссылку, все старые ссылки автоматически деактивируются.
                </p>

                <div className="form-group">
                  <label>Ссылка на оплату (от банка/платёжной системы)</label>
                  <input
                    type="url"
                    placeholder="https://qr.nspk.ru/BS1A002HQMC47ITB9T6PPDIPP45FL6P4?type=01&bank=..."
                    value={newRedirect.target_url}
                    onChange={(e) => setNewRedirect({ ...newRedirect, target_url: e.target.value })}
                    className="form-input"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Действительна с</label>
                    <input
                      type="datetime-local"
                      value={newRedirect.valid_from}
                      onChange={(e) => setNewRedirect({ ...newRedirect, valid_from: e.target.value })}
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label>Действительна до</label>
                    <input
                      type="datetime-local"
                      value={newRedirect.valid_until}
                      onChange={(e) => setNewRedirect({ ...newRedirect, valid_until: e.target.value })}
                      className="form-input"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Примечание (опционально)</label>
                  <textarea
                    placeholder="Например: Счет в Сбербанке, выписка от 1 января"
                    value={newRedirect.notes}
                    onChange={(e) => setNewRedirect({ ...newRedirect, notes: e.target.value })}
                    className="form-textarea"
                    rows="3"
                  />
                </div>

                <button
                  onClick={handleAddRedirect}
                  disabled={loading}
                  className="btn btn-primary btn-large"
                >
                  {loading ? '⏳ Добавляю...' : '✅ Добавить ссылку'}
                </button>
              </div>
            </div>
          )}

          {/* ТАБ: ВСЕ ССЫЛКИ */}
          {activeTab === 'redirects' && (
            <div className="tab-content">
              <h2>🔗 История всех ссылок</h2>

              {redirects.length === 0 ? (
                <div className="no-data">
                  <p>Ссылок нет</p>
                </div>
              ) : (
                <div className="redirects-list">
                  {redirects.map((redirect) => (
                    <div
                      key={redirect.id}
                      className={`redirect-card ${redirect.is_active ? 'active' : 'inactive'}`}
                    >
                      <div className="redirect-status">
                        {redirect.is_active ? '🟢 АКТИВНА' : '⚫ неактивна'}
                      </div>

                      <div className="redirect-info">
                        <p className="redirect-id">ID: {redirect.id}</p>
                        <p className="redirect-url">
                          <strong>Ссылка:</strong><br />
                          <code>{redirect.target_url}</code>
                        </p>
                        <p className="redirect-dates">
                          <strong>Действует:</strong> {formatDate(redirect.valid_from)} — {formatDate(redirect.valid_until)}
                        </p>
                        {redirect.notes && (
                          <p className="redirect-notes">
                            <strong>Примечание:</strong> {redirect.notes}
                          </p>
                        )}
                        <p className="redirect-created">
                          Добавлена: {formatDate(redirect.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ТАБ: РАБОЧЕЕ ВРЕМЯ */}
          {activeTab === 'hours' && (
            <div className="tab-content">
              <h2>⏰ Рабочие часы (Московское время)</h2>
              <p className="section-description">
                Укажите часы, в которые принимаются платежи. Вне этого времени пользователи увидят сообщение о закрытии.
              </p>

              <div className="working-hours-list">
                {days.map((day, idx) => (
                  <div key={idx} className="working-hours-card">
                    <div className="hours-header">
                      <h3>{daysLong[idx]}</h3>
                      <label className="toggle">
                        <input
                          type="checkbox"
                          checked={workingHours[idx]?.is_enabled || false}
                          onChange={(e) => {
                            setWorkingHours({
                              ...workingHours,
                              [idx]: {
                                ...workingHours[idx],
                                is_enabled: e.target.checked
                              }
                            });
                          }}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                    </div>

                    <div className="hours-inputs">
                      <div className="time-input-group">
                        <label>Начало</label>
                        <input
                          type="time"
                          value={workingHours[idx]?.work_start || '10:00'}
                          onChange={(e) => {
                            setWorkingHours({
                              ...workingHours,
                              [idx]: {
                                ...workingHours[idx],
                                work_start: e.target.value
                              }
                            });
                          }}
                          disabled={!workingHours[idx]?.is_enabled}
                          className="form-input"
                        />
                      </div>

                      <div className="time-input-group">
                        <label>Конец</label>
                        <input
                          type="time"
                          value={workingHours[idx]?.work_end || '21:00'}
                          onChange={(e) => {
                            setWorkingHours({
                              ...workingHours,
                              [idx]: {
                                ...workingHours[idx],
                                work_end: e.target.value
                              }
                            });
                          }}
                          disabled={!workingHours[idx]?.is_enabled}
                          className="form-input"
                        />
                      </div>

                      <button
                        onClick={() => handleUpdateWorkingHours(idx)}
                        disabled={loading}
                        className="btn btn-primary"
                      >
                        Сохранить
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../api';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(username, password);

      // Сохраняем токен в localStorage
      localStorage.setItem('admin_token', data.access_token);
      localStorage.setItem('admin_username', data.username);

      // Редирект на админ панель
      navigate('/admin');
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверный логин или пароль');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <div className="login-icon">🔐</div>
          <h1>Вход в админ-панель</h1>
          <p>Введите логин и пароль для доступа</p>
        </div>

        {error && (
          <div className="login-error">
            <span className="error-icon">❌</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Логин</label>
            <input
              id="username"
              type="text"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              disabled={loading}
              className="login-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              className="login-input"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="login-button"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="login-footer">
          <a href="/" className="back-link">← Вернуться на главную</a>
        </div>
      </div>
    </div>
  );
};

export default Login;

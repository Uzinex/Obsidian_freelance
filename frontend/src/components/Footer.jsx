import { Link } from 'react-router-dom';
import { useLocale } from '../context/LocaleContext.jsx';
import Icon from './Icon.jsx';

export default function Footer() {
  const year = new Date().getFullYear();
  const { buildPath } = useLocale();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <img src="/logo.svg" alt="Obsidian Freelance" loading="lazy" decoding="async" width="48" height="48" />
          <div>
            <strong>OBSIDIAN FREELANCE</strong>
            <p>Платформа, где встречаются лучшие заказчики и фрилансеры для совместного роста.</p>
          </div>
        </div>
        <div className="footer-columns">
          <div className="footer-column">
            <h4>Навигация</h4>
            <Link to={buildPath('/')}>Главная</Link>
            <Link to={buildPath('/orders')}>Работы</Link>
            <Link to={buildPath('/freelancers')}>Фрилансеры</Link>
            <Link to={buildPath('/about')}>О нас</Link>
            <Link to={buildPath('/contacts')}>Контакты</Link>
            <Link to={buildPath('/faq')}>FAQ</Link>
            <Link to={buildPath('/profile#pricing')}>Тарифы</Link>
          </div>
          <div className="footer-column">
            <h4>Контакты</h4>
            <span>
              <Icon name="mail" size={18} decorative className="footer-icon" /> hello@obsidian.dev
            </span>
            <span>
              <Icon name="phone" size={18} decorative className="footer-icon" /> +998 (90) 123-45-67
            </span>
            <span>
              <Icon name="marker" size={18} decorative className="footer-icon" /> Ташкент, ул. Инновационная, 7
            </span>
          </div>
          <div className="footer-column">
            <h4>Мы в соцсетях</h4>
            <a href="https://t.me/obsidianfreelance" target="_blank" rel="noopener noreferrer">
              <Icon name="telegram" size={18} decorative className="footer-icon" /> Telegram
            </a>
            <a href="https://www.linkedin.com/company/obsidianfreelance" target="_blank" rel="noopener noreferrer">
              <Icon name="linkedin" size={18} decorative className="footer-icon" /> LinkedIn
            </a>
            <a href="https://www.instagram.com/obsidianfreelance" target="_blank" rel="noopener noreferrer">
              <Icon name="instagram" size={18} decorative className="footer-icon" /> Instagram
            </a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">© {year} Обсидиан Фриланс. Все права защищены.</div>
    </footer>
  );
}

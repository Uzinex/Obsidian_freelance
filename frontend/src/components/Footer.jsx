import { Link } from 'react-router-dom';

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <img src="/logo.svg" alt="Obsidian Freelance" />
          <div>
            <strong>OBSIDIAN FREELANCE</strong>
            <p>Платформа, где встречаются лучшие заказчики и фрилансеры для совместного роста.</p>
          </div>
        </div>
        <div className="footer-columns">
          <div className="footer-column">
            <h4>Навигация</h4>
            <Link to="/">Главная</Link>
            <Link to="/orders">Работы</Link>
            <Link to="/freelancers">Фрилансеры</Link>
            <Link to="/about">О нас</Link>
          </div>
          <div className="footer-column">
            <h4>Контакты</h4>
            <span>
              <img src="https://img.icons8.com/ios-filled/18/777777/secured-letter.png" alt="Email" /> hello@obsidian.dev
            </span>
            <span>
              <img src="https://img.icons8.com/ios-filled/18/777777/phone.png" alt="Телефон" /> +998 (90) 123-45-67
            </span>
            <span>
              <img src="https://img.icons8.com/ios-filled/18/777777/marker.png" alt="Адрес" /> Ташкент, ул. Инновационная, 7
            </span>
          </div>
          <div className="footer-column">
            <h4>Мы в соцсетях</h4>
            <a href="https://t.me/icons8" target="_blank" rel="noreferrer">
              <img src="https://img.icons8.com/ios-filled/18/777777/telegram-app.png" alt="Telegram" /> Telegram
            </a>
            <a href="https://www.linkedin.com/company/icons8/" target="_blank" rel="noreferrer">
              <img src="https://img.icons8.com/ios-filled/18/777777/linkedin.png" alt="LinkedIn" /> LinkedIn
            </a>
            <a href="https://www.instagram.com/icons8/" target="_blank" rel="noreferrer">
              <img src="https://img.icons8.com/ios-filled/18/777777/instagram-new.png" alt="Instagram" /> Instagram
            </a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">© {year} Обсидиан Фриланс. Все права защищены.</div>
    </footer>
  );
}

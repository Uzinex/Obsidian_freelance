export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer>
      <strong>OBSIDIAN FREELANCE</strong>
      <div>Платформа, где встречаются лучшие заказчики и фрилансеры.</div>
      <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>© {year} Обсидиан Фриланс. Все права защищены.</div>
    </footer>
  );
}

const ICONS = {
  spark: (
    <>
      <path d="M12 3.5 13.8 8l4.7.4-3.6 3.2 1.1 4.6L12 13.8 7.9 16.2l1-4.6-3.6-3.2 4.7-.4Z" />
      <circle cx="12" cy="4" r="1.5" />
    </>
  ),
  rocket: (
    <>
      <path d="M14.5 2.7c-1.6-.6-3.4-.6-5 0-.5.2-1 .8-1.1 1.4l-.7 3.3L5 9.3c-.6.6-.6 1.6 0 2.2l.6.6-2 2c-.5.5-.6 1.3-.2 1.9a1.5 1.5 0 0 0 1.9.2l2-1.3.6.6a1.5 1.5 0 0 0 2.2 0l1.9-1.9 3.3-.7c.6-.1 1.2-.6 1.4-1.1.6-1.6.6-3.4 0-5-.6-1.7-2-3.1-3.7-3.7ZM10 14l-2 2 .3-2.4 1.5-1.5 1.6-1.6 2.4-.3-2 2Z" />
      <circle cx="12" cy="7" r="1.5" />
    </>
  ),
  timer: (
    <>
      <circle cx="12" cy="13" r="7" />
      <path d="M12 13V8m0-3V3" />
    </>
  ),
  shield: (
    <>
      <path d="M12 3 5 5v6c0 3.8 2.5 7.3 6.2 8.4a1 1 0 0 0 .6 0C15.5 18.3 18 14.8 18 11V5Z" />
      <path d="m9 11 2 2 4-4" />
    </>
  ),
  home: (
    <>
      <path d="M3.5 11 12 3l8.5 8" />
      <path d="M5 11v8h5v-4h4v4h5v-8" />
    </>
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 10v6m0-9V7" />
    </>
  ),
  idea: (
    <>
      <path d="M12 4a6 6 0 0 0-3.1 11.2c.3.2.5.5.5.9V18a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-1.9c0-.4.2-.7.5-.9A6 6 0 0 0 12 4Z" />
      <path d="M10 21h4" />
    </>
  ),
  escrow: (
    <>
      <path d="M5 8V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2" />
      <rect x="3" y="8" width="18" height="12" rx="2" />
      <path d="m9 14 2 2 4-4" />
    </>
  ),
  orders: (
    <>
      <rect x="6" y="4" width="12" height="16" rx="2" />
      <path d="M9 8h6M9 12h6M9 16h3" />
    </>
  ),
  team: (
    <>
      <circle cx="9" cy="9" r="3" />
      <circle cx="16" cy="9" r="2.5" />
      <path d="M3 19.5c0-2.6 2.7-4.5 6-4.5s6 1.9 6 4.5M14 17c.8-.6 1.9-1 3-1 2.2 0 4 1.4 4 3.2" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M5 20a7 7 0 0 1 14 0" />
    </>
  ),
  bell: (
    <>
      <path d="M15 19a3 3 0 0 1-6 0" />
      <path d="M18 13V9a6 6 0 1 0-12 0v4l-2 3h16Z" />
    </>
  ),
  task: (
    <>
      <rect x="5" y="4" width="14" height="16" rx="2" />
      <path d="M9 4v4h6V4" />
      <path d="m9 13 2 2 4-4" />
    </>
  ),
  todo: (
    <>
      <rect x="4" y="5" width="16" height="14" rx="2" />
      <path d="M8 9h8M8 13h5" />
      <path d="m6 10 1.5 1.5L10 9" />
    </>
  ),
  flash: (
    <>
      <path d="m7 13 6-11v7h4l-6 11v-7Z" />
    </>
  ),
  mail: (
    <>
      <rect x="3" y="6" width="18" height="12" rx="2" />
      <path d="m3 8 9 6 9-6" />
    </>
  ),
  phone: (
    <>
      <path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
      <path d="M11 17h2" />
    </>
  ),
  marker: (
    <>
      <path d="M12 3a6 6 0 0 0-6 6c0 4.1 6 10 6 10s6-5.9 6-10a6 6 0 0 0-6-6Zm0 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4Z" />
    </>
  ),
  telegram: (
    <>
      <path d="m4 11 15-6-3.4 13-4.2-3.6-2.8 2.4.4-4.5Z" />
      <path d="m8.8 12 3.2 2.6" />
    </>
  ),
  linkedin: (
    <>
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <path d="M8 11v5M8 8v.01M12 16v-3.5a2 2 0 1 1 4 0V16" />
    </>
  ),
  instagram: (
    <>
      <rect x="4" y="4" width="16" height="16" rx="5" />
      <circle cx="12" cy="12" r="3.5" />
      <circle cx="16.5" cy="7.5" r="1" />
    </>
  ),
  check: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m9 12 2 2 4-4" />
    </>
  ),
  lightning: (
    <>
      <path d="m7 13 4-10v7h6l-4 10v-7Z" />
    </>
  ),
  badge: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="m9 14-2 7 5-2 5 2-2-7" />
    </>
  ),
  chart: (
    <>
      <path d="M5 19h14" />
      <path d="M7 15v4m5-8v8m5-12v12" />
    </>
  ),
  filter: (
    <>
      <path d="M4 6h16M7 12h10m-6 6h2" />
    </>
  ),
  quick: (
    <>
      <path d="M4 12a8 8 0 1 1 8 8" />
      <path d="m12 6-2 6h4l-2 6" />
    </>
  ),
  bookmark: (
    <>
      <path d="M8 4h8a1 1 0 0 1 1 1v14l-5-3-5 3V5a1 1 0 0 1 1-1Z" />
    </>
  ),
};

export default function Icon({ name, size = 24, title, decorative = false, className = '', strokeWidth = 1.5 }) {
  const paths = ICONS[name];
  if (!paths) {
    return null;
  }
  const ariaHidden = decorative || !title;
  return (
    <svg
      className={`icon ${className}`.trim()}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      role="img"
      aria-hidden={ariaHidden}
      aria-label={ariaHidden ? undefined : title}
      focusable="false"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths}
    </svg>
  );
}

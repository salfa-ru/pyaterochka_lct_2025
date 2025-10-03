import "./TimeZone.css";

const pad2 = (n) => String(n).padStart(2, "0");

// IANA зона, например "Europe/Amsterdam"
const getLocalTimeZone = () =>
  Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

// смещение от UTC в часах, например 2 для UTC+02:00
const getLocalUtcOffsetHours = () => -new Date().getTimezoneOffset() / 60;

function buildUtcOffsetLabel(offsetHrs) {
  const sign = offsetHrs >= 0 ? "+" : "−"; // именно длинное минус
  const absH = Math.floor(Math.abs(offsetHrs));
  const absM = Math.round((Math.abs(offsetHrs) - absH) * 60);
  return `UTC${sign}${pad2(absH)}:${pad2(absM)}`;
}

function buildMskDiffLabel(offsetHrs) {
  const MSK_OFFSET = 3; // Москва UTC+3 круглый год
  const diff = offsetHrs - MSK_OFFSET; // локальное − МСК
  const sign = diff > 0 ? "+" : diff < 0 ? "−" : "±";
  const abs = Math.abs(diff);
  return `МСК${sign}${abs}`;
}

/**
 * Параметры:
 * - compact: уменьшенный шрифт/стили
 */
export default function TimeZone({ compact = true }) {
  const tzIANA = getLocalTimeZone();
  const offsetH = getLocalUtcOffsetHours();
  const utcLabel = buildUtcOffsetLabel(offsetH);
  const mskLabel = buildMskDiffLabel(offsetH);

  return (
    <span
      className={`tz-badge${compact ? " tz-badge--compact" : ""}`}
      title={`${tzIANA}, ${utcLabel}, ${mskLabel}`}
      aria-label={`Часовой пояс: ${tzIANA}, смещение: ${utcLabel}, разница с МСК: ${mskLabel}`}
    >
      ({tzIANA}, {utcLabel}, {mskLabel})
    </span>
  );
}

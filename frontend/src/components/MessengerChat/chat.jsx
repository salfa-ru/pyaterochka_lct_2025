import React, { useEffect, useRef, useState } from "react";
import "./chat.css";
import TimeZone from "../TimeZone/TimeZone.jsx";

const BOT_IMG = "./bot.svg";
const PERSON_IMG = "./user.svg";
const BOT_NAME = "БOT";
const PERSON_NAME = "Пользователь";

// --- Утилиты времени
const pad2 = (n) => String(n).padStart(2, "0");
const nowHHMM = () => {
  const d = new Date();
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
};
const uid = () => Math.random().toString(36).slice(2);

// Демо-ротация ответов (мок)
const BOT_MSGS = [
  "Здравствуйте! Чем я могу помочь?",
  "Понимаю. Могу подобрать варианты по бюджету и предпочтениям.",
  "Могу предложить фильтры: вегетарианское, без глютена, острое, детское меню.",
  "Если подскажете город, покажу, что доступно для доставки рядом.",
  "Добавить что-то в корзину?",
];

export default function MessengerChat({
  headerTitle = "Ваш персональный помощник",
  logoSrc = "/logo.svg",
  mock = true,
}) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(() => [
    {
      id: uid(),
      side: "left",
      name: BOT_NAME,
      img: BOT_IMG,
      time: nowHHMM(),
      text: "Здравствуйте! Я помогу Вам выбрать необходимые продукты. Пожалуйста, введите название продукта, марку, объем или любые другие данные, которые вы знаете",
    },
  ]);

  const chatRef = useRef(null);

  // автоскролл вниз при добавлении сообщений
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages.length]);

  const appendMessage = (name, img, side, text) => {
    setMessages((prev) => [
      ...prev,
      { id: uid(), side, name, img, time: nowHHMM(), text },
    ]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const msgText = input.trim();
    if (!msgText) return;

    // сообщение пользователя
    appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
    setInput("");

    // ответ бота (мок)
    if (mock) {
      const r = Math.floor(Math.random() * BOT_MSGS.length);
      const reply = BOT_MSGS[r];
      const delay = Math.max(300, reply.split(" ").length * 100);
      setTimeout(() => {
        appendMessage(BOT_NAME, BOT_IMG, "left", reply);
      }, delay);
    } else {
      // TODO: интеграция с реальным бекендом /api/food-bot
      // fetch("/api/food-bot", { ... })
      //   .then(res => res.json())
      //   .then(data => appendMessage(BOT_NAME, BOT_IMG, "left", data.reply))
      //   .catch(() => appendMessage(BOT_NAME, BOT_IMG, "left", "Упс, произошла ошибка"));
    }
  };

  // инлайн-зелёный (тот же, что у бота). Оставляем класс для общих стилей.
  const sendBtnStyle = { backgroundColor: "#4CAF50" };

  return (
    <section className="msger" aria-label="Chat">
      <header className="msger-header">
        <div className="msger-header-title">
          <i className="fas fa-comment-alt" aria-hidden="true"></i>
          <img src={logoSrc} alt="logo" />
          {headerTitle}
        </div>
        <div className="msger-header-options">
          <span>
            <i className="fas fa-cog" aria-hidden="true"></i>
          </span>
        </div>
      </header>

      <main className="msger-chat" ref={chatRef} aria-live="polite">
        {messages.map((m) => (
          <div key={m.id} className={`msg ${m.side}-msg`}>
            <div
              className="msg-img"
              style={{ backgroundImage: `url(${m.img})` }}
            ></div>

            <div className="msg-bubble">
              <div className="msg-info">
                <div className="msg-info-name">{m.name}</div>
                <div className="msg-info-time">
                  <span>{m.time}</span>
                  {/* Плашка с TZ и разницей с МСК */}
                  <TimeZone compact />
                </div>
              </div>

              <div className="msg-text">{m.text}</div>
            </div>
          </div>
        ))}
      </main>

      <form className="msger-inputarea" onSubmit={handleSubmit}>
        <input
          type="text"
          className="msger-input"
          placeholder="Введите сообщение…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Message"
        />
        <button
          type="submit"
          className="msger-send-btn"
          style={sendBtnStyle}
          title="Отправить (Send)"
        >
          Отправить
        </button>
      </form>
    </section>
  );
}

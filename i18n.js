(function(){
  const STORAGE_KEY = 'kharkiv-rp-language';
  const translations = {
    ua: {
      languageToggle: 'UA / RU',
      homeTitle: 'Kharkiv RP — Офіційний сервер', ranksPageTitle: 'Kharkiv RP — Перевірка звання',
      licensesPageTitle: 'Kharkiv RP — Ліцензії', adminPageTitle: 'Kharkiv RP — Адмін',
      home: 'Головна', ranks: 'Звання', licenses: 'Ліцензії', admin: 'Адмін',
      rules: 'Правила', constitution: 'Конституція', join: 'Почати гру',
      welcome: 'Ласкаво просимо на офіційний сервер Kharkiv RP',
      online: 'Статус: Онлайн (Kharkiv RP активний)', serverRules: 'Правила сервера',
      searchRules: 'Шукати правила (наприклад: булінг, штраф)', constitutionServer: 'Конституція сервера',
      ranksTitle: 'Звання — Перевірка та список', ranksHint: 'Введіть нікнейм гравця, щоб переглянути його звання.',
      playerNickname: 'Нікнейм гравця', check: 'Перевірити', verifiedList: 'Список підтверджених (за фракціями)', verifiedStatus: 'Перевірено',
      noVerified: 'Немає підтверджених', notFound: 'Гравець не знайдений.', loading: 'Завантаження…',
      loadError: 'Помилка при завантаженні.', faction: 'Фракція', rank: 'Звання', verified: 'Підтверджено',
      licensesTitle: 'Ліцензії', licensesHint: 'Перелік чинних ліцензій, підтверджених адміністрацією.',
      searchNickname: 'Пошук за нікнеймом', clear: 'Очистити', weaponLicense: 'Ліцензія на зброю',
      validUntil: 'Дійсно до:', valid: 'Дійсна', unverified: 'Не підтверджено', noLicenses: 'Немає чинних ліцензій',
      licenseLoadError: 'Помилка при завантаженні ліцензій.',
      adminTitle: 'Панель адміністратора', passwordHint: 'Введіть пароль для доступу до панелі.',
      password: 'Пароль', unlock: 'Розблокувати', wrongPassword: 'Невірний пароль',
      managePlayer: 'Додати / Редагувати гравця', nickname: 'Нікнейм', chooseFaction: '-- Виберіть фракцію --',
      licenseExpiry: 'Термін дії ліцензії', save: 'Зберегти', saving: 'Збереження…', saved: 'Збережено',
      requiredNickname: "Нікнейм обов'язковий", connectionError: "Помилка з'єднання", error: 'Помилка',
      invalidFaction: 'Оберіть категорію', dateRequired: 'Вкажіть дату завершення ліцензії', recordNotFound: 'Запис не знайдено', datePassed: 'Термін дії вже минув',
      dbr: 'ДБР', sbs: 'СБС', court: 'Суд', prosecution: 'Прокуратура'
    },
    ru: {
      languageToggle: 'RU / UA',
      homeTitle: 'Kharkiv RP — Официальный сервер', ranksPageTitle: 'Kharkiv RP — Проверка звания',
      licensesPageTitle: 'Kharkiv RP — Лицензии', adminPageTitle: 'Kharkiv RP — Админ',
      home: 'Главная', ranks: 'Звания', licenses: 'Лицензии', admin: 'Админ',
      rules: 'Правила', constitution: 'Конституция', join: 'Начать игру',
      welcome: 'Добро пожаловать на официальный сервер Kharkiv RP',
      online: 'Статус: Онлайн (Kharkiv RP активен)', serverRules: 'Правила сервера',
      searchRules: 'Искать правила (например: буллинг, штраф)', constitutionServer: 'Конституция сервера',
      ranksTitle: 'Звания — Проверка и список', ranksHint: 'Введите никнейм игрока, чтобы посмотреть его звание.',
      playerNickname: 'Никнейм игрока', check: 'Проверить', verifiedList: 'Список подтверждённых (по фракциям)', verifiedStatus: 'Проверено',
      noVerified: 'Нет подтверждённых', notFound: 'Игрок не найден.', loading: 'Загрузка…',
      loadError: 'Ошибка загрузки.', faction: 'Фракция', rank: 'Звание', verified: 'Подтверждено',
      licensesTitle: 'Лицензии', licensesHint: 'Список действующих лицензий, подтверждённых администрацией.',
      searchNickname: 'Поиск по никнейму', clear: 'Очистить', weaponLicense: 'Лицензия на оружие',
      validUntil: 'Действительно до:', valid: 'Действительна', unverified: 'Не подтверждена', noLicenses: 'Нет действующих лицензий',
      licenseLoadError: 'Ошибка загрузки лицензий.',
      adminTitle: 'Панель администратора', passwordHint: 'Введите пароль для доступа к панели.',
      password: 'Пароль', unlock: 'Войти', wrongPassword: 'Неверный пароль',
      managePlayer: 'Добавить / Редактировать игрока', nickname: 'Никнейм', chooseFaction: '-- Выберите категорию --',
      licenseExpiry: 'Срок действия лицензии', save: 'Сохранить', saving: 'Сохранение…', saved: 'Сохранено',
      requiredNickname: 'Никнейм обязателен', connectionError: 'Ошибка соединения', error: 'Ошибка',
      invalidFaction: 'Выберите категорию', dateRequired: 'Укажите дату окончания лицензии', recordNotFound: 'Запись не найдена', datePassed: 'Срок действия уже истёк',
      dbr: 'ДБР', sbs: 'СБС', court: 'Суд', prosecution: 'Прокуратура'
    }
  };
  let language = localStorage.getItem(STORAGE_KEY) || 'ua';
  if(!translations[language]) language = 'ua';

  function t(key){ return (translations[language] && translations[language][key]) || translations.ua[key] || key; }
  function applyLanguage(){
    document.documentElement.lang = language === 'ru' ? 'ru' : 'uk';
    document.querySelectorAll('[data-i18n]').forEach(el=>{ el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{ el.placeholder = t(el.dataset.i18nPlaceholder); });
    document.querySelectorAll('[data-i18n-title]').forEach(el=>{ el.title = t(el.dataset.i18nTitle); });
    document.querySelectorAll('[data-lang-toggle]').forEach(el=>{ el.textContent = t('languageToggle'); });
    window.dispatchEvent(new CustomEvent('languagechange', { detail: { language } }));
  }
  function setLanguage(next){
    language = next === 'ru' ? 'ru' : 'ua';
    localStorage.setItem(STORAGE_KEY, language);
    applyLanguage();
  }
  function addToggle(){
    document.querySelectorAll('[data-lang-toggle]').forEach(el=>{
      el.addEventListener('click', ()=>setLanguage(language === 'ua' ? 'ru' : 'ua'));
    });
  }
  window.i18n = { t, setLanguage, getLanguage: ()=>language, applyLanguage };
  document.addEventListener('DOMContentLoaded', ()=>{ addToggle(); applyLanguage(); });
})();

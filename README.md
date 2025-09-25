# 🎬 Video Transcription Flask App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

Современное веб-приложение для транскрипции речи из видеофайлов с поддержкой 16 языков и real-time отображением результата.

![Demo](https://via.placeholder.com/800x400/2c3e50/ffffff?text=Video+Transcription+App+Demo)

## ✨ Основные возможности

- 🎥 **Поддержка всех видео форматов** - mp4, avi, mov, mkv, webm, flv и другие
- 🌍 **16 языков** - русский, английский, испанский, французский, немецкий, итальянский, португальский, японский, корейский, китайский, арабский, хинди, турецкий, голландский
- 🔄 **Real-time транскрипция** - текст появляется по мере обработки сегментов
- 🎯 **Автоопределение языка** - умное переключение между русским и английским
- 🚀 **WebSocket интерфейс** - мгновенные обновления статуса
- 🔧 **Debug режим** - подробные логи процесса обработки
- 🎨 **Современный UI** - чистый и интуитивный интерфейс

## 🚀 Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/video-transcription-app.git
cd video-transcription-app

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Запуск

```bash
# Запуск приложения (рекомендуется)
python app_with_speechrecognition.py

# Альтернативный вариант с Whisper (требует дополнительной установки)
pip install openai-whisper torch torchaudio
python app.py
```

Откройте http://localhost:5000 в браузере

## 🎯 Использование

1. **Выберите видеофайл** - нажмите "Choose Video File"
2. **Выберите язык** - из выпадающего списка (16 языков или автоопределение)
3. **Запустите транскрипцию** - нажмите "Start Transcription"
4. **Наблюдайте процесс** - real-time обновления статуса и результата
5. **Получите результат** - готовый текст в текстовом поле

## 🌍 Поддерживаемые языки

| Язык | Код | Статус |
|------|-----|---------|
| 🌐 Auto-detect | `auto` | ✅ Русский → Английский |
| 🇷🇺 Русский | `ru-RU` | ✅ Полная поддержка |
| 🇺🇸 English (US) | `en-US` | ✅ Полная поддержка |
| 🇬🇧 English (UK) | `en-GB` | ✅ Полная поддержка |
| 🇪🇸 Español | `es-ES` | ✅ Полная поддержка |
| 🇫🇷 Français | `fr-FR` | ✅ Полная поддержка |
| 🇩🇪 Deutsch | `de-DE` | ✅ Полная поддержка |
| 🇮🇹 Italiano | `it-IT` | ✅ Полная поддержка |
| 🇧🇷 Português | `pt-BR` | ✅ Полная поддержка |
| 🇯🇵 日本語 | `ja-JP` | ✅ Полная поддержка |
| 🇰🇷 한국어 | `ko-KR` | ✅ Полная поддержка |
| 🇨🇳 中文 | `zh-CN` | ✅ Полная поддержка |
| 🇸🇦 العربية | `ar-SA` | ✅ Полная поддержка |
| 🇮🇳 हिन्दी | `hi-IN` | ✅ Полная поддержка |
| 🇹🇷 Türkçe | `tr-TR` | ✅ Полная поддержка |
| 🇳🇱 Nederlands | `nl-NL` | ✅ Полная поддержка |

## Структура проекта

```
video_transcription/
├── venv/                    # Виртуальное окружение
├── app.py                   # Основное Flask приложение
├── templates/
│   └── index.html          # Веб-интерфейс
├── static/
│   ├── style.css           # Стили
│   └── script.js           # WebSocket клиент
├── uploads/                 # Временные файлы
├── requirements.txt         # Базовые зависимости
└── README.md               # Инструкции
```

## Зависимости

### Базовые (обязательные)
- Flask - веб-фреймворк
- Flask-SocketIO - WebSocket поддержка
- moviepy - обработка видео
- ffmpeg-python - кодеки

### Для транскрипции (дополнительно)
- openai-whisper - модель транскрипции
- torch - нейросетевой движок
- torchaudio - аудио обработка

## Примечания

- **Без Whisper**: Приложение работает с mock-транскрипцией для тестирования интерфейса
- **С Whisper**: Полная функциональность с реальной транскрипцией
- **Безопасность**: Загруженные файлы автоматически удаляются после обработки
- **Производительность**: Обработка происходит в отдельном потоке

## Устранение неисправностей

### MoviePy не найден
```bash
pip install moviepy
```

### Whisper не найден
```bash
pip install openai-whisper torch torchaudio
```

### Проблемы с FFmpeg
Убедитесь, что FFmpeg установлен в системе:
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Скачать с https://ffmpeg.org/

## Разработка

Для разработки можете запустить в debug режиме (по умолчанию включен):
```bash
python app.py
```

Приложение перезапустится автоматически при изменении кода.

## 🔧 Техническая архитектура

- **Frontend**: Vanilla JavaScript + WebSocket для real-time связи
- **Backend**: Flask + SocketIO для обработки запросов и уведомлений
- **Аудио**: MoviePy для извлечения аудио из видео
- **Транскрипция**: Google Speech Recognition API (основной) / Whisper (дополнительный)
- **UI**: Современный адаптивный интерфейс с debug режимом

## 🤝 Участие в разработке

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/new-feature`)
3. Commit изменения (`git commit -m 'Add new feature'`)
4. Push в branch (`git push origin feature/new-feature`)
5. Создайте Pull Request

## 📝 Лицензия

Этот проект лицензирован под MIT License - подробности в файле [LICENSE](LICENSE).

## 🙏 Благодарности

- [OpenAI Whisper](https://github.com/openai/whisper) - за великолепную модель транскрипции
- [Google Speech Recognition](https://cloud.google.com/speech-to-text) - за надежный API
- [MoviePy](https://github.com/Zulko/moviepy) - за простую работу с видео
- [Flask](https://flask.palletsprojects.com/) - за минималистичный веб-фреймворк

## ⭐ Поддержка проекта

Если проект был полезен, поставьте звезду ⭐ на GitHub!

---

**Сделано с ❤️ для сообщества разработчиков**
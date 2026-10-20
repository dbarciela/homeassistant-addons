/**
 * Voice Input (Speech-to-Text) Controller for Google Antigravity Smart Home.
 * Modular, clean Web Speech API integration with language auto-detection,
 * real-time transcript streaming to the chat composer, and accessible UI feedback.
 */
(function(global) {
  'use strict';

  class VoiceInputController {
    constructor() {
      this.recognition = null;
      this.isRecording = false;
      this.micBtn = null;
      this.inputEl = null;
      this.transcriptBuffer = '';
      this.initialInputVal = '';
      this.lang = this._detectLanguage();
      this.SpeechRecognition = global.SpeechRecognition || global.webkitSpeechRecognition || null;
    }

    _detectLanguage() {
      const navLang = (navigator.languages && navigator.languages[0]) || navigator.language || 'pt-PT';
      if (navLang.toLowerCase().startsWith('pt-br')) return 'pt-BR';
      if (navLang.toLowerCase().startsWith('pt')) return 'pt-PT';
      return navLang;
    }

    isSupported() {
      return Boolean(this.SpeechRecognition);
    }

    init() {
      this.micBtn = document.getElementById('mic-btn');
      this.inputEl = document.getElementById('user-input');

      if (!this.micBtn) return;

      if (!this.isSupported()) {
        this.micBtn.classList.add('disabled');
        this.micBtn.setAttribute('title', 'Reconhecimento de voz não suportado neste navegador (Recomenda-se Chrome/Edge).');
        return;
      }

      this.micBtn.setAttribute('title', `Ditar por voz (${this.lang})`);
    }

    toggle() {
      if (this.isRecording) {
        this.stop();
      } else {
        this.start();
      }
    }

    start() {
      if (!this.isSupported()) {
        const isPt = this.lang.startsWith('pt');
        const alertMsg = isPt
          ? 'O seu navegador não suporta a Web Speech API. Recomenda-se o Google Chrome ou Microsoft Edge.'
          : 'Your browser does not support Speech-to-Text. Google Chrome or Microsoft Edge is recommended.';
        alert(alertMsg);
        return;
      }

      if (this.isRecording) return;

      try {
        this.recognition = new this.SpeechRecognition();
        this.recognition.lang = this.lang;
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        if (this.inputEl) {
          this.initialInputVal = this.inputEl.value;
          this.transcriptBuffer = '';
        }

        this.recognition.onstart = () => {
          this.isRecording = true;
          this._updateUiState(true);
        };

        this.recognition.onresult = (event) => {
          if (!this.inputEl) return;
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const piece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += piece;
            } else {
              interimTranscript += piece;
            }
          }

          const currentPiece = finalTranscript || interimTranscript;
          if (currentPiece) {
            const spacer = (this.initialInputVal && !this.initialInputVal.endsWith(' ')) ? ' ' : '';
            this.inputEl.value = (this.initialInputVal ? this.initialInputVal + spacer : '') + currentPiece;

            if (typeof global.autoResizeTextarea === 'function') {
              global.autoResizeTextarea();
            }
            if (typeof global.updateSendBtn === 'function') {
              global.updateSendBtn();
            }
          }
        };

        this.recognition.onerror = (event) => {
          console.warn('[VoiceInput] Speech recognition error:', event.error);
          this._handleError(event.error);
          this.stop();
        };

        this.recognition.onend = () => {
          this.stop();
        };

        this.recognition.start();
      } catch (err) {
        console.error('[VoiceInput] Failed to start recognition:', err);
        this.stop();
      }
    }

    stop() {
      this.isRecording = false;
      this._updateUiState(false);
      if (this.recognition) {
        try {
          this.recognition.stop();
        } catch (e) {}
        this.recognition = null;
      }
      if (this.inputEl) {
        this.inputEl.focus();
      }
    }

    _updateUiState(recording) {
      if (!this.micBtn) return;
      if (recording) {
        this.micBtn.classList.add('recording');
        this.micBtn.setAttribute('title', 'A ouvir... (Clique para parar)');
        this.micBtn.setAttribute('aria-pressed', 'true');
      } else {
        this.micBtn.classList.remove('recording');
        this.micBtn.setAttribute('title', `Ditar por voz (${this.lang})`);
        this.micBtn.setAttribute('aria-pressed', 'false');
      }
    }

    _handleError(error) {
      if (error === 'not-allowed') {
        const isPt = this.lang.startsWith('pt');
        const msg = isPt
          ? 'Permissão de microfone negada. Autorize o microfone nas definições do navegador para ditar.'
          : 'Microphone permission denied. Please allow microphone access in your browser settings.';
        alert(msg);
      }
    }
  }

  // Expose singleton to global window
  const voiceController = new VoiceInputController();
  global.VoiceInput = voiceController;

  // Global backward-compatible hook
  global.toggleRecording = function() {
    voiceController.toggle();
  };

  // Auto-init when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => voiceController.init());
  } else {
    voiceController.init();
  }

})(typeof window !== 'undefined' ? window : globalThis);

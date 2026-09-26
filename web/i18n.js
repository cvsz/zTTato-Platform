/**
 * Internationalization (i18n) utilities for zTTato frontend.
 * Supports dynamic language switching and parameter interpolation.
 */

class I18n {
  constructor() {
    this.locale = 'en';
    this.translations = {};
    this.supportedLocales = ['en', 'th', 'zh', 'ja', 'ko', 'vi'];
    this.listeners = new Set();
  }

  /**
   * Initialize i18n with a specific locale
   */
  async init(locale = 'en') {
    this.locale = this.supportedLocales.includes(locale) ? locale : 'en';
    await this.loadTranslations(this.locale);
    return this;
  }

  /**
   * Load translations for a locale
   */
  async loadTranslations(locale) {
    try {
      const response = await fetch(`/i18n/${locale}.json`);
      if (response.ok) {
        this.translations = await response.json();
        this.locale = locale;
        this.notifyListeners();
      } else {
        console.warn(`Failed to load translations for ${locale}`);
        // Fallback to English
        if (locale !== 'en') {
          await this.loadTranslations('en');
        }
      }
    } catch (error) {
      console.error('Failed to load translations:', error);
      if (locale !== 'en') {
        await this.loadTranslations('en');
      }
    }
  }

  /**
   * Translate a key with optional parameter interpolation
   * @param {string} key - Dot-separated translation key (e.g., "dashboard.video.title")
   * @param {Object} params - Parameters for interpolation
   * @returns {string} Translated string
   */
  t(key, params = {}) {
    const keys = key.split('.');
    let value = this.translations;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to key if translation not found
        return key;
      }
    }

    if (typeof value === 'string') {
      // Interpolate parameters
      return value.replace(/\{(\w+)\}/g, (match, key) => {
        return params[key] !== undefined ? params[key] : match;
      });
    }

    return key;
  }

  /**
   * Get current locale
   */
  getLocale() {
    return this.locale;
  }

  /**
   * Set locale and reload translations
   */
  async setLocale(locale) {
    if (this.supportedLocales.includes(locale)) {
      await this.loadTranslations(locale);
    }
  }

  /**
   * Get supported locales
   */
  getSupportedLocales() {
    return [...this.supportedLocales];
  }

  /**
   * Subscribe to locale changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners() {
    this.listeners.forEach(cb => cb(this.locale));
  }

  /**
   * Get HTML lang attribute value
   */
  getHtmlLang() {
    return this.locale;
  }

  /**
   * Get direction (ltr/rtl) for current locale
   */
  getDirection() {
    // All supported languages are LTR
    return 'ltr';
  }
}

// Singleton instance
const i18n = new I18n();

// Convenience function for translations
function t(key, params) {
  return i18n.t(key, params);
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { I18n, i18n, t };
} else if (typeof window !== 'undefined') {
  window.I18n = I18n;
  window.i18n = i18n;
  window.t = t;
}
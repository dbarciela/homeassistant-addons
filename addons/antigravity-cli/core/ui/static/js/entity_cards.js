/**
 * Interactive Entity Cards Component for Google Antigravity Smart Home.
 * Detects <ha-entity>, [entity:id], and ```ha-entity code blocks in markdown responses
 * and mounts live, interactive Home Assistant controls directly inside chat bubbles.
 */
(function(global) {
  'use strict';

  const DOMAIN_ICONS = {
    light: '💡',
    switch: '🔌',
    climate: '🌡️',
    fan: '🌀',
    cover: '🪟',
    sensor: '📊',
    binary_sensor: '🔔',
    media_player: '🎵',
    lock: '🔒',
    vacuum: '🧹',
    automation: '⚡',
    default: '📦',
  };

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function getDomain(entityId) {
    if (!entityId || !entityId.includes('.')) return 'default';
    return entityId.split('.')[0].toLowerCase();
  }

  function getDomainIcon(domain) {
    return DOMAIN_ICONS[domain] || DOMAIN_ICONS.default;
  }

  class EntityCardsManager {
    constructor() {
      this.pendingCardFetches = new Set();
    }

    /**
     * Scan a DOM container (e.g. an answer-content div) and replace entity tags with interactive cards.
     */
    processContainer(container) {
      if (!container) return;

      // 1. Process custom <ha-entity> tags
      const customTags = container.querySelectorAll('ha-entity');
      customTags.forEach(tag => this._replaceHaEntityTag(tag));

      // 2. Process ```ha-entity code blocks
      const codeBlocks = container.querySelectorAll('code.language-ha-entity, pre.ha-entity');
      codeBlocks.forEach(code => this._replaceCodeBlock(code));

      // 3. Process text shortcodes: [entity:domain.name] or [ha:domain.name]
      this._replaceTextShortcodes(container);

      // Register newly mounted cards with live observer if available
      if (typeof global.getLiveCardObserver === 'function') {
        const observer = global.getLiveCardObserver();
        container.querySelectorAll('.device-card').forEach(el => observer.observe(el));
      }
    }

    _replaceHaEntityTag(tag) {
      const entityId = tag.getAttribute('entity_id') || tag.getAttribute('entity-id');
      if (!entityId) return;

      const domain = tag.getAttribute('domain') || getDomain(entityId);
      const name = tag.getAttribute('name') || tag.getAttribute('friendly_name') || entityId;
      const state = tag.getAttribute('state') || 'off';
      const brightness = tag.getAttribute('brightness');
      const unit = tag.getAttribute('unit') || '';

      const cardData = {
        entity_id: entityId,
        domain: domain,
        friendly_name: name,
        state: state,
        brightness: brightness ? parseInt(brightness) : null,
        unit_of_measurement: unit,
      };

      const wrapper = document.createElement('div');
      wrapper.className = 'interactive-entity-wrapper';
      wrapper.innerHTML = this.renderCardHtml(cardData);
      tag.replaceWith(wrapper);

      // Fetch fresh state if state wasn't explicitly supplied
      if (!tag.hasAttribute('state')) {
        this.fetchAndHydrate(entityId, wrapper);
      }
    }

    _replaceCodeBlock(code) {
      const rawText = code.textContent.trim();
      let cardData = null;
      try {
        cardData = JSON.parse(rawText);
      } catch (e) {
        return;
      }

      if (!cardData || !cardData.entity_id) return;

      const wrapper = document.createElement('div');
      wrapper.className = 'interactive-entity-wrapper';
      wrapper.innerHTML = this.renderCardHtml(cardData);

      const targetToReplace = code.closest('pre') || code;
      targetToReplace.replaceWith(wrapper);
    }

    _replaceTextShortcodes(container) {
      // Find text nodes containing [entity:... ] or [ha:... ]
      const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
      const nodesToReplace = [];
      const regex = /\[(?:entity|ha):([a-z0-9_]+\.[a-z0-9_]+)\]/gi;

      let node;
      while ((node = walker.nextNode())) {
        if (regex.test(node.nodeValue)) {
          nodesToReplace.push(node);
        }
      }

      nodesToReplace.forEach(textNode => {
        const parent = textNode.parentNode;
        if (!parent || parent.nodeName === 'SCRIPT' || parent.nodeName === 'STYLE') return;

        const fragment = document.createDocumentFragment();
        const parts = textNode.nodeValue.split(regex);
        regex.lastIndex = 0;

        for (let i = 0; i < parts.length; i++) {
          if (i % 2 === 0) {
            if (parts[i]) fragment.appendChild(document.createTextNode(parts[i]));
          } else {
            const entityId = parts[i];
            const cardEl = document.createElement('div');
            cardEl.className = 'interactive-entity-wrapper';
            cardEl.innerHTML = this.renderCardHtml({
              entity_id: entityId,
              domain: getDomain(entityId),
              friendly_name: entityId,
              state: '...',
            });
            fragment.appendChild(cardEl);
            this.fetchAndHydrate(entityId, cardEl);
          }
        }
        parent.replaceChild(fragment, textNode);
      });
    }

    renderCardHtml(card) {
      const entityId = escapeHtml(card.entity_id);
      const domain = escapeHtml(card.domain || getDomain(card.entity_id));
      const friendlyName = escapeHtml(card.friendly_name || card.name || entityId);
      const state = escapeHtml(card.state || 'off');
      const icon = getDomainIcon(domain);

      const isOn = domain === 'media_player'
        ? !['off', 'unavailable', 'unknown'].includes(state)
        : state === 'on';

      // Control elements based on domain
      let controlsHtml = '';
      if (['light', 'switch', 'fan', 'input_boolean'].includes(domain)) {
        controlsHtml = `
          <label class="toggle-switch">
            <input type="checkbox" ${isOn ? 'checked' : ''} onchange="window.EntityCards.handleToggle(this, '${entityId}', '${domain}')">
            <span class="toggle-slider"></span>
          </label>
        `;
      } else if (domain === 'cover') {
        controlsHtml = `
          <div class="cover-control-buttons">
            <button type="button" onclick="window.EntityCards.callService('${entityId}', 'cover', 'open_cover')">Abrir</button>
            <button type="button" onclick="window.EntityCards.callService('${entityId}', 'cover', 'stop_cover')">Parar</button>
            <button type="button" onclick="window.EntityCards.callService('${entityId}', 'cover', 'close_cover')">Fechar</button>
          </div>
        `;
      } else if (domain === 'sensor') {
        const unit = escapeHtml(card.unit_of_measurement || '');
        controlsHtml = `<span class="sensor-state-badge"><strong>${state}</strong> ${unit}</span>`;
      } else {
        controlsHtml = `<span class="entity-generic-state">${state}</span>`;
      }

      // Brightness slider for lights if supported or on
      let sliderHtml = '';
      if (domain === 'light' && (card.brightness != null || isOn)) {
        const curBr = card.brightness != null ? Math.round((card.brightness / 255) * 100) : 100;
        sliderHtml = `
          <div class="device-card-row-slider">
            <span class="slider-label">Brilho</span>
            <input type="range" min="1" max="100" value="${curBr}" onchange="window.EntityCards.handleBrightness(this, '${entityId}')">
            <span class="slider-val">${curBr}%</span>
          </div>
        `;
      }

      return `
        <div class="device-card inline-device-card" data-entity-id="${entityId}" data-domain="${domain}">
          <div class="device-card-header">
            <div class="device-card-icon-title">
              <span class="device-icon">${icon}</span>
              <div class="device-text">
                <span class="device-title">${friendlyName}</span>
                <span class="device-sub">${entityId}</span>
              </div>
            </div>
            <div class="device-card-action">
              ${controlsHtml}
            </div>
          </div>
          ${sliderHtml}
        </div>
      `;
    }

    async handleToggle(checkbox, entityId, domain) {
      const service = checkbox.checked ? 'turn_on' : 'turn_off';
      await this.callService(entityId, domain, service, {});
      setTimeout(() => this.refreshCard(entityId), 400);
    }

    async handleBrightness(slider, entityId) {
      const pct = parseInt(slider.value, 10);
      const valSpan = slider.parentElement ? slider.parentElement.querySelector('.slider-val') : null;
      if (valSpan) valSpan.textContent = `${pct}%`;

      const brightness255 = Math.round((pct / 100) * 255);
      await this.callService(entityId, 'light', 'turn_on', { brightness: brightness255 });
    }

    async callService(entityId, domain, service, data = {}) {
      try {
        const url = new URL('api/device/control', window.location.href).href;
        await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ entity_id: entityId, domain, service, data }),
        });
      } catch (err) {
        console.warn('[EntityCards] Service call failed:', err);
      }
    }

    async fetchAndHydrate(entityId, targetEl) {
      if (this.pendingCardFetches.has(entityId)) return;
      this.pendingCardFetches.add(entityId);

      try {
        const url = new URL('api/device/state?entity_id=' + encodeURIComponent(entityId), window.location.href).href;
        const res = await fetch(url);
        const data = await res.json();
        const card = data && data.cards && data.cards[0];
        if (card && targetEl) {
          targetEl.innerHTML = this.renderCardHtml(card);
        }
      } catch (e) {
        // Silent catch for network hiccups
      } finally {
        this.pendingCardFetches.delete(entityId);
      }
    }

    async refreshCard(entityId) {
      document.querySelectorAll(`.device-card[data-entity-id="${entityId}"]`).forEach(cardEl => {
        this.fetchAndHydrate(entityId, cardEl.parentElement || cardEl);
      });
    }
  }

  const manager = new EntityCardsManager();
  global.EntityCards = manager;

})(typeof window !== 'undefined' ? window : globalThis);

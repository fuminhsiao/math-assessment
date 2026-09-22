(() => {
  const clone = (value) => JSON.parse(JSON.stringify(value));

  document.querySelectorAll('[data-value-input]').forEach((widget) => {
    const display = widget.querySelector('[data-display]');
    const hidden = widget.parentElement.querySelector('input[type="hidden"][name^="answer_"]');
    const undoStack = [];
    const redoStack = [];

    let state = {
      tokens: [],
      cursor: { index: 0, part: null, offset: 0 }
    };

    // Existing POST values are restored as ordinary characters. Newly inserted
    // fractions use the structured fraction token below.
    const initial = widget.dataset.initial || '';
    if (initial) {
      state.tokens = [...initial].map((char) => ({ type: 'char', value: char }));
      state.cursor.index = state.tokens.length;
    }

    function snapshot() {
      undoStack.push(clone(state));
      if (undoStack.length > 100) undoStack.shift();
      redoStack.length = 0;
    }

    function serialize() {
      return state.tokens.map((token) => {
        if (token.type === 'char') return token.value;
        return `(${token.num})/(${token.den})`;
      }).join('');
    }

    function sync() {
      if (hidden) hidden.value = serialize();
      const error = widget.closest('.mstep-question-box')?.querySelector('.question-error');
      if (error && hidden?.value.trim()) error.hidden = true;
    }

    function caret() {
      const el = document.createElement('span');
      el.className = 'vi-caret';
      el.setAttribute('aria-hidden', 'true');
      return el;
    }

    function renderPart(text, active, offset) {
      const part = document.createElement('span');
      part.className = 'vi-fraction-part';
      const chars = [...text];
      for (let i = 0; i <= chars.length; i++) {
        if (active && i === offset) part.appendChild(caret());
        if (i < chars.length) part.append(document.createTextNode(chars[i]));
      }
      if (!text) {
        const placeholder = document.createElement('span');
        placeholder.className = 'vi-fraction-placeholder';
        placeholder.textContent = '□';
        part.appendChild(placeholder);
      }
      return part;
    }

    function render() {
      display.replaceChildren();
      state.tokens.forEach((token, index) => {
        if (state.cursor.part === null && state.cursor.index === index) display.appendChild(caret());
        if (token.type === 'char') {
          const span = document.createElement('span');
          span.className = 'vi-char';
          span.textContent = token.value === '-' ? '−' : token.value;
          display.appendChild(span);
        } else {
          const frac = document.createElement('span');
          frac.className = 'vi-fraction';
          frac.appendChild(renderPart(token.num, state.cursor.index === index && state.cursor.part === 'num', state.cursor.offset));
          frac.appendChild(renderPart(token.den, state.cursor.index === index && state.cursor.part === 'den', state.cursor.offset));
          display.appendChild(frac);
        }
      });
      if (state.cursor.part === null && state.cursor.index === state.tokens.length) display.appendChild(caret());
      if (!state.tokens.length) {
        const empty = document.createElement('span');
        empty.className = 'vi-empty-block';
        display.appendChild(empty);
      }
      sync();
    }

    function activeFraction() {
      if (!state.cursor.part) return null;
      const token = state.tokens[state.cursor.index];
      return token?.type === 'fraction' ? token : null;
    }

    function insertChar(value) {
      snapshot();
      const frac = activeFraction();
      if (frac) {
        const key = state.cursor.part;
        frac[key] = frac[key].slice(0, state.cursor.offset) + value + frac[key].slice(state.cursor.offset);
        state.cursor.offset += value.length;
      } else {
        state.tokens.splice(state.cursor.index, 0, { type: 'char', value });
        state.cursor.index += 1;
      }
      render();
    }

    function insertFraction() {
      snapshot();
      // If already inside a fraction, move out first and insert after it.
      if (state.cursor.part) {
        state.cursor = { index: state.cursor.index + 1, part: null, offset: 0 };
      }
      const index = state.cursor.index;
      state.tokens.splice(index, 0, { type: 'fraction', num: '', den: '' });
      state.cursor = { index, part: 'num', offset: 0 };
      render();
    }

    function negative() {
      insertChar('-');
    }

    function moveLeft() {
      const frac = activeFraction();
      if (frac) {
        const text = frac[state.cursor.part];
        if (state.cursor.offset > 0) state.cursor.offset--;
        else if (state.cursor.part === 'den') {
          state.cursor.part = 'num';
          state.cursor.offset = frac.num.length;
        } else state.cursor = { index: state.cursor.index, part: null, offset: 0 };
      } else if (state.cursor.index > 0) {
        const previous = state.tokens[state.cursor.index - 1];
        if (previous?.type === 'fraction') {
          state.cursor = { index: state.cursor.index - 1, part: 'den', offset: previous.den.length };
        } else state.cursor.index--;
      }
      render();
    }

    function moveRight() {
      const frac = activeFraction();
      if (frac) {
        const text = frac[state.cursor.part];
        if (state.cursor.offset < text.length) state.cursor.offset++;
        else if (state.cursor.part === 'num') {
          state.cursor.part = 'den';
          state.cursor.offset = 0;
        } else state.cursor = { index: state.cursor.index + 1, part: null, offset: 0 };
      } else if (state.cursor.index < state.tokens.length) {
        const next = state.tokens[state.cursor.index];
        if (next?.type === 'fraction') state.cursor = { index: state.cursor.index, part: 'num', offset: 0 };
        else state.cursor.index++;
      }
      render();
    }

    function backspace() {
      const frac = activeFraction();
      if (frac) {
        const key = state.cursor.part;
        if (state.cursor.offset > 0) {
          snapshot();
          frac[key] = frac[key].slice(0, state.cursor.offset - 1) + frac[key].slice(state.cursor.offset);
          state.cursor.offset--;
        } else if (!frac.num && !frac.den) {
          snapshot();
          const index = state.cursor.index;
          state.tokens.splice(index, 1);
          state.cursor = { index, part: null, offset: 0 };
        } else {
          moveLeft();
          return;
        }
      } else if (state.cursor.index > 0) {
        snapshot();
        const previous = state.tokens[state.cursor.index - 1];
        if (previous?.type === 'fraction') {
          state.cursor = { index: state.cursor.index - 1, part: 'den', offset: previous.den.length };
          render();
          return;
        }
        state.tokens.splice(state.cursor.index - 1, 1);
        state.cursor.index--;
      }
      render();
    }

    function clearAll() {
      if (!state.tokens.length) return;
      snapshot();
      state = { tokens: [], cursor: { index: 0, part: null, offset: 0 } };
      render();
    }

    function undo() {
      if (!undoStack.length) return;
      redoStack.push(clone(state));
      state = undoStack.pop();
      render();
    }

    function redo() {
      if (!redoStack.length) return;
      undoStack.push(clone(state));
      state = redoStack.pop();
      render();
    }

    widget.addEventListener('click', (event) => {
      const button = event.target.closest('button');
      if (!button) return;
      if (button.dataset.key !== undefined) insertChar(button.dataset.key);
      else {
        const actions = { clear: clearAll, undo, redo, left: moveLeft, right: moveRight, backspace, fraction: insertFraction, negative };
        actions[button.dataset.action]?.();
      }
      display.focus({ preventScroll: true });
    });

    display.addEventListener('keydown', (event) => {
      if (/^[0-9.]$/.test(event.key)) { event.preventDefault(); insertChar(event.key); }
      else if (event.key === '-') { event.preventDefault(); negative(); }
      else if (event.key === 'ArrowLeft') { event.preventDefault(); moveLeft(); }
      else if (event.key === 'ArrowRight') { event.preventDefault(); moveRight(); }
      else if (event.key === 'Backspace' || event.key === 'Delete') { event.preventDefault(); backspace(); }
    });

    render();
  });
})();

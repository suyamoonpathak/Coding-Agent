import { configureStore, createSlice } from '@reduxjs/toolkit';

const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    modelBase: process.env.REACT_APP_MODEL_BASE_URL || 'http://localhost:8000',
    execBase: process.env.REACT_APP_EXEC_BASE_URL || 'http://localhost:5000',
    theme: 'dark',
  },
  reducers: {
    setModelBase(state, action) { state.modelBase = action.payload; },
    setExecBase(state, action) { state.execBase = action.payload; },
    setTheme(state, action) { state.theme = action.payload; },
  },
});

const messagesSlice = createSlice({
  name: 'messages',
  initialState: [],
  reducers: {
    add(state, action) { state.push(action.payload); },
    clear() { return []; },
    updateLast(state, action) {
      if (state.length === 0) return;
      state[state.length - 1] = { ...(state[state.length - 1] || {}), content: action.payload };
    },
  },
});

export const { setModelBase, setExecBase, setTheme } = settingsSlice.actions;
export const { add: addMessage, clear: clearMessages, updateLast } = messagesSlice.actions;

// Load persisted state
let preloaded;
try {
  const raw = localStorage.getItem('coding-agent-state');
  if (raw) preloaded = JSON.parse(raw);
} catch {}

export const store = configureStore({
  reducer: {
    settings: settingsSlice.reducer,
    messages: messagesSlice.reducer,
  },
  preloadedState: preloaded,
});

// Persist to localStorage
store.subscribe(() => {
  try {
    const state = store.getState();
    localStorage.setItem('coding-agent-state', JSON.stringify({
      settings: state.settings,
      messages: state.messages,
    }));
  } catch {}
});



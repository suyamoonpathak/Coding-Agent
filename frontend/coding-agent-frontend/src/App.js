import React, { useState } from 'react';
import './App.css';
import Chat from './components/Chat';
import Executor from './components/Executor';
import { useSelector } from 'react-redux';
import SettingsModal from './components/SettingsModal';

function App() {
  const [tab, setTab] = useState('chat'); // 'chat' | 'execute'
  const [openSettings, setOpenSettings] = useState(false);
  const { modelBase, execBase } = useSelector((s) => s.settings);

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <div className="title">Coding Agent</div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <div className="tabs">
            <div className={`tab ${tab === 'chat' ? 'active' : ''}`} onClick={()=>setTab('chat')}>Chat</div>
            <div className={`tab ${tab === 'execute' ? 'active' : ''}`} onClick={()=>setTab('execute')}>Execute</div>
            </div>
            <div className="tab" onClick={()=>setOpenSettings(true)}>Settings</div>
          </div>
        </div>

        {tab === 'chat' ? (
          <Chat modelBase={modelBase} />
        ) : (
          <Executor execBase={execBase} />
        )}
        <SettingsModal open={openSettings} onClose={()=>setOpenSettings(false)} />
      </div>
    </div>
  );
}

export default App;

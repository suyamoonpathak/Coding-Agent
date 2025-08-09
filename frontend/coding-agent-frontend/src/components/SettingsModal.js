import React from 'react';
import Button from './ui/Button';
import TextArea from './ui/TextArea';
import { useDispatch, useSelector } from 'react-redux';
import { setExecBase, setModelBase } from '../store';

export default function SettingsModal({ open, onClose }) {
  const dispatch = useDispatch();
  const { modelBase, execBase } = useSelector((s) => s.settings);
  const [model, setModel] = React.useState(modelBase);
  const [exec, setExec] = React.useState(execBase);

  React.useEffect(() => {
    setModel(modelBase);
    setExec(execBase);
  }, [modelBase, execBase, open]);

  if (!open) return null;
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }} onClick={onClose}>
      <div style={{ width: 520, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 12, padding: 16 }} onClick={(e)=>e.stopPropagation()}>
        <div className="header" style={{ marginBottom: 12 }}>
          <div className="title">Settings</div>
        </div>
        <div className="row" style={{ marginBottom: 12 }}>
          <div style={{ flex: 1 }}>
            <div className="label" style={{ marginBottom: 6 }}>Model Base URL</div>
            <TextArea rows={2} value={model} onChange={(e)=>setModel(e.target.value)} />
          </div>
        </div>
        <div className="row" style={{ marginBottom: 16 }}>
          <div style={{ flex: 1 }}>
            <div className="label" style={{ marginBottom: 6 }}>Execution Base URL</div>
            <TextArea rows={2} value={exec} onChange={(e)=>setExec(e.target.value)} />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={() => { dispatch(setModelBase(model)); dispatch(setExecBase(exec)); onClose(); }}>Save</Button>
        </div>
      </div>
    </div>
  );
}



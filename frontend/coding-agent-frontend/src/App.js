import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [mode, setMode] = useState('generate'); // 'generate' or 'execute'
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [stream, setStream] = useState(false);
  const modelBase = process.env.REACT_APP_MODEL_BASE_URL || 'http://localhost:8000';
  const execBase = process.env.REACT_APP_EXEC_BASE_URL || 'http://localhost:5000';

  // Handle toggle change between code generation and execution
  const handleToggle = (e) => {
    setMode(e.target.value);
    setOutput('');
  };

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Handle feedback change
  const handleFeedbackChange = (e) => {
    setFeedback(e.target.value);
  };

  const readStream = async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      setOutput((prev) => prev + chunk);
    }
  };

  // Send request to backend based on mode
  const handleSubmit = async () => {
    setLoading(true);
    setOutput('');
    try {
      if (mode === 'generate') {
        if (stream) {
          const resp = await fetch(modelBase + '/generate_code_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: input })
          });
          if (!resp.ok) throw new Error('Stream failed');
          await readStream(resp);
        } else {
          const response = await axios.post(modelBase + '/generate_code/', { prompt: input });
          setOutput(response.data.generated_code || '');
        }
      } else {
        if (stream) {
          const resp = await fetch(execBase + '/execute_code_stream/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: input })
          });
          if (!resp.ok) throw new Error('Exec stream failed');
          await readStream(resp);
        } else {
          const response = await axios.post(execBase + '/execute_code/', { code: input });
          const { logs, exit_code } = response.data;
          setOutput((logs || '') + (typeof exit_code !== 'undefined' ? `\nExit code: ${exit_code}` : ''));
        }
      }
    } catch (error) {
      setOutput('Error: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Autonomous Coding Agent</h1>
      
      {/* Mode toggle */}
      <div>
        <button 
          value="generate"
          onClick={handleToggle} 
          className={mode === 'generate' ? 'active' : ''}>
          Code Generation
        </button>
        <button 
          value="execute" 
          onClick={handleToggle} 
          className={mode === 'execute' ? 'active' : ''}>
          Code Execution
        </button>
      </div>

      {/* Stream toggle */}
      <div style={{ marginTop: 8 }}>
        <label>
          <input type="checkbox" checked={stream} onChange={(e) => setStream(e.target.checked)} /> Stream
        </label>
      </div>

      {/* Input area */}
      <textarea
        placeholder={mode === 'generate' ? "Enter prompt for code generation..." : "Enter Python code for execution..."}
        value={input}
        onChange={handleInputChange}
        rows="6"
        cols="50"
      />
      
      {/* Submit button */}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Submit'}
      </button>

      {/* Output area */}
      <div className="output-area">
        <h3>Output</h3>
        <pre>{output}</pre>
      </div>

      {/* Feedback section */}
      {mode === 'generate' && (
        <div className="feedback">
          <h3>Provide Feedback</h3>
          <textarea 
            placeholder="Tell us what went wrong or if you need improvements."
            value={feedback}
            onChange={handleFeedbackChange}
            rows="4"
            cols="50"
          />
          <button 
            onClick={() => {
              // Handle saving or sending feedback, e.g., to a backend or log file
              alert("Feedback Submitted!");
              setFeedback('');
            }}
          >
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  );
}

export default App;

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [mode, setMode] = useState('generate'); // 'generate' or 'execute'
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');

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

  // Send request to backend based on mode
  const handleSubmit = async () => {
    setLoading(true);
    try {
      let response;
      if (mode === 'generate') {
        // For code generation
        response = await axios.post('http://localhost:8000/generate_code/', {
          prompt: input,
        });
      } else {
        // For code execution
        response = await axios.post('http://localhost:5000/execute_code/', {
          code: input,
        });
      }
      setOutput(response.data.generated_code || response.data.output);
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

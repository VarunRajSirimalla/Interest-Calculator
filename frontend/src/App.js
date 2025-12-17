/**
 * The main App component - super simple!
 * Just wraps our calculator and displays it.
 */

import React from 'react';
import InterestCalculator from './components/InterestCalculator';
import './App.css';

function App() {
  return (
    <div className="App">
      <InterestCalculator />
    </div>
  );
}

export default App;

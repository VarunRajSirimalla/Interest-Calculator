/**
 * The Interest Calculator Component
 * 
 * This is the heart of our app! It handles everything:
 * - Getting input from the user
 * - Making sure the numbers make sense
 * - Talking to our backend API
 * - Showing the results (or any errors)
 */

import React, { useState } from 'react';
import { calculateInterest } from '../services/api';

const InterestCalculator = () => {
  // Form state
  const [principal, setPrincipal] = useState('');
  const [rate, setRate] = useState('');
  const [time, setTime] = useState('');

  // Results state
  const [results, setResults] = useState(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Makes sure all the numbers the user entered are valid.
   * Returns any errors we find, or null if everything's good.
   */
  const validateInputs = () => {
    const errors = {};

    if (!principal || parseFloat(principal) <= 0) {
      errors.principal = 'Principal must be greater than 0';
    }

    if (!rate || parseFloat(rate) <= 0) {
      errors.rate = 'Rate must be greater than 0';
    }

    if (parseFloat(rate) > 100) {
      errors.rate = 'Rate cannot exceed 100%';
    }

    if (!time || parseFloat(time) <= 0) {
      errors.time = 'Time must be greater than 0';
    }

    return Object.keys(errors).length > 0 ? errors : null;
  };

  /**
   * When the user clicks the Calculate button, this is what happens.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous results and errors
    setError('');
    setResults(null);

    // Validate inputs
    const validationErrors = validateInputs();
    if (validationErrors) {
      setError(Object.values(validationErrors).join('. '));
      return;
    }

    // Prepare data
    const data = {
      principal: parseFloat(principal),
      rate: parseFloat(rate),
      time: parseFloat(time),
    };

    // Make API call
    setLoading(true);
    try {
      const result = await calculateInterest(data);
      setResults(result);
      setError('');
    } catch (err) {
      setError(err.message || 'Calculation failed. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Clears everything and starts fresh.
   */
  const handleReset = () => {
    setPrincipal('');
    setRate('');
    setTime('');
    setResults(null);
    setError('');
  };

  /**
   * Makes numbers look pretty with currency formatting.
   */
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};


  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8 col-md-10">
          <div className="card shadow-lg">
            <div className="card-body p-4">
              <div className="text-center mb-4">
                <h1 className="display-4 mb-2">💰 Interest Calculator</h1>
                <p className="text-muted">Calculate Simple and Compound Interest</p>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="principal" className="form-label">
                    Principal Amount (₹) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    id="principal"
                    value={principal}
                    onChange={(e) => setPrincipal(e.target.value)}
                    placeholder="Enter principal amount"
                    step="0.01"
                    min="0"
                    required
                    disabled={loading}
                  />
                  <small className="form-text text-muted">The initial amount of money</small>
                </div>

                <div className="mb-3">
                  <label htmlFor="rate" className="form-label">
                    Interest Rate (%) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    id="rate"
                    value={rate}
                    onChange={(e) => setRate(e.target.value)}
                    placeholder="Enter interest rate"
                    step="0.01"
                    min="0"
                    max="100"
                    required
                    disabled={loading}
                  />
                  <small className="form-text text-muted">Annual interest rate percentage</small>
                </div>

                <div className="mb-3">
                  <label htmlFor="time" className="form-label">
                    Time Period (Years) <span className="text-danger">*</span>
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    id="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    placeholder="Enter time period"
                    step="0.01"
                    min="0"
                    required
                    disabled={loading}
                  />
                  <small className="form-text text-muted">Duration in years</small>
                </div>

                {error && (
                  <div className="alert alert-danger d-flex align-items-center" role="alert">
                    <span className="me-2">⚠️</span>
                    <div>{error}</div>
                  </div>
                )}

                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg px-4"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Calculating...
                      </>
                    ) : (
                      <>
                        <span className="me-2">🧮</span>
                        Calculate Interest
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary btn-lg px-4"
                    onClick={handleReset}
                    disabled={loading}
                  >
                    Reset
                  </button>
                </div>
              </form>

              {results && (
                <div className="mt-5">
                  <h2 className="text-center mb-4">📊 Calculation Results</h2>
                  
                  <div className="row g-3 mb-4">
                    <div className="col-md-6">
                      <div className="card border-primary h-100">
                        <div className="card-body text-center">
                          <div className="display-6 mb-2">📈</div>
                          <h5 className="card-title">Simple Interest</h5>
                          <p className="display-6 text-primary fw-bold">
                            {formatCurrency(results.simpleInterest)}
                          </p>
                          <p className="text-muted small">SI = (P × R × T) / 100</p>
                        </div>
                      </div>
                    </div>

                    <div className="col-md-6">
                      <div className="card border-success h-100">
                        <div className="card-body text-center">
                          <div className="display-6 mb-2">📊</div>
                          <h5 className="card-title">Compound Interest</h5>
                          <p className="display-6 text-success fw-bold">
                            {formatCurrency(results.compoundInterest)}
                          </p>
                          <p className="text-muted small">CI = P × ((1 + R/100)^T - 1)</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="card bg-light">
                    <div className="card-body">
                      <h5 className="card-title">Summary</h5>
                      <div className="row g-3">
                        <div className="col-sm-6 col-md-3">
                          <div className="d-flex flex-column">
                            <span className="text-muted small">Principal:</span>
                            <span className="fw-semibold">{formatCurrency(results.principal)}</span>
                          </div>
                        </div>
                        <div className="col-sm-6 col-md-3">
                          <div className="d-flex flex-column">
                            <span className="text-muted small">Rate:</span>
                            <span className="fw-semibold">{results.rate}%</span>
                          </div>
                        </div>
                        <div className="col-sm-6 col-md-3">
                          <div className="d-flex flex-column">
                            <span className="text-muted small">Time:</span>
                            <span className="fw-semibold">{results.time} years</span>
                          </div>
                        </div>
                        <div className="col-sm-6 col-md-3">
                          <div className="d-flex flex-column">
                            <span className="text-muted small">Total (Principal + CI):</span>
                            <span className="fw-bold text-success">
                              {formatCurrency(results.principal + results.compoundInterest)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="alert alert-info mt-3" role="alert">
                    <strong>Note:</strong> Compound Interest is{' '}
                    {formatCurrency(results.compoundInterest - results.simpleInterest)}{' '}
                    more than Simple Interest for this calculation.
                  </div>
                </div>
              )}
            </div>
          </div>

          <footer className="text-center mt-4 text-muted">
            <small>Powered by Google Sheets | Built with React & FastAPI</small>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default InterestCalculator;

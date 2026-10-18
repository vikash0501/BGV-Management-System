import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'

import CandidateDashboard from './pages/CandidateDashboard'
import Candidates from './pages/Candidates'
import ClientCandidates from './pages/ClientCandidates'

import {
  loginUser,
  getProfile,
  logoutUser,
} from './services/authService'

import {
  getMyCandidateReport,
  getMyCandidateProfile,
} from './services/candidateService'


function App() {
  const location = useLocation()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)


  const handleLogin = async (event) => {
    event.preventDefault()

    setMessage('')
    setProfile(null)
    setLoading(true)

    try {
      await loginUser({
        username,
        password,
      })

      const profileData = await getProfile()

      setProfile(profileData)
      setMessage('Login successful.')
    } catch (error) {
      console.error('Login error:', error)

      setMessage(
        error.response
          ? `Login failed (${error.response.status}): ${
              error.response.data?.detail ||
              JSON.stringify(error.response.data)
            }`
          : `Login request failed: ${error.message}`
      )
    } finally {
      setLoading(false)
    }
  }


  const handleLogout = async () => {
    try {
      await logoutUser()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setProfile(null)
      setUsername('')
      setPassword('')
      setMessage('')
    }
  }


  const handleViewMyReport = async () => {
    try {
      const candidateProfile = await getMyCandidateProfile()

      const caseId = candidateProfile?.case_id

      if (!caseId) {
        alert('BGV case not found.')
        return
      }

      const pdfBlob = await getMyCandidateReport(caseId)

      const pdfUrl = window.URL.createObjectURL(pdfBlob)

      window.open(pdfUrl, '_blank')
    } catch (error) {
      console.error('View candidate report error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load your BGV report.'
      )
    }
  }


  return (
    <div className="min-h-screen bg-slate-100">

      {location.pathname === '/' && (
        <div className="container py-5">

          <div className="row justify-content-center">

            <div className="col-md-8 col-lg-10">

              <div className="card shadow-sm border-0">

                <div className="card-body p-4">

                  <h2 className="text-center mb-2">
                    BGV Management System
                  </h2>

                  <p className="text-center text-muted mb-4">
                    Login to continue
                  </p>


                  {!profile && (
                    <form onSubmit={handleLogin}>

                      <div className="mb-3">

                        <label className="form-label">
                          Username
                        </label>

                        <input
                          type="text"
                          className="form-control"
                          autoComplete="username"
                          value={username}
                          onChange={(event) =>
                            setUsername(event.target.value)
                          }
                          placeholder="Enter username"
                          required
                        />

                      </div>


                      <div className="mb-3">

                        <label className="form-label">
                          Password
                        </label>

                        <input
                          type="password"
                          className="form-control"
                          autoComplete="current-password"
                          value={password}
                          onChange={(event) =>
                            setPassword(event.target.value)
                          }
                          placeholder="Enter password"
                          required
                        />

                      </div>


                      <button
                        type="submit"
                        className="btn btn-primary w-100"
                        disabled={loading}
                      >
                        {loading ? 'Logging in...' : 'Login'}
                      </button>

                    </form>
                  )}


                  {message && (
                    <div className="alert alert-info mt-3">
                      {message}
                    </div>
                  )}


                  {profile && (
                    <div className="mt-4">

                      {/* Header */}

                      <div className="d-flex justify-content-between align-items-center mb-4">

                        <div>

                          <h4 className="mb-1">
                            Welcome, {profile.username}
                          </h4>

                          <p className="text-muted mb-0">
                            BGV Management System Dashboard
                          </p>

                        </div>


                        <button
                          type="button"
                          className="btn btn-danger"
                          onClick={handleLogout}
                        >
                          Logout
                        </button>

                      </div>


                      {/* User Information */}

                      <div className="card border-0 shadow-sm mb-4">

                        <div className="card-body">

                          <h5 className="card-title mb-3">
                            User Information
                          </h5>

                          <p className="mb-2">
                            <strong>Username:</strong>{' '}
                            {profile.username}
                          </p>

                          <p className="mb-2">
                            <strong>Email:</strong>{' '}
                            {profile.email}
                          </p>

                          <p className="mb-0">
                            <strong>Role:</strong>{' '}

                            <span className="badge bg-primary">
                              {profile.role}
                            </span>
                          </p>

                        </div>

                      </div>


                      {/* Dashboard Cards */}

                      <div className="row g-3">


                        {/* Candidates / My BGV Profile */}

                        <div className="col-md-4">

                          <div className="card border-0 shadow-sm h-100">

                            <div className="card-body">

                              <h5 className="card-title">

                                {profile.role === 'CANDIDATE'
                                  ? 'My BGV Profile'
                                  : profile.role === 'CLIENT'
                                  ? 'My Candidates'
                                  : 'Candidates'}

                              </h5>


                              <p className="text-muted">

                                {profile.role === 'CANDIDATE'
                                  ? 'View your personal details and BGV status.'
                                  : profile.role === 'CLIENT'
                                  ? 'View candidates assigned to you.'
                                  : 'Manage candidate information and records.'}

                              </p>


                              {profile.role === 'CANDIDATE' ? (

                                <Link
                                  to="/candidate/dashboard"
                                  className="btn btn-primary"
                                >
                                  My BGV Dashboard
                                </Link>

                              ) : profile.role === 'CLIENT' ? (

                                <Link
                                  to="/client/candidates"
                                  className="btn btn-primary"
                                >
                                  Open My Candidates
                                </Link>

                              ) : (

                                <Link
                                  to="/candidates"
                                  className="btn btn-primary"
                                >
                                  Open Candidates
                                </Link>

                              )}

                            </div>

                          </div>

                        </div>


                        {/* BGV Cases / My BGV Status */}

                        <div className="col-md-4">

                          <div className="card border-0 shadow-sm h-100">

                            <div className="card-body">

                              <h5 className="card-title">

                                {profile.role === 'CANDIDATE'
                                  ? 'My BGV Status'
                                  : 'BGV Cases'}

                              </h5>


                              <p className="text-muted">

                                {profile.role === 'CANDIDATE'
                                  ? 'View your background verification case status.'
                                  : profile.role === 'CLIENT'
                                  ? 'View and monitor BGV cases for your candidates.'
                                  : 'Manage background verification cases.'}

                              </p>


                              {profile.role === 'CANDIDATE' ? (

                                <Link
                                  to="/candidate/dashboard"
                                  className="btn btn-primary"
                                >
                                  View My BGV Status
                                </Link>

                              ) : (

                                <button
                                  type="button"
                                  className="btn btn-primary"
                                >
                                  Open Cases
                                </button>

                              )}

                            </div>

                          </div>

                        </div>


                        {/* Reports */}

                        <div className="col-md-4">

                          <div className="card border-0 shadow-sm h-100">

                            <div className="card-body">

                              <h5 className="card-title">

                                {profile.role === 'CANDIDATE'
                                  ? 'My BGV Report'
                                  : 'Reports'}

                              </h5>


                              <p className="text-muted">

                                {profile.role === 'CANDIDATE'
                                  ? 'View your background verification report.'
                                  : 'View and manage BGV reports.'}

                              </p>


                              {profile.role === 'CANDIDATE' ? (

                                <button
                                  type="button"
                                  className="btn btn-primary"
                                  onClick={handleViewMyReport}
                                >
                                  View My Report
                                </button>

                              ) : (

                                <button
                                  type="button"
                                  className="btn btn-primary"
                                >
                                  Open Reports
                                </button>

                              )}

                            </div>

                          </div>

                        </div>


                      </div>

                    </div>
                  )}

                </div>

              </div>

            </div>

          </div>

        </div>
      )}


      {/* Application Routes */}

      <Routes>

        <Route
          path="/"
          element={<div />}
        />

        <Route
          path="/candidates"
          element={<Candidates />}
        />

        <Route
          path="/client/candidates"
          element={<ClientCandidates />}
        />

        <Route
          path="/candidate/dashboard"
          element={<CandidateDashboard />}
        />

      </Routes>

    </div>
  )
}


export default App
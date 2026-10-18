import { useEffect, useState } from 'react'

import {
  getMyCandidateProfile,
  getMyCandidateBGVCase,
} from '../services/candidateService'

function CandidateDashboard() {
  const [candidate, setCandidate] = useState(null)
  const [bgvCase, setBgvCase] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showStatus, setShowStatus] = useState(false)

  const loadBGVCase = async (caseId) => {
    try {
      const data = await getMyCandidateBGVCase(caseId)

      console.log('BGV Case API response:', data)

      setBgvCase(data)
    } catch (error) {
      console.error('Get BGV case error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load BGV case status.'
      )
    }
  }

  const loadCandidateProfile = async () => {
    try {
      setLoading(true)

      const data = await getMyCandidateProfile()

      console.log('Candidate API response:', data)

      setCandidate(data)

      if (data.case_id) {
        await loadBGVCase(data.case_id)
      } else {
        setBgvCase(null)
      }
    } catch (error) {
      console.error('Get candidate profile error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load your profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCandidateProfile()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-3 shadow-sm p-5 text-center">
          <div
            className="spinner-border text-primary mb-3"
            role="status"
          >
            <span className="visually-hidden">
              Loading...
            </span>
          </div>

          <p className="mb-0 text-slate-600">
            Loading your BGV dashboard...
          </p>
        </div>
      </div>
    )
  }

  if (!candidate) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="alert alert-warning shadow-sm">
          Candidate profile not found.
        </div>
      </div>
    )
  }

  const summary = bgvCase?.verification_summary

  return (
    <div className="min-h-screen bg-slate-100 py-4 py-md-5">

      <div className="container">

        {/* Header */}
        <div className="mb-4">

          <p className="text-primary fw-semibold mb-1">
            Candidate Portal
          </p>

          <h1 className="fw-bold text-slate-900 mb-2">
            My BGV Dashboard
          </h1>

          <p className="text-slate-500 mb-0">
            View your personal information and background
            verification progress.
          </p>

        </div>


        {/* Personal Information */}
        <div className="bg-white rounded-3 shadow-sm border-0 mb-4">

          <div className="p-4 border-bottom">

            <h5 className="fw-bold mb-1">
              Personal Information
            </h5>

            <p className="text-slate-500 mb-0">
              Your registered candidate information.
            </p>

          </div>


          <div className="p-4">

            <div className="row g-4">

              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Candidate Code
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.candidate_code}
                </p>

              </div>


              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Full Name
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.first_name}{' '}
                  {candidate.last_name}
                </p>

              </div>


              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Email
                </p>

                <p className="fw-semibold mb-0 text-break">
                  {candidate.email}
                </p>

              </div>


              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Phone
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.phone}
                </p>

              </div>


              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Date of Birth
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.date_of_birth || 'Not provided'}
                </p>

              </div>


              <div className="col-12 col-md-6">

                <p className="text-slate-500 small mb-1">
                  Candidate Status
                </p>

                <span className="badge bg-success-subtle text-success border border-success-subtle px-3 py-2">
                  {candidate.status}
                </span>

              </div>


              <div className="col-12 col-md-4">

                <p className="text-slate-500 small mb-1">
                  City
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.city || 'Not provided'}
                </p>

              </div>


              <div className="col-12 col-md-4">

                <p className="text-slate-500 small mb-1">
                  State
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.state || 'Not provided'}
                </p>

              </div>


              <div className="col-12 col-md-4">

                <p className="text-slate-500 small mb-1">
                  Pincode
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.pincode || 'Not provided'}
                </p>

              </div>


              <div className="col-12">

                <p className="text-slate-500 small mb-1">
                  Address
                </p>

                <p className="fw-semibold mb-0">
                  {candidate.address || 'Not provided'}
                </p>

              </div>

            </div>

          </div>

        </div>


        {/* BGV Overview */}
        <div className="bg-white rounded-3 shadow-sm border-0 mb-4">

          <div className="p-4 border-bottom">

            <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">

              <div>

                <h5 className="fw-bold mb-1">
                  BGV Overview
                </h5>

                <p className="text-slate-500 mb-0">
                  Current status of your background verification.
                </p>

              </div>

              {bgvCase?.case?.status && (
                <span className="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2">
                  {bgvCase.case.status}
                </span>
              )}

            </div>

          </div>


          <div className="p-4">

            {bgvCase?.case ? (

              <>

                <div className="row g-3 mb-4">

                  <div className="col-12 col-md-6">

                    <div className="bg-slate-50 rounded-3 p-3 h-100">

                      <p className="text-slate-500 small mb-1">
                        Case Number
                      </p>

                      <p className="fw-bold mb-0">
                        {bgvCase.case.case_number}
                      </p>

                    </div>

                  </div>


                  <div className="col-12 col-md-6">

                    <div className="bg-slate-50 rounded-3 p-3 h-100">

                      <p className="text-slate-500 small mb-1">
                        Verification Progress
                      </p>

                      <p className="fw-bold mb-0">
                        {summary?.verified ?? 0} of{' '}
                        {summary?.total ?? 0} verified
                      </p>

                    </div>

                  </div>

                </div>


                <div className="row g-3">

                  <div className="col-6 col-lg-3">

                    <div className="border rounded-3 p-3 text-center h-100">

                      <p className="text-slate-500 small mb-1">
                        Total
                      </p>

                      <h4 className="fw-bold mb-0">
                        {summary?.total ?? 0}
                      </h4>

                    </div>

                  </div>


                  <div className="col-6 col-lg-3">

                    <div className="border border-success-subtle rounded-3 p-3 text-center h-100">

                      <p className="text-success small mb-1">
                        Verified
                      </p>

                      <h4 className="fw-bold text-success mb-0">
                        {summary?.verified ?? 0}
                      </h4>

                    </div>

                  </div>


                  <div className="col-6 col-lg-3">

                    <div className="border border-warning-subtle rounded-3 p-3 text-center h-100">

                      <p className="text-warning small mb-1">
                        Pending
                      </p>

                      <h4 className="fw-bold text-warning mb-0">
                        {summary?.pending ?? 0}
                      </h4>

                    </div>

                  </div>


                  <div className="col-6 col-lg-3">

                    <div className="border border-danger-subtle rounded-3 p-3 text-center h-100">

                      <p className="text-danger small mb-1">
                        Failed
                      </p>

                      <h4 className="fw-bold text-danger mb-0">
                        {summary?.failed ?? 0}
                      </h4>

                    </div>

                  </div>

                </div>


                <div className="mt-4 d-flex flex-column flex-sm-row gap-2">

                  <button
                    type="button"
                    className="btn btn-primary px-4"
                    onClick={() =>
                      setShowStatus(!showStatus)
                    }
                  >
                    {showStatus
                      ? 'Hide BGV Status'
                      : 'View BGV Status'}
                  </button>

                </div>

              </>

            ) : (

              <div className="alert alert-info mb-0">
                BGV case information is not available yet.
              </div>

            )}

          </div>

        </div>


        {/* Detailed BGV Status */}
        {showStatus && bgvCase?.case && (

          <div className="bg-white rounded-3 shadow-sm border-0 mb-4">

            <div className="p-4 border-bottom">

              <h5 className="fw-bold mb-1">
                BGV Status Details
              </h5>

              <p className="text-slate-500 mb-0">
                Detailed verification status for your case.
              </p>

            </div>


            <div className="p-4">

              {/* Case Details */}

              <div className="row g-3 mb-4">

                <div className="col-12 col-md-6">

                  <p className="text-slate-500 small mb-1">
                    Case Number
                  </p>

                  <p className="fw-semibold mb-0">
                    {bgvCase.case.case_number}
                  </p>

                </div>


                <div className="col-12 col-md-6">

                  <p className="text-slate-500 small mb-1">
                    Case Status
                  </p>

                  <span className="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2">
                    {bgvCase.case.status}
                  </span>

                </div>

              </div>


              {/* Verification Summary */}

              <h6 className="fw-bold mb-3">
                Verification Summary
              </h6>

              <div className="row g-3 mb-4">

                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border rounded-3 p-3 text-center">

                    <small className="text-slate-500">
                      Total
                    </small>

                    <h5 className="fw-bold mb-0 mt-1">
                      {summary?.total ?? 0}
                    </h5>

                  </div>

                </div>


                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border border-success-subtle rounded-3 p-3 text-center">

                    <small className="text-success">
                      Verified
                    </small>

                    <h5 className="fw-bold text-success mb-0 mt-1">
                      {summary?.verified ?? 0}
                    </h5>

                  </div>

                </div>


                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border border-warning-subtle rounded-3 p-3 text-center">

                    <small className="text-warning">
                      Pending
                    </small>

                    <h5 className="fw-bold text-warning mb-0 mt-1">
                      {summary?.pending ?? 0}
                    </h5>

                  </div>

                </div>


                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border border-info-subtle rounded-3 p-3 text-center">

                    <small className="text-info">
                      In Progress
                    </small>

                    <h5 className="fw-bold text-info mb-0 mt-1">
                      {summary?.in_progress ?? 0}
                    </h5>

                  </div>

                </div>


                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border border-danger-subtle rounded-3 p-3 text-center">

                    <small className="text-danger">
                      Failed
                    </small>

                    <h5 className="fw-bold text-danger mb-0 mt-1">
                      {summary?.failed ?? 0}
                    </h5>

                  </div>

                </div>


                <div className="col-6 col-md-4 col-lg-2">

                  <div className="border border-secondary-subtle rounded-3 p-3 text-center">

                    <small className="text-secondary">
                      On Hold
                    </small>

                    <h5 className="fw-bold text-secondary mb-0 mt-1">
                      {summary?.on_hold ?? 0}
                    </h5>

                  </div>

                </div>

              </div>


              {/* Verification Details */}

              <h6 className="fw-bold mb-3">
                Verification Details
              </h6>

              {bgvCase.verifications?.length > 0 ? (

                <div className="table-responsive">

                  <table className="table table-hover align-middle">

                    <thead className="table-light">

                      <tr>
                        <th>Verification Type</th>
                        <th>Status</th>
                        <th>Remarks</th>
                        <th>Result</th>
                      </tr>

                    </thead>


                    <tbody>

                      {bgvCase.verifications.map(
                        (verification) => (

                          <tr key={verification.id}>

                            <td className="fw-semibold">
                              {verification.verification_type}
                            </td>

                            <td>

                              <span
                                className={
                                  verification.status ===
                                  'VERIFIED'
                                    ? 'badge bg-success-subtle text-success border border-success-subtle'
                                    : verification.status ===
                                      'FAILED'
                                    ? 'badge bg-danger-subtle text-danger border border-danger-subtle'
                                    : 'badge bg-warning-subtle text-warning border border-warning-subtle'
                                }
                              >
                                {verification.status}
                              </span>

                            </td>

                            <td>
                              {verification.remarks ||
                                'No remarks'}
                            </td>

                            <td>
                              {verification.result ||
                                'No result'}
                            </td>

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              ) : (

                <div className="alert alert-info mb-0">
                  No verification records are available yet.
                </div>

              )}

            </div>

          </div>

        )}

      </div>

    </div>
  )
}

export default CandidateDashboard
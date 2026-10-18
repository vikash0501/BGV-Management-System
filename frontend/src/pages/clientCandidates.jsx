import { useEffect, useState } from 'react'
import { getMyClientCandidates } from '../services/candidateService'

function ClientCandidates() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  const loadCandidates = async () => {
    try {
      setLoading(true)

      const data = await getMyClientCandidates()

      setCandidates(data.results || data)
    } catch (error) {
      console.error('Get client candidates error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load assigned candidates.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCandidates()
  }, [])

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>My Candidates</h2>

        <button
          type="button"
          className="btn btn-primary"
          onClick={loadCandidates}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p>Loading candidates...</p>
      ) : candidates.length === 0 ? (
        <div className="alert alert-info">
          No candidates assigned to you.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-bordered table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Candidate Code</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {candidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td>{candidate.id}</td>
                  <td>{candidate.candidate_code}</td>
                  <td>
                    {candidate.first_name} {candidate.last_name}
                  </td>
                  <td>{candidate.email}</td>
                  <td>{candidate.phone}</td>
                  <td>{candidate.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default ClientCandidates
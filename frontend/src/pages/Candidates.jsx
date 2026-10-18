import { useEffect, useState } from 'react'
import {
  getCandidates,
  createCandidate,
  getCandidate,
  updateCandidate,
  deleteCandidate,
  assignCandidateToClient,
  getClients,
} from '../services/candidateService'

function Candidates() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  const [selectedCandidate, setSelectedCandidate] = useState(null)
  const [clients, setClients] = useState([])
  const [selectedClientId, setSelectedClientId] = useState('')
  const [showDetail, setShowDetail] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [hasNextPage, setHasNextPage] = useState(false)
  const [hasPreviousPage, setHasPreviousPage] = useState(false)

  const [editFormData, setEditFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  })

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
  })

  useEffect(() => {
    loadCandidates()
    loadClients()
  }, [])

  const loadCandidates = async (
  searchValue = search,
  statusValue = statusFilter,
  page = currentPage
  ) => {
    try {
      setLoading(true)

      const params = {
        page,
      }

      if (searchValue.trim()) {
        params.search = searchValue.trim()
      }

      if (statusValue) {
        params.status = statusValue
      }

      const data = await getCandidates(params)

      setCandidates(data.results || data)

      setTotalCount(data.count || 0)
      setHasNextPage(Boolean(data.next))
      setHasPreviousPage(Boolean(data.previous))
    } catch (error) {
      console.error('Get candidates error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load candidates.'
      )
    } finally {
      setLoading(false)
    }
  }

  const loadClients = async () => {
    try {
      const data = await getClients()
      setClients(data.results || data)
    } catch (error) {
      console.error('Get clients error:', error)
      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load clients.'
      )
    }
  }
  const handleAssignClient = async () => {
    if (!selectedCandidate?.id) {
      alert('Please select a candidate.')
      return
    }

    if (!selectedClientId) {
      alert('Please select a client.')
      return
    }

    try {
      await assignCandidateToClient(
        selectedCandidate.id,
        Number(selectedClientId)
      )

      alert('Candidate assigned to client successfully.')

      const updatedCandidate = await getCandidate(selectedCandidate.id)
      setSelectedCandidate(updatedCandidate)

      setSelectedClientId('')
      loadCandidates()
    } catch (error) {
      console.error('Assign client error:', error)
      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to assign candidate to client.'
      )
    }
  }

  const handleChange = (event) => {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  const handleEditChange = (event) => {
    const { name, value } = event.target

    setEditFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    try {
      const data = await createCandidate(formData)

      alert('Candidate created successfully.')

      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        date_of_birth: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
      })

      await loadCandidates()

      console.log('Created candidate:', data)
    } catch (error) {
      console.error('Create candidate error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to create candidate.'
      )
    }
  }

  const handleView = async (candidateId) => {
    try {
      const data = await getCandidate(candidateId)

      setSelectedCandidate(data)

      setEditFormData({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        email: data.email || '',
        phone: data.phone || '',
      })

      setEditMode(false)
      setShowDetail(true)
    } catch (error) {
      console.error('Get candidate detail error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to load candidate details.'
      )
    }
  }

  const handleUpdate = async () => {
    try {
      const data = await updateCandidate(
        selectedCandidate.id,
        editFormData
      )

      setSelectedCandidate(data)
      setEditMode(false)

      await loadCandidates()

      alert('Candidate updated successfully.')
    } catch (error) {
      console.error('Update candidate error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to update candidate.'
      )
    }
  }

  const handleDelete = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete this candidate?'
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteCandidate(selectedCandidate.id)

      alert('Candidate deleted successfully.')

      setSelectedCandidate(null)
      setShowDetail(false)
      setEditMode(false)

      await loadCandidates()
    } catch (error) {
      console.error('Delete candidate error:', error)

      alert(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : 'Failed to delete candidate.'
      )
    }
  }

  const handleCloseDetail = () => {
    setSelectedCandidate(null)
    setShowDetail(false)
    setEditMode(false)
  }

  return (
                <div className="container-fluid py-4">

      {/* PAGE HEADER */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Candidates</h2>
          <p className="text-muted mb-0">
            Manage background verification candidates
          </p>
        </div>
      </div>

      {/* ADD CANDIDATE FORM */}
      {!showDetail && (
        <div className="card border-0 shadow-sm mb-4">
          <div className="card-body">
            <h5 className="fw-bold mb-4">Add Candidate</h5>

            <form onSubmit={handleSubmit}>
              <div className="row g-3">

                <div className="col-md-6">
                  <label className="form-label">First Name</label>

                  <input
                    type="text"
                    name="first_name"
                    className="form-control"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">Last Name</label>

                  <input
                    type="text"
                    name="last_name"
                    className="form-control"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">Email</label>

                  <input
                    type="email"
                    name="email"
                    className="form-control"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">Phone</label>

                  <input
                    type="text"
                    name="phone"
                    className="form-control"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">Date of Birth</label>

                  <input
                    type="date"
                    name="date_of_birth"
                    className="form-control"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">Pincode</label>

                  <input
                    type="text"
                    name="pincode"
                    className="form-control"
                    value={formData.pincode}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-12">
                  <label className="form-label">Address</label>

                  <textarea
                    name="address"
                    className="form-control"
                    rows="2"
                    value={formData.address}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">City</label>

                  <input
                    type="text"
                    name="city"
                    className="form-control"
                    value={formData.city}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label">State</label>

                  <input
                    type="text"
                    name="state"
                    className="form-control"
                    value={formData.state}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-12">
                  <button
                    type="submit"
                    className="btn btn-primary"
                  >
                    Add Candidate
                  </button>
                </div>

              </div>
            </form>
          </div>
        </div>
      )}

      {/* CANDIDATE DETAIL */}
      {showDetail && selectedCandidate && (
        <div className="card border-0 shadow-sm mb-4">

          <div className="card-body">

            {/* DETAIL HEADER */}
            <div className="d-flex justify-content-between align-items-center mb-4">

              <div>
                <h5 className="fw-bold mb-1">
                  Candidate Details
                </h5>
                <div className="mt-4">
                  <label className="form-label fw-semibold">
                    Assign Client
                  </label>

                  <select
                    className="form-select"
                    value={selectedClientId}
                    onChange={(event) => setSelectedClientId(event.target.value)}
                  >
                    <option value="">Select Client</option>

                    {clients.map((client) => (
                      <option key={client.id} value={client.id}>
                        {client.first_name} {client.last_name}                 ({client.email})
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn btn-primary mt-2"
                    disabled={!selectedClientId}
                    onClick={handleAssignClient}
                  >
                    Assign Client
                  </button>
                </div>

                <p className="text-muted mb-0">
                  Candidate ID: {selectedCandidate.id}
                </p>
              </div>

              <div>

                {!editMode && (
                  <>
                    <button
                      type="button"
                      className="btn btn-primary me-2"
                      onClick={() => setEditMode(true)}
                    >
                      Edit Candidate
                    </button>

                    <button
                      type="button"
                      className="btn btn-danger me-2"
                      onClick={handleDelete}
                    >
                      Delete Candidate
                    </button>
                  </>
                )}

                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={handleCloseDetail}
                >
                  Close
                </button>

              </div>

            </div>

            {/* CANDIDATE DETAILS */}
            {!editMode && (
              <div className="row g-3">

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Candidate Code
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.candidate_code || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Name
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.first_name || '-'}{' '}
                      {selectedCandidate.last_name || ''}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Email
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.email || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Phone
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.phone || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Date of Birth
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.date_of_birth || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Status
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.status || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      City
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.city || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      State
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.state || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-12">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Address
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.address || '-'}
                    </div>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3">
                    <small className="text-muted">
                      Pincode
                    </small>

                    <div className="fw-semibold">
                      {selectedCandidate.pincode || '-'}
                    </div>
                  </div>
                </div>

              </div>
            )}

            {/* EDIT CANDIDATE */}
            {editMode && (
              <div className="mt-4 pt-4 border-top">

                <h6 className="mb-3">
                  Edit Candidate
                </h6>

                <div className="row g-3">

                  <div className="col-md-6">
                    <label className="form-label">
                      First Name
                    </label>

                    <input
                      type="text"
                      name="first_name"
                      className="form-control"
                      value={editFormData.first_name}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="col-md-6">
                    <label className="form-label">
                      Last Name
                    </label>

                    <input
                      type="text"
                      name="last_name"
                      className="form-control"
                      value={editFormData.last_name}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="col-md-6">
                    <label className="form-label">
                      Email
                    </label>

                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      value={editFormData.email}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="col-md-6">
                    <label className="form-label">
                      Phone
                    </label>

                    <input
                      type="text"
                      name="phone"
                      className="form-control"
                      value={editFormData.phone}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="col-12">

                    <button
                      type="button"
                      className="btn btn-success"
                      onClick={handleUpdate}
                    >
                      Update Candidate
                    </button>

                    <button
                      type="button"
                      className="btn btn-outline-secondary ms-2"
                      onClick={() => setEditMode(false)}
                    >
                      Cancel
                    </button>

                  </div>

                </div>
              </div>
            )}

          </div>
        </div>
      )}

      {/* CANDIDATE LIST */}
      {!showDetail && (
        <div className="card border-0 shadow-sm">

          <div className="card-body">
            {/* SEARCH & FILTER */}
            <div className="row g-3 mb-4">

              <div className="col-md-6">
                <label className="form-label">
                  Search Candidate
                </label>

                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by name or email..."
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value)
                    setCurrentPage(1)
                  }}
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">
                  Status
                </label>

                <select
                  className="form-select"
                  value={statusFilter}
                  onChange={(event) => {
                    setStatusFilter(event.target.value)
                    setCurrentPage(1)
                  }}
                >
                  <option value="">All Status</option>
                  <option value="ACTIVE">Active</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="HOLD">Hold</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </div>

              <div className="col-md-2 d-flex align-items-end">
                <button
                  type="button"
                  className="btn btn-primary w-100"
                  onClick={() => loadCandidates(search, statusFilter, 1)}
                >
                  Search
                </button>
              </div>

            </div>

            <div className="d-flex justify-content-between align-items-center mb-3">

              <h5 className="fw-bold mb-0">
                Candidate List
              </h5>

              <span className="badge bg-primary">
                {candidates.length} Candidates
              </span>

            </div>

            {loading ? (
              <div className="text-center py-4">
                <div
                  className="spinner-border text-primary"
                  role="status"
                >
                  <span className="visually-hidden">
                    Loading...
                  </span>
                </div>
              </div>
            ) : candidates.length === 0 ? (
              <div className="text-center text-muted py-4">
                No candidates found.
              </div>
            ) : (
              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Candidate Code</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>

                    {candidates.map((candidate) => (
                      <tr key={candidate.id}>

                        <td>
                          {candidate.id}
                        </td>

                        <td>
                          {candidate.candidate_code || '-'}
                        </td>

                        <td>
                          {candidate.first_name || '-'}{' '}
                          {candidate.last_name || ''}
                        </td>

                        <td>
                          {candidate.email || '-'}
                        </td>

                        <td>
                          {candidate.phone || '-'}
                        </td>

                        <td>
                          <span className="badge bg-success">
                            {candidate.status || 'ACTIVE'}
                          </span>
                        </td>

                        <td>
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-primary"
                            onClick={() =>
                              handleView(candidate.id)
                            }
                          >
                            View
                          </button>
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>
                {/* PAGINATION */}
                {totalCount > 0 && (
                  <div className="d-flex justify-content-between align-items-center mt-3">

                    <div className="text-muted">
                      Total Candidates: {totalCount}
                    </div>

                    <div>
                      <button
                        type="button"
                        className="btn btn-outline-primary me-2"
                        disabled={!hasPreviousPage}
                        onClick={() => {
                          const previousPage = currentPage - 1
                          setCurrentPage(previousPage)
                          loadCandidates(search, statusFilter, previousPage)
                        }}
                      >
                         ← Previous
                                       </button>

                      <span className="mx-2 fw-semibold">
                        Page {currentPage}
                      </span>

                      <button
                        type="button"
                        className="btn btn-outline-primary"
                        disabled={!hasNextPage}
                        onClick={() => {
                          const nextPage = currentPage + 1
                          setCurrentPage(nextPage)
                          loadCandidates(search, statusFilter, nextPage)
                        }}
                      >
                        Next →
                      </button>
                    </div>

                  </div>
                )}

              </div>
            )}

          </div>
        </div>
      )}

    </div>
  )
}

export default Candidates
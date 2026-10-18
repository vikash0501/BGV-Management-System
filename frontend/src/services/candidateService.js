import api from './api'

export const getCandidates = async (params = {}) => {
  const response = await api.get('/candidates/list/', {
    params,
  })

  return response.data
}
export const createCandidate = async (candidateData) => {
  const response = await api.post('/candidates/', candidateData)
  return response.data
}
export const getCandidate = async (candidateId) => {
  const response = await api.get(`/candidates/${candidateId}/`)
  return response.data
}
export const updateCandidate = async (candidateId, candidateData) => {
  const response =await api.patch(
    `/candidates/${candidateId}/`,
    candidateData
  )
  return response.data
}
export const deleteCandidate = async (candidateId) => {
  const response = await api.delete(
    `/candidates/${candidateId}/`
  )

  return response.data
}
export const assignCandidateToClient = async (
  candidateId,
  clientId
) => {
  const response = await api.patch(
    `/candidates/${candidateId}/assign-client/`,
    {
      client_id: clientId,
    }
  )

  return response.data
}
export const getClients = async () => {
  const response = await api.get('/accounts/clients/')
  return response.data
}
export const getMyClientCandidates = async () =>{
  const response =await api.get('/candidates/client/my')
  return reponse.data
}
export const getMyCandidateProfile = async () => {
  const response = await api.get('/candidates/my/')
  return response.data
}
export const getMyCandidateBGVCase = async (caseId) => {
  const response = await api.get(`/cases/${caseId}/candidate/dashboard/`)
  return response.data
}

export const getMyCandidateReport = async (caseId) => {
  const response = await api.get(
    `/cases/${caseId}/candidate/report/pdf/`,
    {
      responseType: 'blob',
    }
  )

  return response.data
}
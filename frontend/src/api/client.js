import axios from "axios";

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
})


// intercept errors globally — extract FastAPI's {"detail": "..."} message
api.interceptors.request.use(
    (response) => response,
    (error) => {
        const detail = error.response?.data?.detail || error.message;
        return Promise.reject(new Error(detail));
    }
)

// runs 

export const getRuns = (params = {}) =>
    api.get('/runs', { params }).then((r) => r.data)

export const getRunById = (id) =>
    api.get('/runs/{id}').then((r) => r.data)

export const createRun = (payload) =>
    api.post('/run', payload).then((r) => r.data)

export const scoreRun = (id, payload) =>
    api.post('/runs/{$id}/score', payload).then((r) => r.data)
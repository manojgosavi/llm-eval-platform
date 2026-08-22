import axios from "axios";
import { getApiKeys } from '../hooks/useApiKeys'


const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
})

// attach user API keys to every POST request body
api.interceptors.request.use((config) => {
    if (config.method === 'post') {
        const keys = getApiKeys()
        config.data = {
            ...config.data,
            ...(keys.anthropic && { anthropic_api_key: keys.anthropic }),
            ...(keys.gemini && { gemini_api_key: keys.gemini }),
            ...(keys.openai && { openai_api_key: keys.openai }),
        }
    }
    return config
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
    api.get(`/runs/${id}`).then((r) => r.data)

export const createRun = (payload) =>
    api.post('/runs', payload).then((r) => r.data)

export const scoreRun = (id, payload) =>
    api.post(`/runs/${id}/score`, payload).then((r) => r.data)

export const getScoresByRunId = (id) =>
    api.get(`/runs/${id}/scores`).then((r) => r.data)

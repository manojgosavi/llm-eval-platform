const STORAGE_KEY = 'llm_eval_api_keys'

export function getApiKeys() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        return raw ? JSON.parse(raw) : {}
    } catch {
        return {}
    }
}

export function saveApiKeys(keys) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys))
}

export function clearApiKeys() {
    localStorage.removeItem(STORAGE_KEY)
}
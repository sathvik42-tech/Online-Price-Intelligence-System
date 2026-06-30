/**
 * api.js — centralized API client with authentication
 *
 * All calls use relative paths (e.g. '/api/wishlist/123') so the Vite dev-server
 * proxy forwards them to the appropriate backend (Express on port 5001 or Flask on 8000).
 * 
 * For production, set VITE_API_URL environment variable to your API endpoint.
 *
 * On every 401 response the user is automatically redirected to /login.
 *
 * Usage:
 *   import { apiGet, apiPost, apiDelete, apiPut } from '../api';
 *   const data = await apiGet('/api/wishlist/42');
 *   const result = await apiPost('/api/wishlist', { ... });
 */

// Use relative path for development (Vite proxy), or environment variable for production
const BASE = import.meta.env.VITE_API_URL || '';

function getToken() {
    return localStorage.getItem('intelToken') || '';
}

function handleUnauthorised() {
    localStorage.removeItem('intelToken');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

async function request(method, path, body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
    };

    const config = { method, headers };
    if (body !== null) {
        config.body = JSON.stringify(body);
    }

    const res = await fetch(BASE + path, config);

    if (res.status === 401) {
        handleUnauthorised();
        // Return a resolved promise that won't throw so callers don't need try/catch just for auth
        return null;
    }

    // Attempt to parse JSON; fall back to raw text for non-JSON responses
    const contentType = res.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await res.json() : await res.text();

    if (!res.ok) {
        const message = (data && data.error) || (data && data.detail) || `HTTP ${res.status}`;
        throw new Error(message);
    }

    return data;
}

export const apiGet = (path) => request('GET', path);
export const apiPost = (path, body) => request('POST', path, body);
export const apiDelete = (path) => request('DELETE', path);
export const apiPut = (path, body) => request('PUT', path, body);

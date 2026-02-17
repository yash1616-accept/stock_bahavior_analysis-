/**
 * API Service
 * All calls to the Flask backend go through here
 */

const BASE_URL = "http://localhost:5000/api";

// ─── Analyze stock from Yahoo Finance ───────────────────────────────────────
export async function analyzeStock(ticker, period) {
    const res = await fetch(`${BASE_URL}/analyze?ticker=${ticker}&period=${period}`);
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to fetch stock data");
    }
    return res.json();
    // Returns: { ticker, period, data: [...rows], summary: {...}, insights: [...] }
}

// ─── Analyze uploaded file ───────────────────────────────────────────────────
export async function analyzeFile(file, ticker) {
    const form = new FormData();
    form.append("file", file);
    form.append("ticker", ticker);

    const res = await fetch(`${BASE_URL}/analyze-file`, {
        method: "POST",
        body: form,
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to analyze file");
    }
    return res.json();
}

// ─── Health check ────────────────────────────────────────────────────────────
export async function checkHealth() {
    try {
        const res = await fetch(`${BASE_URL}/health`);
        return res.ok;
    } catch {
        return false;
    }
}

// ─── Get ticker list ─────────────────────────────────────────────────────────
export async function getTickers() {
    const res = await fetch(`${BASE_URL}/tickers`);
    if (!res.ok) throw new Error("Failed to fetch tickers");
    return res.json();
}
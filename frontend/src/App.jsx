import { useState, useEffect, useCallback } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ScatterChart, Scatter, Cell,
  BarChart, Bar, AreaChart, Area, ReferenceLine
} from "recharts";
import {
  TrendingDown, TrendingUp, Activity, AlertCircle,
  Upload, RefreshCw, BarChart2, Home, FileText,
  Info, ChevronDown, Search, Moon, Sun, Download,
  Wifi, WifiOff, X
} from "lucide-react";
import { analyzeStock, analyzeFile, checkHealth } from "./api";

// ─── Constants ───────────────────────────────────────────────────────────────
const BEHAVIOR_COLORS = {
  "Normal": "#6b7280",
  "Panic Selling": "#ef4444",
  "FOMO Buying": "#10b981",
  "Overconfidence": "#f59e0b",
};
const TICKERS = [
  { label: "Apple (AAPL)", value: "AAPL" },
  { label: "Tesla (TSLA)", value: "TSLA" },
  { label: "Microsoft (MSFT)", value: "MSFT" },
  { label: "Google (GOOGL)", value: "GOOGL" },
  { label: "NVIDIA (NVDA)", value: "NVDA" },
  { label: "Reliance (RELIANCE.NS)", value: "RELIANCE.NS" },
  { label: "TCS (TCS.NS)", value: "TCS.NS" },
  { label: "AB Capital (ABCAPITAL.NS)", value: "ABCAPITAL.NS" },
];
const PERIODS = ["1mo", "3mo", "6mo", "1y", "2y"];

// ─── Small reusable components ───────────────────────────────────────────────
const Badge = ({ behavior }) => {
  const s = {
    "Panic Selling": "bg-red-100 text-red-700",
    "FOMO Buying": "bg-green-100 text-green-700",
    "Overconfidence": "bg-yellow-100 text-yellow-700",
    "Normal": "bg-gray-100 text-gray-600",
  };
  return <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${s[behavior] || s.Normal}`}>{behavior}</span>;
};

const StatCard = ({ title, value, sub, icon: Icon, color, dark }) => (
  <div className={`rounded-2xl p-5 shadow flex items-center gap-4 ${dark ? "bg-gray-800" : "bg-white"}`}>
    <div className="rounded-full p-3" style={{ background: `${color}22` }}>
      <Icon size={22} style={{ color }} />
    </div>
    <div>
      <p className={`text-xs font-semibold ${dark ? "text-gray-400" : "text-gray-500"}`}>{title}</p>
      <p className="text-2xl font-bold" style={{ color }}>{value}</p>
      <p className={`text-xs mt-0.5 ${dark ? "text-gray-500" : "text-gray-400"}`}>{sub}</p>
    </div>
  </div>
);

const SectionCard = ({ title, children, dark }) => (
  <div className={`rounded-2xl shadow p-5 ${dark ? "bg-gray-800" : "bg-white"}`}>
    <h3 className={`font-bold text-base mb-4 ${dark ? "text-white" : "text-gray-800"}`}>{title}</h3>
    {children}
  </div>
);

const CustomTooltip = ({ active, payload, label, dark }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className={`rounded-xl shadow-lg p-3 text-xs ${dark ? "bg-gray-900 text-white border border-gray-700" : "bg-white border border-gray-100"}`}>
      <p className="font-bold mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === "number" ? p.value.toFixed(2) : p.value}</p>
      ))}
    </div>
  );
};

// ─── Overview Page ────────────────────────────────────────────────────────────
function OverviewPage({ data, summary, ticker, dark }) {
  const { behaviors = {} } = summary;
  const priceData = data.filter((_, i) => i % Math.max(1, Math.floor(data.length / 80)) === 0);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Panic Selling" value={behaviors["Panic Selling"] || 0} sub="days detected" icon={TrendingDown} color="#ef4444" dark={dark} />
        <StatCard title="FOMO Buying" value={behaviors["FOMO Buying"] || 0} sub="days detected" icon={TrendingUp} color="#10b981" dark={dark} />
        <StatCard title="Overconfidence" value={behaviors["Overconfidence"] || 0} sub="days detected" icon={Activity} color="#f59e0b" dark={dark} />
        <StatCard title="Risk Level" value={`${summary.risk_pct}%`} sub="abnormal days" icon={AlertCircle} color="#6366f1" dark={dark} />
      </div>

      <SectionCard title={`📈 ${ticker} — Price with Behaviour Zones`} dark={dark}>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={priceData}>
            <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#374151" : "#f0f0f0"} />
            <XAxis dataKey="Date" tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }} domain={["auto", "auto"]} />
            <Tooltip content={<CustomTooltip dark={dark} />} />
            <Line type="monotone" dataKey="Close" stroke="#6366f1" strokeWidth={2} dot={false} name="Close" />
          </LineChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-4 mt-3 justify-center">
          {Object.entries(BEHAVIOR_COLORS).map(([k, c]) => (
            <div key={k} className="flex items-center gap-1.5 text-xs" style={{ color: c }}>
              <span className="w-3 h-3 rounded-full" style={{ background: c }} />
              {k}
            </div>
          ))}
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="📊 Volume Analysis" dark={dark}>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={priceData}>
              <defs>
                <linearGradient id="vG" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#374151" : "#f0f0f0"} />
              <XAxis dataKey="Date" tick={{ fontSize: 9, fill: dark ? "#9ca3af" : "#6b7280" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: dark ? "#9ca3af" : "#6b7280" }} tickFormatter={v => `${(v / 1e6).toFixed(1)}M`} />
              <Tooltip content={<CustomTooltip dark={dark} />} />
              <Area type="monotone" dataKey="Volume" stroke="#8b5cf6" fill="url(#vG)" dot={false} name="Volume" />
              <Line type="monotone" dataKey="Volume_MA20" stroke="#ec4899" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Avg Volume" />
            </AreaChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="🌡️ Volatility Index" dark={dark}>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={priceData}>
              <defs>
                <linearGradient id="vIdx" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#374151" : "#f0f0f0"} />
              <XAxis dataKey="Date" tick={{ fontSize: 9, fill: dark ? "#9ca3af" : "#6b7280" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: dark ? "#9ca3af" : "#6b7280" }} />
              <Tooltip content={<CustomTooltip dark={dark} />} />
              <ReferenceLine y={2} stroke="#ef4444" strokeDasharray="3 3" label={{ value: "Panic", fill: "#ef4444", fontSize: 10 }} />
              <ReferenceLine y={1.5} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: "FOMO", fill: "#f59e0b", fontSize: 10 }} />
              <Area type="monotone" dataKey="Volatility" stroke="#f97316" fill="url(#vIdx)" dot={false} name="Volatility %" />
            </AreaChart>
          </ResponsiveContainer>
        </SectionCard>
      </div>
    </div>
  );
}

// ─── Behaviour Page ───────────────────────────────────────────────────────────
function BehaviourPage({ data, summary, dark }) {
  const scatter = data.filter(d => d.Price_Change_Pct != null && d.Price_Change_Pct !== 0);
  const abnormal = data.filter(d => d.Behavior !== "Normal")
    .sort((a, b) => (b.Confidence_Score || 0) - (a.Confidence_Score || 0))
    .slice(0, 15);

  const barData = Object.entries(summary.behaviors || {}).map(([name, count]) => ({
    name, count, color: BEHAVIOR_COLORS[name]
  }));

  return (
    <div className="space-y-6">
      <SectionCard title="🔍 Behaviour Classification — Price Change vs Volume Spike" dark={dark}>
        <ResponsiveContainer width="100%" height={320}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#374151" : "#f0f0f0"} />
            <XAxis type="number" dataKey="Price_Change_Pct" name="Price Change %"
              tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }}
              label={{ value: "Price Change (%)", position: "insideBottom", offset: -5, fill: dark ? "#9ca3af" : "#6b7280", fontSize: 11 }} />
            <YAxis type="number" dataKey="Volume_Zscore" name="Volume Z-Score"
              tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }}
              label={{ value: "Volume Z-Score", angle: -90, position: "insideLeft", fill: dark ? "#9ca3af" : "#6b7280", fontSize: 11 }} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0]?.payload;
              return (
                <div className={`rounded-xl p-3 text-xs shadow-lg ${dark ? "bg-gray-900 text-white border border-gray-700" : "bg-white border border-gray-100"}`}>
                  <p className="font-bold mb-1">{d?.Date}</p>
                  <Badge behavior={d?.Behavior} />
                  <p className="mt-1">Price: {d?.Price_Change_Pct}% | Vol: {parseFloat(d?.Volume_Zscore || 0).toFixed(2)}σ</p>
                  <p>Confidence: {parseFloat(d?.Confidence_Score || 0).toFixed(1)}%</p>
                </div>
              );
            }} />
            <ReferenceLine x={-2.5} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine x={2.5} stroke="#10b981" strokeDasharray="3 3" />
            <ReferenceLine y={1.5} stroke="#f59e0b" strokeDasharray="3 3" />
            <Scatter data={scatter} name="Days">
              {scatter.map((e, i) => <Cell key={i} fill={BEHAVIOR_COLORS[e.Behavior]} fillOpacity={0.75} />)}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="📊 Behaviour Distribution" dark={dark}>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} barSize={40}>
              <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#374151" : "#f0f0f0"} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }} />
              <YAxis tick={{ fontSize: 10, fill: dark ? "#9ca3af" : "#6b7280" }} />
              <Tooltip content={<CustomTooltip dark={dark} />} />
              <Bar dataKey="count" name="Days" radius={[6, 6, 0, 0]}>
                {barData.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="⚠️ Top High-Risk Incidents" dark={dark}>
          <div className="space-y-2 overflow-y-auto max-h-52">
            {abnormal.length === 0
              ? <p className={`text-sm ${dark ? "text-gray-400" : "text-gray-500"}`}>No abnormal behaviour detected.</p>
              : abnormal.map((d, i) => (
                <div key={i} className={`flex items-center justify-between p-2 rounded-lg text-xs ${dark ? "bg-gray-700" : "bg-gray-50"}`}>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ background: BEHAVIOR_COLORS[d.Behavior] }} />
                    <span className={dark ? "text-gray-200" : "text-gray-700"}>{d.Date}</span>
                    <Badge behavior={d.Behavior} />
                  </div>
                  <div className="flex items-center gap-3 text-right">
                    <span className={parseFloat(d.Price_Change_Pct) < 0 ? "text-red-500" : "text-green-500"}>
                      {parseFloat(d.Price_Change_Pct) > 0 ? "+" : ""}{parseFloat(d.Price_Change_Pct).toFixed(2)}%
                    </span>
                    <span className="text-purple-400">{parseFloat(d.Confidence_Score || 0).toFixed(0)}%</span>
                  </div>
                </div>
              ))
            }
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

// ─── Insights Page ────────────────────────────────────────────────────────────
function InsightsPage({ data, summary, insights, ticker, period, dark }) {
  const insightStyles = {
    warning: { bg: dark ? "bg-red-900/30" : "bg-red-50", border: "border-red-400", text: "text-red-600" },
    caution: { bg: dark ? "bg-yellow-900/30" : "bg-yellow-50", border: "border-yellow-400", text: "text-yellow-600" },
    info: { bg: dark ? "bg-blue-900/30" : "bg-blue-50", border: "border-blue-400", text: "text-blue-600" },
    success: { bg: dark ? "bg-green-900/30" : "bg-green-50", border: "border-green-400", text: "text-green-600" },
  };
  const riskPct = summary.risk_pct || 0;
  const riskLabel = riskPct > 30 ? "HIGH RISK 🔴" : riskPct > 20 ? "MODERATE RISK 🟡" : "LOW RISK 🟢";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Return", value: `${summary.total_return}%`, color: summary.total_return >= 0 ? "#10b981" : "#ef4444" },
          { label: "Avg Volatility", value: `${summary.avg_volatility}%`, color: "#f97316" },
          { label: "Max Volatility", value: `${summary.max_volatility}%`, color: "#ef4444" },
          { label: "Abnormal Days", value: `${riskPct}%`, color: "#6366f1" },
        ].map((s, i) => (
          <div key={i} className={`rounded-2xl p-4 shadow text-center ${dark ? "bg-gray-800" : "bg-white"}`}>
            <p className={`text-xs mb-1 ${dark ? "text-gray-400" : "text-gray-500"}`}>{s.label}</p>
            <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="💰 Price Statistics" dark={dark}>
          {[
            ["Ticker", ticker],
            ["Period", period],
            ["Start Price", `$${summary.start_price}`],
            ["End Price", `$${summary.end_price}`],
            ["All-Time High", `$${summary.max_price}`],
            ["All-Time Low", `$${summary.min_price}`],
            ["Total Return", `${summary.total_return}%`],
            ["Trading Days", summary.total],
          ].map(([k, v]) => (
            <div key={k} className={`flex justify-between py-2 border-b text-sm ${dark ? "border-gray-700 text-gray-300" : "border-gray-100 text-gray-700"}`}>
              <span className={dark ? "text-gray-400" : "text-gray-500"}>{k}</span>
              <span className="font-semibold">{v}</span>
            </div>
          ))}
        </SectionCard>

        <SectionCard title="🔍 Behaviour Breakdown" dark={dark}>
          {Object.entries(BEHAVIOR_COLORS).map(([b, c]) => {
            const cnt = summary.behaviors?.[b] || 0;
            const pct = summary.total ? (cnt / summary.total * 100) : 0;
            return (
              <div key={b} className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className={`font-medium ${dark ? "text-gray-300" : "text-gray-700"}`}>{b}</span>
                  <span style={{ color: c }}>{cnt} days ({pct.toFixed(1)}%)</span>
                </div>
                <div className={`w-full rounded-full h-2 ${dark ? "bg-gray-700" : "bg-gray-100"}`}>
                  <div className="h-2 rounded-full transition-all" style={{ width: `${pct}%`, background: c }} />
                </div>
              </div>
            );
          })}
          <p className={`mt-3 text-xs font-bold ${dark ? "text-gray-400" : "text-gray-500"}`}>Overall Risk: {riskLabel}</p>
        </SectionCard>
      </div>

      <SectionCard title="💡 System Insights & Recommendations" dark={dark}>
        {!insights?.length
          ? <p className={`text-sm ${dark ? "text-gray-400" : "text-gray-500"}`}>No strong signals in recent data.</p>
          : <div className="space-y-3">
            {insights.map((ins, i) => {
              const s = insightStyles[ins.type] || insightStyles.info;
              return (
                <div key={i} className={`${s.bg} border-l-4 ${s.border} p-3 rounded-lg`}>
                  <p className={`font-bold text-sm ${s.text}`}>{ins.title}</p>
                  <p className={`text-xs mt-1 ${dark ? "text-gray-300" : "text-gray-600"}`}>{ins.text}</p>
                </div>
              );
            })}
          </div>
        }
      </SectionCard>

      <SectionCard title="📐 Detection Methodology" dark={dark}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: "🔴 Panic Selling", color: "#ef4444", rules: ["Price change < −2.5%", "Volume Z-score > 1.5σ", "Volatility > 2%"] },
            { label: "🟢 FOMO Buying", color: "#10b981", rules: ["Price change > +2.5%", "Volume Z-score > 1.5σ", "Volatility > 1.5%"] },
            { label: "🟡 Overconfidence", color: "#f59e0b", rules: ["Price change < ±1%", "Volume Z-score > 2.0σ", "Volatility > 1.8%"] },
          ].map((m, i) => (
            <div key={i} className={`p-3 rounded-xl border-l-4 ${dark ? "bg-gray-700" : "bg-gray-50"}`} style={{ borderColor: m.color }}>
              <p className="font-bold text-sm mb-2" style={{ color: m.color }}>{m.label}</p>
              {m.rules.map((r, j) => (
                <p key={j} className={`text-xs ${dark ? "text-gray-300" : "text-gray-600"}`}>• {r}</p>
              ))}
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

// ─── Data Table Page ──────────────────────────────────────────────────────────
function DataPage({ data, dark }) {
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const PAGE = 15;

  const filtered = data.filter(d => {
    const bOk = filter === "All" || d.Behavior === filter;
    const sOk = !search || d.Date?.includes(search);
    return bOk && sOk;
  });
  const paged = filtered.slice(page * PAGE, (page + 1) * PAGE);
  const totalPages = Math.ceil(filtered.length / PAGE);

  const headers = ["Date", "Close", "Change %", "Vol Z", "Volatility", "Behaviour", "Confidence"];

  const downloadCSV = () => {
    const cols = ["Date", "Close", "Price_Change_Pct", "Volume_Zscore", "Volatility", "Behavior", "Confidence_Score"];
    const csv = [cols.join(","), ...data.map(d => cols.map(c => d[c] ?? "").join(","))].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = "stock_analysis.csv";
    a.click();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          {["All", "Normal", "Panic Selling", "FOMO Buying", "Overconfidence"].map(b => (
            <button key={b} onClick={() => { setFilter(b); setPage(0); }}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition`}
              style={filter === b
                ? { background: BEHAVIOR_COLORS[b] || "#6366f1", color: "#fff" }
                : { background: dark ? "#374151" : "#f3f4f6", color: dark ? "#d1d5db" : "#374151" }}>
              {b}
            </button>
          ))}
        </div>
        <div className="flex gap-2 items-center">
          <div className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm ${dark ? "bg-gray-700" : "bg-gray-100"}`}>
            <Search size={14} className={dark ? "text-gray-400" : "text-gray-500"} />
            <input value={search} onChange={e => { setSearch(e.target.value); setPage(0); }}
              placeholder="Search date…"
              className={`bg-transparent outline-none text-xs w-28 ${dark ? "text-white placeholder-gray-500" : "text-gray-700"}`} />
          </div>
          <button onClick={downloadCSV} className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition">
            <Download size={13} /> CSV
          </button>
        </div>
      </div>

      <div className={`rounded-2xl shadow overflow-hidden ${dark ? "bg-gray-800" : "bg-white"}`}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className={dark ? "bg-gray-700" : "bg-gray-50"}>
                {headers.map(h => (
                  <th key={h} className={`px-4 py-3 text-left text-xs font-bold ${dark ? "text-gray-300" : "text-gray-600"}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.map((row, i) => (
                <tr key={i} className={`border-t ${dark ? "border-gray-700 hover:bg-gray-700" : "border-gray-50 hover:bg-gray-50"}`}>
                  <td className={`px-4 py-2.5 text-xs ${dark ? "text-gray-300" : "text-gray-600"}`}>{row.Date}</td>
                  <td className={`px-4 py-2.5 font-medium ${dark ? "text-white" : "text-gray-800"}`}>${parseFloat(row.Close).toFixed(2)}</td>
                  <td className={`px-4 py-2.5 font-medium ${parseFloat(row.Price_Change_Pct) >= 0 ? "text-green-500" : "text-red-500"}`}>
                    {parseFloat(row.Price_Change_Pct) > 0 ? "+" : ""}{parseFloat(row.Price_Change_Pct).toFixed(2)}%
                  </td>
                  <td className={`px-4 py-2.5 ${dark ? "text-gray-300" : "text-gray-600"}`}>{parseFloat(row.Volume_Zscore || 0).toFixed(2)}</td>
                  <td className={`px-4 py-2.5 ${dark ? "text-gray-300" : "text-gray-600"}`}>{parseFloat(row.Volatility || 0).toFixed(2)}%</td>
                  <td className="px-4 py-2.5"><Badge behavior={row.Behavior} /></td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className={`w-16 rounded-full h-1.5 ${dark ? "bg-gray-600" : "bg-gray-200"}`}>
                        <div className="h-1.5 rounded-full" style={{ width: `${row.Confidence_Score || 0}%`, background: BEHAVIOR_COLORS[row.Behavior] }} />
                      </div>
                      <span className={`text-xs ${dark ? "text-gray-400" : "text-gray-500"}`}>{parseFloat(row.Confidence_Score || 0).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className={`flex items-center justify-between px-4 py-3 border-t text-xs ${dark ? "border-gray-700 text-gray-400" : "border-gray-100 text-gray-500"}`}>
          <span>Showing {page * PAGE + 1}–{Math.min((page + 1) * PAGE, filtered.length)} of {filtered.length}</span>
          <div className="flex gap-2">
            <button disabled={page === 0} onClick={() => setPage(p => p - 1)}
              className={`px-3 py-1 rounded-lg ${dark ? "bg-gray-700 text-gray-300" : "bg-gray-100"} disabled:opacity-40`}>← Prev</button>
            <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}
              className={`px-3 py-1 rounded-lg ${dark ? "bg-gray-700 text-gray-300" : "bg-gray-100"} disabled:opacity-40`}>Next →</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [dark, setDark] = useState(true);
  const [ticker, setTicker] = useState("AAPL");
  const [period, setPeriod] = useState("6mo");
  const [customTicker, setCustomTicker] = useState("");
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState({});
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState("overview");
  const [backendOK, setBackendOK] = useState(null); // null=checking
  const [uploadName, setUploadName] = useState("");

  const nav = [
    { id: "overview", label: "Overview", icon: Home },
    { id: "behaviour", label: "Behaviour", icon: BarChart2 },
    { id: "insights", label: "Insights", icon: Info },
    { id: "data", label: "Data Table", icon: FileText },
  ];

  // Check backend health on mount
  useEffect(() => {
    checkHealth().then(ok => setBackendOK(ok));
  }, []);

  const runAnalysis = useCallback(async (t, p) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeStock(t, p);
      setData(result.data);
      setSummary(result.summary);
      setInsights(result.insights);
      setTicker(result.ticker);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // File upload handler
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadName(file.name);
    const name = (customTicker.trim() || file.name.split(".")[0]).toUpperCase();
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeFile(file, name);
      setData(result.data);
      setSummary(result.summary);
      setInsights(result.insights || []);
      setTicker(result.ticker);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = () => {
    const t = customTicker.trim().toUpperCase() || ticker;
    runAnalysis(t, period);
  };

  const bg = dark ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900";
  const nav_bg = dark ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200";

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>

      {/* ── Top Bar ── */}
      <header className={`sticky top-0 z-30 border-b px-4 py-3 flex flex-wrap items-center gap-2 justify-between ${nav_bg}`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <BarChart2 size={18} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-sm leading-none">StockBehaviour AI</p>
            <div className="flex items-center gap-1">
              {backendOK === null && <span className="text-xs text-gray-400">Checking backend…</span>}
              {backendOK === true && <><Wifi size={10} className="text-green-500" /><span className="text-xs text-green-500">Backend connected</span></>}
              {backendOK === false && <><WifiOff size={10} className="text-red-400" /><span className="text-xs text-red-400">Backend offline — start app.py</span></>}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Custom ticker */}
          <div className={`flex items-center gap-1 rounded-lg px-2 py-1.5 ${dark ? "bg-gray-700" : "bg-gray-100"}`}>
            <Search size={13} className={dark ? "text-gray-400" : "text-gray-500"} />
            <input value={customTicker} onChange={e => setCustomTicker(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleAnalyze()}
              placeholder="Ticker…"
              className={`bg-transparent outline-none text-xs w-20 ${dark ? "text-white placeholder-gray-500" : "text-gray-700"}`} />
          </div>

          {/* Preset */}
          <div className={`relative flex items-center rounded-lg px-2 py-1.5 ${dark ? "bg-gray-700" : "bg-gray-100"}`}>
            <select value={ticker} onChange={e => { setTicker(e.target.value); setCustomTicker(""); }}
              className={`bg-transparent outline-none cursor-pointer pr-4 text-xs ${dark ? "text-white" : "text-gray-700"}`}>
              {TICKERS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <ChevronDown size={12} className="absolute right-1 pointer-events-none" />
          </div>

          {/* Period */}
          <div className={`relative flex items-center rounded-lg px-2 py-1.5 ${dark ? "bg-gray-700" : "bg-gray-100"}`}>
            <select value={period} onChange={e => setPeriod(e.target.value)}
              className={`bg-transparent outline-none cursor-pointer pr-4 text-xs ${dark ? "text-white" : "text-gray-700"}`}>
              {PERIODS.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <ChevronDown size={12} className="absolute right-1 pointer-events-none" />
          </div>

          {/* Upload file */}
          <label className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition ${dark ? "bg-gray-700 text-gray-300 hover:bg-gray-600" : "bg-gray-100 text-gray-700 hover:bg-gray-200"}`}>
            <Upload size={13} />
            {uploadName ? uploadName.slice(0, 12) + "…" : "Upload CSV"}
            <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFileUpload} />
          </label>

          {/* Analyze */}
          <button onClick={handleAnalyze} disabled={loading || !backendOK}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition">
            {loading ? <RefreshCw size={13} className="animate-spin" /> : <RefreshCw size={13} />}
            Analyze
          </button>

          {/* Dark mode */}
          <button onClick={() => setDark(d => !d)}
            className={`p-1.5 rounded-lg transition ${dark ? "bg-gray-700 text-yellow-400" : "bg-gray-100 text-gray-600"}`}>
            {dark ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-57px)]">
        {/* ── Sidebar ── */}
        <aside className={`hidden md:flex flex-col w-44 sticky top-14 h-[calc(100vh-57px)] border-r pt-6 px-3 gap-1 ${nav_bg}`}>
          {nav.map(n => {
            const Icon = n.icon;
            const active = page === n.id;
            return (
              <button key={n.id} onClick={() => setPage(n.id)}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition ${active ? "bg-indigo-600 text-white" : ""}`}
                style={active ? {} : { color: dark ? "#9ca3af" : "#6b7280" }}>
                <Icon size={16} />{n.label}
              </button>
            );
          })}
          <div className="mt-auto mb-4 px-1">
            <div className={`rounded-xl p-3 text-center ${dark ? "bg-gray-700" : "bg-indigo-50"}`}>
              <p className="text-xs text-indigo-500 font-semibold">Analysing</p>
              <p className="font-bold text-lg text-indigo-600">{ticker || "—"}</p>
              <p className={`text-xs ${dark ? "text-gray-400" : "text-gray-500"}`}>{period} period</p>
              <p className={`text-xs ${dark ? "text-gray-500" : "text-gray-400"}`}>{summary.total || 0} days</p>
            </div>
          </div>
        </aside>

        {/* ── Mobile bottom nav ── */}
        <div className={`md:hidden fixed bottom-0 left-0 right-0 z-30 flex border-t ${nav_bg}`}>
          {nav.map(n => {
            const Icon = n.icon;
            const active = page === n.id;
            return (
              <button key={n.id} onClick={() => setPage(n.id)}
                className={`flex-1 flex flex-col items-center py-2 text-xs gap-0.5 ${active ? "text-indigo-600" : dark ? "text-gray-500" : "text-gray-400"}`}>
                <Icon size={18} /><span>{n.label}</span>
              </button>
            );
          })}
        </div>

        {/* ── Main Content ── */}
        <main className="flex-1 p-4 md:p-6 pb-24 md:pb-6 overflow-y-auto">

          {/* Error banner */}
          {error && (
            <div className="mb-4 flex items-center justify-between bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
              <span>❌ {error}</span>
              <button onClick={() => setError(null)}><X size={16} /></button>
            </div>
          )}

          {/* Backend offline banner */}
          {backendOK === false && (
            <div className="mb-4 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl px-4 py-3 text-sm">
              <p className="font-bold">⚠️ Backend not running</p>
              <p className="text-xs mt-1">Open a terminal and run: <code className="bg-yellow-100 px-1 rounded">python app.py</code></p>
            </div>
          )}

          <div className="mb-5">
            <h2 className="font-bold text-xl">{nav.find(n => n.id === page)?.label}</h2>
            <p className={`text-sm ${dark ? "text-gray-400" : "text-gray-500"}`}>
              {ticker} · {period} · {summary.total || 0} trading days
              {summary.total ? ` · Real data from Yahoo Finance` : ""}
            </p>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
              <RefreshCw size={30} className="animate-spin text-indigo-500" />
              <p className={dark ? "text-gray-400" : "text-gray-500"}>Fetching & analysing {ticker} from backend…</p>
            </div>
          ) : data.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-center">
              <BarChart2 size={40} className="text-indigo-400 opacity-50" />
              <p className={`font-medium ${dark ? "text-gray-400" : "text-gray-500"}`}>
                {backendOK ? "Click Analyze to load real stock data" : "Start the backend first, then click Analyze"}
              </p>
            </div>
          ) : (
            <>
              {page === "overview" && <OverviewPage data={data} summary={summary} ticker={ticker} dark={dark} />}
              {page === "behaviour" && <BehaviourPage data={data} summary={summary} dark={dark} />}
              {page === "insights" && <InsightsPage data={data} summary={summary} insights={insights} ticker={ticker} period={period} dark={dark} />}
              {page === "data" && <DataPage data={data} dark={dark} />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
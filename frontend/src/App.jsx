import React, { useEffect, useMemo, useState } from "react";
import { api } from "./api";

const NAV = [
  ["dashboard", "Dashboard"],
  ["scanner", "URL Scanner"],
  ["history", "Scan History"],
  ["analytics", "Analytics"],
  ["models", "Model Performance"],
  ["how", "How It Works"],
  ["about", "About"]
];

function Logo({ compact = false }) {
  return (
    <div className={`brand ${compact ? "compact" : ""}`}>
      <div className="brand-mark">TF</div>
      <div>
        <strong>TRACEFAKE</strong>
        {!compact && <span>Trace the Link. Detect the Threat.</span>}
      </div>
    </div>
  );
}

function RiskBadge({ value }) {
  return (
    <span className={`badge ${value?.toLowerCase()}`}>
      {value}
    </span>
  );
}

function Stat({ label, value, accent }) {
  return (
    <div className={`stat ${accent || ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RiskMeter({ score }) {
  const pct = Math.max(0, Math.min(100, Number(score || 0)));

  return (
    <div className="meter-wrap">
      <div className="meter">
        <div
          className="meter-fill"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="meter-labels">
        <span>0 Safe</span>
        <span>100 High Risk</span>
      </div>

      <div className="meter-score">
        {pct.toFixed(0)}
        <small>/100</small>
      </div>
    </div>
  );
}

function Empty({
  title = "No data yet.",
  text = "Run your first URL analysis to populate this section."
}) {
  return (
    <div className="empty">
      <div className="empty-icon">TF</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

function Dashboard({ analytics, history, onScan }) {
  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Security overview</p>
          <h1>URL Security Overview</h1>
          <p>
            Monitor your local URL analysis activity and detection results.
          </p>
        </div>

        <button className="primary" onClick={onScan}>
          Analyze a URL
        </button>
      </header>

      <div className="stats-grid">
        <Stat
          label="Total scans"
          value={analytics.total_scans}
        />

        <Stat
          label="Safe"
          value={analytics.safe}
          accent="safe-stat"
        />

        <Stat
          label="Suspicious"
          value={analytics.suspicious}
          accent="sus-stat"
        />

        <Stat
          label="Phishing"
          value={analytics.phishing}
          accent="bad-stat"
        />

        <Stat
          label="Average risk"
          value={`${analytics.average_risk}/100`}
        />
      </div>

      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Recent Scans</h2>
            <p>Latest locally stored analyses.</p>
          </div>
        </div>

        {history.length === 0 ? (
          <Empty />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>URL</th>
                  <th>Result</th>
                  <th>Risk</th>
                </tr>
              </thead>

              <tbody>
                {history.slice(0, 8).map((s) => (
                  <tr key={s.id}>
                    <td>
                      {new Date(s.timestamp).toLocaleString()}
                    </td>

                    <td className="url-cell">
                      {s.url}
                    </td>

                    <td>
                      <RiskBadge value={s.classification} />
                    </td>

                    <td>{s.risk_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function Scanner({ onResult }) {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");

    if (!url.trim()) {
      setError("Please enter a URL.");
      return;
    }

    setBusy(true);

    const stages = [
      "Parsing URL",
      "Extracting features",
      "Running security heuristics",
      "Running ML model",
      "Calculating risk",
      "Preparing analysis"
    ];

    for (const s of stages) {
      setStage(s);
      await new Promise((r) => setTimeout(r, 180));
    }

    try {
      const response = await api.analyze(url);
      onResult(response);
      setUrl("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      setStage("");
    }
  }

  return (
    <div className="page scanner-page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Static URL analysis</p>
          <h1>Analyze a suspicious URL</h1>
          <p>
            TraceFake analyzes the URL structure without opening
            the destination.
          </p>
        </div>
      </header>

      <section className="scan-hero">
        <form onSubmit={submit}>
          <label htmlFor="url">URL to analyze</label>

          <div className="url-input">
            <input
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/login"
              autoComplete="off"
            />

            <button
              className="primary"
              disabled={busy}
            >
              {busy ? "Analyzing..." : "Analyze URL"}
            </button>
          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </form>

        {busy && (
          <div className="scan-progress">
            <div className="spinner" />

            <div>
              <strong>{stage}</strong>
              <p>
                Running local analysis. The destination is not opened.
              </p>
            </div>
          </div>
        )}

        <div className="safety-note">
          <strong>Static analysis only.</strong>{" "}
          Submitted URLs are parsed as text. TraceFake does not
          automatically visit, execute, or download content from them.
        </div>
      </section>
    </div>
  );
}

function Result({ result, onBack }) {
  if (!result) {
    return null;
  }

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Analysis complete</p>
          <h1>Detection Result</h1>
          <p className="result-url">
            {result.url}
          </p>
        </div>

        <button
          className="secondary"
          onClick={onBack}
        >
          New analysis
        </button>
      </header>

      <section
        className={`result-hero ${result.classification.toLowerCase()}`}
      >
        <div>
          <p className="eyebrow">
            Final classification
          </p>

          <h2>
            <RiskBadge value={result.classification} />
          </h2>

          <p className="disclaimer">
            Risk assessment, not a guarantee.
          </p>
        </div>

        <div className="risk-box">
          <span>Risk Score</span>
          <strong>{result.risk_score}</strong>
          <small>/ 100</small>
        </div>
      </section>

      <div className="two-col">
        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Risk Assessment</h2>
              <p>
                Combined local model and security heuristics.
              </p>
            </div>
          </div>

          <RiskMeter score={result.risk_score} />

          <div className="signal-grid">
            <div>
              <span>ML model</span>
              <strong>
                {result.model_ready
                  ? `${result.ml_score}/100`
                  : "Not trained"}
              </strong>
            </div>

            <div>
              <span>Rule engine</span>
              <strong>
                {result.rule_score}/100
              </strong>
            </div>

            <div>
              <span>Reputation</span>
              <strong>
                {result.reputation_status}
              </strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Detection Summary</h2>
              <p>
                Actual signals used by the engine.
              </p>
            </div>
          </div>

          <div className="reason-list">
            {result.reasons.map((r, i) => (
              <div
                className="reason"
                key={i}
              >
                <span
                  className={`dot ${r.severity.toLowerCase()}`}
                />

                <div>
                  <strong>{r.description}</strong>
                  <small>
                    {r.source} · {r.severity}
                  </small>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Technical Analysis</h2>
            <p>
              Features extracted from the URL string.
            </p>
          </div>
        </div>

        <div className="feature-grid">
          {result.features.map((f) => (
            <div
              className="feature"
              key={f.name}
            >
              <span>
                {f.name.replaceAll("_", " ")}
              </span>

              <strong>{f.value}</strong>

              <em className={f.risk.toLowerCase()}>
                {f.risk}
              </em>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Recommendations</h2>
          </div>
        </div>

        <ul className="recommendations">
          {result.recommendations.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>

        {result.id && (
          <a
            className="secondary report-link"
            href={api.reportUrl(result.id)}
            target="_blank"
            rel="noreferrer"
          >
            Generate PDF report
          </a>
        )}
      </section>
    </div>
  );
}

function History({ rows, onOpen, onDelete }) {
  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Local database</p>
          <h1>Scan History</h1>
          <p>
            Searchable history of TraceFake analyses.
          </p>
        </div>
      </header>

      <section className="panel">
        {rows.length === 0 ? (
          <Empty />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>URL</th>
                  <th>Result</th>
                  <th>Risk</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {rows.map((s) => (
                  <tr key={s.id}>
                    <td>
                      {new Date(
                        s.timestamp
                      ).toLocaleString()}
                    </td>

                    <td className="url-cell">
                      {s.url}
                    </td>

                    <td>
                      <RiskBadge
                        value={s.classification}
                      />
                    </td>

                    <td>{s.risk_score}</td>

                    <td>
                      <button
                        className="table-btn"
                        onClick={() => onOpen(s)}
                      >
                        Open
                      </button>

                      <button
                        className="table-btn danger-text"
                        onClick={() => onDelete(s.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function Analytics({ data }) {
  const bars = data.risk_buckets || [];

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">
            Real database data
          </p>

          <h1>Analytics</h1>

          <p>
            Charts are generated from stored scans.
            No synthetic dashboard numbers are used.
          </p>
        </div>
      </header>

      {data.total_scans === 0 ? (
        <Empty />
      ) : (
        <>
          <div className="stats-grid">
            <Stat
              label="Total scans"
              value={data.total_scans}
            />

            <Stat
              label="Safe"
              value={data.safe}
            />

            <Stat
              label="Suspicious"
              value={data.suspicious}
            />

            <Stat
              label="Phishing"
              value={data.phishing}
            />

            <Stat
              label="Average risk"
              value={`${data.average_risk}/100`}
            />
          </div>

          <section className="panel">
            <div className="panel-head">
              <div>
                <h2>Risk Distribution</h2>
              </div>
            </div>

            <div className="bars">
              {bars.map((b) => (
                <div
                  className="bar-row"
                  key={b.range}
                >
                  <span>{b.range}</span>

                  <div>
                    <i
                      style={{
                        width: `${
                          data.total_scans
                            ? (b.count /
                                data.total_scans) *
                              100
                            : 0
                        }%`
                      }}
                    />
                  </div>

                  <strong>{b.count}</strong>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function Models() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.models()
      .then(setData)
      .catch(() => setData({ ready: false }));
  }, []);

  if (!data) {
    return (
      <div className="page">
        <Empty title="Loading model information..." />
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">
            Measured performance
          </p>

          <h1>Model Performance</h1>

          <p>
            Metrics below come from the actual
            training pipeline, not hardcoded values.
          </p>
        </div>
      </header>

      {!data.ready ? (
        <Empty
          title="Model not trained yet."
          text="Download the UCI dataset and run the training command from the README."
        />
      ) : (
        <>
          <section className="panel">
            <div className="model-header">
              <div>
                <h2>{data.model_name}</h2>
                <p>{data.methodology}</p>
              </div>

              <RiskBadge value="READY" />
            </div>

            <div className="metric-grid">
              {Object.entries(data.metrics).map(
                ([k, v]) => (
                  <div
                    className="metric"
                    key={k}
                  >
                    <span>
                      {k.replaceAll("_", " ")}
                    </span>

                    <strong>
                      {typeof v === "number"
                        ? v.toFixed(4)
                        : v}
                    </strong>
                  </div>
                )
              )}
            </div>
          </section>

          <section className="panel">
            <h2>Model Comparison</h2>

            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1</th>
                    <th>ROC-AUC</th>
                  </tr>
                </thead>

                <tbody>
                  {data.comparison.map((m) => (
                    <tr key={m.model}>
                      <td>{m.model}</td>
                      <td>
                        {m.accuracy.toFixed(4)}
                      </td>
                      <td>
                        {m.precision.toFixed(4)}
                      </td>
                      <td>
                        {m.recall.toFixed(4)}
                      </td>
                      <td>
                        {m.f1.toFixed(4)}
                      </td>
                      <td>
                        {m.roc_auc.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="two-col">
            <section className="panel">
              <h2>Confusion Matrix</h2>

              <div className="matrix">
                {(data.confusion_matrix || []).map(
                  (row, i) =>
                    row.map((v, j) => (
                      <div
                        key={`${i}-${j}`}
                      >
                        <span>{v}</span>

                        <small>
                          {i === 0
                            ? j === 0
                              ? "True legitimate / predicted legitimate"
                              : "True legitimate / predicted phishing"
                            : j === 0
                              ? "True phishing / predicted legitimate"
                              : "True phishing / predicted phishing"}
                        </small>
                      </div>
                    ))
                )}
              </div>
            </section>

            <section className="panel">
              <h2>Top Features</h2>

              <div className="feature-bars">
                {(data.feature_importance || []).map(
                  (f) => (
                    <div key={f.feature}>
                      <span>{f.feature}</span>

                      <div>
                        <i
                          style={{
                            width: `${Math.min(
                              100,
                              f.importance * 100 * 3
                            )}%`
                          }}
                        />
                      </div>
                    </div>
                  )
                )}
              </div>
            </section>
          </section>
        </>
      )}
    </div>
  );
}

function How() {
  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">
            Detection pipeline
          </p>

          <h1>How TraceFake Works</h1>

          <p>
            A transparent local pipeline designed
            for safe URL analysis.
          </p>
        </div>
      </header>

      <div className="flow">
        {[
          "URL Input",
          "Safe URL Parsing",
          "Feature Extraction",
          "Machine Learning",
          "Rule Analysis",
          "Risk Scoring",
          "Classification",
          "Explanation"
        ].map((x, i) => (
          <div
            className="flow-step"
            key={x}
          >
            <span>
              {String(i + 1).padStart(2, "0")}
            </span>

            <strong>{x}</strong>

            {i < 7 && <i>→</i>}
          </div>
        ))}
      </div>

      <section className="panel prose">
        <h2>Why the result is not absolute</h2>

        <p>
          Phishing detection is a classification
          problem with false positives and false
          negatives. A model can miss a malicious URL,
          and a legitimate URL can sometimes look
          suspicious.
        </p>

        <p>
          TraceFake therefore presents a risk score
          and evidence rather than claiming certainty.
          The default scanner performs static analysis
          and does not automatically open the submitted
          destination.
        </p>
      </section>
    </div>
  );
}

function About() {
  return (
    <div className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Project</p>

          <h1>About TraceFake</h1>

          <p>
            Trace the Link. Detect the Threat.
          </p>
        </div>
      </header>

      <section className="about-grid">
        <div className="panel">
          <h2>Purpose</h2>

          <p>
            TraceFake combines URL feature
            engineering, machine learning, security
            heuristics, explainability,
            database-backed history, analytics, and
            PDF reporting into one local cybersecurity
            application.
          </p>
        </div>

        <div className="panel">
          <h2>Security principle</h2>

          <p>
            The default application treats URLs as
            untrusted input. It parses and analyzes the
            string without automatically visiting the
            destination.
          </p>
        </div>

        <div className="panel">
          <h2>Academic principle</h2>

          <p>
            Metrics are produced by the training
            pipeline. No accuracy, precision, recall,
            F1-score, or ROC-AUC is hardcoded into the
            interface.
          </p>
        </div>

        <div className="panel">
          <h2>Limitations</h2>

          <p>
            No phishing detector can guarantee perfect
            detection. Dataset bias, concept drift, URL
            obfuscation, and unseen attack techniques
            can affect results.
          </p>
        </div>
      </section>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [history, setHistory] = useState([]);

  const [analytics, setAnalytics] = useState({
    total_scans: 0,
    safe: 0,
    suspicious: 0,
    phishing: 0,
    average_risk: 0,
    risk_buckets: [],
    timeline: []
  });

  const [result, setResult] = useState(null);
  const [online, setOnline] = useState(false);

  async function refresh() {
    try {
      const [h, a] = await Promise.all([
        api.history(),
        api.analytics()
      ]);

      setHistory(h);
      setAnalytics(a);
      setOnline(true);
    } catch {
      setOnline(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  function showResult(r) {
    setResult(r);
    setPage("result");
    refresh();
  }

  async function deleteScan(id) {
    if (!confirm("Delete this scan?")) {
      return;
    }

    await api.remove(id);
    refresh();

    if (result?.id === id) {
      setResult(null);
    }
  }

  const content = useMemo(() => {
    if (page === "dashboard") {
      return (
        <Dashboard
          analytics={analytics}
          history={history}
          onScan={() => setPage("scanner")}
        />
      );
    }

    if (page === "scanner") {
      return (
        <Scanner
          onResult={showResult}
        />
      );
    }

    if (page === "result") {
      return (
        <Result
          result={result}
          onBack={() => setPage("scanner")}
        />
      );
    }

    if (page === "history") {
      return (
        <History
          rows={history}
          onOpen={(r) => {
            setResult(r);
            setPage("result");
          }}
          onDelete={deleteScan}
        />
      );
    }

    if (page === "analytics") {
      return (
        <Analytics data={analytics} />
      );
    }

    if (page === "models") {
      return <Models />;
    }

    if (page === "how") {
      return <How />;
    }

    return <About />;
  }, [
    page,
    analytics,
    history,
    result
  ]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Logo />

        <nav>
          {NAV.map(([id, label]) => (
            <button
              key={id}
              className={
                page === id
                  ? "active"
                  : ""
              }
              onClick={() => setPage(id)}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="status">
          <span
            className={
              online ? "online" : ""
            }
          />

          <div>
            <strong>
              Detection Engine
            </strong>

            <small>
              {online
                ? "Online"
                : "Offline"}
            </small>
          </div>
        </div>
      </aside>

      <main className="main">
        {content}

        <footer>
          TraceFake · Local-first security analysis ·
          Results are probabilistic and not a guarantee
          of safety.
        </footer>
      </main>
    </div>
  );
}
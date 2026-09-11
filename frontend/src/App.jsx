import { useEffect, useState } from "react";

import {
  getDashboardSummary,
  getFindings,
  getOrganizations,
  getProjects,
  getRepositories,
  getPullRequests,
  getReviews,
  getReview,
  getStoredUser,
  getToken,
  login,
  logout,
  runGithubReview,
} from "./api";

const COLORS = {
  background: "#070a12",
  panel: "#101522",
  panel2: "#141a2b",
  border: "#252c40",
  text: "#f4f6ff",
  muted: "#8c97b5",
  accent: "#6c5cff",
  accentSoft: "#201b50",
  success: "#27d6a1",
  warning: "#ffad4a",
  danger: "#ff667d",
};

function formatStatus(status) {
  if (!status) return "Unknown";

  return status
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function scoreLabel(score) {
  if (score === null || score === undefined) return "—";
  return `${score}%`;
}

function scoreColor(score) {
  if (score >= 80) return COLORS.success;
  if (score >= 60) return COLORS.warning;
  return COLORS.danger;
}

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("developer@gmail.com");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      await login(email, password);
      onLogin();
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 80% 10%, #201b50 0%, transparent 35%), #070a12",
        display: "grid",
        placeItems: "center",
        padding: 24,
        color: COLORS.text,
      }}
    >
      <div
        style={{
          width: "min(460px, 100%)",
          background: "rgba(16,21,34,.94)",
          border: `1px solid ${COLORS.border}`,
          borderRadius: 24,
          padding: 34,
          boxShadow: "0 24px 80px rgba(0,0,0,.4)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            marginBottom: 30,
          }}
        >
          <div
            style={{
              width: 46,
              height: 46,
              borderRadius: 14,
              background: COLORS.accent,
              display: "grid",
              placeItems: "center",
              fontWeight: 900,
            }}
          >
            D
          </div>

          <div>
            <div style={{ fontSize: 22, fontWeight: 800 }}>DevFlow</div>
            <div style={{ color: COLORS.muted, fontSize: 13 }}>
              Engineering workspace
            </div>
          </div>
        </div>

        <div
          style={{
            color: COLORS.accent,
            letterSpacing: 2,
            fontSize: 11,
            fontWeight: 800,
            textTransform: "uppercase",
          }}
        >
          Developer workspace
        </div>

        <h1 style={{ fontSize: 38, margin: "10px 0 8px" }}>
          Developer review,
          <br />
          organized.
        </h1>

        <p style={{ color: COLORS.muted, lineHeight: 1.7 }}>
          Inspect pull requests, automated reviews, findings, projects, and
          connected GitHub repositories from one workspace.
        </p>

        <form onSubmit={handleSubmit} style={{ marginTop: 26 }}>
          <label
            style={{
              display: "block",
              fontSize: 13,
              fontWeight: 700,
              marginBottom: 8,
            }}
          >
            Email
          </label>

          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            required
            style={inputStyle}
          />

          <label
            style={{
              display: "block",
              fontSize: 13,
              fontWeight: 700,
              margin: "18px 0 8px",
            }}
          >
            Password
          </label>

          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            required
            style={inputStyle}
          />

          {error && (
            <div
              style={{
                marginTop: 16,
                padding: 12,
                borderRadius: 12,
                background: "rgba(255,102,125,.1)",
                border: "1px solid rgba(255,102,125,.25)",
                color: "#ff9cad",
                fontSize: 13,
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              ...buttonStyle,
              width: "100%",
              marginTop: 20,
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Signing in..." : "Sign in to DevFlow"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Sidebar({ currentPage, setCurrentPage, user }) {
  const items = [
    ["dashboard", "▦", "Dashboard"],
    ["projects", "◫", "Projects"],
    ["pulls", "⌘", "Pull requests"],
    ["reviews", "✓", "Reviews"],
    ["github", "◆", "GitHub"],
  ];

  return (
    <aside
      style={{
        width: 240,
        minHeight: "100vh",
        background: "#060910",
        borderRight: `1px solid ${COLORS.border}`,
        padding: "24px 16px",
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "0 8px 28px",
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 12,
            background: COLORS.accent,
            display: "grid",
            placeItems: "center",
            fontWeight: 900,
            color: "white",
          }}
        >
          D
        </div>

        <div>
          <div style={{ fontWeight: 800, fontSize: 17 }}>DevFlow</div>
          <div style={{ fontSize: 11, color: COLORS.muted }}>
            Engineering workspace
          </div>
        </div>
      </div>

      <div
        style={{
          color: "#69738f",
          fontSize: 10,
          letterSpacing: 2,
          fontWeight: 800,
          margin: "4px 12px 12px",
        }}
      >
        WORKSPACE
      </div>

      {items.map(([id, icon, label]) => (
        <button
          key={id}
          type="button"
          onClick={() => setCurrentPage(id)}
          style={{
            width: "100%",
            border:
              currentPage === id
                ? "1px solid rgba(108,92,255,.35)"
                : "1px solid transparent",
            borderRadius: 12,
            padding: "14px 12px",
            display: "flex",
            alignItems: "center",
            gap: 14,
            background:
              currentPage === id ? "rgba(108,92,255,.15)" : "transparent",
            color: currentPage === id ? COLORS.text : COLORS.muted,
            cursor: "pointer",
            textAlign: "left",
            fontWeight: currentPage === id ? 750 : 600,
            marginBottom: 6,
          }}
        >
          <span
            style={{
              width: 20,
              color: currentPage === id ? "#a79fff" : "#69738f",
            }}
          >
            {icon}
          </span>

          {label}
        </button>
      ))}

      <div
        style={{
          position: "absolute",
          left: 16,
          right: 16,
          bottom: 18,
          borderTop: `1px solid ${COLORS.border}`,
          paddingTop: 16,
          color: COLORS.muted,
          fontSize: 12,
        }}
      >
        <div style={{ color: COLORS.text, fontWeight: 700 }}>
          {user?.username || "Developer"}
        </div>

        <div style={{ marginTop: 4 }}>{user?.email || ""}</div>
      </div>
    </aside>
  );
}

function Topbar({ title, user, onRefresh, onSignOut, refreshing }) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        marginBottom: 24,
      }}
    >
      <div>
        <div
          style={{
            color: COLORS.accent,
            fontSize: 10,
            letterSpacing: 2,
            fontWeight: 800,
          }}
        >
          DEVFLOW / WORKSPACE
        </div>

        <h1 style={{ margin: "7px 0 0", fontSize: 28 }}>{title}</h1>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <button
          type="button"
          onClick={onRefresh}
          style={secondaryButtonStyle}
        >
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 12px",
            border: `1px solid ${COLORS.border}`,
            borderRadius: 12,
            background: COLORS.panel,
          }}
        >
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: 9,
              background: COLORS.accent,
              display: "grid",
              placeItems: "center",
              fontWeight: 800,
            }}
          >
            D
          </div>

          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontSize: 12, fontWeight: 750 }}>
              {user?.username}
            </div>

            <div style={{ fontSize: 10, color: COLORS.muted }}>
              {user?.email}
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={onSignOut}
          style={{
            ...secondaryButtonStyle,
            borderColor: "transparent",
            color: COLORS.muted,
          }}
        >
          Sign out
        </button>
      </div>
    </header>
  );
}

function StatCard({ label, value }) {
  return (
    <div style={cardStyle}>
      <div style={{ color: COLORS.muted, fontSize: 12 }}>{label}</div>

      <div
        style={{
          fontSize: 32,
          fontWeight: 850,
          marginTop: 22,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function EmptyState({ title, text }) {
  return (
    <div
      style={{
        ...cardStyle,
        textAlign: "center",
        padding: 50,
      }}
    >
      <div style={{ fontSize: 18, fontWeight: 800 }}>{title}</div>
      <div style={{ color: COLORS.muted, marginTop: 8 }}>{text}</div>
    </div>
  );
}

function DashboardPage({ dashboard, onSelectReview }) {
  const recentReviews = dashboard?.recent_reviews || [];

  return (
    <>
      <div
        style={{
          ...heroStyle,
          marginBottom: 18,
        }}
      >
        <div>
          <div style={eyebrowStyle}>ENGINEERING INSIGHTS</div>

          <h2 style={{ fontSize: 34, margin: "12px 0 10px" }}>
            Know what needs attention.
          </h2>

          <p
            style={{
              color: COLORS.muted,
              maxWidth: 650,
              lineHeight: 1.7,
              margin: 0,
            }}
          >
            Track pull requests, review quality, and automated findings across
            your connected repositories.
          </p>
        </div>

        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: "50%",
            border: "1px solid rgba(108,92,255,.35)",
            display: "grid",
            placeItems: "center",
          }}
        >
          <div
            style={{
              width: 62,
              height: 62,
              borderRadius: "50%",
              background: COLORS.accent,
              display: "grid",
              placeItems: "center",
              fontWeight: 900,
            }}
          >
            DF
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 14,
          marginBottom: 18,
        }}
      >
        <StatCard
          label="Pull requests"
          value={dashboard?.total_pull_requests ?? 0}
        />

        <StatCard
          label="Reviews"
          value={dashboard?.total_reviews ?? 0}
        />

        <StatCard
          label="Findings"
          value={dashboard?.total_findings ?? 0}
        />

        <StatCard
          label="Average score"
          value={
            dashboard?.average_score === null ||
            dashboard?.average_score === undefined
              ? "—"
              : `${dashboard.average_score}%`
          }
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.7fr) minmax(280px, .8fr)",
          gap: 18,
        }}
      >
        <div style={cardStyle}>
          <div style={eyebrowStyle}>ACTIVITY</div>

          <h3 style={{ fontSize: 18, margin: "8px 0 18px" }}>
            Recent reviews
          </h3>

          {recentReviews.length === 0 ? (
            <EmptyState
              title="No reviews yet"
              text="Run an AI review to start building review history."
            />
          ) : (
            recentReviews.map((review) => (
              <button
                key={review.review_id}
                type="button"
                onClick={() => onSelectReview(review.review_id)}
                style={{
                  width: "100%",
                  padding: "15px 0",
                  display: "grid",
                  gridTemplateColumns: "38px minmax(0,1fr) auto",
                  gap: 12,
                  alignItems: "center",
                  background: "transparent",
                  color: COLORS.text,
                  border: "none",
                  borderBottom: `1px solid ${COLORS.border}`,
                  textAlign: "left",
                  cursor: "pointer",
                }}
              >
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 11,
                    background: COLORS.accentSoft,
                    color: "#aaa2ff",
                    display: "grid",
                    placeItems: "center",
                    fontSize: 11,
                    fontWeight: 800,
                  }}
                >
                  PR
                </div>

                <div>
                  <div style={{ fontWeight: 750 }}>
                    #{review.pull_request_number}{" "}
                    {review.pull_request_title}
                  </div>

                  <div
                    style={{
                      color: COLORS.muted,
                      fontSize: 11,
                      marginTop: 4,
                    }}
                  >
                    {review.project_name} · {review.repository_name}
                  </div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <div
                    style={{
                      color: scoreColor(review.score),
                      fontWeight: 800,
                    }}
                  >
                    {scoreLabel(review.score)}
                  </div>

                  <div
                    style={{
                      color: COLORS.muted,
                      fontSize: 11,
                      marginTop: 4,
                    }}
                  >
                    {review.finding_count} findings
                  </div>
                </div>
              </button>
            ))
          )}
        </div>

        <div style={cardStyle}>
          <div style={eyebrowStyle}>QUALITY</div>

          <h3 style={{ fontSize: 18, margin: "8px 0 20px" }}>
            Review health
          </h3>

          <div
            style={{
              width: 180,
              height: 180,
              borderRadius: "50%",
              margin: "20px auto",
              display: "grid",
              placeItems: "center",
              background: `conic-gradient(${COLORS.accent} ${
                (dashboard?.average_score || 0) * 3.6
              }deg, #20263b 0deg)`,
            }}
          >
            <div
              style={{
                width: 140,
                height: 140,
                borderRadius: "50%",
                background: COLORS.panel,
                display: "grid",
                placeItems: "center",
                fontSize: 30,
                fontWeight: 850,
              }}
            >
              {dashboard?.average_score ?? 0}

              <span style={{ fontSize: 12, color: COLORS.muted }}>
                /100
              </span>
            </div>
          </div>

          <div
            style={{
              textAlign: "center",
              color: COLORS.muted,
              lineHeight: 1.6,
              fontSize: 12,
            }}
          >
            Average score across completed reviews in your organization
            workspace.
          </div>
        </div>
      </div>
    </>
  );
}

function ProjectsPage({ projects, repositories }) {
  return (
    <div>
      <div style={pageIntroStyle}>
        <div>
          <div style={eyebrowStyle}>WORKSPACE</div>

          <h2 style={pageTitleStyle}>Projects & repositories</h2>

          <p style={pageTextStyle}>
            Connected projects and the repositories DevFlow can review.
          </p>
        </div>
      </div>

      {projects.length === 0 ? (
        <EmptyState
          title="No projects found"
          text="Your organization does not have any visible projects yet."
        />
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: 16,
          }}
        >
          {projects.map((project) => {
            const projectRepos = repositories.filter(
              (repo) => repo.project_id === project.id,
            );

            return (
              <div key={project.id} style={cardStyle}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 19, fontWeight: 800 }}>
                      {project.name}
                    </div>

                    <div
                      style={{
                        marginTop: 5,
                        color: COLORS.accent,
                        fontWeight: 800,
                        fontSize: 12,
                      }}
                    >
                      {project.key}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: "5px 9px",
                      borderRadius: 8,
                      background: COLORS.accentSoft,
                      color: "#afa8ff",
                      fontSize: 11,
                    }}
                  >
                    {projectRepos.length} repos
                  </div>
                </div>

                <p
                  style={{
                    color: COLORS.muted,
                    lineHeight: 1.6,
                    fontSize: 13,
                  }}
                >
                  {project.description || "No project description."}
                </p>

                <div style={{ marginTop: 18 }}>
                  {projectRepos.length === 0 ? (
                    <div style={{ color: COLORS.muted, fontSize: 12 }}>
                      No repositories connected.
                    </div>
                  ) : (
                    projectRepos.map((repo) => (
                      <div
                        key={repo.id}
                        style={{
                          padding: 12,
                          borderRadius: 10,
                          background: "#0c111d",
                          border: `1px solid ${COLORS.border}`,
                          marginTop: 8,
                        }}
                      >
                        <div style={{ fontWeight: 700 }}>
                          {repo.external_id || `Repository #${repo.id}`}
                        </div>

                        <div
                          style={{
                            color: COLORS.muted,
                            fontSize: 11,
                            marginTop: 4,
                          }}
                        >
                          {repo.provider} · default branch:{" "}
                          {repo.default_branch}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function PullRequestsPage({
  pullRequests,
  repositories,
  onOpenReviews,
}) {
  return (
    <div>
      <div style={pageIntroStyle}>
        <div>
          <div style={eyebrowStyle}>CODE COLLABORATION</div>

          <h2 style={pageTitleStyle}>Pull requests</h2>

          <p style={pageTextStyle}>
            Review activity across connected repositories.
          </p>
        </div>
      </div>

      {pullRequests.length === 0 ? (
        <EmptyState
          title="No pull requests"
          text="Connect a repository and start reviewing pull requests."
        />
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {pullRequests.map((pr) => {
            const repo = repositories.find(
              (item) => item.id === pr.repository_id,
            );

            return (
              <div
                key={pr.id}
                style={{
                  ...cardStyle,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 20,
                }}
              >
                <div>
                  <div style={eyebrowStyle}>
                    PR #{pr.external_number} · {formatStatus(pr.status)}
                  </div>

                  <h3 style={{ margin: "8px 0", fontSize: 18 }}>
                    {pr.title}
                  </h3>

                  <div
                    style={{
                      color: COLORS.muted,
                      fontSize: 12,
                    }}
                  >
                    {repo?.external_id || "Connected repository"}
                  </div>

                  <div
                    style={{
                      color: COLORS.muted,
                      fontSize: 11,
                      marginTop: 6,
                    }}
                  >
                    {pr.source_branch} → {pr.target_branch}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onOpenReviews(pr.id)}
                  style={buttonStyle}
                >
                  View reviews
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ReviewsPage({
  reviews,
  pullRequests,
  onSelectReview,
}) {
  return (
    <div>
      <div style={pageIntroStyle}>
        <div>
          <div style={eyebrowStyle}>CODE QUALITY</div>

          <h2 style={pageTitleStyle}>Reviews</h2>

          <p style={pageTextStyle}>
            Every automated code review generated by DevFlow.
          </p>
        </div>
      </div>

      {reviews.length === 0 ? (
        <EmptyState
          title="No reviews"
          text="Run an AI review from GitHub to create your first review."
        />
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {reviews.map((review) => {
            const pr = pullRequests.find(
              (item) => item.id === review.pull_request_id,
            );

            return (
              <button
                key={review.id}
                type="button"
                onClick={() => onSelectReview(review.id)}
                style={{
                  ...cardStyle,
                  width: "100%",
                  cursor: "pointer",
                  color: COLORS.text,
                  textAlign: "left",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 16,
                  }}
                >
                  <div>
                    <div style={eyebrowStyle}>
                      Review #{review.id} · PR #
                      {pr?.external_number || review.pull_request_id}
                    </div>

                    <h3 style={{ margin: "8px 0" }}>
                      {pr?.title || "Pull request review"}
                    </h3>

                    <div
                      style={{
                        color: COLORS.muted,
                        fontSize: 12,
                      }}
                    >
                      {review.summary || "No summary available."}
                    </div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <div
                      style={{
                        color: scoreColor(review.score),
                        fontSize: 24,
                        fontWeight: 850,
                      }}
                    >
                      {scoreLabel(review.score)}
                    </div>

                    <div
                      style={{
                        marginTop: 6,
                        color:
                          review.status === "completed"
                            ? COLORS.success
                            : COLORS.warning,
                        fontSize: 11,
                      }}
                    >
                      {formatStatus(review.status)}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ReviewDetail({ review, findings, onBack }) {
  if (!review) {
    return (
      <EmptyState
        title="Review not found"
        text="The selected review could not be loaded."
      />
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        style={{
          ...secondaryButtonStyle,
          marginBottom: 18,
        }}
      >
        ← Back to reviews
      </button>

      <div style={cardStyle}>
        <div style={eyebrowStyle}>REVIEW #{review.id}</div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 24,
            alignItems: "start",
          }}
        >
          <div>
            <h2 style={{ margin: "8px 0" }}>Automated code review</h2>

            <p
              style={{
                color: COLORS.muted,
                lineHeight: 1.7,
                maxWidth: 760,
              }}
            >
              {review.summary || "No summary available."}
            </p>
          </div>

          <div style={{ textAlign: "right" }}>
            <div
              style={{
                color: scoreColor(review.score),
                fontSize: 34,
                fontWeight: 900,
              }}
            >
              {scoreLabel(review.score)}
            </div>

            <div
              style={{
                color: COLORS.muted,
                fontSize: 11,
                marginTop: 5,
              }}
            >
              {formatStatus(review.status)}
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 18 }}>
        <div style={eyebrowStyle}>FINDINGS</div>

        <h3 style={{ margin: "8px 0 16px" }}>
          {findings.length} issue{findings.length === 1 ? "" : "s"} detected
        </h3>

        {findings.length === 0 ? (
          <EmptyState
            title="Clean review"
            text="No findings were generated for this review."
          />
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {findings.map((finding) => (
              <div key={finding.id} style={cardStyle}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 16,
                  }}
                >
                  <div>
                    <div
                      style={{
                        color:
                          finding.severity === "critical" ||
                          finding.severity === "high"
                            ? COLORS.danger
                            : finding.severity === "medium"
                              ? COLORS.warning
                              : COLORS.accent,
                        fontSize: 11,
                        fontWeight: 800,
                        textTransform: "uppercase",
                        letterSpacing: 1,
                      }}
                    >
                      {finding.severity} · {finding.category}
                    </div>

                    <h3 style={{ margin: "8px 0" }}>
                      {finding.title}
                    </h3>
                  </div>

                  {finding.line_number && (
                    <div
                      style={{
                        padding: "5px 9px",
                        borderRadius: 8,
                        background: "#0c111d",
                        border: `1px solid ${COLORS.border}`,
                        color: COLORS.muted,
                        fontSize: 11,
                      }}
                    >
                      Line {finding.line_number}
                    </div>
                  )}
                </div>

                <p
                  style={{
                    color: COLORS.muted,
                    lineHeight: 1.65,
                  }}
                >
                  {finding.description}
                </p>

                <div
                  style={{
                    marginTop: 12,
                    padding: 13,
                    borderRadius: 10,
                    background: "rgba(108,92,255,.06)",
                    border: "1px solid rgba(108,92,255,.18)",
                  }}
                >
                  <div
                    style={{
                      color: "#aaa2ff",
                      fontSize: 11,
                      fontWeight: 800,
                      marginBottom: 5,
                    }}
                  >
                    SUGGESTION
                  </div>

                  <div
                    style={{
                      color: COLORS.text,
                      fontSize: 13,
                      lineHeight: 1.6,
                    }}
                  >
                    {finding.suggestion}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function GithubPage({
  repositories,
  pullRequests,
  onReviewComplete,
}) {
  const githubRepos = repositories.filter(
    (repo) => repo.provider?.toLowerCase() === "github",
  );

  const [selectedRepoId, setSelectedRepoId] = useState("");
  const [pullNumber, setPullNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const activeRepoId =
    Number(selectedRepoId) || githubRepos[0]?.id || "";

  const selectedRepo = githubRepos.find(
    (repo) => repo.id === activeRepoId,
  );

  const defaultPullRequest = pullRequests.find(
    (pr) => pr.repository_id === activeRepoId,
  );

  const activePullNumber =
    pullNumber || defaultPullRequest?.external_number || "";

  function handleRepositoryChange(event) {
    const repositoryId = Number(event.target.value);

    setSelectedRepoId(repositoryId);

    const firstPullRequest = pullRequests.find(
      (pr) => pr.repository_id === repositoryId,
    );

    setPullNumber(firstPullRequest?.external_number || "");
    setMessage("");
  }

  async function handleReview() {
    if (!selectedRepo?.external_id) {
      setMessage("Select a GitHub repository first.");
      return;
    }

    if (!activePullNumber) {
      setMessage("Enter a pull request number.");
      return;
    }

    const [owner, repository] = selectedRepo.external_id.split("/");

    if (!owner || !repository) {
      setMessage(
        "This repository does not have a valid GitHub owner/repository mapping.",
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      await runGithubReview(
        owner,
        repository,
        activePullNumber,
      );

      setMessage(
        `AI review completed for ${owner}/${repository}#${activePullNumber}.`,
      );

      await onReviewComplete();
    } catch (error) {
      setMessage(error.message || "GitHub review failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={pageIntroStyle}>
        <div>
          <div style={eyebrowStyle}>GITHUB INTEGRATION</div>

          <h2 style={pageTitleStyle}>Run a GitHub review</h2>

          <p style={pageTextStyle}>
            Pull the latest PR diff from GitHub and run DevFlow&apos;s
            automated review pipeline.
          </p>
        </div>
      </div>

      {githubRepos.length === 0 ? (
        <EmptyState
          title="No GitHub repository connected"
          text="Connect a GitHub repository to your DevFlow project first."
        />
      ) : (
        <div style={{ maxWidth: 760 }}>
          <div style={cardStyle}>
            <label style={labelStyle}>Repository</label>

            <select
              value={activeRepoId}
              onChange={handleRepositoryChange}
              style={inputStyle}
            >
              {githubRepos.map((repo) => (
                <option key={repo.id} value={repo.id}>
                  {repo.external_id}
                </option>
              ))}
            </select>

            <label
              style={{
                ...labelStyle,
                marginTop: 18,
              }}
            >
              Pull request number
            </label>

            <input
              value={activePullNumber}
              onChange={(event) => setPullNumber(event.target.value)}
              type="number"
              min="1"
              style={inputStyle}
            />

            <button
              type="button"
              onClick={handleReview}
              disabled={loading}
              style={{
                ...buttonStyle,
                marginTop: 18,
                opacity: loading ? 0.6 : 1,
              }}
            >
              {loading ? "Running AI review..." : "Run AI review"}
            </button>

            {message && (
              <div
                style={{
                  marginTop: 16,
                  padding: 12,
                  borderRadius: 10,
                  background: "rgba(108,92,255,.08)",
                  border: "1px solid rgba(108,92,255,.2)",
                  color: COLORS.muted,
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              >
                {message}
              </div>
            )}
          </div>

          <div
            style={{
              ...cardStyle,
              marginTop: 16,
            }}
          >
            <div style={eyebrowStyle}>CONNECTED REPOSITORY</div>

            <h3 style={{ margin: "8px 0" }}>
              {selectedRepo?.external_id}
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3,1fr)",
                gap: 12,
                marginTop: 18,
              }}
            >
              <MiniStat label="Provider" value="GitHub" />

              <MiniStat
                label="Branch"
                value={selectedRepo?.default_branch || "main"}
              />

              <MiniStat
                label="Pull requests"
                value={
                  pullRequests.filter(
                    (pr) => pr.repository_id === selectedRepo?.id,
                  ).length
                }
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div
      style={{
        padding: 13,
        borderRadius: 10,
        background: "#0c111d",
        border: `1px solid ${COLORS.border}`,
      }}
    >
      <div style={{ color: COLORS.muted, fontSize: 10 }}>
        {label}
      </div>

      <div
        style={{
          fontWeight: 750,
          marginTop: 6,
        }}
      >
        {value}
      </div>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(getStoredUser());
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [repositories, setRepositories] = useState([]);
  const [pullRequests, setPullRequests] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [selectedReview, setSelectedReview] = useState(null);
  const [selectedFindings, setSelectedFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const pageTitles = {
    dashboard: "Review overview",
    projects: "Projects",
    pulls: "Pull requests",
    reviews: "Reviews",
    github: "GitHub",
    "review-detail": "Review details",
  };

  async function loadWorkspace(showSpinner = true) {
    if (!getToken()) {
      return;
    }

    if (showSpinner) {
      setLoading(true);
    }

    setError("");

    try {
      const [dashboardData, organizationData] = await Promise.all([
        getDashboardSummary(),
        getOrganizations(),
      ]);

      const projectResults = await Promise.all(
        organizationData.map((organization) =>
          getProjects(organization.id),
        ),
      );

      const allProjects = projectResults.flat();

      const repositoryResults = await Promise.all(
        allProjects.map((project) => getRepositories(project.id)),
      );

      const allRepositories = repositoryResults.flat();

      const pullRequestResults = await Promise.all(
        allRepositories.map((repository) =>
          getPullRequests(repository.id),
        ),
      );

      const allPullRequests = pullRequestResults.flat();

      const reviewResults = await Promise.all(
        allPullRequests.map((pullRequest) =>
          getReviews(pullRequest.id),
        ),
      );

      const allReviews = reviewResults.flat();

      setDashboard(dashboardData);
      setProjects(allProjects);
      setRepositories(allRepositories);
      setPullRequests(allPullRequests);
      setReviews(allReviews);
    } catch (err) {
      setError(err.message || "Unable to load workspace.");
    } finally {
      setLoading(false);
    }
  }

  async function refreshWorkspace() {
    setRefreshing(true);

    try {
      await loadWorkspace(false);
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    if (user) {
      // Workspace loading updates async request state intentionally.
      // eslint-disable-next-line react/set-state-in-effect
      void loadWorkspace();
    }
  }, [user]);

  async function selectReview(reviewId) {
    try {
      const [reviewData, findingData] = await Promise.all([
        getReview(reviewId),
        getFindings(reviewId),
      ]);

      setSelectedReview(reviewData);
      setSelectedFindings(findingData);
      setCurrentPage("review-detail");
    } catch (err) {
      setError(err.message || "Unable to load review details.");
    }
  }

  function openPullRequestReviews(pullRequestId) {
    setCurrentPage("reviews");

    const prReviews = reviews.filter(
      (review) => review.pull_request_id === pullRequestId,
    );

    if (prReviews.length === 1) {
      void selectReview(prReviews[0].id);
    }
  }

  if (!user) {
    return (
      <LoginScreen
        onLogin={() => {
          setUser(getStoredUser());
        }}
      />
    );
  }

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: COLORS.background,
          color: COLORS.text,
          display: "grid",
          placeItems: "center",
        }}
      >
        Loading DevFlow workspace...
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: COLORS.background,
        color: COLORS.text,
      }}
    >
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        user={user}
      />

      <main
        style={{
          marginLeft: 240,
          minHeight: "100vh",
          padding: "34px 36px 60px",
        }}
      >
        <Topbar
          title={pageTitles[currentPage]}
          user={user}
          onRefresh={refreshWorkspace}
          onSignOut={() => {
            logout();
            setUser(null);
          }}
          refreshing={refreshing}
        />

        {error && (
          <div
            style={{
              marginBottom: 18,
              padding: 13,
              borderRadius: 12,
              background: "rgba(255,102,125,.08)",
              border: "1px solid rgba(255,102,125,.2)",
              color: "#ff9cad",
              fontSize: 13,
            }}
          >
            {error}
          </div>
        )}

        {currentPage === "dashboard" && (
          <DashboardPage
            dashboard={dashboard}
            onSelectReview={selectReview}
          />
        )}

        {currentPage === "projects" && (
          <ProjectsPage
            projects={projects}
            repositories={repositories}
          />
        )}

        {currentPage === "pulls" && (
          <PullRequestsPage
            pullRequests={pullRequests}
            repositories={repositories}
            onOpenReviews={openPullRequestReviews}
          />
        )}

        {currentPage === "reviews" && (
          <ReviewsPage
            reviews={reviews}
            pullRequests={pullRequests}
            onSelectReview={selectReview}
          />
        )}

        {currentPage === "review-detail" && (
          <ReviewDetail
            review={selectedReview}
            findings={selectedFindings}
            onBack={() => setCurrentPage("reviews")}
          />
        )}

        {currentPage === "github" && (
          <GithubPage
            repositories={repositories}
            pullRequests={pullRequests}
            onReviewComplete={refreshWorkspace}
          />
        )}
      </main>
    </div>
  );
}

const cardStyle = {
  background: COLORS.panel,
  border: `1px solid ${COLORS.border}`,
  borderRadius: 16,
  padding: 20,
};

const heroStyle = {
  background:
    "radial-gradient(circle at 85% 50%, rgba(108,92,255,.18), transparent 30%), #11172b",
  border: "1px solid rgba(108,92,255,.3)",
  borderRadius: 18,
  padding: 30,
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 24,
};

const eyebrowStyle = {
  color: "#7f76ff",
  fontSize: 10,
  letterSpacing: 2,
  fontWeight: 800,
};

const pageIntroStyle = {
  marginBottom: 22,
};

const pageTitleStyle = {
  fontSize: 30,
  margin: "8px 0",
};

const pageTextStyle = {
  color: COLORS.muted,
  lineHeight: 1.7,
  maxWidth: 700,
};

const labelStyle = {
  display: "block",
  color: COLORS.text,
  fontSize: 12,
  fontWeight: 750,
  marginBottom: 8,
};

const inputStyle = {
  width: "100%",
  boxSizing: "border-box",
  padding: "12px 13px",
  borderRadius: 10,
  border: `1px solid ${COLORS.border}`,
  outline: "none",
  background: "#0b101b",
  color: COLORS.text,
  fontSize: 13,
};

const buttonStyle = {
  border: "none",
  borderRadius: 10,
  padding: "11px 16px",
  background: COLORS.accent,
  color: "white",
  fontWeight: 800,
  cursor: "pointer",
};

const secondaryButtonStyle = {
  border: `1px solid ${COLORS.border}`,
  borderRadius: 10,
  padding: "10px 14px",
  background: COLORS.panel,
  color: COLORS.text,
  fontWeight: 700,
  cursor: "pointer",
};
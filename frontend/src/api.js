const API_BASE = "/api/v1";

async function readResponse(response) {
  const text = await response.text();

  if (!text) {
    throw new Error(`Server returned an empty response (HTTP ${response.status}).`);
  }

  let data;

  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Server returned an invalid response (HTTP ${response.status}).`);
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (HTTP ${response.status}).`,
    );
  }

  return data;
}

async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout();
    throw new Error("Your session has expired. Please sign in again.");
  }

  return readResponse(response);
}

export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  if (!data.access_token) {
    throw new Error("Login succeeded but no access token was returned.");
  }

  localStorage.setItem("devflow_token", data.access_token);
  localStorage.setItem("devflow_user", JSON.stringify(data.user));

  return data;
}

export function logout() {
  localStorage.removeItem("devflow_token");
  localStorage.removeItem("devflow_user");
}

export function getToken() {
  return localStorage.getItem("devflow_token");
}

export function getStoredUser() {
  const value = localStorage.getItem("devflow_user");

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

export async function getDashboardSummary() {
  return request("/dashboard/summary");
}

export async function getOrganizations() {
  return request("/organizations");
}

export async function getProjects(organizationId) {
  return request(`/projects/organizations/${organizationId}`);
}

export async function getRepositories(projectId) {
  return request(`/projects/${projectId}/repositories`);
}

export async function getPullRequests(repositoryId) {
  return request(`/repositories/${repositoryId}/pull-requests`);
}

export async function getPullRequest(pullRequestId) {
  return request(`/pull-requests/${pullRequestId}`);
}

export async function getReviews(pullRequestId) {
  return request(`/pull-requests/${pullRequestId}/reviews`);
}

export async function getReview(reviewId) {
  return request(`/code-reviews/${reviewId}`);
}

export async function getFindings(reviewId) {
  return request(`/code-reviews/${reviewId}/findings`);
}

export async function runGithubReview(owner, repository, pullNumber) {
  return request("/github/pull-request-review", {
    method: "POST",
    body: JSON.stringify({
      owner,
      repository,
      pull_number: Number(pullNumber),
    }),
  });
}
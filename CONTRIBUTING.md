📌 Contribution Guidelines

This project follows Conventional Commits (PR-title based) to ensure:

clean Git history

automated semantic versioning

reliable CI/CD and DevSecOps workflows

All pull requests must follow the rules below.

🔀 Branching Strategy

We use a promotion-based workflow:

feature/* → dev → qa → main


feature/*: feature development or fixes

dev: integration branch

qa: stabilisation and testing

main: release-ready code (protected)

All changes must be merged via Pull Requests.

🧩 Pull Request Title Convention (Required)

Every Pull Request title must start with one of the prefixes below, followed by a short, clear description.

Format
<prefix>: <short description>


Example:

feat: add authenticated file download endpoint


PRs that do not follow this format will be blocked by CI.

🏷️ Allowed Prefixes & Their Meanings
🚀 feat: — New feature (MINOR version bump)

Use when introducing new functionality that users can see or use.

Examples:

feat: add file upload validation

feat: implement dashboard file listing

🐛 fix: — Bug fix (PATCH version bump)

Use when fixing incorrect or broken behaviour.

Examples:

fix: return 404 for non-owned file access

fix: prevent upload without authentication

💥 feat!: — Breaking change (MAJOR version bump)

Use when a change breaks existing behaviour or contracts.

Examples:

feat!: change JWT payload structure

feat!: remove legacy auth headers

🧹 chore: — Maintenance / housekeeping (NO version bump)

Use for changes that do not affect runtime behaviour.

Examples:

chore: update CI workflow

chore: refactor folder structure

chore: update Docker base image

📚 docs: — Documentation only (NO version bump)

Use for README updates, comments, or documentation changes.

Examples:

docs: update setup instructions

docs: clarify testing strategy

🧪 test: — Tests only (NO version bump)

Use when adding or modifying tests without changing functionality.

Examples:

test: add dashboard ownership tests

test: improve auth-service coverage

🔧 refactor: — Code restructuring (NO functional change)

Use when improving code structure without changing behaviour.

Examples:

refactor: simplify file service query logic

refactor: extract auth middleware

⚡ perf: — Performance improvements

Use when improving performance without changing functionality.

Examples:

perf: optimise file metadata query

perf: reduce unnecessary DB calls

🤖 ci: — CI/CD & DevOps changes

Use for pipeline, automation, or workflow changes.

Examples:

ci: add pr title lint workflow

ci: enable docker image signing

🏗️ build: — Build system & dependencies

Use for dependency or build configuration changes.

Examples:

build: update python dependencies

build: adjust docker build context

🚫 What NOT to do

❌ Bad PR titles:

Update files
Fix bug
Changes
Final version


✅ Good PR titles:

fix: prevent unauthenticated file download
chore: update github actions workflow
feat!: migrate to JWT-only authentication

🔒 Enforcement

PR title format is automatically enforced via GitHub Actions

PRs that do not comply cannot be merged

main branch is protected and requires:

PR approval

resolved conversations

passing CI checks

🧠 Why this matters

Following these rules allows us to:

automate semantic versioning

generate release notes automatically

publish signed and scanned Docker images

maintain a clean, auditable history

This is industry-standard DevSecOps practice.
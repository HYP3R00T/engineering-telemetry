# Developer Resources

Reference links for the tools and standards used in this repository.

Use this page as a starting point when you need official docs, best practices, or setup
guidance. The sections are ordered by **scope of responsibility** — from the widest
(project-level governance) to the most specific (AI augmentation). A new contributor
should be able to read this top-to-bottom and understand not just *what* the tools are,
but *why they exist and where they fit*.

## Open Source Governance

Defines how humans interact with the project — before any code is written or any tool
is installed. These documents establish the social contract, contribution rules, and
legal standing of the project.

**Purpose:** Legitimacy, contribution clarity, and compliance.

- **License:**
  Project license terms and usage permissions.
    - [choosealicense.com](https://choosealicense.com/)

- **Contributing Guide:**
  Contributor workflow, expectations, and process guidance.
    - CONTRIBUTING.md (in repo root)

- **Code of Conduct:**
  Community behavior and collaboration standards.
    - [contributor-covenant.org](https://www.contributor-covenant.org/)

- **Security Policy:**
  Vulnerability reporting and security handling policy.
    - SECURITY.md (in repo root)

> **Heuristic:** If someone needs to decide whether to *use or contribute to* this project, they read this section first.

## Repository Conventions

Language-agnostic rules that every file, editor, and collaborator must follow. These
are configuration files checked into the repository — a contributor can read and follow
them without running anything.

**Purpose:** Consistency across editors, operating systems, and contributors.

- **Git Ignore:**
  Rules for excluding local or generated files from Git tracking.
    - [git-scm.com/docs/gitignore](https://git-scm.com/docs/gitignore)
    - [github/gitignore templates](https://github.com/github/gitignore)

- **Git Attributes:**
  File handling rules for diff, merge, and line-ending behavior.
    - [git-scm.com/docs/gitattributes](https://git-scm.com/docs/gitattributes)
    - [gitattributes/gitattributes](https://github.com/gitattributes/gitattributes)

- **EditorConfig:**
  Cross-editor formatting and whitespace consistency.
    - [editorconfig.org](https://editorconfig.org)

- **CommonMark:**
  Markdown syntax specification reference.
    - [commonmark.org](https://commonmark.org)

> **Heuristic:** If you switched from Python to Go tomorrow, these conventions would still apply unchanged.

## Development Environment

How you get a working machine, regardless of language. These are infrastructure-level
tools that exist before any language runtime is considered.

**Purpose:** Reproducible, portable development environments for every contributor.

- **Docker:**
  Container runtime used by development environments.
    - [docker.com](https://www.docker.com)

- **Dev Containers:**
  Reproducible development environments for this project.
    - [containers.dev](https://containers.dev)

- **mise (toolchain manager):**
  Toolchain/version manager and task runner for local development.
    - [mise.jdx.dev](https://mise.jdx.dev)

> **Heuristic:** These tools run before your language is even selected. They are infrastructure, not runtime.

## Language and Runtime

Everything tied to a specific language — how code runs, how dependencies are managed,
and how the environment is isolated. Subsectioned by language so this scales cleanly
when new runtimes are added.

**Purpose:** Define how code runs and how the language environment is managed.

> **Heuristic:** If you removed this language from the project, the entire section disappears with it.

### Python

- **Python:**
  Core language runtime and standard library reference.
    - [docs.python.org](https://docs.python.org/3)

- **uv (dependency and env management):**
  Dependency management and virtual environment workflow.
    - [docs.astral.sh/uv](https://docs.astral.sh/uv)

## Code Quality

Everything that enforces correctness — statically (before running) and dynamically
(at runtime via tests). Split into two sub-concerns: static analysis and test coverage.

**Purpose:** Ensure the codebase behaves correctly and meets defined standards.

### Static Analysis

Catches errors, style violations, and type inconsistencies without running the code.

- **Ruff (linting and formatting):**
  Python linting and formatting checks.
    - [docs.astral.sh/ruff](https://docs.astral.sh/ruff)

- **ty (type checker):**
  Static type checking for Python code.
    - [github.com/astral-sh/ty](https://github.com/astral-sh/ty)

- **ShellCheck (shell script linting):**
  Static analysis for shell scripts.
    - [www.shellcheck.net](https://www.shellcheck.net)

- **Rumdl (Markdown linting):**
  Markdown linting and style checks.
    - [rumdl.dev](https://rumdl.dev/)

### Testing

Validates that the system behaves as expected at runtime.

- **pytest:**
  Test runner and assertion framework.
    - [docs.pytest.org](https://docs.pytest.org)

- **pytest-cov:**
  Coverage reporting integration for pytest.
    - [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io)

> **Heuristic:** Static analysis catches *incorrect code*. Tests catch *incorrect behavior*. Keep them conceptually separate even when they share a CI step.

## Commit Workflow

What happens between `git add` and `git push`. These are executable tools — distinct
from the configuration files in Repository Conventions — and are the most common source
of contributor friction when not documented clearly.

**Purpose:** Ensure all changes are consistent, reviewable, and policy-compliant before
entering the codebase.

- **pre-commit (hook framework):**
  Framework for running checks in Git hooks.
    - [pre-commit.com](https://pre-commit.com)

- **prek (hook installer/runner):**
  Hook installer and runner used by this template.
    - [prek.j178.dev](https://prek.j178.dev/)

- **Commitizen (commit message standards):**
  Conventional commit message tooling.
    - [commitizen-tools.github.io/commitizen](https://commitizen-tools.github.io/commitizen)

- **Gitleaks (secret scanning):**
  Detects accidental secret exposure in commits.
    - [gitleaks.io](https://gitleaks.io)

> **Heuristic:** If a tool runs automatically on `git commit`, it belongs here — not in CI/CD.

## CI/CD and Automation

The execution layer that turns local rules into automated, repeatable pipelines. These
tools run *after* the commit leaves your machine.

**Purpose:** Automate quality checks, builds, releases, and deployments consistently
across environments.

- **GitHub Actions:**
  CI/CD workflow platform used in this repository.
    - [docs.github.com/actions](https://docs.github.com/actions)

- **checkout action:**
  Checks out repository code in workflow jobs.
    - [github.com/actions/checkout](https://github.com/actions/checkout)

- **setup-uv action:**
  Installs uv in GitHub Actions workflows.
    - [github.com/astral-sh/setup-uv](https://github.com/astral-sh/setup-uv)

- **configure-pages action:**
  Configures GitHub Pages deployment environment.
    - [github.com/actions/configure-pages](https://github.com/actions/configure-pages)

- **deploy-pages action:**
  Deploys built docs/site artifacts to GitHub Pages.
    - [github.com/actions/deploy-pages](https://github.com/actions/deploy-pages)

- **upload-pages-artifact action:**
  Uploads build artifacts for Pages deployment.
    - [github.com/actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact)

> **Heuristic:** If it runs in a pipeline triggered by a push or PR, it belongs here.

## Documentation

How the project explains itself — how knowledge is written, structured, and published
for contributors and users.

**Purpose:** Make the project understandable and teachable, both now and as it grows.

- **Zensical (docs site generation):**
  Static documentation site generator used by this repository.
    - [zensical.org/docs](https://zensical.org/docs)

> **Future additions:** Architecture Decision Records (ADRs), design docs, API references.

## AI and Agent Ecosystem

A first-class layer for tools that augment development with machine intelligence.
This project follows an **agent-agnostic, standards-first** approach so workflows can
work across different assistants and platforms over time.

**Purpose:** Augment development workflows with AI assistance and programmable agent
capabilities.

> **Heuristic:** Prefer open standards first, then vendor-specific implementations.

### Core Standards

These standards define interoperability and reusable behavior across tooling.

- **Agents.md:**
  Agent behavior and repository interaction conventions.
    - [agents.md](https://agents.md/)

- **AgentSkills:**
  Reusable, composable skill definitions for agents.
    - [agentskills.io/home](https://agentskills.io/home)

- **Model Context Protocol (MCP):**
  Open protocol for tool and context interoperability.
    - [modelcontextprotocol.io](https://modelcontextprotocol.io)

## Keeping This Current

- Add a tool as soon as it appears in a project config or workflow.
- Remove tools that are no longer active — stale links erode trust.
- Prefer official documentation over blog posts or tutorials.
- Keep descriptions short and practical — link to the details, don't duplicate them.
- If a language is added, create a new subsection under **Language and Runtime**
  before adding anything else.

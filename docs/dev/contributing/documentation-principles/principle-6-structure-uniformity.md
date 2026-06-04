# Principle 6: Documentation structure uniformity

Consistency in structure helps readers navigate confidently and maintainers scale without confusion.

## File Naming

Use lowercase with hyphens only.

**DO:**

- `layer-1-docker.md`
- `bump-api.md`
- `environment-variables-guide.md`

**DON'T:**

- `Layer1Docker.md`
- `BumpApi.md`
- `Environment_Variables.md`

## Folder Structure

Every folder with 2 or more docs needs an `index.md` as a navigation hub. Single-document folders should flatten to the parent directory.

`index.md` should:

- List all documents in the folder with one-line descriptions
- Be the entry point for readers discovering the folder
- Use consistent naming (`index.md`, not `README.md`)

## Document Structure

Every document must:

- Start with `# Title` matching the navigation label in `zensical.toml`
- Begin with a sentence establishing context and relationship to the system
- Use standard sections in this order:
  1. Purpose or Overview
  2. How It Works
  3. Steps or Configuration
  4. Key Concepts
  5. Examples (optional)
  6. Permissions or Requirements
  7. Next Steps or Related Documents

## Documentation Location

All documentation belongs in `docs/` following its existing folder structure.

Use folders that actually exist in the repository, and only introduce new top-level domains when content growth requires them.

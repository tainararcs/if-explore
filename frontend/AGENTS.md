# AGENTS.md

## 1. Scope and source of guidance

These instructions apply to the current frontend project directory. The project uses Vue 3,
TypeScript, Vite, and Node.js 24.22.0. The current styling is CSS; do not assume
adoption of other libraries without checking the repository configuration.

Use [docs/project-guidelines.md](docs/project-guidelines.md) as the source for
organization and architecture conventions. This file summarizes the operational
rules to follow while working.

## 2. Mandatory rules

1. Preserve the existing TypeScript, lint, build, and security configuration.
2. Do not use `any`, `@ts-ignore`, or unsafe assertions to bypass errors.
3. Keep functions, components, composables, and modules cohesive, with clear
   responsibilities.
4. Prefer feature-oriented organization and do not create directories, layers, or
   abstractions without a concrete need.
5. Keep business logic and presentation separate when this improves clarity or
   testability.
6. Do not duplicate code between a feature and shared directories.
7. Do not introduce dependencies without a clear technical justification that
   fits the current configuration.
8. Do not assume a library mentioned in documentation is installed or configured;
   check `package.json`, scripts, and configuration files.
9. Preserve existing behavior unless a change is requested.
10. Treat external data as untrusted and do not expose secrets.

## 3. Working in the repository

Before implementing:

1. Read this file and `docs/project-guidelines.md`.
2. Inspect the structure, relevant files, dependencies, and scripts.
3. Look for existing components, composables, services, and utilities that can be
   reused.
4. Choose the smallest complete change that satisfies the requirement.

During implementation:

- Make focused changes and preserve unrelated work.
- Follow patterns already used in the repository.
- Write components as Single-File Components (`.vue`) using the Composition API
  with `<script setup lang="ts">`.
- Use ordinary TypeScript functions for logic that does not need Vue reactivity.
- Use composables only for reactive state, watchers, lifecycle hooks,
  `provide`/`inject`, subscriptions, or other cohesive behavior tied to Vue's
  reactivity system or component lifecycle.
- Prefer `computed` for derived values. Avoid unnecessary watchers, synchronized
  derived state, and premature optimization.
- Use semantic HTML and accessible patterns.
- Use English for code identifiers, variable names, function names, class names,
  and file names.
- Document public contracts, components, composables, and non-obvious logic with
  TSDoc in Brazilian Portuguese (`pt-BR`). Write explanatory code comments in
  Brazilian Portuguese as well. Do not add comments for trivial callbacks or
  self-explanatory code.

Before completing:

1. Review the diff for unnecessary complexity or out-of-scope changes.
2. Run applicable checks, such as `npm run lint`, `npm run typecheck`, and
   `npm run build`.
3. Clearly report checks that ran, failed, do not exist, or could not be run.
4. Update documentation when an established convention changes.

Never claim that a command, test, or verification passed unless it was run.

## 4. Internationalization, security, and dependencies

- Use the internationalization solution configured in the project when one exists.
- Do not introduce hardcoded text in new interfaces when a translation solution
  is configured.
- Validate external data at appropriate boundaries.
- Do not use `v-html` or other unsafe HTML rendering without a specific
  justification.
- Remember that Vite variables prefixed with `VITE_` are exposed to the client.
- Do not weaken compiler, lint, or security settings to make an implementation
  pass.

## 5. Definition of done

An implementation is complete when it:

- satisfies the requested requirement;
- preserves types, module boundaries, and project conventions;
- introduces no unjustified abstractions or dependencies;
- includes proportional documentation when needed;
- passes applicable checks, or reports their limitations;
- contains no unrelated changes.

Detailed conventions for directories, models, services, components, views,
composables, routing, and `lib` are defined in `docs/project-guidelines.md`.
Avoid duplicating rules between the two files: this file governs agent
procedure, while the guidelines define detailed technical conventions.

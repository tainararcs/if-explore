# AGENTS.md

## 1. Project Overview

This project uses React, TypeScript, Vite, Tailwind CSS, and Node.js 24.22.0.

The codebase must prioritize type safety, modularity, maintainability, documentation, accessibility, and simplicity.

Detailed architectural and implementation conventions are defined in `docs/project-guidelines.md`.

## 2. Mandatory Rules

The following rules are mandatory for all implementations:

1. **Type safety:** Use strict TypeScript. Do not use `any`, `@ts-ignore`, or unsafe type assertions to bypass compiler errors.
2. **Documentation:** Every function, method, custom hook, and React component must have TSDoc documentation in Brazilian Portuguese (`pt-BR`), following the project's documentation conventions.
3. **Single responsibility:** Every function, method, component, and module must have a clear, well-defined purpose.
4. **SOLID principles:** Consider and apply SOLID principles where relevant, without introducing unnecessary abstractions or complexity.
5. **Modularity:** Keep related functionality together and maintain clear module boundaries.
6. **Internationalization:** All user-facing text must use the project's internationalization mechanism. Only `pt-BR` is implemented initially.
7. **Code quality:** Follow existing conventions, avoid duplication, and prefer readable, maintainable solutions.
8. **Security:** Treat external data as untrusted and never expose secrets or sensitive information.
9. **Verification:** Run applicable type checks, lint, tests, and production builds before considering a task complete.
10. **Documentation consistency:** Update project documentation whenever an established architectural convention or implementation rule changes.

## 3. Architecture and Implementation

- Follow the modular architecture described in `docs/project-guidelines.md`.
- Keep business logic separate from presentation when doing so improves clarity and testability.
- Prefer small, cohesive functions and components with explicit responsibilities.
- Avoid unnecessary coupling, circular dependencies, duplicated state, and premature abstractions.
- Reuse existing components, utilities, hooks, and dependencies when appropriate.
- Do not introduce new dependencies without a clear technical justification.
- Do not create abstractions solely to comply superficially with SOLID principles.
- Preserve existing behavior unless a change is explicitly requested.

## 4. TypeScript and React

- Preserve strict compiler settings and existing quality checks.
- Define explicit types for public module contracts, component props, function parameters, and return values when required for clarity and safety.
- Use `unknown` and runtime validation when handling untrusted data.
- Prefer type inference for straightforward local variables.
- Use function components and React hooks.
- Avoid unnecessary effects, redundant state, and premature memoization.
- Use semantic HTML and accessible interaction patterns.
- Never suppress type or lint errors without a documented, justified reason.

## 5. Componentization and Reusability

- Build reusable React components when UI patterns, behavior, or responsibilities are shared across the application.
- Before creating a new component, inspect existing components and determine whether they can be reused or extended without compromising their responsibilities.
- Keep components focused on a single, well-defined purpose, following the Single Responsibility Principle.
- Separate reusable, business-agnostic UI components from feature-specific components.
- Place shared UI components under `src/components/ui/` and feature-specific components within their respective feature modules.
- Prefer composition and explicit props over duplicated markup or components with excessive configuration options.
- Extract repeated UI patterns into reusable components when doing so improves consistency, maintainability, or testability.
- Avoid premature componentization: do not create abstractions for isolated, trivial markup without a concrete reuse or clarity benefit.
- Define and document component props using TypeScript, ensuring that their contracts are explicit and type-safe.
- Keep styling consistent with the project's Tailwind CSS conventions and shared design tokens.
- When modifying a shared component, evaluate the impact on all its consumers and update relevant tests.
- Every React component must include TSDoc documentation describing its purpose and intended use.

## 6. Documentation Requirements

All functions, methods, custom hooks, and React components must include TSDoc documentation written in Brazilian Portuguese.

Documentation must:

- Explain the purpose and responsibilities of the documented unit.
- Describe parameters using `@param`.
- Describe return values using `@returns` when applicable.
- Describe relevant exceptions or failure conditions when applicable.
- Document component props and custom hook return contracts when needed.
- Remain consistent with the actual implementation.

Keep documentation concise and proportional to complexity. Do not add redundant inline comments that merely repeat the code.

Types and interfaces must also be documented when they represent meaningful domain concepts or non-obvious contracts.

## 7. Internationalization

- Use the project's configured internationalization library and conventions.
- Implement only Brazilian Portuguese (`pt-BR`) initially.
- Do not hardcode user-facing text in components, hooks, or business logic.
- Keep translation resources organized and typed whenever supported by the chosen library.
- Avoid duplicating translations and keep translation keys descriptive and consistent.
- Do not introduce additional implemented languages unless explicitly requested.

## 8. Security and Configuration

- Never commit secrets, credentials, tokens, or private environment files.
- Remember that Vite variables prefixed with `VITE_` are exposed to client-side code.
- Validate external data at appropriate boundaries.
- Avoid unsafe HTML rendering and other unnecessary security risks.
- Do not weaken compiler, lint, or security settings to make an implementation pass.

## 9. Agent Workflow

Before implementing a task:

1. Read this file and consult `docs/project-guidelines.md` when available.
2. Inspect the relevant code, existing conventions, dependencies, and package scripts.
3. Identify the smallest complete change that satisfies the requirement.

During implementation:

- Make focused, incremental changes.
- Preserve unrelated code and user modifications.
- Prefer existing project conventions over introducing new ones.
- Add or update tests for meaningful behavior changes.
- Update documentation when necessary.

Before completing a task:

1. Review the diff for correctness, unnecessary complexity, and unrelated changes.
2. Run applicable type checks, lint, tests, and production builds.
3. Report which checks passed, failed, or could not be executed.
4. Explicitly disclose relevant limitations and unverified behavior.

Never claim that a command, test, or verification succeeded unless it actually ran and passed.

## 10. Definition of Done

A task is complete only when:

- The requested behavior is implemented.
- TypeScript and project conventions are respected.
- Required TSDoc documentation is present and accurate.
- Relevant tests and quality checks pass, or execution limitations are reported.
- No unrelated changes, accidental secrets, or unjustified suppressions are introduced.
- Relevant documentation is updated.

## 11. Source of Truth

`docs/project-guidelines.md` defines the detailed architecture, module organization, coding conventions, documentation examples, testing strategy, and internationalization implementation.

When a task conflicts with an established convention, identify the conflict and resolve it explicitly rather than silently weakening the project's rules.

Follow tool-specific instruction files only as entry points or adapters to these shared rules. Avoid maintaining conflicting copies of project conventions.
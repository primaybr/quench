# Hallucination Catalog

Taxonomy of common AI failure modes, phantom APIs, fabricated flags, and memory drift traps.

---

## 1. Phantom APIs (Non-Existent Methods on Real Libraries)

Definition: Inventing method names that sound plausible for a library or class, but do not exist in the actual library.

Common Examples:
- Pandas: Calling `df.apply_complex_filter(...)` instead of `df.query(...)` or boolean indexing.
- Node.js `fs`: Calling `fs.readJSONSync(...)` (which only exists in `fs-extra`, not the native `node:fs` module).
- Python Requests / Urllib: Calling `urllib.request.urlopen(...).json()` (response is an HTTPResponse, not a JSON object).
- AWS SDK: Calling `s3_client.upload_file_from_string(...)` instead of `s3_client.put_object(Body=...)`.

Mitigation:
- Check library source or official documentation before invoking non-core helper methods.
- If unsure whether a convenience method exists, use primitive standard operations (e.g. read bytes then parse JSON).

---

## 2. Fabricated CLI Flags (Non-Existent Command Options)

Definition: Inventing command-line switches or arguments based on intuitive natural language rather than actual command specifications.

Common Examples:
- Git: Calling `git commit --message-all` or `git checkout --create` instead of `git commit -a -m` or `git checkout -b`.
- Docker: Calling `docker run --clean` or `docker build --no-intermediate` instead of `--rm` or `--no-cache`.
- Package Managers: Calling `npm install --skip-dev` or `pip install --no-deps-update` instead of `--omit=dev` or `--no-deps`.

Mitigation:
- Run `<cmd> --help` or inspect man pages before proposing multi-flag command invocations.
- Restrict generated commands to standard, widely documented flags.

---

## 3. Memory Drift Traps (Context Decay and Constraint Amnesia)

Definition: Forgetting earlier user constraints, file modifications, or project conventions mid-session and reverting to default habits.

Common Examples:
- Language/Runtime Reversion: Switching to asynchronous syntax after being told the environment is synchronous Python 3.8.
- Naming Drift: Renaming an endpoint from `/api/v2/items` to `/v2/items` between earlier and later edits in the same conversation.
- Framework Reversion: Using React class components in a project that strictly uses functional components and hooks.

Mitigation:
- Re-read recent conversation turns and existing files before outputting new code.
- Maintain an explicit mental register of project constraints (runtime version, framework style, naming conventions).

---

## 4. Plausible-Sounding Methods (Semantic Guessing)

Definition: Generating a method name that intuitively describes the desired action instead of looking up the real method name.

Common Examples:
- Object Serialization: Calling `obj.to_json()` when the class defines `obj.json()` (Pydantic v1) or `obj.model_dump_json()` (Pydantic v2).
- String Manipulation: Calling `str.trim()` in Python (where it is `str.strip()`), or `str.strip()` in JavaScript (where it is `str.trim()`).
- Database ORMs: Calling `db.delete_all()` when the ORM specifies `db.query(...).delete()`.

Mitigation:
- Never guess method names across languages or libraries.
- Verify the class definition or inspect typings before composing calls.

---

## 5. Version Conflation (Cross-Version Bleed)

Definition: Mixing syntax, methods, or configurations from different versions of the same ecosystem within a single file.

Common Examples:
- React: Using `useEffect` inside a class component lifecycle, or importing `Switch` from `react-router-dom` v6 (which replaced it with `Routes`).
- Python: Using union type syntax `str | int` in a project configured for Python 3.9 without `from __future__ import annotations`.
- Java / Spring: Mixing Spring Boot 2.x properties with Spring Boot 3.x Jakarta imports.

Mitigation:
- Check package manifests (`package.json`, `pom.xml`, `pyproject.toml`) to determine exact major/minor versions.
- Adhere strictly to the API contract of the target version.

---

## 6. Invented Configuration Schemas

Definition: Creating configuration keys or environment variable names based on intuition rather than verified schema definitions.

Common Examples:
- Environment Variables: Referencing `DB_PORT` and `DB_HOST` when the application parser expects a single `DATABASE_URL` string.
- Linter / Formatter Configs: Inventing rule names in `eslint.config.js` or `pyproject.toml` [tool.ruff] that do not exist.
- CI/CD Configurations: Fabricating step parameters in GitHub Actions or GitLab CI workflows.

Mitigation:
- Read existing config files and sample templates in the workspace before adding or editing settings.
- Verify schema definitions against documentation when adding new configuration blocks.

---

## Self-Correction Protocol

When you recognize any pattern in this catalog during response generation:
1. Stop immediate output.
2. Identify the specific hallucination category.
3. Replace the speculative construct with a verified implementation or tool-read fact.
4. If unable to verify, declare the uncertainty explicitly using Inferred or Uncertain markers.

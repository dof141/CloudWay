# CloudWay Branding Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the public TripStar / 旅途星辰 brand with CloudWay / 云程 while preserving browser-storage keys, CSS selectors, logger identifiers, the local directory, and the upstream remote.

**Architecture:** Apply direct, explicit replacements in user-facing frontend content, backend metadata, deployment configuration, and documentation. Do not introduce a runtime branding abstraction. Validate structured files and use a repository-wide allowlist scan to ensure old-brand references remain only in compatibility identifiers and migration documents.

**Tech Stack:** Vue 3, TypeScript, Vue I18n, FastAPI, Python, Docker Compose, Markdown, Git.

---

### Task 1: Rebrand User-Facing Frontend Content

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/components/NavBar.vue`
- Modify: `frontend/src/views/Landing.vue`
- Modify: `frontend/src/views/Result.vue`
- Modify: `frontend/src/i18n/locales/zh.json`
- Modify: `frontend/src/i18n/locales/en.json`
- Modify: `frontend/src/i18n/locales/ja.json`

- [ ] **Step 1: Record a failing frontend brand scan**

Run:

```powershell
rg -n -i "TripStar|旅途星辰|github.com/1sdv/TripStar" frontend/index.html frontend/src/components/NavBar.vue frontend/src/views/Landing.vue frontend/src/views/Result.vue frontend/src/i18n/locales
```

Expected: matches appear in the page title, navbar, landing headline, export content, repository links, and locale text.

- [ ] **Step 2: Update document, navbar, and landing branding**

Apply these exact replacements:

```text
frontend/index.html
  <title>TripStar</title> -> <title>CloudWay</title>

frontend/src/components/NavBar.vue
  visible brand TripStar -> CloudWay
  https://github.com/1sdv/TripStar -> https://github.com/dof141/CloudWay

frontend/src/views/Landing.vue
  TRIPSTAR -> CLOUDWAY
```

Do not rename component classes such as `landing-brand`.

- [ ] **Step 3: Update result export branding and repository targets**

In `frontend/src/views/Result.vue`, replace only user-visible values:

```text
QR payload repository:
  https://github.com/1sdv/TripStar -> https://github.com/dof141/CloudWay

Export heading:
  TripStar -> CloudWay

Export repository text:
  https://github.com/1sdv/TripStar -> https://github.com/dof141/CloudWay
```

Keep `.tripstar-map-*` class names and `--tripstar-map-*` variables unchanged.

- [ ] **Step 4: Update Chinese locale branding**

In `frontend/src/i18n/locales/zh.json`, use this mapping:

```text
app.title: 云程
app.brand: 云程
app.subBrand: CloudWay - AI 旅行引擎
app.footerBrand: 云程
chat welcome speaker: 云程 AI
export footer: 由 云程 CloudWay - AI 旅行引擎 生成
```

Replace every remaining user-visible `旅途星辰` or `TripStar` occurrence in this locale with the corresponding new brand.

- [ ] **Step 5: Update English and Japanese locale branding**

In both `frontend/src/i18n/locales/en.json` and `frontend/src/i18n/locales/ja.json`:

```text
app.title: CloudWay
app.brand: CloudWay
app.subBrand: CloudWay - existing localized AI Travel Engine wording
app.footerBrand: CloudWay
chat welcome speaker: CloudWay AI
export footer brand: CloudWay
```

Preserve all non-brand translations.

- [ ] **Step 6: Validate locale JSON and frontend brand removal**

Run:

```powershell
@'
import json
from pathlib import Path
for path in sorted(Path('frontend/src/i18n/locales').glob('*.json')):
    json.loads(path.read_text(encoding='utf-8'))
print('Locale JSON validation passed')
'@ | python -

rg -n -i "TripStar|旅途星辰|github.com/1sdv/TripStar" frontend/index.html frontend/src/components/NavBar.vue frontend/src/views/Landing.vue frontend/src/views/Result.vue frontend/src/i18n/locales
```

Expected: JSON validation passes and the brand scan returns no matches. Internal `tripstar` CSS selectors are intentionally not included in this case-sensitive scan.

- [ ] **Step 7: Commit frontend branding**

```powershell
git add frontend/index.html frontend/src/components/NavBar.vue frontend/src/views/Landing.vue frontend/src/views/Result.vue frontend/src/i18n/locales/zh.json frontend/src/i18n/locales/en.json frontend/src/i18n/locales/ja.json
git commit -m "feat: rebrand frontend as CloudWay"
```

---

### Task 2: Rebrand Backend Metadata And Deployment Identifiers

**Files:**
- Modify: `backend/app/__init__.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/services/chat_service.py`
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Modify: `docker-compose.yaml`
- Modify: `start.sh`

- [ ] **Step 1: Record a failing runtime metadata scan**

Run:

```powershell
rg -n -i "TripStar|旅途星辰|helloagents-trip-planner|HelloAgents智能旅行助手" backend/app frontend/package.json frontend/package-lock.json docker-compose.yaml start.sh -g '!backend/app/services/xhs_sign/**'
```

Expected: matches appear in backend application metadata, assistant persona, package metadata, Docker identifiers, and startup output.

- [ ] **Step 2: Update backend public metadata**

Apply these exact values:

```python
# backend/app/config.py
app_name: str = "云程 AI 旅行助手"
```

```text
backend/app/__init__.py module description:
  云程 AI 旅行助手 - 后端应用

backend/app/services/chat_service.py assistant persona:
  云程 AI
```

Keep `tripstar.memory` unchanged.

- [ ] **Step 3: Update frontend package metadata**

Set the package name in both files:

```json
"name": "cloudway-frontend"
```

Update `frontend/package.json` and both root package-name locations in `frontend/package-lock.json` without changing dependency versions.

- [ ] **Step 4: Update Docker Compose identifiers**

Use these exact identifiers in `docker-compose.yaml`:

```yaml
services:
  cloudway:
    container_name: cloudway-app
    volumes:
      - cloudway_data:/app/backend/data

volumes:
  cloudway_data:
```

Keep ports, environment variables, build arguments, and mount destination unchanged.

- [ ] **Step 5: Update startup branding**

In `start.sh`, change the startup message to:

```bash
echo "🚀 启动云程 AI 旅行助手..."
```

Keep the Gunicorn module path and process settings unchanged.

- [ ] **Step 6: Validate structured metadata and Python syntax**

Run:

```powershell
@'
import ast
import json
from pathlib import Path

for path in sorted(Path('backend').rglob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

package = json.loads(Path('frontend/package.json').read_text(encoding='utf-8'))
lock = json.loads(Path('frontend/package-lock.json').read_text(encoding='utf-8'))
assert package['name'] == 'cloudway-frontend'
assert lock['name'] == 'cloudway-frontend'
assert lock['packages']['']['name'] == 'cloudway-frontend'
print('Backend syntax and package metadata validation passed')
'@ | python -

rg -n -i "TripStar|旅途星辰|helloagents-trip-planner|HelloAgents智能旅行助手" backend/app frontend/package.json frontend/package-lock.json docker-compose.yaml start.sh -g '!backend/app/services/xhs_sign/**'
```

Expected: validation passes. The scan may return only `tripstar.memory`, which is an approved compatibility identifier.

- [ ] **Step 7: Commit runtime and deployment branding**

```powershell
git add backend/app/__init__.py backend/app/config.py backend/app/services/chat_service.py frontend/package.json frontend/package-lock.json docker-compose.yaml start.sh
git commit -m "chore: rename runtime metadata to CloudWay"
```

---

### Task 3: Rebrand Multilingual Documentation

**Files:**
- Modify: `README.md`
- Modify: `README_en.md`
- Modify: `README_ja.md`

- [ ] **Step 1: Record a failing documentation brand scan**

Run:

```powershell
rg -n -i "TripStar|旅途星辰|1sdv/TripStar" README.md README_en.md README_ja.md
```

Expected: matches appear in titles, introductions, directory trees, repository links, Star History URLs, and acknowledgements.

- [ ] **Step 2: Update the Chinese README**

Apply this mapping throughout `README.md`:

```text
旅途星辰 -> 云程
TripStar -> CloudWay
TripStar/ directory root -> CloudWay/
1sdv/TripStar repository and Star History references -> dof141/CloudWay
```

Keep references to HelloAgents as framework attribution.

- [ ] **Step 3: Update the English README**

Apply this mapping throughout `README_en.md`:

```text
TripStar -> CloudWay
TripStar/ directory root -> CloudWay/
1sdv/TripStar repository and Star History references -> dof141/CloudWay
```

Remove or replace any old online-demo link label that presents TripStar as the current product name; do not invent a new deployment URL.

- [ ] **Step 4: Update the Japanese README**

Apply this mapping throughout `README_ja.md`:

```text
TripStar -> CloudWay
1sdv/TripStar repository references -> dof141/CloudWay
```

Preserve the existing Japanese prose outside brand substitutions.

- [ ] **Step 5: Validate documentation branding**

Run:

```powershell
rg -n -i "TripStar|旅途星辰|1sdv/TripStar" README.md README_en.md README_ja.md
```

Expected: no matches.

- [ ] **Step 6: Commit documentation branding**

```powershell
git add README.md README_en.md README_ja.md
git commit -m "docs: rename project to CloudWay"
```

---

### Task 4: Run Final Compatibility And Build Verification

**Files:**
- Verify: all modified files
- Preserve: `.idea/**`

- [ ] **Step 1: Verify compatibility identifiers remain present**

Run:

```powershell
rg -n "tripstar\.runtime|tripstar\.user_id|tripstar-locale|tripstar:runtime-settings-updated|tripstar-map|--tripstar-map|tripstar\.memory" frontend/src backend/app
```

Expected: all existing storage keys, event names, CSS identifiers, and logger identifier remain present.

- [ ] **Step 2: Scan for unauthorized old-brand references**

Run:

```powershell
rg -n -i "TripStar|旅途星辰" . -g '!backend/app/services/xhs_sign/**' -g '!docs/superpowers/**' -g '!.git/**' -g '!.idea/**'
```

Expected: matches are limited to approved lowercase compatibility identifiers such as `tripstar.runtime`, `tripstar-map`, and `tripstar.memory`; no user-visible `TripStar` or `旅途星辰` values remain.

- [ ] **Step 3: Run whitespace and source-format checks**

```powershell
git diff --check origin/main..HEAD

@'
import ast
import json
from pathlib import Path

for path in sorted(Path('backend').rglob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
for path in sorted(Path('frontend/src/i18n/locales').glob('*.json')):
    json.loads(path.read_text(encoding='utf-8'))
json.loads(Path('frontend/package.json').read_text(encoding='utf-8'))
json.loads(Path('frontend/package-lock.json').read_text(encoding='utf-8'))
print('Source-format checks passed')
'@ | python -
```

Expected: both commands exit successfully.

- [ ] **Step 4: Run the production frontend build**

Run without modifying the lock file:

```powershell
Set-Location frontend
npm install --package-lock=false --prefer-offline --no-audit --no-fund
npx vite build
Set-Location ..
```

Expected: Vite exits with code 0. Existing large-chunk and unresolved legacy asset warnings may remain.

- [ ] **Step 5: Remove generated verification directories**

Resolve and verify that both targets are inside the repository before deleting:

```powershell
$root = (Resolve-Path '.').Path
foreach ($relative in @('frontend\node_modules', 'frontend\dist')) {
  $target = [System.IO.Path]::GetFullPath((Join-Path $root $relative))
  if (-not $target.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Refusing to clean outside repository: $target"
  }
  if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
  }
}
```

- [ ] **Step 6: Confirm Git status excludes IDE files from project commits**

Run:

```powershell
git status --short --branch
git log --oneline origin/main..HEAD
```

Expected: only the user's pre-existing `.idea` state remains uncommitted; branding commits are listed ahead of `origin/main`.

- [ ] **Step 7: Push the completed branding migration**

```powershell
git push origin main
git ls-remote origin refs/heads/main
```

Expected: the remote `main` hash matches local `HEAD`.

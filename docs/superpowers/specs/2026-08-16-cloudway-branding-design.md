# CloudWay / 云程 Branding Migration Design

## Goal

Migrate the public product brand from `TripStar / 旅途星辰` to `CloudWay / 云程` across the user interface, multilingual copy, documentation, backend application metadata, frontend package metadata, and Docker deployment identifiers. Preserve internal identifiers that protect existing browser data and styling compatibility.

## Brand Standard

- English product name: `CloudWay`
- Chinese product name: `云程`
- Chinese product descriptions: `云程 AI 旅行助手` and `云程 AI 旅行引擎`
- English product description: `CloudWay - AI Travel Engine`
- Japanese product description: `CloudWay - AI Travel Engine`, localized using the existing Japanese wording
- Chinese assistant name: `云程 AI`
- English and Japanese assistant name: `CloudWay AI`
- Landing-page headline: `CLOUDWAY`
- Project repository: `https://github.com/dof141/CloudWay`

## Change Scope

### Frontend Presentation

- Change the browser document title.
- Change the landing-page headline and navigation brand.
- Update product names, subtitles, welcome messages, footer text, and export copy in Chinese, English, and Japanese locale files.
- Update branding, QR code target, and repository address in exported itinerary content.
- Point all user-visible GitHub links to `dof141/CloudWay`.

### Backend Presentation

- Change the FastAPI application name to `云程 AI 旅行助手`.
- Update the Chinese startup message in `start.sh`.
- Update public module descriptions that still use the old Chinese brand.
- Keep API paths, request schemas, and response schemas unchanged.

### Engineering And Deployment

- Rename the frontend package to `cloudway-frontend` and update the root package name in the lock file.
- Rename the Docker Compose service to `cloudway`.
- Rename the Docker container to `cloudway-app`.
- Rename the Docker volume to `cloudway_data` while keeping its container mount path unchanged.
- Change README directory-tree roots to `CloudWay/`.
- Update branding, repository references, and Star History URLs in the Chinese, English, and Japanese README files.

## Compatibility Boundary

The following internal identifiers must remain unchanged:

- `tripstar.runtime.*` local-storage keys.
- `tripstar.user_id` anonymous user identifier key.
- `tripstar-locale` locale key.
- `tripstar:runtime-settings-updated` browser event name.
- `.tripstar-*` CSS classes.
- `--tripstar-*` CSS variables.
- `tripstar.memory` backend logger name.
- Historical Git commit messages and content.
- The `upstream` remote pointing to `1sdv/TripStar`.
- The local workspace path `E:\WorkPace\AiAgent\TripStar`.

Keeping these identifiers prevents loss of saved API settings, map keys, locale state, anonymous memory identity, and existing style behavior.

## Implementation Strategy

Use direct and explicit replacement rather than adding a dynamic white-label configuration layer:

1. Update structured configuration and locale content.
2. Update hard-coded page branding and repository addresses.
3. Update backend metadata, Docker identifiers, and package metadata.
4. Update all README variants and perform a final repository-wide brand scan.

This migration does not add runtime brand configuration, redesign the logo, change the visual theme, or move the working directory.

## Acceptance Criteria

- User-facing UI, browser titles, assistant greetings, and exported content no longer show `TripStar` or `旅途星辰`.
- Chinese UI uses `云程`; English and Japanese UI use `CloudWay`.
- All README variants use the new brand and repository address.
- FastAPI metadata, startup output, frontend package metadata, and Docker identifiers use CloudWay branding.
- All compatibility-boundary identifiers remain unchanged.
- All three locale JSON files parse successfully.
- All Python source files parse successfully.
- `git diff --check` reports no whitespace errors.
- The Vite production build succeeds.
- Remaining old-brand search results are limited to the compatibility boundary, historical explanation, or upstream repository reference.

## Non-Goals

- Do not change product features, API behavior, data models, or database formats.
- Do not fix the project's existing TypeScript unused-variable failures.
- Do not change colors, fonts, layouts, or other visual design decisions.
- Do not migrate data from an existing Docker volume.
- Do not rename the local project directory.

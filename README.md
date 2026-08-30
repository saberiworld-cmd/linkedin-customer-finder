# LinkedIn Customer Finder

Scheduled lead-discovery engine for up to **5 new, relevant records per day**. LinkedIn is the primary source and Composio is the integration layer.

## Operating rules

- Use authorized LinkedIn/Composio access; do not bypass platform controls or collect credentials/session cookies.
- Five records/day is a **maximum target**, not a reason to create low-quality records.
- Deduplicate before persistence.
- Preserve source URLs and collection timestamps.
- Never commit API keys, OAuth secrets, cookies, or session tokens.
- Keep the source adapter modular so Facebook and later enrichment can be added safely.

## Record schema

`company`, `person_name`, `job_title`, `linkedin_url`, `company_linkedin_url`, `website`, `country`, `industry`, `email`, `phone`, `source`, `collected_at`, `confidence`

## Runtime

Designed for GitHub Actions. Runtime configuration and credentials belong in GitHub Actions Secrets/Variables.

## Current status

Initial repository setup. Next step is wiring the exact LinkedIn Composio action available to the connected account, then adding validation, deduplication, persistence, and the daily scheduler.

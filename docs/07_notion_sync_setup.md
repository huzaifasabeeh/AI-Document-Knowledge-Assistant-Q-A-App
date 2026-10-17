# GitHub to Notion status sync

Status: implementation prepared; activation and a live end-to-end run require NOTION_TOKEN.

## One-time activation

1. Create an internal Notion integration for this workspace at https://www.notion.so/profile/integrations with Read content and Update content capabilities.
2. Grant that integration access to the Project Task Tracker database (under the project dashboard). The ChatGPT Notion connection is separate.
3. In this GitHub repository, open Settings > Secrets and variables > Actions > New repository secret. Name it NOTION_TOKEN and paste the integration token there. Never commit or paste the token in chat.
4. Open Actions > Sync task status to Notion > Run workflow, choosing main. Confirm the run succeeds and review the Notion statuses. If the workflow is not visible, ensure the workflow file exists on main and Actions is enabled.

## Daily workflow

Implement and test a task, then edit its status in project/tasks.json in the same commit and push to main. The workflow reads the latest main branch and syncs managed statuses. It also supports manual reruns on main. A push alone does not prove completion; the developer or coding agent must update the manifest after verifying the task's acceptance criteria.

Allowed statuses: Planned, In progress, Pending review, Completed. Existing tasks are mapped by page ID, not title. The initial manifest preserves the tracker status at setup; it does not mark any Week 2 work complete.

GitHub is authoritative for managed Status fields. Manual changes to those status fields in Notion are overwritten on the next sync. Reviewer approval and submission have managed=false and are never read or changed by the sync. Notes, evidence links, page content, and all other properties remain unchanged. New Notion tasks require an explicit manifest entry; no pages are automatically created or deleted.

The workflow runs manifest validation and sync unit tests before contacting Notion. These check the sync implementation, not whether application features are complete. Add application acceptance tests to the development workflow as those features are implemented.

## Reliability and verification

The script validates task IDs and status values, checks all managed page parents and Status types before writing, skips unchanged statuses, verifies returned statuses, and retries rate limits/server failures. Partial network failures can leave some statuses updated; rerunning is safe. Sync runs are serialized and read current main to avoid an older queued push reverting newer task statuses.

Run offline checks:
- python scripts/sync_notion.py --validate-only
- python -m unittest discover -s tests -p test_notion_sync.py

To disable, disable the workflow in GitHub Actions or remove NOTION_TOKEN. Revoke the integration token if no longer needed.

## References

- https://developers.notion.com/reference/patch-page
- https://developers.notion.com/guides/get-started/authorization
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets

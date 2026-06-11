# clone_website_resources/

This sibling directory (`docs/clone_website_resources/`) is **not checked in**.
It is fetched on demand by:

    just cf_resources_sync

which clones (or refreshes to `origin/main`) the repo
https://github.com/pthom/imgui_bundle_website_resources

It is only needed for Cloudflare Pages staging/deploy
(`just cf_stage_prepare`, `just cf_stage`, `just cf_deploy`).
Regular contributors who do not work on the website do not need it.

## History

This used to be a git submodule (`docs/submodule_website_resources/`).
It was converted to an on-demand clone so that a 38 MB tree of
non-source assets does not pollute every contributor's checkout.

## Editing the website resources

1. `cd docs/clone_website_resources` and work as in any normal git clone.
2. Commit and **push to `origin/main`** before running
   `just cf_deploy_from_github`, since the GitHub workflow re-syncs from
   `origin/main` and would otherwise deploy a stale snapshot.

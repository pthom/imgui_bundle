---
name: fork-maintenance
description: Rules for the forks of the bundle's libraries (external/<lib>/<lib>, branch imgui_bundle) - which commits are generic, and how to rewrite, reorder or slim a fork's history without breaking the bundle's submodule pointers, and how to prepare a pull request upstream (Dear ImGui and the others). Use before committing to a fork, rebasing or rewriting its history, force-pushing it, removing a submodule, or preparing a PR to a library's author.
---

# Fork maintenance

The fork model (remotes `official` and `fork`, branch `imgui_bundle`, rebase rather than merge, `[Bundle]` prefix, `[ADAPT_IMGUI_BUNDLE]` markers) is in `docs/book/devel_docs/bindings_forks.md`. Read it first.

## Entry points

- Recipes (group `libs` of `just --list`): `libs_info` (remotes and branches), `libs_check_upstream` (which forks have new upstream commits), `libs_log <lib>`, `libs_rebase <lib>` (tags the current state, then rebases on `official`), `libs_tag <lib>`, `libs_check_pushed` (before pushing the bundle: every submodule commit it points to is on a remote branch), `libs_reattach`, `libs_fetch`, `libs_pull`. After a rebase: `libs_bindings <lib>`.
- Docs: `docs/book/devel_docs/bindings_forks.md` (the fork model), `bindings_update.md` (the update procedure, with these recipes).

## Generic commits first

A commit that any user of the library could want is generic:
- no `[Bundle]` prefix, no `[ADAPT_IMGUI_BUNDLE]` marker, no "specific to ImGui Bundle" comment;
- it sits before the Bundle-specific commits;
- its message explains the problem and what the change does, with a short code example.

For each `[Bundle]` commit, ask whether it really is specific. Often the better answer is to make it unnecessary (a litgen option, a wrapper header or a custom binding in the bundle, in the order of `bindings_forks.md`), or to make it generic. Propose this classification to the user up front, commit by commit.

The audience of a fork: people who cherry-pick from it. The branch name `imgui_bundle` is its only advertisement.

## Rewriting a fork's history

Plan the bundle commits and the verification commands before starting.

1. No bundle commit between two rewrites of the fork. Each rewrite changes the fork's hashes: the bundle commit would point to a commit that only existed locally, and `git checkout` / `git bisect` could never resolve it. Commit the bundle once, when the fork branch is final and pushed, or squash the bundle commits before publishing. Check each pointer: `git -C <fork> branch -r --contains <sha>` (or `tag --contains`).
2. Prove that a reordering changed nothing: `git diff <old tip> <new tip>` must be empty. To build the intermediate states of a file, remove blocks from the final file, and assert on every cut.
3. Before a forced push: keep the old tip (a legacy branch, or a dated tag `bundle_YYYYMMDD`), and use `--force-with-lease=<branch>:<expected sha>`. Only on the user's go-ahead.
4. Before removing a submodule (`git submodule deinit`, `rm -rf .git/modules/<path>`): check that every commit the bundle points to is pushed, including those of its unpushed history: `git -C <sub> branch -r --contains <sha>` for each value of the gitlink. A local-only commit is lost with the git folder, and every CI checkout of the bundle then fails ("upload-pack: not our ref").
5. The shell traps of the environment rules apply: CRLF files, zsh `$VAR:t`, removing the worktrees and branches you create.

After a rebase of the imgui fork, follow step 4b of `bindings_update.md` (node editor patches, pinned tags).

## A pull request upstream

The process of three PRs to Dear ImGui (2026-10-15), for any upstream library.

1. **The branch:** a worktree from `official/master`, never the fork's `imgui_bundle` branch nor the bundle's checkout: `git -C external/<lib>/<lib> worktree add -b <topic> builds/claude_<lib>_pr_<topic> official/master`. Dear ImGui: target master, not docking (the fork follows docking; Omar carries master into docking). A fork commit brought over with `cherry-pick -n` leaves a `MERGE_MSG`, which Fork shows as the commit message: delete it.
2. **The code, in upstream's style:** no `[Bundle]` prefix, no `[ADAPT_IMGUI_BUNDLE]` markers; fields initialized where upstream does it (Dear ImGui: in `ImGuiContext`'s constructor); one-line comments, none that only points to what the next line names.
3. **The proof:** a headless test for an API (balanced calls, the state at the call). For a behavior, an A/B app: the library's stock example built twice (master, the change), an auto mode that plays the case and prints the result, and a recording mode for the PR (each frame piped to ffmpeg, `io.MouseDrawCursor` on, A above B with captions, about 10 s). Inject the mouse after the backend's `NewFrame()`, the position before the wheel or the click. Real input (a trackpad) gets into the auto runs: nobody touches the machine meanwhile.
4. **The facts:** `_plans/scratch/<topic>_pr/<topic>_pr__findings.md`: the branch, the symptom, the cause, the change, the tests, the links, the pictures and the movie. Check that a linked issue still relates: cite the recent commit that the change completes, not only old issues.
5. **Show the code to the user:** in CLion at the changed lines, the diff in Fork (`fork status` from inside the worktree), each hunk commented.
6. **The text is the user's** (Dear ImGui's PR template: no AI-generated prose). The commit: one line in the author's style ("Area: what changes."), written or approved by the user, who may commit in Fork himself. A draft of the PR's text only on his request, in Obsidian (`<topic>_pr__draft.md`), marked to reword.
7. **Push and open:** `git push -u fork <topic>`, then open `https://github.com/<owner>/<repo>/compare/master...pthom:<repo>:<topic>?expand=1`.
8. **After:** a pending item per PR, for each answer. Merged: the fork drops its copy at its next rebase, a Python port follows then (never before: C++ and Python would differ), the worktree and the test app go. Declined: the fork keeps the commit, as a generic one.

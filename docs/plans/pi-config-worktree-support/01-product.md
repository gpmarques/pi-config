# Product: isolated project workspaces for agent tasks

## Problem
When I delegate project work to several agents, I expect them to work independently. Today, spawned agents and agents they spawn can share my project checkout, allowing one task to overwrite another task's edits or change files while I am using them. I need concurrent task work isolated by default, preserved for review, and refused safely whenever that separation cannot be guaranteed.

## Success metric
In a 10-round acceptance trial, each round runs five overlapping agent tasks in one project—three directly spawned tasks and two nested tasks—for 50 task runs total. Success is 0 instances in which a task's file changes appear in the top-level controller's checkout or any other task's workspace, measured by assigning every task a distinct change to the same project files and comparing all workspaces before, during, and after each round.

## Announcement — the blog post before the feature
Pi-config now gives every spawned agent task its own project workspace, including tasks spawned by other agents. Concurrent tasks can edit the same project files without changing the top-level controller's checkout or one another's work. Each task starts from its immediate caller's current committed state; if that caller has uncommitted changes, the new task does not start and explains that the work must be committed or finished first. Finished or stopped task work is retained for review, and cleanup is explicit: only completed workspaces with no outstanding changes can be removed, while committed work remains available. The first release supports local macOS and Linux Git projects and refuses non-Git projects or projects using currently unsupported features such as submodules or Git LFS rather than falling back to a shared workspace. It does not isolate the already-running top-level controller, automatically integrate or publish task work, support Windows or remote tasks, or protect shared credentials, services, and other machine-wide state.

## Screens
no UI

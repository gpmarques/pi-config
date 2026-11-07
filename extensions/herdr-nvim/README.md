# herdr-nvim (external Herdr TUI integration)

This directory documents [`ChmaraX/herdr-nvim`](https://github.com/ChmaraX/herdr-nvim), not a Pi package or extension. There is no implementation to copy from this directory. The integration has two halves: a Herdr TUI sidebar/file picker and a Neovim plugin for annotations.

## Reviewed version and requirements

The reviewed version is v1.3.1 at commit [`88a68c77fe82476bdfcba39d36c3fa37109f35a8`](https://github.com/ChmaraX/herdr-nvim/commit/88a68c77fe82476bdfcba39d36c3fa37109f35a8). Follow the [TUI guide at that commit](https://github.com/ChmaraX/herdr-nvim/blob/88a68c77fe82476bdfcba39d36c3fa37109f35a8/TUI.md), not the desktop-app instructions.

Herdr TUI 0.7.5 or later and Neovim 0.10 or later must already be installed. The local reference uses Herdr TUI 0.9.1 and Neovim 0.11.6. This guide does not install either tool or claim automated UI test coverage.

## Install both halves

Review the upstream build hook before installing. At this commit, it downloads prebuilt release binaries without checking a published checksum. The source pin does not verify those binary downloads.

Install the Herdr plugin at the reviewed commit:

```sh
herdr plugin install --ref 88a68c77fe82476bdfcba39d36c3fa37109f35a8 --yes ChmaraX/herdr-nvim
```

For a Kickstart configuration that already imports `custom.plugins`, add `~/.config/nvim/lua/custom/plugins/herdr.lua`:

```lua
return {
  { 'ChmaraX/herdr-nvim', opts = {} },
}
```

The local Kickstart configuration already enables `{ import = 'custom.plugins' }`. For other lazy.nvim setups, add the plugin specification at the existing location for plugins. Do not replace `init.lua`.

This Lua specification is not pinned. The local `lazy-lock.json` records commit `88a68c77fe82476bdfcba39d36c3fa37109f35a8`. Use your existing lazy.nvim workflow to install the plugin and manage its lock entry, not a copy of the full local lockfile.

## Bind and use the sidebar

Before editing `~/.config/herdr/config.toml`, note that these bindings replace the default `edit_scrollback` and `open_notification_target` actions. Preserve unrelated bindings and avoid duplicate entries for these keys. Add or update these two entries:

```toml
[[keys.command]]
key = "prefix+e"
type = "plugin_action"
command = "chmarax.herdr-nvim.toggle"
description = "nvim sidebar"

[[keys.command]]
key = "prefix+o"
type = "plugin_action"
command = "chmarax.herdr-nvim.pick-file"
description = "open file from agent output"
```

Reload the Herdr configuration:

```sh
herdr server reload-config
```

Use your configured prefix, then `e`, to toggle the sidebar. Use your configured prefix, then `o`, to open the file picker. The local prefix was `Ctrl+b`, but the prefix depends on your Herdr configuration.

In Neovim, `:Herdr comment` adds a code annotation and `:Herdr list` lists annotations. `:Herdr send` pastes annotations into the agent's input. `:Herdr submit` sends them and submits the input.

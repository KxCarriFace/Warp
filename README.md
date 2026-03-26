# Warp

A lightweight CLI tool for navigating your filesystem through directory aliases. Instead of typing long paths or relying on shell history, Warp lets you assign short names to directories and jump to them instantly from anywhere.

```bash
warp add ~/Documents/projects/my-project proj
warp to proj
```

---

## Requirements

- Python 3.3+
- Bash (Git Bash on Windows, or any standard Linux/macOS terminal)

---

## Installation

Download and run the bootstrap script — it handles everything else automatically:

```bash
curl -sL https://raw.githubusercontent.com/KxCarriFace/warp/main/setup.sh | bash
```

Or with wget:

```bash
wget -qO- https://raw.githubusercontent.com/KxCarriFace/warp/main/setup.sh | bash
```

`setup.sh` will:
1. Download the project files into `$HOME/.usr/warp`
2. Check Python 3 is installed (exits with instructions if not)
3. Create a Python virtual environment (`.venv`)
4. Install all dependencies from `requirements.txt`
5. Add Warp to your shell by sourcing `warp.sh` in `~/.bashrc`
6. Create a default `home` alias pointing to your home directory
7. Reload your shell so Warp is available immediately

If `warp` is not recognized after setup, run `source ~/.bashrc` manually.

> Already have the project downloaded? You can run `install.sh` directly:
> ```bash
> bash "$HOME/.usr/warp/install.sh"
> ```

---

## Commands

### `warp add <path> <alias>`
Create a new alias for a directory.

```bash
warp add . work          # alias current directory
warp add ~/dev/api api   # alias an absolute path
warp add . api -d "Main API service"   # with a description
```

| Flag | Description |
|---|---|
| `-d`, `--description` | Add a description to the alias |

---

### `warp to <alias>`
Navigate to an aliased directory.

```bash
warp to work
```

---

### `warp list`
Display all active aliases and their metadata.

```bash
warp list                  # show all active aliases
warp list --alias work     # show details for a specific alias
warp list -s api           # search aliases by name
warp list -a               # include soft-deleted aliases
```

| Flag | Description |
|---|---|
| `--alias <name>` | Show detailed info for a specific alias |
| `-s`, `--search <term>` | Filter aliases by name |
| `-a`, `--all` | Show all aliases, including soft-deleted ones (Status column added) |

---

### `warp update <alias>`
Update an existing alias. At least one flag is required.

```bash
warp update work -n workspace          # rename
warp update work -p ~/dev/workspace    # change path
warp update work -d "Main workspace"   # update description
warp update work -n workspace -p ~/dev/workspace -d "Main workspace"  # all at once
```

| Flag | Description |
|---|---|
| `-n`, `--name <new_name>` | Rename the alias |
| `-p`, `--path <path>` | Update the directory path |
| `-d`, `--description <text>` | Replace the description |

---

### `warp delete <alias>`
Delete an alias. Soft-deletes by default — the alias is marked as deleted but kept in the config file for recovery via `doctor-paths`.

```bash
warp delete work           # soft-delete (recoverable)
warp delete work -p        # permanently remove with no recovery
```

| Flag | Description |
|---|---|
| `-p`, `--permanent` | Permanently remove the alias with no recovery |

---

### `warp doctor-paths`
Scan all active aliases and check whether their paths still exist on disk. Any alias pointing to a missing directory is soft-deleted and reported in a table.

```bash
warp doctor-paths               # scan and soft-delete invalid paths
warp doctor-paths --perm-delete # permanently remove invalid paths and purge all soft-deleted aliases
```

| Flag | Description |
|---|---|
| `--perm-delete` | Permanently delete invalid paths and purge all previously soft-deleted aliases |

Running `doctor-paths` always produces a report table showing each alias, its path, description, and what happened to it (`Validated` or `Soft-deleted`/`Perm. Deleted`). With `--perm-delete`, a second table is shown listing every soft-deleted alias that was permanently purged.

---

## Alias Metadata

Every alias stores the following fields in `config/alias.json`:

| Field | Description |
|---|---|
| `path` | Absolute path to the directory |
| `description` | Optional description |
| `created_at` | UTC timestamp of when the alias was created |
| `last_used` | UTC timestamp of the last `warp to` call |
| `usage` | Number of times the alias has been used |
| `tags` | Reserved for future use |
| `delete_info` | `null` if active; otherwise contains `deleted_at` and `method` (`user_delete` or `doctored`) |

---

## Soft-Delete vs Permanent Delete

Warp uses a soft-delete system by default. Deleted aliases are not removed from the config file — they are marked with a `delete_info` timestamp and method, and hidden from normal output.

- `warp delete <alias>` — soft-deletes with method `user_delete`
- `warp doctor-paths` — soft-deletes invalid paths with method `doctored`
- `warp delete <alias> --permanent` — removes the alias entirely
- `warp doctor-paths --perm-delete` — removes all invalid and previously soft-deleted aliases permanently

A soft-deleted alias name can be reused. Adding a new alias with the same name as a soft-deleted one will overwrite the old entry.

# conan-hal-command

Conan custom command providing libhal development tools for embedded systems.

## 📥 Installation

You must have Conan 2 installed and available on your machine for this to work.
Copy and paste the command below to install the `hal` conan command extension.

```bash
conan config install -sf extensions -tf extensions https://github.com/libhal/conan-hal-command.git
```

Test by writing:

```bash
conan hal --version
```

Should respond with something like the text below:

```plaintext
conan-hal-command: 0.0.0
```

## 🔧 Available Commands

### `conan hal setup`

Set up your libhal development environment by configuring remotes and installing profiles.

**What it does:**

1. Adds/updates the `libhal` remote repository
2. Installs baremetal settings for embedded development
3. Detects your OS/architecture and installs the appropriate host profile
4. Installs ARM MCU device profiles (lpc4078, stm32f103c8, etc.)
5. Installs ARM GCC compiler profiles

> [!NOTE]
> This command will continue to be updated with additional platforms, and
> compilers as they roll out.

**Usage:**

```bash
# Basic setup
conan hal setup

# Verbose output
conan hal --verbose setup

# Skip remote configuration
conan hal setup --skip-remotes

# Skip user settings installation
conan hal setup --skip-user-settings

# Skip default host profile installation
conan hal setup --skip-default

# Skip target device profiles installation
conan hal setup --skip-target-profiles

# Skip compiler profiles installation
conan hal setup --skip-compiler-profiles

# Combine multiple skip flags
conan hal setup --skip-default --skip-compiler-profiles
```

**Options:**

- `--skip-remotes` - Skip adding/updating the libhal remote
- `--skip-user-settings` - Skip user settings (baremetal settings) installation
- `--skip-default` - Skip default host profile installation
- `--skip-target-profiles` - Skip target device profiles installation
- `--skip-compiler-profiles` - Skip cross compiler profiles installation

---

### Other Commands (Coming Soon)

- `conan hal new` - Create a new libhal project, library, platform, or board
- `conan hal install` - Install profiles or cross-compilers
- `conan hal build-matrix` - Build against multiple profiles/configurations
- `conan hal deploy` - Build and create packages for deployment
- `conan hal profiles` - Manage libhal profiles
- `conan hal package` - Create Conan package without deployment
- `conan hal flash` - Flash binary to target device
- `conan hal debug` - Start debug session with target device

---

### Global Options

- `--verbose` - Enable verbose output (shows debug information)
- `--version` - Show version and exit
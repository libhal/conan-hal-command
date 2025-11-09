#!/usr/bin/python
#
# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import platform
from pathlib import Path
from typing import List, Optional
from conan.api.conan_api import ConanAPI
from conan.api.model import Remote
from conan.cli.command import conan_command, conan_subcommand

logger = logging.getLogger(__name__)


class Profile:
    """
    Represents a Conan profile with a name and content.
    """

    def __init__(self, name: str, content: str, build_dir: Optional[Path] = None):
        self.name = name
        self.content = content
        self._build_dir = build_dir

    def set_build_dir(self, build_dir: Path) -> None:
        """Set the build directory for this profile"""
        self._build_dir = build_dir

    def build_dir(self) -> Path:
        """Get the build directory for this profile"""
        if self._build_dir is None:
            raise ValueError(f"No build directory set for profile '{self.name}'. "
                             "Set it via set_build_dir() or during initialization")
        return self._build_dir / self.name

    def profile_path(self) -> Path:
        """Get the profile file path for this profile"""
        return self.build_dir() / 'profile'

    def log_file(self) -> Path:
        """Get the log file path for this profile"""
        return self.build_dir() / 'log'


class BuildProfileResult:
    """
    Represents the result of building a profile.
    """

    def __init__(self, profile_name: str, success: bool, log_file: Optional[Path]):
        self.profile_name = profile_name
        self.success = success
        self.log_file = log_file


def generate_arm_cortex_m_profiles() -> List[Profile]:
    """
    Generate all possible profile combinations for ARM GCC toolchains

    Returns:
        List[Profile]: List of Profile objects containing profile configurations
    """
    compilers = {
        "gcc": {
            'package': 'arm-gnu-toolchain',
            'versions': ['12.3', '13.2', '13.3', '14.2']
        }
        # We plan to support LLVM at some future point
    }

    # Architectures can be either strings or tuples (arch_name, min_version)
    # Tuple format: (architecture_name, minimum_compiler_version)
    architectures = [
        'cortex-m0',
        'cortex-m0plus',
        'cortex-m1',
        'cortex-m3',
        'cortex-m4',
        'cortex-m4f',
        'cortex-m7',  # comment these out later
        'cortex-m7f',  # comment these out later
        'cortex-m7d',  # comment these out later
        'cortex-m23',  # comment these out later
        'cortex-m33',  # comment these out later
        'cortex-m33f',  # comment these out later
        'cortex-m35pf',  # comment these out later
        'cortex-m55',  # comment these out later
        ('cortex-m85', '13.2'),  # comment these out later
    ]

    build_types = [
        'Debug',
        'Release',
        'MinSizeRel',
    ]

    def version_compare(v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]

        for i in range(max(len(v1_parts), len(v2_parts))):
            part1 = v1_parts[i] if i < len(v1_parts) else 0
            part2 = v2_parts[i] if i < len(v2_parts) else 0
            if part1 < part2:
                return -1
            elif part1 > part2:
                return 1
        return 0

    profiles: List[Profile] = []
    for compiler, compiler_config in compilers.items():
        compiler_package = compiler_config['package']
        for arch_entry in architectures:
            # Check if this is a tuple with minimum version requirement
            if isinstance(arch_entry, tuple):
                arch, min_version = arch_entry
            else:
                arch = arch_entry
                min_version = None

            for version in compiler_config['versions']:
                # Skip if compiler version doesn't meet minimum requirement
                if min_version and version_compare(version, min_version) < 0:
                    continue

                for build_type in build_types:
                    NAME = f"{arch}-{compiler}-{version}-{build_type}"
                    TEXT = f"""[settings]
os=baremetal
arch={arch}
compiler={compiler}
compiler.version={version}
compiler.libcxx=libstdc++11
compiler.cppstd=23
build_type={build_type}

[tool_requires]
{compiler_package}/{version}"""

                    profiles.append(Profile(NAME, TEXT))

    return profiles


def generate_all_profiles():
    """
    Generate all possible profile combinations for ARM GCC toolchains

    Returns:
        list: List of dictionaries containing profile configurations
              Each dict has keys: arch, compiler, compiler_version, compiler_package, os
    """
    arm_cortex_m_profiles = generate_arm_cortex_m_profiles()
    return arm_cortex_m_profiles


@conan_subcommand()
def hal_new(conan_api: ConanAPI, parser, subparser, *args):
    """
    Create a new libhal project, library, platform, or board
    """
    subparser.add_argument('type', choices=['project', 'library', 'platform', 'board'],
                           help='Type of item to create')
    subparser.add_argument('name', help='Name of the new item')
    subparser.add_argument('--template', help='Template to use')
    args = parser.parse_args(*args)

    logger.info(f"Creating new {args.type}: {args.name}")
    logger.info("TODO: Implement new command")


def remote_exists(conan_api: ConanAPI, remote_name: str):
    try:
        conan_api.remotes.get(remote_name)
        return True
    except Exception:
        return False


@conan_subcommand()
def hal_setup(conan_api: ConanAPI, parser, subparser, *args):
    """
    Set up libhal development environment (remotes + profiles)
    """
    subparser.add_argument(
        '--skip-remotes', action='store_true', help='Skip remote configuration')
    subparser.add_argument(
        '--skip-user-settings', action='store_true', help='Skip user settings installation')
    subparser.add_argument(
        '--skip-default-profile', action='store_true', help='Skip default host profile installation')
    subparser.add_argument(
        '--skip-target-profiles', action='store_true', help='Skip target device profiles installation')
    subparser.add_argument(
        '--skip-compiler-profiles', action='store_true', help='Skip compiler profiles installation')
    args = parser.parse_args(*args)

    logger.info("Setting up libhal environment...")

    REPO = "https://libhal.jfrog.io/artifactory/api/conan/trunk-conan"
    REMOTE_NAME = "libhal"
    CONFIG_GIT_LINK = "https://github.com/libhal/conan-config.git"
    CONFIG_SRC = "profiles/baremetal/v2"

    # Step 1: Add the libhal remote
    if not args.skip_remotes:
        logger.info("\n📦 Configuring libhal-trunk remote...")
        REPO_REMOTE = Remote(REMOTE_NAME, REPO)
        logger.debug(f"Remote URL: {REPO}")

        try:
            if remote_exists(conan_api, REMOTE_NAME):
                logger.debug(
                    f"Remote '{REMOTE_NAME}' already exists, updating...")
                conan_api.remotes.update(REMOTE_NAME, url=REPO)
                logger.info(f"✅ Remote '{REMOTE_NAME}' updated successfully")
            else:
                logger.debug(
                    f"Remote '{REMOTE_NAME}' does not exist, adding...")
                conan_api.remotes.add(REPO_REMOTE)
                logger.info(f"✅ Remote '{REMOTE_NAME}' added successfully")
        except Exception as e:
            logger.error(f"❌ Failed to configure remote: {e}")
            return

    # Step 2: Install user settings
    if not args.skip_user_settings:
        logger.info("\n⚙️  Installing user settings...")
        logger.info(f"ℹ️ Source: {CONFIG_GIT_LINK} ({CONFIG_SRC})")
        try:
            conan_api.config.install(
                CONFIG_GIT_LINK, True, source_folder=CONFIG_SRC,
            )
            logger.info("✅ User settings installed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to install user settings: {e}")
            return

    # Step 3: Detect default profile and install host-specific profile
    if not args.skip_default_profile:
        # Host profile mapping for different OS and architecture combinations
        HOST_PROFILE_MAP = {
            ('Linux', 'x86_64'): 'profiles/x86_64/linux/',
            ('Linux', 'aarch64'): 'profiles/armv8/linux/',
            ('Linux', 'arm64'): 'profiles/armv8/linux/',
            ('Windows', 'AMD64'): 'profiles/x86_64/windows/',
            ('Windows', 'x86_64'): 'profiles/x86_64/windows/',
            ('Windows', 'ARM64'): 'profiles/armv8/windows/',
            ('Windows', 'aarch64'): 'profiles/armv8/windows/',
            ('Darwin', 'x86_64', '13'): 'profiles/x86_64/mac-13/',
            ('Darwin', 'x86_64', '14'): 'profiles/x86_64/mac-14/',
            ('Darwin', 'x86_64', '15'): 'profiles/x86_64/mac-15/',
            ('Darwin', 'arm64', '13'): 'profiles/armv8/mac-13/',
            ('Darwin', 'arm64', '14'): 'profiles/armv8/mac-14/',
            ('Darwin', 'arm64', '15'): 'profiles/armv8/mac-15/',
        }

        try:
            # Detect OS and architecture
            os_type = platform.system()
            arch = platform.machine()
            logger.debug(f"Detected OS: {os_type}, Architecture: {arch}")

            # Determine profile source folder
            if os_type == 'Darwin':
                # For macOS, also get the major version
                mac_version = platform.mac_ver()[0].split('.')[0]
                logger.debug(f"Detected macOS version: {mac_version}")
                PROFILE_SRC = HOST_PROFILE_MAP[(
                    os_type, arch, mac_version)]
            else:
                PROFILE_SRC = HOST_PROFILE_MAP[(os_type, arch)]

            logger.info(
                f"📥 Installing host profile for {os_type} {arch}...")
            logger.info(
                f"ℹ️ Profile source: {CONFIG_GIT_LINK} ({PROFILE_SRC})")
            conan_api.config.install(
                CONFIG_GIT_LINK, True,
                source_folder=PROFILE_SRC,
                target_folder="profiles",
            )
            logger.info("✅ Host profile installed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to detect profile: {e}")
            return

    # Step 4: Install ARM MCU device profiles
    if not args.skip_target_profiles:
        logger.info("\n🔧 Installing ARM MCU device profiles...")
        ARM_MCU_REPO = "https://github.com/libhal/libhal-arm-mcu.git"
        ARM_MCU_SRC = "conan/profiles/v1"
        logger.debug(f"ℹ️ Source: {ARM_MCU_REPO} ({ARM_MCU_SRC})")
        try:
            conan_api.config.install(
                ARM_MCU_REPO, True,
                source_folder=ARM_MCU_SRC,
                target_folder="profiles",
            )
            logger.info("✅ ARM MCU device profiles installed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to install ARM MCU profiles: {e}")
            return

        # Step 5: Install ARM GCC compiler profiles
    if not args.skip_compiler_profiles:
        logger.info("\n🛠️  Installing ARM GCC compiler profiles...")
        ARM_GNU_TOOLCHAIN_REPO = "https://github.com/libhal/arm-gnu-toolchain.git"
        ARM_GNU_PROFILES = "conan/profiles/v1"
        logger.info(
            f"ℹ️ Source: {ARM_GNU_TOOLCHAIN_REPO} ({ARM_GNU_PROFILES})")
        try:
            conan_api.config.install(
                ARM_GNU_TOOLCHAIN_REPO,
                True,
                source_folder=ARM_GNU_PROFILES,
                target_folder="profiles"
            )
            logger.info("✅ ARM GCC compiler profiles installed successfully")
        except Exception as e:
            logger.error(f"❌ Failed to install ARM GCC compiler profiles: {e}")
            return

    logger.info("\n✅ libhal environment setup complete!")
    logger.info("\nYou can now build projects with commands like:")
    logger.info("  conan build demos -pr lpc4078 -pr arm-gcc-12.3")
    logger.info("  conan build demos -pr stm32f103c8 -pr arm-gcc-12.3")


@conan_subcommand()
def hal_install(conan_api: ConanAPI, parser, subparser, *args):
    """
    Install profiles or cross-compilers
    """
    subparser.add_argument('what', choices=['profiles', 'compilers', 'all'],
                           help='What to install')
    subparser.add_argument('--arch', help='Architecture to install for')
    args = parser.parse_args(*args)

    logger.info(f"Installing {args.what}...")
    logger.info("TODO: Implement install command")


@conan_subcommand()
def hal_build_matrix(conan_api: ConanAPI, parser, subparser, *args):
    """
    Build against multiple architecture/compiler profile combinations
    """
    import os
    import subprocess
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    subparser.add_argument('path', nargs='?', default='.',
                           help='Path to build (default: current directory)')
    subparser.add_argument('--continue-on-error', action='store_true',
                           help='Continue building remaining profiles if one fails')
    subparser.add_argument('-j', '--jobs', type=int, default=os.cpu_count(),
                           help=f'Number of parallel builds (default: {os.cpu_count()})')
    args = parser.parse_args(*args)

    # Get all profiles
    profiles = generate_all_profiles()
    total_profiles = len(profiles)

    logger.info(f"Building {total_profiles} profile combinations...")
    logger.info(f"Using {args.jobs} parallel jobs")

    # Create build-matrix directory for logs
    BUILD_PATH: Path = Path(args.path).resolve()

    # Check for conanfile.py existence
    if not (BUILD_PATH / "conanfile.py").exists():
        logger.error(f"❌ No conanfile.py found in {BUILD_PATH}")
        logger.error(
            "Please ensure you're running this command in a directory with a 'conanfile.py' file")
        return 1

    BUILD_DIR: Path = BUILD_PATH / "build-matrix"
    BUILD_DIR.mkdir(exist_ok=True)
    logger.info(f"Binaries will be written to: {BUILD_DIR}")

    # Track progress
    completed_count = 0
    failed_builds = []
    lock = threading.Lock()

    logging.debug(f"PROFILE_BUILD_DIR={BUILD_DIR}")

    # Sequential install to avoid CMakePresets.json & compile_commands.json
    # collision
    for profile in profiles:
        profile.set_build_dir(BUILD_DIR)
        PROFILE_BUILD_DIR = BUILD_DIR / profile.name

        logging.debug(f"PROFILE_PATH={profile.profile_path()}")
        logging.debug(f"LOG_FILE={profile.log_file()}")

        PROFILE_BUILD_DIR.mkdir(exist_ok=True)
        Path(profile.profile_path()).write_text(profile.content)

        logging.info(f"⚙️ Running Conan Install: {profile.name}")
        subprocess.run(
            ['conan', 'install', '.', '-pr',
                str(profile.profile_path().resolve())],
            capture_output=True,
            check=True,
            timeout=30
        )

    def build_profile(profile: Profile) -> BuildProfileResult:
        """Build a single profile and return result"""
        nonlocal completed_count

        LOG_FILE = profile.log_file()

        COMMAND = ['conan', 'build', str(BUILD_PATH),
                   '-pr', str(profile.profile_path().resolve()),
                   '-of', str(profile.build_dir().resolve())]
        try:
            # Run conan build command
            result = subprocess.run(COMMAND,
                                    capture_output=True,
                                    text=True,
                                    # 5 minute timeout per build
                                    timeout=300)

            # Write logs
            log_content = f"Command: {' '.join(COMMAND)}\n"
            log_content += f"Return code: {result.returncode}\n\n"
            log_content += "=== STDOUT ===\n"
            log_content += result.stdout
            log_content += "\n=== STDERR ===\n"
            log_content += result.stderr
            LOG_FILE.write_text(log_content)

            # Update progress
            with lock:
                completed_count += 1
                if result.returncode == 0:
                    logger.info(
                        f"✅ [{completed_count}/{total_profiles}] {profile.name}")
                    return BuildProfileResult(profile.name, True, None)
                else:
                    logger.error(
                        f"❌ [{completed_count}/{total_profiles}] {profile.name}")
                    return BuildProfileResult(profile.name, False, LOG_FILE)

        except subprocess.TimeoutExpired:
            with lock:
                completed_count += 1
                logger.error(
                    f"‼️⏱️[{completed_count}/{total_profiles}] {profile.name} TIMEOUT")
                LOG_FILE.write_text(f"Build timed out after 600 seconds")
                return BuildProfileResult(profile.name, False, LOG_FILE)
        except Exception as e:
            with lock:
                completed_count += 1
                logger.error(
                    f"‼️ [{completed_count}/{total_profiles}] {profile.name} ERROR: {e}")
                LOG_FILE.write_text(f"Build error: {e}")
                return BuildProfileResult(profile.name, False, LOG_FILE)

    # Execute builds in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        # Submit all build jobs
        future_to_profile = {executor.submit(
            build_profile, profile): profile for profile in profiles}

        # Collect results as they complete
        for future in as_completed(future_to_profile):
            result = future.result()
            if not result.success:
                failed_builds.append(result)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(
        f"Build Matrix Complete: {completed_count}/{total_profiles} profiles processed")
    logger.info(f"Successful: {completed_count - len(failed_builds)}")
    logger.info(f"Failed: {len(failed_builds)}")

    if failed_builds:
        logger.error("\nFailed builds:")
        for result in failed_builds:
            logger.error(f"  - {result.profile_name}: {result.log_file}")
        return 1
    else:
        logger.info("\nAll builds successful!")
        return 0


@conan_subcommand()
def hal_package(conan_api: ConanAPI, parser, subparser, *args):
    """
    Create Conan package against multiple architecture/compiler profile combinations
    """
    import os
    import subprocess
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    subparser.add_argument('path', nargs='?', default='.',
                           help='Path to build (default: current directory)')
    subparser.add_argument('--version', required=True,
                           help='Version to use for conan create command')
    subparser.add_argument('--continue-on-error', action='store_true',
                           help='Continue building remaining profiles if one fails')
    subparser.add_argument('-j', '--jobs', type=int, default=os.cpu_count(),
                           help=f'Number of parallel builds (default: {os.cpu_count()})')
    args = parser.parse_args(*args)

    # Get all profiles
    profiles = generate_all_profiles()
    total_profiles = len(profiles)

    logger.info(
        f"Creating packages for {total_profiles} profile combinations...")
    logger.info(f"Using {args.jobs} parallel jobs")

    # Create build-matrix directory for logs
    BUILD_PATH: Path = Path(args.path).resolve()

    # Check for conanfile.py existence
    if not (BUILD_PATH / "conanfile.py").exists():
        logger.error(f"❌ No conanfile.py found in {BUILD_PATH}")
        logger.error(
            "Please ensure you're running this command in a directory with a 'conanfile.py' file")
        return 1

    BUILD_DIR: Path = BUILD_PATH / "build-matrix"
    BUILD_DIR.mkdir(exist_ok=True)
    logger.info(f"Package builds will be logged to: {BUILD_DIR}")

    # Set build directory for all profiles
    for profile in profiles:
        profile.set_build_dir(BUILD_DIR)

    # Track progress
    completed_count = 0
    failed_builds = []
    lock = threading.Lock()

    def build_profile(profile: Profile) -> BuildProfileResult:
        """Create package for a single profile and return result"""
        nonlocal completed_count

        # Create profile directory and write profile file
        PROFILE_BUILD_DIR = profile.build_dir()
        PROFILE_BUILD_DIR.mkdir(exist_ok=True)
        Path(profile.profile_path()).write_text(profile.content)

        LOG_FILE = profile.log_file()

        COMMAND = ['conan', 'create', str(BUILD_PATH),
                   '-pr', str(profile.profile_path().resolve()),
                   '--version', args.version]
        try:
            # Run conan create command
            result = subprocess.run(COMMAND,
                                    capture_output=True,
                                    text=True,
                                    # 5 minute timeout per package creation
                                    timeout=300)

            # Write logs
            log_content = f"Command: {' '.join(COMMAND)}\n"
            log_content += f"Return code: {result.returncode}\n\n"
            log_content += "=== STDOUT ===\n"
            log_content += result.stdout
            log_content += "\n=== STDERR ===\n"
            log_content += result.stderr
            LOG_FILE.write_text(log_content)

            # Update progress
            with lock:
                completed_count += 1
                if result.returncode == 0:
                    logger.info(
                        f"✅ [{completed_count}/{total_profiles}] {profile.name}")
                    return BuildProfileResult(profile.name, True, None)
                else:
                    logger.error(
                        f"❌ [{completed_count}/{total_profiles}] {profile.name}")
                    return BuildProfileResult(profile.name, False, LOG_FILE)

        except subprocess.TimeoutExpired:
            with lock:
                completed_count += 1
                logger.error(
                    f"‼️⏱️[{completed_count}/{total_profiles}] {profile.name} TIMEOUT")
                LOG_FILE.write_text(
                    f"Package creation timed out after 300 seconds")
                return BuildProfileResult(profile.name, False, LOG_FILE)
        except Exception as e:
            with lock:
                completed_count += 1
                logger.error(
                    f"‼️ [{completed_count}/{total_profiles}] {profile.name} ERROR: {e}")
                LOG_FILE.write_text(f"Package creation error: {e}")
                return BuildProfileResult(profile.name, False, LOG_FILE)

    # Execute package creation in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        # Submit all package creation jobs
        future_to_profile = {executor.submit(
            build_profile, profile): profile for profile in profiles}

        # Collect results as they complete
        for future in as_completed(future_to_profile):
            result = future.result()
            if not result.success:
                failed_builds.append(result)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(
        f"Package Creation Complete: {completed_count}/{total_profiles} profiles processed")
    logger.info(f"Successful: {completed_count - len(failed_builds)}")
    logger.info(f"Failed: {len(failed_builds)}")

    if failed_builds:
        logger.error("\nFailed packages:")
        for result in failed_builds:
            logger.error(f"  - {result.profile_name}: {result.log_file}")
        return 1
    else:
        logger.info("\nAll packages created successfully!")
        return 0


@conan_subcommand()
def hal_flash(conan_api: ConanAPI, parser, subparser, *args):
    """
    Flash binary to target device
    """
    subparser.add_argument('--profile', required=True,
                           help='Profile of the binary to flash')
    subparser.add_argument('--port', help='Serial port for flashing')
    subparser.add_argument('--binary', help='Path to binary file')
    subparser.add_argument('--verify', action='store_true',
                           help='Verify after flashing')
    args = parser.parse_args(*args)

    logger.info(f"Flashing to device on {args.port}...")
    logger.info("TODO: Implement flash command")


@conan_subcommand()
def hal_debug(conan_api: ConanAPI, parser, subparser, *args):
    """
    Start debug session with target device
    """
    subparser.add_argument('--profile', help='Profile to debug')
    subparser.add_argument('--port', help='Debug port')
    subparser.add_argument('--gdb', action='store_true', help='Use GDB')
    args = parser.parse_args(*args)

    logger.info("Starting debug session...")
    logger.info("TODO: Implement debug command")


@conan_command(group="libhal")
def hal(conan_api: ConanAPI, parser, *args):
    """
    libhal development tools for embedded systems
    """
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    # parser.add_argument(
    #     '--version',
    #     action='version',
    #     version='conan-hal-command: 0.0.0',
    #     help='Show version and exit'
    # )

    parser.epilog = """
Examples:
  conan hal setup
  conan hal new project my-robot
  conan hal flash --binary=app.elf.bin --target=stm32f103c8 --port=/dev/ttyUSB0

Use "conan hal <command> --help" for more information on a specific command.
"""

    # Parse args to get verbose flag
    parsed_args, _ = parser.parse_known_args(*args)

    # Configure logging based on verbose flag
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        force=True
    )

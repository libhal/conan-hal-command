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

from conan.api.conan_api import ConanAPI
from conan.cli.command import conan_command, conan_subcommand


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

    print(f"Creating new {args.type}: {args.name}")
    print(f"TODO: Implement new command")


@conan_subcommand()
def hal_setup(conan_api: ConanAPI, parser, subparser, *args):
    """
    Set up libhal development environment (remotes + profiles)
    """
    subparser.add_argument(
        '--skip-remotes', action='store_true', help='Skip remote configuration')
    subparser.add_argument(
        '--skip-profiles', action='store_true', help='Skip profile installation')
    args = parser.parse_args(*args)

    print("Setting up libhal environment...")
    print(f"TODO: Implement setup command")


@conan_subcommand()
def hal_install(conan_api: ConanAPI, parser, subparser, *args):
    """
    Install profiles or cross-compilers
    """
    subparser.add_argument('what', choices=['profiles', 'compilers', 'all'],
                           help='What to install')
    subparser.add_argument('--arch', help='Architecture to install for')
    args = parser.parse_args(*args)

    print(f"Installing {args.what}...")
    print(f"TODO: Implement install command")


@conan_subcommand()
def hal_build_matrix(conan_api: ConanAPI, parser, subparser, *args):
    """
    Build against multiple profiles/configurations
    """
    subparser.add_argument('--all', action='store_true',
                           help='Build for all profiles')
    subparser.add_argument('--profiles', nargs='+',
                           help='Specific profiles to build')
    subparser.add_argument('--configurations', nargs='+',
                           help='Build configurations')
    args = parser.parse_args(*args)

    print("Building matrix...")
    print(f"TODO: Implement build-matrix command")


@conan_subcommand()
def hal_deploy(conan_api: ConanAPI, parser, subparser, *args):
    """
    Build and create packages for deployment
    """
    subparser.add_argument('--remote', help='Remote to deploy to')
    subparser.add_argument('--profile', help='Profile to use')
    args = parser.parse_args(*args)

    print("Deploying packages...")
    print(f"TODO: Implement deploy command")


@conan_subcommand()
def hal_profiles(conan_api: ConanAPI, parser, subparser, *args):
    """
    Manage libhal profiles
    """
    subparser.add_argument('action', choices=['list', 'show', 'create', 'delete'],
                           help='Action to perform')
    subparser.add_argument('--name', help='Profile name')
    args = parser.parse_args(*args)

    print("Managing profiles...")
    print(f"TODO: Implement profiles command")


@conan_subcommand()
def hal_package(conan_api: ConanAPI, parser, subparser, *args):
    """
    Create Conan package without deployment
    """
    subparser.add_argument('--profile', help='Profile to use')
    subparser.add_argument('--export', action='store_true',
                           help='Export to local cache')
    args = parser.parse_args(*args)

    print("Creating package...")
    print(f"TODO: Implement package command")


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

    print(f"Flashing to device on {args.port}...")
    print(f"TODO: Implement flash command")


@conan_subcommand()
def hal_debug(conan_api: ConanAPI, parser, subparser, *args):
    """
    Start debug session with target device
    """
    subparser.add_argument('--profile', help='Profile to debug')
    subparser.add_argument('--port', help='Debug port')
    subparser.add_argument('--gdb', action='store_true', help='Use GDB')
    args = parser.parse_args(*args)

    print("Starting debug session...")
    print(f"TODO: Implement debug command")


@conan_command(group="libhal")
def hal(conan_api: ConanAPI, parser, *args):
    """
    libhal development tools for embedded systems
    """
    parser.epilog = """
Examples:
  conan hal new project my-robot
  conan hal setup
  conan hal build-matrix --all
  conan hal flash --profile stm32f103c8 --port /dev/ttyUSB0

Use "conan hal <command> --help" for more information on a specific command.
"""

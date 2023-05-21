import base64
import logging
import os
import shlex
import shutil
import subprocess
import sys

from contextlib import ExitStack
from dataclasses import dataclass
from tempfile import NamedTemporaryFile


class CommandLineOptions:
    """
    Utility class for manipulating command line options.
    """

    def __init__(self):
        self._store: dict[str, str | bool] = {}

    @staticmethod
    def normalize(argument: str) -> str:
        """
        Normalize the argument name to the inner argument representation
        to avoid duplicates.
        """
        return argument.removeprefix("--").replace("_", "-").lower()

    def set(self, argument: str, value: str | bool = True) -> None:
        """
        Set or unset a command line argument.
        """
        if not value:
            self.unset(argument)
            return

        if isinstance(value, str) and value.lower() == "true":
            value = True

        self._store[self.normalize(argument)] = value

    def unset(self, argument: str) -> str | bool:
        """
        Remove a command line argument.
        """
        return self._store.pop(self.normalize(argument))

    def __iter__(self):
        """
        Iterate over the formatted command line arguments.
        """
        for k, v in self._store.items():
            yield f"--{k}" if v is True else f"--{k}={v}"


@dataclass
class Context:
    """
    Dataclass used to hold the global runtime context.
    """

    arguments: list[str]
    logger: logging.Logger
    on_exit: ExitStack
    options: CommandLineOptions
    inputs: dict[str, str]


def setup_private_key(context: Context) -> None:
    """
    If available, write the private key to a file so salt-ssh can access
    it.
    """
    if "PRIVATE-KEY" not in context.inputs:
        return

    private_key = base64.b64decode(context.inputs.pop("PRIVATE-KEY"))

    f = NamedTemporaryFile("w", delete=False, encoding="utf-8")
    f.write(private_key.decode())
    f.close()

    context.on_exit.callback(lambda: os.remove(f.name))
    context.options.set("--priv", f.name)


def setup_known_hosts(context: Context) -> None:
    """
    If available, write to the known hosts file.
    """
    known_hosts_file = "/etc/ssh/ssh_known_hosts"

    if "KNOWN-HOSTS" in context.inputs:
        known_hosts = base64.b64decode(context.inputs.pop("KNOWN-HOSTS"))

        f = open(known_hosts_file, "+w", encoding="utf-8")
        f.write(known_hosts.decode())
        f.close()

        context.on_exit.callback(lambda: os.remove(known_hosts_file))

    elif "KNOWN-HOSTS-FILE" in context.inputs:
        shutil.copy(context.inputs.pop("KNOWN-HOSTS-FILE"), known_hosts_file)
        context.on_exit.callback(lambda: os.remove(known_hosts_file))


def prepend_option_paths(context: Context) -> None:
    """
    Loop over options that may contain paths and prepend the mountpoint
    made by GitHub.
    """
    options_with_paths = (
        "CONFIG-DIR",
        "EXTRA-FILEREFS",
        "KNOWN-HOSTS-FILE",
        "LOG-FILE",
        "OUTPUT-FILE",
        "PRIV",
        "ROSTER-FILE",
        "SALTFILE",
    )

    for option in options_with_paths:
        if option in context.inputs:
            context.inputs[option] = os.path.normpath(
                os.path.join("/", "github", "workspace", context.inputs[option])
            )


def run(context: Context) -> None:
    """
    Setup options and run salt-ssh.
    """
    prepend_option_paths(context)
    setup_private_key(context)
    setup_known_hosts(context)

    for k, v in context.inputs.items():
        context.options.set(k, v)

    command = ["salt-ssh", *context.options, *context.arguments]
    context.logger.debug("Will run command %s:", command)

    subprocess.run(command, check=True, env=os.environ)


def main() -> int:
    """
    Main entrypoint.
    """
    logging.basicConfig(format="[%(levelname)-9s] %(message)s", level=logging.DEBUG)
    logger = logging.getLogger()

    try:
        if sys.argv[1] == "test":
            subprocess.run(["/usr/sbin/sshd"], check=True)
    except IndexError:
        pass

    args = [
        os.environ.pop("INPUT_TARGET"),
        os.environ.pop("INPUT_FUNCTION"),
        *shlex.split(os.environ.pop("INPUT_ARGUMENTS")),
    ]
    logger.debug("Received arguments %s:", args)

    inputs = {
        k.removeprefix("INPUT_"): v
        for k, v in os.environ.items()
        if v and k.startswith("INPUT_")
    }
    logger.debug("Received inputs: %s", inputs)

    with ExitStack() as exitstack:
        try:
            run(Context(args, logger, exitstack, CommandLineOptions(), inputs))
        except KeyboardInterrupt:
            return 1
        except Exception as exception:
            import traceback

            traceback.print_exception(exception)
        else:
            return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

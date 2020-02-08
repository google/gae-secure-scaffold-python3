import os
import re
import subprocess
import urllib.parse
import urllib.request


class DatastoreEmulator:
    """Helper to create an instance of the datastore emulator.

    Requires the gcloud command be on the $PATH.
    """

    default_project = "test"
    # Work around a bug where NDB cannot connect to "::1".
    default_host_port = "localhost"
    startup_pattern = re.compile(r"\[datastore\] API endpoint: (.*)")

    def __init__(
        self,
        consistency=None,
        data_dir=None,
        host_port=None,
        store_on_disk=None,
        project=None,
        quiet=True,
        environ=os.environ,
    ):
        self.consistency = consistency
        self.data_dir = data_dir
        self.host_port = host_port or self.default_host_port
        self.store_on_disk = store_on_disk
        self.project = project or self.default_project
        self.quiet = quiet
        self.environ = environ
        self._proc = None
        self._env = {}

    def start(self):
        """Start an emulator instance."""
        args = [
            "gcloud",
            "beta",
            "emulators",
            "datastore",
            "start",
            "--project",
            self.project,
        ]

        # Special case for --quiet, which needs to come before the sub-command.
        # If quiet is True, and you don't have the beta commands, they get
        # installed automatically.
        if self.quiet:
            args.insert(1, "--quiet")

        # And optional emulator flags.
        for name in ("data_dir", "host_port", "store_on_disk", "consistency"):
            value = getattr(self, name)

            if value is not None:
                flag_name = name.replace("_", "-")

                if isinstance(value, bool):
                    # "--store-on-disk" vs --no-store-on-disk".
                    flag = ("--" if value else "--no-") + flag_name
                    args.append(flag)
                else:
                    flag = "--" + flag_name
                    args.extend([flag, str(value)])

        self._proc = subprocess.Popen(args, stderr=subprocess.PIPE, text=True)
        self._env = self._parse_startup(self._proc.stderr, self.project)

        if self.environ is not None:
            self.env_init(self.environ)

    def stop(self):
        """Stop the running emulator instance."""
        shutdown_url = self._env["DATASTORE_HOST"] + "/shutdown"
        req = urllib.request.Request(shutdown_url, method="POST")
        urllib.request.urlopen(req)

    def env_init(self, environ) -> None:
        """Add info about the emulator to the process environment."""
        environ.update(self._env)

    @classmethod
    def _parse_startup(cls, fh, project: str):
        # Reading startup has the side-effect of blocking until the emulator
        # is ready for connections. Things that can happen:
        # - Success: "[datastore] API endpoint http://..."
        # - Failure: "ERROR: (gcloud) ..."
        for line in fh:
            match = cls.startup_pattern.match(line)

            if match:
                url = match.group(1)
                env = cls._parse_env_url(url)
                env["DATASTORE_DATASET"] = project
                env["DATASTORE_PROJECT_ID"] = project
                env["GOOGLE_CLOUD_PROJECT"] = project

                return env
        else:
            raise RuntimeError("Failed to start the datastore emulator")

    @classmethod
    def _parse_env_url(cls, url: str) -> dict:
        # url will be like "http://localhost:8081".
        result = urllib.parse.urlparse(url)
        env = {
            "DATASTORE_DATASET": "",
            "DATASTORE_EMULATOR_HOST": result.netloc,
            "DATASTORE_EMULATOR_HOST_PATH": result.netloc + "/datastore",
            "DATASTORE_HOST": url,
            "DATASTORE_PROJECT_ID": "",
            "GOOGLE_CLOUD_PROJECT": "",
        }

        return env

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class DatastoreEmulatorForTests(DatastoreEmulator):
    default_project = "in-memory-test"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("consistency", "1.0")
        kwargs.setdefault("store_on_disk", False)

        super().__init__(*args, **kwargs)

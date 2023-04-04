"""Invoke tasks."""
import os

from distutils.util import strtobool
from invoke import Collection, task as invoke_task


NETBOX_VERSION = "v3.4.4"

namespace = Collection("netbox")
namespace.configure(
    {
        "netbox": {
            "project_name": "netbox-nornir",
            "python_ver": "3.9",
            "local": bool(strtobool(os.environ.get("INVOKE_NETBOX_LOCAL", "false"))),
            "compose_dir": os.path.join(os.path.dirname(__file__), "docker/"),
            "local_compose_files": [
                "docker-compose.local.yml",
            ],
            "dev_compose_files": [
                "docker-compose.yml",
                "docker-compose.dev.yml",
            ],
            "prod_compose_files": [
                "docker-compose.yml",
                "docker-compose.prod.yml",
            ],
        }
    }
)


def is_truthy(arg):
    """Convert "truthy" strings into Booleans.

    Examples:
        >>> is_truthy('yes')
        True
    Args:
        arg (str): Truthy string (True values are y, yes, t, true, on and 1; false values are n, no,
        f, false, off and 0. Raises ValueError if val is anything else.
    """
    if isinstance(arg, bool):
        return arg
    return bool(strtobool(arg))


def task(function=None, *args, **kwargs):
    """Task decorator to override the default Invoke task decorator."""

    def task_wrapper(function=None):
        """Wrapper around invoke.task to add the task to the namespace as well."""
        if args or kwargs:
            task_func = invoke_task(*args, **kwargs)(function)
        else:
            task_func = invoke_task(function)
        namespace.add_task(task_func)
        return task_func

    if function:
        # The decorator was called with no arguments
        return task_wrapper(function)
    # The decorator was called with arguments
    return task_wrapper


def docker_compose(context, command, target="dev", **kwargs):
    """Helper function for running a specific docker compose command with all appropriate parameters and environment.

    Args:
        context (obj): Used to run specific commands
        command (str): Command string to append to the "docker compose ..." command, such as "build", "up", etc.
        **kwargs: Passed through to the context.run() call.
    """
    compose_command = f'docker compose --project-name {context.netbox.project_name} --project-directory "{context.netbox.compose_dir}"'

    for compose_file in getattr(context.netbox, f"{target}_compose_files"):
        compose_file_path = os.path.join(context.netbox.compose_dir, compose_file)
        compose_command += f' -f "{compose_file_path}"'

    compose_command += f" {command}"

    # If `service` was passed as a kwarg, add it to the end.
    service = kwargs.pop("service", None)
    if service is not None:
        compose_command += f" {service}"

    print(f'Running docker compose command "{command}"')

    return context.run(
        compose_command,
        env={"PYTHON_VER": context.netbox.python_ver},
        **kwargs,
    )


def run_cmd(context, command, **kwargs):
    """Run a command locally or inside container."""
    if is_truthy(context.netbox.local):
        context.run(command, pty=True, **kwargs)
    else:
        # Check if netbox is running; no need to start another netbox container to run a command
        docker_compose_status = "ps --services --filter status=running"
        results = docker_compose(context, docker_compose_status, hide="out")
        if "netbox" in results.stdout:
            compose_command = f"exec netbox {command}"
        else:
            compose_command = f"run --entrypoint '{command}' netbox"
        docker_compose(context, compose_command, pty=True)


@task(help={"container": "Name of the container to shell into"})
def cli(context, container="netbox"):
    """Launch a bash shell inside the running netbox container."""
    docker_compose(context, f"exec {container} bash", pty=True)


@task(
    help={
        "user": "Name of the superuser to create. (Default: admin)",
    }
)
def createsuperuser(context, user="admin"):
    """Create a new netbox superuser account (default: "admin"), will prompt for password."""
    command = "python manage.py createsuperuser --username admin"
    run_cmd(context, command)


@task(
    help={
        "force_rm": "Always remove intermediate containers.",
        "cache": "Whether to use Docker's cache when building the image. (Default: enabled)",
    }
)
def build(
    context,
    force_rm=False,
    cache=True,
    target="dev",
    image_name="netbox",
    tag="latest",
):
    """Build netbox docker image."""
    command = f"build --build-arg PYTHON_VER={context.netbox.python_ver}"

    if not cache:
        command += " --no-cache"
    if force_rm:
        command += " --force-rm"

    print(f"Building netbox with Python {context.netbox.python_ver}...")
    docker_compose(context, command, target=target)


@task(
    help={
        "cache": "Whether to use Docker's cache when building the image. (Default: enabled)",
        "cache_dir": "Directory to use for caching buildx output. (Default: /home/travis/.cache/docker)",
        "platforms": "Comma-separated list of strings for which to build. (Default: linux/amd64)",
        "target": "Build target from the Dockerfile. (Default: dev)",
    }
)
def buildx(
    context,
    cache=False,
    cache_dir="",
    platforms="linux/amd64",
    target="dev",
    image_name="netbox",
):
    """Build netbox docker image using the experimental buildx docker functionality (multi-arch capablility)."""
    print(f"Building netbox with Python {context.netbox.python_ver} for {platforms}...")
    command = f"docker buildx build --tag {image_name} --platform {platforms} --load -f ./docker/Dockerfile --build-arg PYTHON_VER={context.netbox.python_ver} ."
    if not cache:
        command += " --no-cache"
    else:
        command += f" --cache-to type=local,dest={cache_dir}/{context.netbox.python_ver} --cache-from type=local,src={cache_dir}/{context.netbox.python_ver}"

    context.run(command, env={"PYTHON_VER": context.netbox.python_ver})


@task(
    help={
        "cache": "Whether to use Docker's cache when building the image. (Default: enabled)",
        "cache_dir": "Directory to use for caching buildx output. (Default: /home/travis/.cache/docker)",
        "platforms": "Comma-separated list of strings for which to build. (Default: linux/amd64)",
        "target": "Build target from the Dockerfile. (Default: dev)",
    }
)
def docker_build(
    context,
    cache=False,
    cache_dir="",
    platforms="linux/amd64",
    target="dev",
    image_name="netbox",
):
    """Build netbox docker image using the experimental buildx docker functionality (multi-arch capablility)."""
    print(f"Building netbox with Python {context.netbox.python_ver} for {platforms}...")
    command = f"docker build --tag {image_name} --platform {platforms} --target {target} -f ./docker/Dockerfile --build-arg PYTHON_VER={context.netbox.python_ver} ."
    if not cache:
        command += " --no-cache"
    else:
        command += f" --cache-to type=local,dest={cache_dir}/{context.netbox.python_ver} --cache-from type=local,src={cache_dir}/{context.netbox.python_ver}"

    context.run(command, env={"PYTHON_VER": context.netbox.python_ver})


@task(help={"service": "If specified, only affect this service."})
def debug(context, service=None, target="dev"):
    """Start netbox and its dependencies in debug mode."""
    print("Starting netbox in debug mode...")
    docker_compose(context, "up", service=service, target=target)


@task(help={"service": "If specified, only affect this service."})
def start(context, service=None, target="dev"):
    """Start netbox and its dependencies in detached mode."""
    print("Starting netbox in detached mode...")
    docker_compose(context, "up --detach", service=service, target=target)


@task(help={"service": "If specified, only affect this service."})
def restart(context, service=None, target="dev"):
    """Gracefully restart containers."""
    print("Restarting netbox...")
    docker_compose(context, "restart", service=service, target=target)


@task(help={"service": "If specified, only affect this service."})
def stop(context, service=None, target="dev"):
    """Stop netbox and its dependencies."""
    print("Stopping netbox...")
    if not service:
        docker_compose(context, "down", target=target)
    else:
        docker_compose(context, "stop", service=service, target=target)


@task
def destroy(context, target="dev"):
    """Destroy all containers and volumes."""
    print("Destroying netbox...")
    docker_compose(context, "down --volumes", target=target)


@task
def build_local_env(context):
    """Build local environment for development."""
    print("Building local environment...")

    context.run("rm -rf netbox")
    context.run("mkdir netbox")
    context.run(
        f"curl -L https://codeload.github.com/netbox-community/netbox/tar.gz/refs/tags/{NETBOX_VERSION} | tar -xz --strip=1 -C ./netbox"
    )
    context.run("pip install -r ./netbox/requirements.txt")
    context.run("poetry install")
    if not os.path.isfile("./docker/configuration/configuration.py"):
        context.run(
            "cp $(pwd)/docker/configuration/configuration.example.py $(pwd)/docker/configuration/configuration.py"
        )
    if not os.path.islink("./netbox/netbox/netbox/configuration.py"):
        context.run("rm -f $(pwd)/netbox/netbox/netbox/configuration.py")
        context.run("ln -s $(pwd)/docker/configuration/configuration.py $(pwd)/netbox/netbox/netbox/")
    print("To run with containerized db use `invoke debug --target=local` before starting Django process.")


@task
def manage(context, command, target="dev"):
    """Run a Django management command."""
    print(f"Running Django management command: {command}")
    docker_compose(context, f"run --rm netbox python3 ./manage.py {command}", target=target)


@task(help={"name": "Use this name for migration file(s). If unspecified, a name will be generated."})
def makemigrations(context, name=""):
    """Perform makemigrations operation in Django."""
    command = "python manage.py makemigrations"

    if name:
        command += f" --name {name}"

    run_cmd(context, command)


@task
def migrate(context):
    """Perform migrate operation in Django."""
    command = "python manage.py migrate"

    run_cmd(context, command)


@task()
def pytest(context):
    """Launch pytest for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    # Install python module
    exec_cmd = "pytest -vv"
    run_cmd(context, exec_cmd)


@task()
def black(context):
    """Launch black to check that Python files adherence to black standards.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "black --exclude ./workspace --check --diff ."
    run_cmd(context, exec_cmd)


@task()
def blacken(context):
    """Launch black to apply black standards to the code.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "black ."
    run_cmd(context, exec_cmd)


@task()
def flake8(context):
    """Launch flake8 for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "flake8 --exclude=./workspace,./netbox ."
    run_cmd(context, exec_cmd)


@task()
def pylint(context):
    """Launch pylint for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = 'find . -type f -name "*.py" | xargs pylint'
    run_cmd(context, exec_cmd)


@task()
def yamllint(context):
    """Launch yamllint to validate formatting.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = 'yamllint -d "{ignore: ./workspace}" .'
    run_cmd(context, exec_cmd)


@task()
def pydocstyle(context):
    """Launch pydocstyle to validate docstring.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "pydocstyle ."
    run_cmd(context, exec_cmd)


@task()
def bandit(context):
    """Launch bandit to validate basic static code security analysis.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "bandit --recursive ./"
    run_cmd(context, exec_cmd)


@task()
def tests(context):
    """Launch all tests for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    print("Running black...")
    black(context)
    print("Running flake8...")
    flake8(context)
    # print("Running pylint...")
    # pylint(context)
    print("Running yamllint...")
    yamllint(context)
    # print("Running pydocstyle...")
    # pydocstyle(context)
    # print("Running bandit...")
    # bandit(context)
    # print("Running pytest...")
    # pytest(context)

    print("All tests have passed!")

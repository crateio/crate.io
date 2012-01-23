import datetime
import os

from fabric.api import abort, env, hide, local, task


@task
def compile():
    BASE_DIR = os.path.dirname(env["real_fabfile"])

    with hide("stdout"):
        local("git stash save")

        local("%s collectstatic --noinput --clear" % os.path.join(BASE_DIR, "manage.py"))

        # Delete Non Less Files
        files_to_delete = set()
        for root, dirs, files in os.walk(os.path.join(BASE_DIR, "crate_project", "site_media", "static")):
            for file in files:
                if not file.endswith(".less"):
                    files_to_delete.add(os.path.abspath(os.path.join(root, file)))
        for f in files_to_delete:
            os.remove(f)

        # Compile the Less Files
        files_to_compile = set([
            os.path.join(BASE_DIR, "crate_project", "site_media", "static", "less", "bootstrap.less"),
            os.path.join(BASE_DIR, "crate_project", "site_media", "static", "less", "crate.less"),
        ])

        for f in files_to_compile:
            filename = os.path.splitext(os.path.basename(f))[0] + ".css"
            output_file = os.path.join(BASE_DIR, "crate_project", "static", "css", filename)
            local(" ".join(["lessc -x", f, output_file]))
            local("git add %s" % output_file)

        pending = False

        changes = local("git status --porcelain", capture=True)
        for line in changes.splitlines():
            if not line.startswith("??"):
                print line
                pending = True
                break

        if pending:
            local("git commit -m 'automatically compiled CSS files on %sZ'" % datetime.datetime.utcnow().isoformat())

        local("git stash pop")


@task
def deploy(instance=None):
    if instance is None:
        abort("Must provide an instance name.")

    # Get the Current Branch
    branch = local("git name-rev --name-only HEAD", capture=True)

    if branch.failed:
        abort("Unable to get the current branch name")

    # Compile Less Files
    compile()

    local("gondor deploy %(instance)s %(branch)s" % {"instance": instance, "branch": branch})


@task
def host():
    BASE_DIR = os.path.dirname(env["real_fabfile"])
    local("%s runserver" % os.path.join(BASE_DIR, "manage.py"))

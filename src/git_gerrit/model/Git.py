import subprocess
import shlex


class Git:
    def __init__(self):
        self.fetched = []

    def fetch(self, refspec, repo="origin"):
        if refspec not in self.fetched:
            self.cmd(f"git fetch {repo} {refspec}")
            self.fetched.append(refspec)

    def has_file(self, sha, path):
        try:
            self.cmd(f"git rev-parse --verify --quiet {sha}:{path}")
            return True
        except Exception:
            return False

    def cmd(self, cmd, output=[]):
        with subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            out, err = p.communicate()
            output[:] = [out, err]
            if p.returncode != 0:
                raise Exception('Failed: ' + cmd)

    def get_file(self, sha, path, target_file, content_if_missing=""):
        with open(target_file, 'w', encoding='utf-8') as f:
            if self.has_file(sha, path):
                output = []
                self.cmd(f"git show {sha}:{path}", output)
                f.write(output[0])
            else:
                f.write(content_if_missing)

    def index_clean(self):
        try:
            self.cmd("git diff-index --quiet HEAD")
            return True
        except Exception:
            return False

    def cherry_pick(self, sha):
        if self.index_clean():
            output = []
            try:
                self.cmd(f"git cherry-pick {sha}", output)
            except Exception as e:
                msg = str(e) + "\n" + output[0] + output[1]
                raise Exception(msg)
        else:
            raise Exception("Your index is dirty, reset, commit or stash your changes")

    def checkout(self, sha):
        if self.index_clean():
            output = []
            try:
                self.cmd(f"git checkout {sha}", output)
            except Exception as e:
                msg = str(e) + "\n" + output[0] + output[1]
                raise Exception(msg)
        else:
            raise Exception("Your index is dirty, reset, commit or stash your changes")

    def reset(self, sha):
        output = []
        try:
            self.cmd(f"git reset --hard {sha}", output)
        except Exception as e:
            msg = str(e) + "\n" + output[0] + output[1]
            raise Exception(msg)

import subprocess
import shlex

class Git(object):
    def __init__(self):
        self.fetched = []

    def fetch(self, refspec, repo="origin"):
        if refspec not in self.fetched:
            self.cmd("git fetch %s %s" % (repo, refspec))
            self.fetched.append(refspec)

    def has_file(self, sha, path):
        try:
            self.cmd("git rev-parse --verify --quiet %s:%s" % (sha, path))
            return True
        except Exception:
            return False

    def cmd(self, cmd, output=[]):
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        output[:] = [out, err]
        if p.returncode != 0:
            raise Exception('Failed: ' + cmd)

    def get_file(self, sha, path, target_file, content_if_missing=""):
        with open(target_file, 'w') as f:
            if self.has_file(sha, path):
                output = []
                self.cmd("git show %s:%s" % (sha, path), output)
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
                self.cmd("git cherry-pick %s" % (sha), output)
            except Exception as e:
                msg = str(e) + "\n" + output[0] + output[1]
                raise Exception(msg)
        else:
            raise Exception("Your index is dirty, reset, commit or stash your changes")

    def checkout(self, sha):
        if self.index_clean():
            output = []
            try:
                self.cmd("git checkout %s" % (sha), output)
            except Exception as e:
                msg = str(e) + "\n" + output[0] + output[1]
                raise Exception(msg)
        else:
            raise Exception("Your index is dirty, reset, commit or stash your changes")

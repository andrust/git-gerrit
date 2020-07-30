import datetime
import re
import urwid
import subprocess
import shlex

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import os
from threading import Thread
import time

from SelectableListItem import SelectableListItem

class Jenkins(object):
    def __init__(self, jenkins_url, user, token, colored=True):
        self.auth_token = HTTPBasicAuth(user, token)
        self.url = jenkins_url
        self.colored = colored


    def get_console_log(self, job, build_number):
        u = self.url
        u += '/job/'
        u += job
        u += '/'
        u += build_number
        if self.colored:
            u+='/logText/progressiveHtml?start=0'
        else:
            u += '/consoleText'
        log = requests.get(u, auth=self.auth_token, verify=False).content
        if self.colored:
            log = '<br/>\n'.join(log.splitlines())
            p = subprocess.Popen(shlex.split("elinks -dump -dump-color-mode 1 -dump-width 150 -dump-charset utf8 -no-references"), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
            log = p.communicate(input=log)[0]
        return log

    def get_console_log_since_line(self, job, build_number, since_line):
        new = self.get_console_log(job, build_number).splitlines()
        return '\n'.join(new[since_line:])


class StoppableThread(object):
    def __init__(self, fn, args, sleep_time):
        self.fn = fn
        self.args = args
        self.term_flag = False
        self.sleep_time = sleep_time
        self.t = Thread(target=self.run)
        self.t.start()

    def run(self):
        while False == self.term_flag:
            self.fn(*self.args)
            if self.sleep_time > 0.1:
                sleeped = 0.0
                while sleeped < self.sleep_time and not self.term_flag:
                    time.sleep(0.1)
                    sleeped += 0.1
            else:
                time.sleep(0.1)

    def terminate(self):
        self.term_flag = True
        self.t.join()


class CIJobs(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, active_patch_number):
        self.console_refresher = None
        self.main = gerrittui
        if "colored_console" in self.main.cfg.keys():
            self.colored_console_log = self.main.cfg["colored_console"]
        else:
            self.colored_console_log = False

        super(CIJobs, self).__init__(urwid.Filler(urwid.Text("Loading")))
        self.refresh(change, active_patch_number)

    def refresh(self, change, active_patch_number):
        results = []
        if 'ci' in self.main.cfg:
            ci_id = self.main.gerrit.accounts(self.main.cfg['ci']['ci_user'])["_account_id"]

            for v in get_job_status(change, self.main.cfg['ci']['jenkins_url'], ci_id, active_patch_number).itervalues():
                txt = "%20s[%3s]: %s" % (v.name, v.id, v.status)
                results.append(SelectableListItem(("job_" + v.status, txt)))
                urwid.connect_signal(results[-1], "click", self.open_popup, v)

        self._w = urwid.ListBox(results)


    def close_popup(self, widget=None):
        if self.console_refresher is not None:
            self.console_refresher.terminate()
            self.console_refresher = None
        self.main.close_popup()


    def pull_log(self, w, target_file):
        with open(target_file, "w") as f:
            if 'ci' in self.main.cfg:
                txt = Jenkins(self.main.cfg['ci']['jenkins_url'], self.main.cfg['user'], self.main.cfg['ci']['jenkins_token'], self.colored_console_log).get_console_log(w.name, w.id)
            else:
                txt = "No jenkins setting in config!"
            f.write(txt)
            self.log_len = len(txt.splitlines())


    def refresh_log(self, w, target_file):
        with open(target_file, "a") as f:
            if 'ci' in self.main.cfg:
                txt = Jenkins(self.main.cfg['ci']['jenkins_url'], self.main.cfg['user'], self.main.cfg['ci']['jenkins_token'], self.colored_console_log).get_console_log_since_line(w.name, w.id, self.log_len)
            else:
                txt = "No jenkins setting in config!"
            txt_len = len(txt.splitlines())
            self.log_len += txt_len
            if txt_len > 0:
                f.write('\n')
            f.write(txt)

    def open_popup(self, w):
        logfile = os.path.join(self.main.cfg['tmp_dir'], "JenkinsConsole.txt")
        self.pull_log(w, logfile)
        self.console_refresher = StoppableThread(self.refresh_log, (w, logfile), 2.0)

        term = urwid.Terminal(["/bin/less", '-R', logfile], main_loop=self.main.mainloop, escape_sequence='meta a')
        term.change_focus(True)
        urwid.connect_signal(term, "closed", self.close_popup)
        self.main.open_popup(urwid.LineBox(term), ("relative", 80), ("relative", 80))


class JobInfo(object):
    def __init__(self, name, id, status, ts):
        self.name = name
        self.id = id
        self.status = status
        self.ts = ts

    @staticmethod
    def assign(lhs, rhs):
        if lhs:
            if lhs.id > rhs.id:
                return lhs
            elif lhs.id < rhs.id:
                return rhs
            elif lhs.ts > rhs.ts:
                return lhs
        return rhs

def get_job_status(resp, url, ci_user_id, active_patch_number):
    build_started = re.compile("Build Started %s/job/([^/]*)/(\d*)/" % url)
    # build_started = re.compile("Build Started %s/job/([^/]*)/(\d*)/ \(\d*/\d*\)" % url)
    build_finished = re.compile("%s/job/([^/]*)/(\d*)/ : (\w*)" % url)

    jenkins_jobs = {}
    for m in reversed(resp['messages']):
        if 'author' not in m.keys():
            continue
        user_id = m['author']['_account_id']
        if user_id == ci_user_id:
            rev_num = m['_revision_number']
            if rev_num != active_patch_number:
                continue
            msg = m['message']

            match = build_started.search(msg)
            if match:
                m_date = datetime.datetime.strptime(m['date'][:-3], "%Y-%m-%d %H:%M:%S.%f").strftime('%s%f')
                name = match.group(1)
                id = match.group(2)
                jenkins_jobs[name] = JobInfo.assign(jenkins_jobs.get(name),
                                                    JobInfo(name, id, "STARTED", m_date))
            else:
                m_date = datetime.datetime.strptime(m['date'][:-3], "%Y-%m-%d %H:%M:%S.%f").strftime('%s%f')
                for x in build_finished.finditer(msg):
                    name = x.group(1)
                    id = x.group(2)
                    result = x.group(3)
                    jenkins_jobs[name] = JobInfo.assign(jenkins_jobs.get(name),
                                                        JobInfo(name, id, result, m_date))
    return jenkins_jobs

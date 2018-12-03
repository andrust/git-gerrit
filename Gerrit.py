import json
import requests
from requests.auth import HTTPBasicAuth

class Gerrit(object):
    def __init__(self, url, user, token, status_callback):
        self.status_callback = status_callback
        self.auth_token = HTTPBasicAuth(user, token)
        self.url = url
        self.account_cache = {}

    def query_changes(self, q=['owner:self', 'status:open'], o=[]):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/?q='
        u += '+'.join(q)
        if len(o):
            u += '&'
            u += '&'.join(['o=%s' % (i) for i in o])
        ret = json.loads(requests.get(u, auth=self.auth_token).text[4:])
        self.status_callback("Loaded")
        return ret

    def sha_to_id(self, sha):
        self.status_callback("Loading")
        c = self.query_changes([sha])
        self.status_callback("Loaded")
        return c[0]['id']

    def abandon(self, change_id):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/abandon/'
        requests.post(u, auth=self.auth_token, data='{}', headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")

    def submit(self, change_id, revision):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/revisions/'
        u += revision
        u += '/submit/'
        requests.post(u, auth=self.auth_token, data='{}', headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")

    def set_labels(self, change_id, revision, labels):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/revisions/'
        u += revision
        u += '/review/'
        req = json.dumps({"labels": labels})
        resp = requests.post(u, auth=self.auth_token, data=req, headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")
        return str(resp.status_code) + resp.text

    def post_comment(self, change_id, revision, comment):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/revisions/'
        u += revision
        u += '/review/'
        req = json.dumps({"message": comment})
        requests.post(u, auth=self.auth_token, data=req, headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")

    def change_details(self, change_id):
        self.status_callback("Loading")
        options = ['ALL_REVISIONS', 'ALL_COMMITS', 'ALL_FILES', 'MESSAGES', 'SUBMITTABLE', 'COMMIT_FOOTERS', 'DETAILED_LABELS', 'SUBMITTABLE']
        u = self.url
        u += '/changes/' + change_id
        u += '/?'
        u += '&'.join(['o=%s' % (i) for i in options])
        ret = json.loads(requests.get(u, auth=self.auth_token).text[4:])
        self.status_callback("Loaded")
        return ret

    def accounts(self, account_id='self'):
        if account_id in self.account_cache.keys():
            return self.account_cache[account_id]

        self.status_callback("Loading")
        u = self.url
        u += '/accounts/'
        u += str(account_id)

        ret = json.loads(requests.get(u, auth=self.auth_token).text[4:])
        self.account_cache[account_id] = ret
        self.status_callback("Loaded")
        return ret

    def reviewers(self, change_id):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/' + change_id
        u += '/reviewers/'
        ret = json.loads(requests.get(u, auth=self.auth_token).text[4:])
        self.status_callback("Loaded")
        return ret

    def add_reviewer(self, change_id, acc_id):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/reviewers/'
        req = json.dumps({"reviewer": str(acc_id)})
        requests.post(u, auth=self.auth_token, data=req, headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")

    def remove_reviewer(self, change_id, acc_id):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/'
        u += change_id
        u += '/reviewers/'
        u += str(acc_id)

        requests.delete(u, auth=self.auth_token)

        u += "/delete"
        req = json.dumps({"notify": "NONE"})
        requests.post(u, auth=self.auth_token, data=req, headers={"Content-Type": 'application/json'})
        self.status_callback("Loaded")

    def comments(self, change_id):
        self.status_callback("Loading")
        u = self.url
        u += '/changes/' + change_id
        u += '/comments/'
        ret = json.loads(requests.get(u, auth=self.auth_token).text[4:])
        self.status_callback("Loaded")
        return ret

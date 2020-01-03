import urwid

from Timestamp import Timestamp

class ChangeInfo(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, selected_revision_number, selected_revision_sha):
        self.main = gerrittui
        self.items = []
        super(ChangeInfo, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_number, selected_revision_sha)

    def add_item(self, field, value):
        self.items.append("%8s: %s" % (field, value))

    def refresh(self, change, selected_revision_number, selected_revision_sha):
        self.items = []
        self.add_item("Owner", self.main.gerrit.accounts(change["owner"]["_account_id"])["name"])
        self.add_item("Project", change["project"])
        self.add_item("Branch", change["branch"])
        self.add_item("State", change["status"].lower())
        self.add_item("Created", Timestamp(change["revisions"][selected_revision_sha]['created']).str)
        self.add_item("Updated", Timestamp(change["updated"]).str)
        self.add_item("Refspec", change["revisions"][selected_revision_sha]["ref"])
        self.add_item("Patchset", str(selected_revision_number))

        if change['status'] == 'NEW':
            mergeable = False
            submittable = False
            if "mergeable" in change.keys():
                mergeable = change["mergeable"]
            if "submittable" in change.keys():
                submittable = change["submittable"]

            if mergeable:
                if submittable:
                    self.add_item("Status", "ready to submit")
                else:
                    self.add_item("Status", "review needed")
            else:
                self.add_item("Status", "merge conflict")
        self._w = urwid.ListBox([urwid.Text(i) for i in self.items])

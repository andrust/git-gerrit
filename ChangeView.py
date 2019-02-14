# -*- coding: utf-8 -*-

import urwid
import os
import shutil

from FileList import FileList
from Comments import Comments
from JenkinsComments import JenkinsComments
from Reviewers import Reviewers
from ChangeInfo import ChangeInfo
from CommitMsg import CommitMsg

from AbandonAction import AbandonAction
from ReviewAction import ReviewAction
from PublishAction import PublishAction
from InstantSubmitAction import InstantSubmitAction
from SubmitAction import SubmitAction
from SelectPatchSetAction import SelectPatchSetAction
from CommentAction import CommentAction
from ManageReviewersAction import ManageReviewersAction
from CIJobs import CIJobs
from DLCherryPickAction import DLCherryPickAction
from DLCheckoutAction import DLCheckoutAction

class ChangeView(urwid.WidgetWrap):
    def __init__(self, gerrittui, change_id):
        self.change_id = change_id
        self.main = gerrittui
        super(ChangeView, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.clear_tempdir()

        # State
        self.change = self.main.gerrit.change_details(self.change_id)
        self.change_reviewers = self.main.gerrit.reviewers(self.change_id)
        self.active_revision_number = self.change['revisions'][self.change['current_revision']]['_number']
        self.active_revision_sha = self.change['current_revision']

        # Contents
        self.filelist = FileList(gerrittui, self.change, self.active_revision_sha)
        self.comments = Comments(self.main, self.change)
        self.jenkins_comments = JenkinsComments(self.main, self.change, self.active_revision_number)
        self.reviewers = Reviewers(self.change_reviewers)
        self.change_info = ChangeInfo(self.main, self.change, self.active_revision_number, self.active_revision_sha)
        self.commit_msg = CommitMsg(self.change, self.active_revision_sha)
        self.ci_jobs = CIJobs(self.main, self.change, self.active_revision_number)

        self.setup_layout()

    def clear_tempdir(self):
        tmpdir = self.main.cfg['tmp_dir']
        for f in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, f)
            if os.path.isdir(fpath):
                shutil.rmtree(fpath)
            else:
                os.unlink(fpath)


    def setup_layout(self):
        top_row = urwid.Columns([self.commit_msg, self.change_info, self.reviewers])
        file_row = urwid.Columns([self.filelist, self.ci_jobs])
        comments_row = urwid.Columns([self.comments, self.jenkins_comments])

        main_column = urwid.Pile([top_row, file_row, comments_row])
        actions_column = self.actions()

        self._w = urwid.Columns([(19, actions_column), main_column], dividechars=1, box_columns=[1])

    def actions(self):
        buttons = []
        buttons.append(ReviewAction(self)),
        if self.change["status"] == 'NEW':
            buttons.append(SubmitAction(self)),
            buttons.append(InstantSubmitAction(self)),
        if self.change["status"] == 'DRAFT':
            buttons.append(PublishAction(self)),
        buttons.append(SelectPatchSetAction(self)),
        buttons.append(CommentAction(self)),
        buttons.append(ManageReviewersAction(self)),
        if self.change["status"] in ['NEW', 'DRAFT']:
            buttons.append(AbandonAction(self)),
        buttons.append(urwid.Divider()),
        buttons.append(urwid.Divider()),
        buttons.append(urwid.Divider()),
        buttons.append(urwid.Text('Download')),
        buttons.append(urwid.Divider()),
        buttons.append(DLCherryPickAction(self)),
        buttons.append(DLCheckoutAction(self))

        return urwid.Filler(urwid.ListBox(buttons), height=len(buttons), valign='middle', min_height=len(buttons))

    def refresh(self):
        self.change = self.main.gerrit.change_details(self.change_id)
        self.change_reviewers = self.main.gerrit.reviewers(self.change_id)

        self.filelist.refresh(self.change, self.active_revision_sha)
        self.comments.refresh(self.change)
        self.jenkins_comments.refresh(self.change, self.active_revision_number)
        self.reviewers.refresh(self.change_reviewers)
        self.change_info.refresh(self.change, self.active_revision_number, self.active_revision_sha)
        self.commit_msg.refresh(self.change, self.active_revision_sha)
        self.ci_jobs.refresh(self.change, self.active_revision_number)

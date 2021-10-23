# -*- coding: utf-8 -*-

import urwid
import os
import shutil

from git_gerrit.model.FileList import FileList
from git_gerrit.model.Comments import Comments
from git_gerrit.model.JenkinsComments import JenkinsComments
from git_gerrit.model.Reviewers import Reviewers
from git_gerrit.model.ChangeInfo import ChangeInfo
from git_gerrit.model.CommitMsg import CommitMsg
from git_gerrit.model.InputHandler import InputHandler

from git_gerrit.action.AbandonAction import AbandonAction
from git_gerrit.action.ReviewAction import ReviewAction
from git_gerrit.action.PublishAction import PublishAction
from git_gerrit.action.InstantSubmitAction import InstantSubmitAction
from git_gerrit.action.SubmitAction import SubmitAction
from git_gerrit.action.RestoreAction import RestoreAction
from git_gerrit.action.SelectPatchSetAction import SelectPatchSetAction
from git_gerrit.action.CommentAction import CommentAction
from git_gerrit.action.ManageReviewersAction import ManageReviewersAction
from git_gerrit.model.CIJobs import CIJobs
from git_gerrit.action.DLCherryPickAction import DLCherryPickAction
from git_gerrit.action.DLCheckoutAction import DLCheckoutAction
from git_gerrit.action.GitResetHeadAction import GitResetHeadAction
from git_gerrit.action.GitResetPrevAction import GitResetPrevAction
from git_gerrit.model.RelatedChanges import RelatedChanges

class ChangeView(urwid.WidgetWrap):
    def __init__(self, gerrittui, change_id):
        self.change_id = change_id
        self.main = gerrittui
        super(ChangeView, self).__init__(urwid.Filler(urwid.Text("Loading...")))

        self.hotkeys = {}

        # State
        self.change = self.main.gerrit.change_details(self.change_id)
        self.change_reviewers = self.main.gerrit.reviewers(self.change_id)
        self.active_revision_number = self.change['revisions'][self.change['current_revision']]['_number']
        self.active_revision_sha = self.change['current_revision']

        # Contents
        self.filelist = FileList(gerrittui, self.change, self.active_revision_sha)
        self.comments = Comments(self.main, self.change)
        self.jenkins_comments = JenkinsComments(self.main, self.change, self.active_revision_number)
        self.reviewers = Reviewers(self.change_reviewers, self.change['permitted_labels'].keys())
        self.change_info = ChangeInfo(self.main, self.change, self.active_revision_number, self.active_revision_sha)
        self.commit_msg = CommitMsg(self.change, self.active_revision_sha)
        self.ci_jobs = CIJobs(self.main, self.change, self.active_revision_number)
        self.related = RelatedChanges(self.main, self.change, self.active_revision_sha)

        self.setup_layout()


    def add_hotkey(self, key, action):
        self.hotkeys[key] = action


    def setup_layout(self):
        top_row = urwid.Columns([self.commit_msg, (40, self.change_info), (25, self.reviewers), self.related])
        file_row = urwid.Columns([self.filelist, self.ci_jobs])
        comments_row = urwid.Columns([self.comments, self.jenkins_comments])

        main_column = urwid.Pile([top_row, file_row, comments_row])
        actions_column = self.actions()

        self._w = InputHandler(urwid.Columns([(19, actions_column), main_column], dividechars=1, box_columns=[1]), self.hotkeys)

    def actions(self):
        buttons = []
        if self.change["status"] in ['NEW', 'DRAFT']:
            buttons.append(ReviewAction(self))
        if self.change["status"] == 'NEW':
            buttons.append(SubmitAction(self))
            buttons.append(InstantSubmitAction(self))
        if self.change["status"] == 'DRAFT':
            buttons.append(PublishAction(self))
        if self.change["status"] == 'ABANDONED':
            buttons.append(RestoreAction(self))
        buttons.append(SelectPatchSetAction(self))
        buttons.append(CommentAction(self))
        if self.change["status"] in ['NEW', 'DRAFT']:
            buttons.append(ManageReviewersAction(self))
        if self.change["status"] in ['NEW', 'DRAFT']:
            buttons.append(AbandonAction(self))
        buttons.append(urwid.Divider())
        buttons.append(urwid.Divider())
        buttons.append(urwid.Divider())
        buttons.append(urwid.Text('Download'))
        buttons.append(urwid.Divider())
        buttons.append(DLCherryPickAction(self))
        buttons.append(DLCheckoutAction(self))
        buttons.append(urwid.Divider())
        buttons.append(urwid.Text('Git'))
        buttons.append(GitResetHeadAction(self))
        buttons.append(GitResetPrevAction(self))


        return urwid.Filler(urwid.ListBox(buttons), height=len(buttons), valign='middle', min_height=len(buttons))

    def refresh(self):
        self.change = self.main.gerrit.change_details(self.change_id)
        self.change_reviewers = self.main.gerrit.reviewers(self.change_id)

        self.filelist.refresh(self.change, self.active_revision_sha)
        self.comments.refresh(self.change)
        self.jenkins_comments.refresh(self.change, self.active_revision_number)
        self.related.refresh(self.change, self.active_revision_sha)

        self.reviewers.refresh(self.change_reviewers)
        self.change_info.refresh(self.change, self.active_revision_number, self.active_revision_sha)
        self.commit_msg.refresh(self.change, self.active_revision_sha)
        self.ci_jobs.refresh(self.change, self.active_revision_number)

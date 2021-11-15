import json
import os
# pylint: disable=import-error
import vim


class FileDescriptor:
    def __init__(self, buffer_path):
        self.__comments = []
        self.__drafts = []
        self.__buffer = buffer_path

    @property
    def comments(self):
        return self.__comments

    @property
    def drafts(self):
        return self.__drafts

    @property
    def buffer(self):
        return self.__buffer

    def add_comment(self, message, row, author, date):
        c = Comment(message, row, author, date, CommentHandler.COMMENT_SIGN, self.__buffer)
        self.__comments.append(c)
        vim.command(f"sign place {c.id} line={row} name={CommentHandler.COMMENT_SIGN} file={self.__buffer}")

    def add_draft(self, message, row):
        c = Comment(message, row, "", "", CommentHandler.DRAFT_SIGN, self.__buffer)
        self.__drafts.append(c)
        vim.command(f"sign place {c.id} line={row} name={CommentHandler.DRAFT_SIGN} file={self.__buffer}")
        return c

    def delete_draft(self, in_buffer):
        to_remove = None
        for c in self.__drafts:
            if c.visible_in_buffer == in_buffer:
                to_remove = c
                break

        self.__drafts[:] = [x for x in self.__drafts if x.visible_in_buffer != in_buffer]

        if to_remove is not None:
            for c in self.__drafts:
                if c.row == to_remove.row:
                    break
            vim.command(f"sign unplace {to_remove.id}")


class Comment:
    def __init__(self, message, row, author, date, comment_type, commented_buffer):
        self.message = message
        self.row = row
        self.author = author
        self.date = date
        self.visible_in_buffer = None
        self.type = comment_type
        self.commented_buffer = commented_buffer
        self.id = CommentHandler.sign_id()

    def comment_content(self):
        content = [f"{self.author} on {self.date} wrote:", ""]
        return content + self.message.splitlines()

    def draft_content(self):
        return self.message.splitlines()

    def draft_serialize(self, patchset):
        content = {"line": self.row, "message": self.message, "patch_set": patchset}
        return content


class CommentHandler:
    COMMENT_SIGN = 'Comment'
    DRAFT_SIGN = 'Draft'
    sign_counter = 0

    @staticmethod
    def sign_id():
        CommentHandler.sign_counter += 1
        return CommentHandler.sign_counter

    def __init__(self, tmp_dir):
        self.__tmp_dir = os.path.join(tmp_dir, vim.eval("g:change_id"))
        self.__open_comments = []
        self.__diff_properties = {}

        self.setup_vim()
        with open(os.path.join(self.__tmp_dir, 'diff_properties.json'), 'r', encoding='utf-8') as f:
            self.__diff_properties = json.load(f)

        self.__before = FileDescriptor(self.__diff_properties['before']['fname'])
        self.__after = FileDescriptor(self.__diff_properties['after']['fname'])

        with open(os.path.join(self.__tmp_dir, 'comments.json'), 'r', encoding='utf-8') as f:
            self.load_comments(json.load(f))
        try:
            with open(os.path.join(self.__tmp_dir, 'drafts.json'), 'r', encoding='utf-8') as f:
                self.load_drafts(json.load(f))
        except Exception:
            pass

    def buffer_exists(self, filename):
        for buf in vim.buffers:
            if os.path.basename(buf.name) == filename:
                return True
        return False

    def setup_vim(self):
        vim.command(f"sign define {CommentHandler.COMMENT_SIGN} text=C")
        vim.command(f"sign define {CommentHandler.DRAFT_SIGN} text=D")
        vim.command('set splitbelow')

    def load_drafts(self, draft_json):
        for file_path_in_repo, comments in draft_json.items():
            for comment in comments:
                if 'line' not in comment.keys():
                    comment['line'] = 1

                if self.__diff_properties['after']['repopath'] == file_path_in_repo and self.__diff_properties['after']['patch_set'] == str(comment['patch_set']):
                    commented_descriptor = self.__after
                    self.commented_buffer = self.__diff_properties['after']['fname']
                elif self.__diff_properties['before']['repopath'] == file_path_in_repo and self.__diff_properties['before']['patch_set'] == str(comment['patch_set']):
                    commented_descriptor = self.__before
                    self.commented_buffer = self.__diff_properties['before']['fname']
                else:
                    continue

                commented_descriptor.add_draft(comment['message'], comment['line'])

    def load_comments(self, comments_json):
        for file_path_in_repo, comments in comments_json.items():
            for comment in comments:
                if 'line' not in comment.keys():
                    comment['line'] = 1

                if self.__diff_properties['after']['repopath'] == file_path_in_repo and self.__diff_properties['after']['patch_set'] == str(comment['patch_set']):
                    commented_descriptor = self.__after
                    self.commented_buffer = self.__diff_properties['after']['fname']
                elif self.__diff_properties['before']['repopath'] == file_path_in_repo and self.__diff_properties['before']['patch_set'] == str(comment['patch_set']):
                    commented_descriptor = self.__before
                    self.commented_buffer = self.__diff_properties['before']['fname']
                else:
                    continue

                commented_descriptor.add_comment(comment['message'], comment['line'], comment['author']['name'], comment['updated'][0:16])

    def open_comment(self, comment):
        comment.visible_in_buffer = self.open_split(CommentHandler.COMMENT_SIGN, comment.comment_content(), has_focus=False)
        self.__open_comments.append(comment)

    def open_draft(self, comment, has_focus=False):
        comment.visible_in_buffer = self.open_split(CommentHandler.DRAFT_SIGN, comment.draft_content(), has_focus=has_focus)
        self.__open_comments.append(comment)

    def open_split(self, file_type, content, has_focus=False):
        width = vim.current.window.width
        longlines = 0
        for line in content:
            longlines += int(len(line) / (width - 4))
        vim.command(f"{min(10, max(3, len(content) + longlines))}new")
        vim.command(f"set filetype={file_type}")
        vim.current.buffer[:] = content
        bufnum = vim.current.buffer.number
        if not has_focus:
            vim.command('wincmd p')
        return bufnum

    def close_splits(self):
        for c in self.__open_comments:
            try:
                vim.command(f"bdelete! {c.visible_in_buffer}")
                c.visible_in_buffer = None
            except vim.error:
                pass
        # self.__open_splits = []
        # self.__last_draft = None
        self.__open_comments = []

    def check_position_for_buffer(self, buffer, row):
        for c in buffer.comments:
            if c.row == row:
                self.open_comment(c)

        for c in buffer.drafts:
            if c.row == row:
                self.open_draft(c)

    def check_position(self, file_path, row):
        if not file_path:
            return

        if len(self.__open_comments) != 0:
            if file_path in (self.__before.buffer, self.__after.buffer):
                self.close_splits()

        if file_path == self.__before.buffer:
            self.check_position_for_buffer(self.__before, row)

        if file_path == self.__after.buffer:
            self.check_position_for_buffer(self.__after, row)

    def propose_draft(self, file_path, row, col):
        if file_path == self.__before.buffer:
            comment = self.__before.add_draft("", row)
        if file_path == self.__after.buffer:
            comment = self.__after.add_draft("", row)

        self.open_draft(comment, has_focus=True)
        vim.command('call SetMapping()')

    def save_draft(self):
        bufnr = vim.current.buffer.number

        for c in self.__open_comments:
            if c.visible_in_buffer == bufnr and c.type == CommentHandler.DRAFT_SIGN:
                c.message = '\n'.join(vim.current.buffer[:])
                break

    def dispose(self):

        drafts = None
        try:
            with open(os.path.join(self.__tmp_dir, 'drafts.json'), 'r', encoding='utf-8') as f:
                drafts = json.load(f)
        except Exception:
            drafts = {}

        if len(self.__before.drafts) > 0 or len(self.__after.drafts) > 0:
            drafts[self.__diff_properties['before']['repopath']] = []
            drafts[self.__diff_properties['after']['repopath']] = []
        else:
            drafts.pop(self.__diff_properties['before']['repopath'], None)
            drafts.pop(self.__diff_properties['after']['repopath'], None)

        for d in self.__before.drafts:
            drafts[self.__diff_properties['before']['repopath']].append(d.draft_serialize(self.__diff_properties['before']['patch_set']))

        for d in self.__after.drafts:
            drafts[self.__diff_properties['after']['repopath']].append(d.draft_serialize(self.__diff_properties['after']['patch_set']))

        with open(os.path.join(self.__tmp_dir, 'drafts.json'), 'w', encoding='utf-8') as f:
            json.dump(drafts, f)

    def discard_draft(self):
        bufnr = vim.current.buffer.number
        self.__before.delete_draft(bufnr)
        self.__after.delete_draft(bufnr)

    def next_comment_in_buffer(self, buf, row):
        next_row = len(vim.current.buffer)
        for c in buf.comments:
            if c.row < next_row and c.row > row:
                next_row = c.row
        for c in buf.drafts:
            if c.row < next_row and c.row > row:
                next_row = c.row
        vim.current.window.cursor = (next_row, 1)
        vim.command("normal! zz")

    def prev_comment_in_buffer(self, buf, row):
        next_row = 1
        for c in buf.comments:
            if c.row > next_row and c.row < row:
                next_row = c.row
        for c in buf.drafts:
            if c.row > next_row and c.row < row:
                next_row = c.row
        vim.current.window.cursor = (next_row, 1)
        vim.command("normal! zz")

    def next_comment(self, buffer_path, row):
        if self.__after.buffer == buffer_path:
            self.next_comment_in_buffer(self.__after, row)
        if self.__before.buffer == buffer_path:
            self.next_comment_in_buffer(self.__before, row)

    def prev_comment(self, buffer_path, row):
        if self.__after.buffer == buffer_path:
            self.prev_comment_in_buffer(self.__after, row)
        if self.__before.buffer == buffer_path:
            self.prev_comment_in_buffer(self.__before, row)


def get_config():
    rcpath = os.path.join(os.path.expanduser('~'), '.gerritrc.json')
    with open(rcpath, 'r', encoding='utf-8') as f:
        return json.load(f)


# Interface for vimdiff
cfg = get_config()
command_handler = CommentHandler(cfg['tmp_dir'])


def check_current_pos():
    row, _ = vim.current.window.cursor
    command_handler.check_position(vim.current.buffer.name, row)


def propose_draft():
    row, col = vim.current.window.cursor
    command_handler.propose_draft(vim.current.buffer.name, row, col)


def save_draft():
    command_handler.save_draft()


def discard_draft():
    command_handler.discard_draft()


def dispose():
    command_handler.dispose()


def next_comment():
    row, _ = vim.current.window.cursor
    command_handler.next_comment(vim.current.buffer.name, row)


def prev_comment():
    row, _ = vim.current.window.cursor
    command_handler.prev_comment(vim.current.buffer.name, row)

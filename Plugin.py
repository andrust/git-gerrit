import json
import os
import vim

class FileDescriptor(object):
    def __init__(self,filename):
        self.__filename = filename
        self.__comments = []

    @property
    def filename(self):
        return self.__filename

    @property
    def comments(self):
        return self.__comments

    def add_comment(self, message, row):
        self.__comments.append(Comment(message, row))

class Comment(object):
    def __init__(self, message, row):
        self.message = message
        self.row = row

class CommentHandler(object):
    COMMENT_SIGN = 'Comment'
    DRAFT_SIGN = 'Draft'
    sign_counter = 0

    @staticmethod
    def sign_id():
        CommentHandler.sign_counter += 1
        return CommentHandler.sign_counter

    def __init__(self, tmp_dir):
        self.__tmp_dir = tmp_dir
        self.__comments = {}
        self.__drafts = {}
        self.__last_draft = None
        self.__last_row = None
        self.__last_split = None

        self.setup_vim()
        self.load_comments(json.load(open(os.path.join(self.__tmp_dir, 'comments'))))

    def get_buffer(self, filename):
        return os.path.join(self.__tmp_dir, filename)

    def buffer_exists(self, filename):
        for buf in vim.buffers:
            if os.path.basename(buf.name) == filename:
                return True
        return False

    def setup_vim(self):
        vim.command('sign define %s text=C' % CommentHandler.COMMENT_SIGN)
        vim.command('sign define %s text=D' % CommentHandler.DRAFT_SIGN)
        vim.command('set splitbelow')
        vim.command('autocmd FileType %s nnoremap q :q!<cr>' % CommentHandler.COMMENT_SIGN)
        vim.command('autocmd FileType %s nnoremap q :call SaveDraft()<cr>:q!<cr>' % CommentHandler.DRAFT_SIGN)

    def load_comments(self, comments_json):
        for file,comments in comments_json.iteritems():
            file = os.path.basename(file)
            for comment in comments:
                filename = 'ps%d_%s' % (comment['patch_set'], file)

                if 'line' not in comment.iterkeys():
                    comment['line'] = 1

                if self.buffer_exists(filename):
                    vim.command('sign place %d line=%d name=%s file=%s' % (CommentHandler.sign_id(), comment['line'], CommentHandler.COMMENT_SIGN, self.get_buffer(filename)))

                if filename not in self.__comments:
                    self.__comments[filename] = FileDescriptor(filename)
                self.__comments[filename].add_comment(comment['message'], comment['line'])

    def open_split(self, type):
        vim.command('10new')
        vim.command('set filetype=%s' % type)
        self.__last_split = vim.current.buffer.number

    def check_position_in_dict(self, filename, row, comments_dict, sign):
        fd = comments_dict.get(filename, None)
        if fd and self.__last_row != row:
            for c in fd.comments:
                if c.row == row:
                    self.open_split(sign)
                    vim.current.buffer[:] = c.message.splitlines()
                    vim.command('wincmd p')



    def check_position(self, file_path, row):
        if not file_path:
            return

        if row != self.__last_row and self.__last_split is not None:
            vim.command('bdelete! %i' % (self.__last_split))
            self.__last_split = None

        filename = os.path.basename(file_path)
        self.check_position_in_dict(filename, row, self.__comments,
                                    CommentHandler.COMMENT_SIGN)
        self.check_position_in_dict(filename, row, self.__drafts,
                                    CommentHandler.DRAFT_SIGN)
        self.__last_row = row

    def propose_draft(self, file_path, row, col):
        filename = os.path.basename(file_path)
        self.__last_draft = self.__drafts.get(filename, FileDescriptor(filename))
        self.open_split(CommentHandler.DRAFT_SIGN)

    def save_draft(self):
        if self.__last_draft:
            vim.command('sign place %d line=%d name=%s file=%s' % (CommentHandler.sign_id(), self.__last_row, CommentHandler.DRAFT_SIGN, self.get_buffer(self.__last_draft.filename)))
            self.__last_draft.add_comment('\n'.join(vim.current.buffer[0:]),
                                          self.__last_row)

            self.__drafts[self.__last_draft.filename] = self.__last_draft
            self.__last_draft = None
            self.__last_split = None

    def dispose(self):
        # TODO: send drafts to gerrit
        with open(os.path.join(self.__tmp_dir, 'drafts.json'), 'w') as result:
            for fd in self.__drafts.itervalues():
                result.write('[%s]\n' % (fd.filename))
                for c in fd.comments:
                    result.write('%s:%d\n' % (c.message, c.row))
            result.write('\n')

def get_tmp_dir():
    rcpath = os.path.join(os.path.expanduser('~'), '.gerritrc.json')
    with open(rcpath, 'r') as f:
        return json.load(f)['tmp_dir']

command_handler = CommentHandler(get_tmp_dir())

def check_current_pos():
    row, col = vim.current.window.cursor
    command_handler.check_position(vim.current.buffer.name, row)

def propose_draft():
    row, col = vim.current.window.cursor
    command_handler.propose_draft(vim.current.buffer.name, row, col)

def save_draft():
    command_handler.save_draft()

def dispose():
    command_handler.dispose()

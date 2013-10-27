import sys
import sublime
import sublime_plugin
is_python3 = sys.version_info[0] > 2

if is_python3:
    from .typograph.typograph import Typograph
    from .Edit import Edit as Edit
else:
    from typograph import Typograph


class BaseTypographer(sublime_plugin.TextCommand):
    """Base Sorter"""

    def __init__(self, view):
        self.view = view

    def run(self, edit):
        self.settings = sublime.load_settings("Typographer.sublime-settings")
        # sublime.save_settings('Typographer.sublime-settings')

        selections = self.get_selections()

        threads = []
        for sel in selections:
            selbody = self.view.substr(sel)
            selbody = selbody.encode('utf-8')
            thread = Typograph(sel, selbody,
                self.settings.get('entity_type'),
                self.settings.get('add_br_tags'),
                self.settings.get('wrap_in_paragraph'),
                self.settings.get('maximum_nobr'))

            threads.append(thread)
            thread.start()

        self.handle_threads(edit, threads, selections, offset=0, i=0)

    def get_selections(self):
        selections = self.view.sel()

        # check if the user has any actual selections
        has_selections = False
        for sel in selections:
            if sel.empty() == False:
                has_selections = True

        # if not, add the entire file as a selection
        if not has_selections:
            full_region = sublime.Region(0, self.view.size())
            selections.add(full_region)

        return selections

    def handle_threads(self, edit, threads, selections, offset=0, i=0):

        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue
            self.handle_result(edit, thread, selections, offset)
        threads = next_threads

        if len(threads):
            sublime.set_timeout(lambda: self.handle_threads(edit, threads, selections, offset, i), 100)
            return

        self.view.end_edit(edit)
        sublime.status_message('Successfully typographed text')

    def handle_result(self, edit, thread, selections, offset):
        result = thread.result

        if thread.error:
            sublime.error_message(result)
            return
        elif result is None:
            sublime.error_message('There was an error typographing text.')
            return

        return thread


class TypographText(BaseTypographer):

    def handle_result(self, edit, thread, selections, offset):
        result = super(TypographText, self).handle_result(edit, thread, selections, offset)

        sel = thread.sel
        result = thread.result

        with Edit(self.view) as edit:
            edit.replace(sel, result);

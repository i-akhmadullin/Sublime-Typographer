import sublime
import sublime_plugin
from typograph import Typograph


class BaseTypographer(sublime_plugin.TextCommand):
    """Base Sorter"""

    def __init__(self, view):
        self.view = view

    def run(self, edit):
        self.settings = sublime.load_settings("Typographer.sublime-settings")
        # if not self.settings.has('entity_type'):
        #     self.settings.set('entity_type', 'html')
        # if not self.settings.has('add_br_tags'):
        #     self.settings.set('add_br_tags', 1)
        # if not self.settings.has('wrap_in_paragraph'):
        #     self.settings.set('wrap_in_paragraph', 'true')
        # if not self.settings.has('maximum_nobr'):
        #     self.settings.set('maximum_nobr', 3)

        # sublime.save_settings('Typographer.sublime-settings')

        selections = self.get_selections()
        TypographerCall = Typograph

        threads = []
        for sel in selections:
            selbody = self.view.substr(sel)
            selbody = selbody.encode('utf-8')
            thread = TypographerCall(sel, selbody,
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
        result = unicode(thread.result, 'utf-8')
        # result = thread.result
        # if offset:
            # sel = sublime.Region(thread.sel.begin() + offset, thread.sel.end() + offset)

        self.view.replace(edit, sel, result)

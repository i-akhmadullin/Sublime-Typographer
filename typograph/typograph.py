# -*- encoding: utf-8 -*-
import threading
import urllib
# import urllib2

from .RemoteTypograf import RemoteTypograf


class Typograph(threading.Thread):

    def __init__(self, sel, original, entity_type, add_br_tags, wrap_in_paragraph, maximum_nobr):
        self.sel = sel
        self.original = original
        self.result = None
        self.error = None

        self.entity_type = entity_type
        self.add_br_tags = add_br_tags
        self.wrap_in_paragraph = wrap_in_paragraph
        self.maximum_nobr = maximum_nobr
        threading.Thread.__init__(self)

    def exec_request(self):
        rt = RemoteTypograf('windows-1251')  # UTF-8

        entity_type = self.entity_type
        if entity_type == "html":
            rt.htmlEntities()
        elif entity_type == "xml":
            rt.xmlEntities()
        elif entity_type == "no":
            rt.noEntities()
        elif entity_type == "mixed":
            rt.mixedEntities()

        rt.br(self.add_br_tags)
        rt.p(self.wrap_in_paragraph)
        rt.nobr(self.maximum_nobr)

        processed_text = rt.processText(str(self.original, 'utf-8')).strip(' \n\r')
        if len(processed_text) > 0:
            return processed_text
        else:
            return None

    def run(self):
        try:
            self.result = self.exec_request()
        except (OSError):
            self.error = True
            self.result = 'Some OSError'
        except (urllib.error.HTTPError):  # as (e):
        # except (urllib2.HTTPError):  # as (e):
            self.error = True
            self.result = 'HTTP error %s contacting API'  # % (str(e.code))
        except (urllib.error.URLError):  # as (e):
        # except (urllib2.URLError):  # as (e):
            self.error = True
            self.result = 'Error: '  # + str(e.reason)

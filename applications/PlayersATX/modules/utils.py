from gluon.contrib.markdown.markdown2 import markdown
import urllib

def extractPipeEncodedValues(pipeEncodedString):
    """Returns a dict containing keys/values extract from a "pipe-encoded" string.
    A "pipe-encoded" string looks like this:
        "param1:value1|param2:value2"

    The above string would result in the following dictionary:
        {"param1": "value1", "param2": "value2"}
    """
    elems = pipeEncodedString.split('|')
    attrs = {}

    # String was not properly pipe encoded, so there are no attributes to extract
    if len(elems) == 1 and ":" not in elems[0]:
        return attrs

    for elem in elems:
        if elem:
            field, value = elem.split(':', 1)
            attrs[field] = value

    return attrs

def renderMarkdown(text):
    if text:
        text = markdown(text)
    return text


def maybeRenderMarkdown(text, should_render_markdown=False):
    if should_render_markdown:
        return renderMarkdown(text)

    return text


def unix_time(dt):
    from datetime import datetime
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0

def urldecode(string):
    return urllib.unquote_plus(string).decode('utf8')
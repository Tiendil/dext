# coding: utf-8


def mime_type_to_response_type(content_type):
    if content_type is None:
        return 'json'

    if any(tp in content_type for tp in ('application/xhtml+xml', 'text/html', 'text/plain', 'text/xml')):
        return 'html'

    if any(tp in content_type for tp in ('application/x-javascript',)):
        return 'js'

    return 'json'

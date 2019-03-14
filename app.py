#! /usr/bin/env python
"""
    WSGI APP to convert wkhtmltopdf As a webservice

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import json
import tempfile
import os

from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from executor import execute


@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return

    if not os.path.exists("/tmp/pdf"):
        os.makedirs("/tmp/pdf")

    request_is_json = request.content_type.endswith('json')

    with tempfile.NamedTemporaryFile(suffix='.html', dir='/tmp/pdf') as source_file:
        url = "";
        if request_is_json:
            # If a JSON payload is there, all data is in the payload
            payload = json.loads(request.data)
            if 'url' in payload:
                url = payload['url']
            else:
                source_file.write(payload['contents'].decode('base64'))
            options = payload.get('options', {})
        elif request.files:
            # First check if any files were uploaded
            source_file.write(request.files['file'].read())
            # Load any options that may have been provided in options
            options = json.loads(request.form.get('options', '{}'))

        source_file.flush()

        # Evaluate argument to run with subprocess
        args = ['wkhtmltopdf']

        # Add Global Options
        if options:
            for option, value in options.items():
                args.append('--%s' % option)
                if value:
                    args.append('"%s"' % value)

        # Add source file name and output file name
        file_name = url if url!="" else source_file.name
        result_file = tempfile.NamedTemporaryFile(suffix='.pdf', dir='/tmp/pdf')
        args += [file_name, result_file.name]

        # Execute the command using executor
        execute(' '.join(args))

        return Response(
            wrap_file(request.environ, open(result_file.name)),
            mimetype='application/pdf',
        )


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
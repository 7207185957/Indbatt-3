"""
Shared CSV export helper. Keeping this generic (rather than baking CSV
logic into each view) makes it straightforward to add Excel/PDF export
later - a new `export_xlsx()`/`export_pdf()` helper with the same
`(filename, headers, rows)` signature can be dropped in without touching
the report views themselves.
"""

import csv

from django.http import HttpResponse


def export_csv(filename, headers, rows):
    """
    Build a CSV HttpResponse.

    `headers` is a list of column titles.
    `rows` is an iterable of iterables (or of objects convertible via str()).
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response

import io
import zipfile

from extractors import extract_text


def _minimal_xlsx(rows):
    shared = []
    shared_index = {}

    def sidx(value):
        value = str(value)
        if value not in shared_index:
            shared_index[value] = len(shared)
            shared.append(value)
        return shared_index[value]

    row_xml = []
    for row_number, row_values in enumerate(rows, start=1):
        cells = []
        for col_number, value in enumerate(row_values, start=1):
            col_name = chr(ord("A") + col_number - 1)
            cells.append(
                f'<c r="{col_name}{row_number}" t="s"><v>{sidx(value)}</v></c>'
            )
        row_xml.append(f'<row r="{row_number}">{"".join(cells)}</row>')

    shared_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{len(shared)}" uniqueCount="{len(shared)}">'
        + "".join(f"<si><t>{value}</t></si>" for value in shared)
        + "</sst>"
    )

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Associados" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/sharedStrings.xml", shared_xml)
    return out.getvalue()


def test_extract_text_reads_xlsx_rows_for_rag_context():
    raw = _minimal_xlsx(
        [
            ["Associado", "Segmento"],
            ["ACME Energia", "Energia"],
            ["Beta Alimentos", "Alimentos"],
        ]
    )

    text, chars = extract_text("Base de Associados - Amcham RS. 2026.xlsx", raw)

    assert chars > 0
    assert "Sheet: Associados" in text
    assert "ACME Energia" in text
    assert "Beta Alimentos" in text

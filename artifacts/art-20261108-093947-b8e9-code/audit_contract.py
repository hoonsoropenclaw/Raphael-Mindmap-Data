import json

def normalize_text(text):
    return text.replace('（', '(').replace('）', ')').strip().replace(' ', '').replace('。', '.')

def check_unit_mismatch(axis_label, ticks_or_labels):
    if not axis_label or not ticks_or_labels:
        return False
    label_units = axis_label.split('(')[-1].split(')')[0]
    for item in ticks_or_labels:
        value = item.get('value')
        if value and any(unit in value for unit in ('元', '秒', '分鐘')):
            return label_units != value.split()[1]
    return False

def check_duplicate_source(chart_footer, slide_footer):
    chart_footer = normalize_text(chart_footer)
    slide_footer = normalize_text(slide_footer)
    return chart_footer == slide_footer

def check_missing_time_budget(notes):
    time_budget_pattern = r'(\d+\.?\d*)\s*(秒|分鐘)'
    match = re.search(time_budget_pattern, notes, re.IGNORECASE)
    return not match

def check_unverified_claim(title, notes, fields):
    verified_phrases = ['已驗算', '已核對', '已確認']
    if any(phrase in title or phrase in notes for phrase in verified_phrases):
        disambiguation = fields.get('disambiguation')
        return not disambiguation
    return False

def check_terminology_drift(fields, terms):
    if not fields:
        return False
    disambiguation = fields.get('disambiguation')
    for term1, term2 in terms.items():
        if (term1 in fields and term2 not in fields) or (term2 in fields and term1 not in fields) and not disambiguation:
            return True
    return False

def audit_contract(slides):
    findings = []
    for slide_id, slide in enumerate(slides, start=1):
        title = slide.get('title', '')
        notes = slide.get('notes', '')
        chart_footer = slide.get('chart', {}).get('footer', '')
        footer = slide.get('footer', '')
        fields = slide.get('fields', {})

        if check_unit_mismatch(slide.get('chart', {}).get('axis_label'), [item['value'] for item in slide.get('chart', {}).get('ticks', [])] + [item['value'] for item in slide.get('chart', {}).get('value_labels', [])]):
            findings.append({'slide_id': f's{slide_id:02d}', 'category': 'unit_mismatch', 'evidence': chart_footer})

        if check_duplicate_source(chart_footer, footer):
            findings.append({'slide_id': f's{slide_id:02d}', 'category': 'duplicate_source', 'evidence': chart_footer})

        if check_missing_time_budget(notes):
            findings.append({'slide_id': f's{slide_id:02d}', 'category': 'missing_time_budget', 'evidence': notes})

        if check_unverified_claim(title, notes, fields):
            findings.append({'slide_id': f's{slide_id:02d}', 'category': 'unverified_claim', 'evidence': title + notes})

        if check_terminology_drift(fields, {'校舍': '校園', '安東': 'Anton', '資料': '數據', '公文': '文書'}):
            findings.append({'slide_id': f's{slide_id:02d}', 'category': 'terminology_drift', 'evidence': title + notes})

    return findings

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Audit contract for compliance issues.')
    parser.add_argument('fixture', type=str, help='Path to the fixture JSON file')
    parser.add_argument('--out', type=str, default=None, help='Output path for the findings JSON')

    args = parser.parse_args()

    try:
        with open(args.fixture, 'r') as f:
            slides = json.load(f).get('slides', [])
    except Exception as e:
        print(f"Error reading fixture file: {e}", file=sys.stderr)
        sys.exit(2)

    findings = audit_contract(slides)

    if args.out:
        try:
            with open(args.out, 'w') as f:
                json.dump({'findings': findings}, f, indent=4)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(2)

    if findings:
        print(json.dumps({'findings': findings}, indent=4))
        sys.exit(1)
    else:
        print(json.dumps({'findings': []}))
        sys.exit(0)

if __name__ == "__main__":
    main()

import json

with open('output/gha_hakt_30s_pbd_1789279473_receipt.json') as f:
    r = json.load(f)
checks = (r.get('policyReport') or {}).get('checks') or {}

for check_name in ['lineCount', 'captionCollision', 'headOcclusion', 'safeRegionBounds', 'shadowBudget', 'lookConformance']:
    v = checks.get(check_name) or {}
    print('=== ' + check_name + ' ===')
    print('status:', v.get('status'))
    for k2, v2 in v.items():
        if k2 != 'status' and not isinstance(v2, (dict, list)):
            print(f'  {k2}: {v2}')
        elif k2 == 'violations':
            print(f'  violations: {v2}')
        elif k2 == 'pixelTruth':
            print(f"  pixelTruth: wrapRows={v2.get('wrapInducedRowsDetected')}")

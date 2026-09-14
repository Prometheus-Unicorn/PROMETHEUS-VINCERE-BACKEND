import json

receipt_path = 'docs/mini_run_studio/run_34837285119/render-receipt-gha_hakt_30s_pbd_1789384516/receipt_gha_hakt_30s_pbd_1789384516.json'
r = json.load(open(receipt_path, 'r', encoding='utf-8'))
print('gitSha:', r.get('deploymentFingerprint', {}).get('gitSha'))
pr = r.get('policyReport', {})
print('policyReport status:', pr.get('status'))
print('totalChecks:', pr.get('totalChecks'))
print('passedChecks:', pr.get('passedChecks'))
print('failedChecks:', pr.get('failedChecks'))
print('violations:', pr.get('violations'))

for check_name, check_data in pr.get('checks', {}).items():
    print(f"Check [{check_name}]: {check_data.get('status')}")
    if check_data.get('status') == 'failed':
        print(f"  Details: {check_data}")

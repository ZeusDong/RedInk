from backend.app import create_app

app = create_app()
print("=== All Reference Routes ===")
for rule in app.url_map.iter_rules():
    if 'reference' in rule.rule.lower():
        print(f"{rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")

print("\n=== Checking specific route ===")
from flask import url_for
with app.test_request_context():
    try:
        url = url_for('api.reference.get_record', record_id='test123')
        print(f"URL for get_record with test123: {url}")
    except Exception as e:
        print(f"Error building URL: {e}")

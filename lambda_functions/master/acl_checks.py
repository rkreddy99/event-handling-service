import json

STRATEGY_JSON_FILEPATH = "all_strategy_details.json"
with open(STRATEGY_JSON_FILEPATH) as f:
    strategy_data = json.load(f)

def admin_tag_check(username: str, event_json) -> bool:
    if "strategy" not in event_json:
        return False
    strategy = event_json['strategy']
    strat_details = strategy_data[strategy]
    strategy_users = strat_details.get("users", {})
    # print(strategy_users, username)
    if strategy_users:
        user_tags = strategy_users.get(username, [])
        return 'admin' in user_tags
    return False

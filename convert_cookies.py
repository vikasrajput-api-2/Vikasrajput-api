import json

# ✅ Load JSON cookies
with open("cookies.json", "r", encoding="utf-8") as file:
    cookies = json.load(file)

# ✅ Convert to Netscape format
netscape_cookies = ""
for cookie in cookies:
    netscape_cookies += f"{cookie['domain']}   TRUE   {cookie['path']}   {'TRUE' if cookie['secure'] else 'FALSE'}   {cookie.get('expiry', '0')}   {cookie['name']}   {cookie['value']}\n"

# ✅ Save as cookies.txt
with open("cookies.txt", "w", encoding="utf-8") as file:
    file.write(netscape_cookies)

print("✅ JSON cookies converted to Netscape format (cookies.txt)")

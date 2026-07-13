# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
benchmarks/community_corpus.py — labelled vulnerable/secure pairs.

Each case ships a vulnerable snippet (must be flagged with the declared CWE)
and a secure snippet (must NOT be flagged — a finding there is a false
positive on real, correct code). This is what `benchmarks/measure.py` scores,
so the recall/precision numbers in the README are reproducible from source.

Languages: python, javascript, go, java, php, ruby, csharp, kotlin, rust, cpp.
"""
from __future__ import annotations

# (id, language, cwe, vulnerable, secure)
CASES = [
    # ── Python · weak cryptography (CWE-327) ──────────────────────────────────
    ("py-weak-hash", "python", "CWE-327",
     "import hashlib\ndigest = hashlib.md5(payload).hexdigest()\n",
     "import hashlib\ndigest = hashlib.sha256(payload).hexdigest()\n"),
    ("py-weak-hash-new", "python", "CWE-327",
     "import hashlib\nh = hashlib.new('sha1', data)\n",
     "import hashlib\nh = hashlib.new('sha256', data)\n"),
    ("py-weak-cipher-des", "python", "CWE-327",
     "from Crypto.Cipher import DES\ncipher = DES.new(key, DES.MODE_CBC, iv)\n",
     "from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_GCM, nonce=nonce)\n"),
    ("py-weak-cipher-rc4", "python", "CWE-327",
     "from Crypto.Cipher import ARC4\ncipher = ARC4.new(key)\n",
     "from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_GCM, nonce=nonce)\n"),
    ("py-ecb-mode", "python", "CWE-327",
     "from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_ECB)\n",
     "from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_GCM, nonce=nonce)\n"),

    # ── Python · TLS verification disabled (CWE-295) ──────────────────────────
    ("py-tls-verify", "python", "CWE-295",
     "import requests\nr = requests.get(url, verify=False)\n",
     "import requests\nr = requests.get(url, verify=True)\n"),
    ("py-tls-context", "python", "CWE-295",
     "import ssl\nctx = ssl._create_unverified_context()\n",
     "import ssl\nctx = ssl.create_default_context()\n"),

    # ── Python · unsafe deserialization (CWE-502) ─────────────────────────────
    ("py-pickle", "python", "CWE-502",
     "import pickle\nobj = pickle.loads(untrusted_bytes)\n",
     "import json\nobj = json.loads(untrusted_text)\n"),
    ("py-yaml", "python", "CWE-502",
     "import yaml\ncfg = yaml.load(stream)\n",
     "import yaml\ncfg = yaml.safe_load(stream)\n"),
    ("py-yaml-loader", "python", "CWE-502",
     "import yaml\ncfg = yaml.load(stream, Loader=yaml.Loader)\n",
     "import yaml\ncfg = yaml.load(stream, Loader=yaml.SafeLoader)\n"),

    # ── Python · code injection (CWE-95) ──────────────────────────────────────
    ("py-eval", "python", "CWE-95",
     "def run(expr):\n    return eval(expr)\n",
     "import ast\ndef run(expr):\n    return ast.literal_eval(expr)\n"),
    ("py-exec", "python", "CWE-95",
     "def run(code):\n    exec(code)\n",
     "def run(code):\n    return registry[code]()\n"),

    # ── Python · OS command injection (CWE-78) ────────────────────────────────
    ("py-os-system", "python", "CWE-78",
     "import os\ndef ping(host):\n    os.system('ping -c1 ' + host)\n",
     "import subprocess\ndef ping(host):\n    subprocess.run(['ping', '-c1', host])\n"),
    ("py-shell-true", "python", "CWE-78",
     "import subprocess\ndef run(cmd):\n    subprocess.run(cmd, shell=True)\n",
     "import subprocess\ndef run(args):\n    subprocess.run(args, shell=False)\n"),

    # ── Python · SQL injection (CWE-89) ───────────────────────────────────────
    ("py-sql-fstring", "python", "CWE-89",
     "def get(cur, uid):\n    cur.execute(f\"SELECT * FROM users WHERE id = {uid}\")\n",
     "def get(cur, uid):\n    cur.execute(\"SELECT * FROM users WHERE id = ?\", (uid,))\n"),
    ("py-sql-percent", "python", "CWE-89",
     "def get(cur, name):\n    cur.execute(\"SELECT * FROM users WHERE name = '%s'\" % name)\n",
     "def get(cur, name):\n    cur.execute(\"SELECT * FROM users WHERE name = %s\", (name,))\n"),
    ("py-sql-format", "python", "CWE-89",
     "def get(cur, uid):\n    cur.execute(\"SELECT * FROM users WHERE id = {}\".format(uid))\n",
     "def get(cur, uid):\n    cur.execute(\"SELECT * FROM users WHERE id = %s\", (uid,))\n"),
    ("py-sql-concat", "python", "CWE-89",
     "def get(cur, uid):\n    cur.execute(\"SELECT * FROM users WHERE id = \" + uid)\n",
     "def get(cur, uid):\n    cur.execute(\"SELECT * FROM users WHERE id = ?\", (uid,))\n"),
    # SQL assembled into a local variable, then executed (local def-use).
    ("py-sql-indirect", "python", "CWE-89",
     "def get(cur, uid):\n    q = f\"SELECT * FROM users WHERE id = {uid}\"\n    cur.execute(q)\n",
     "def get(cur, uid):\n    q = \"SELECT * FROM users WHERE id = ?\"\n    cur.execute(q, (uid,))\n"),

    # ── Python · XSS / SSTI sinks (CWE-79) ────────────────────────────────────
    ("py-ssti", "python", "CWE-79",
     "from flask import render_template_string, request\n"
     "def page():\n    return render_template_string(request.args.get('tpl'))\n",
     "from flask import render_template\n"
     "def page():\n    return render_template('page.html')\n"),
    ("py-mark-safe", "python", "CWE-79",
     "from django.utils.safestring import mark_safe\ndef bio(user):\n    return mark_safe(user.bio)\n",
     "from django.utils.html import escape\ndef bio(user):\n    return escape(user.bio)\n"),

    # ── Python · insecure randomness (CWE-330) ────────────────────────────────
    ("py-weak-random", "python", "CWE-330",
     "import random\ntoken = str(random.randint(0, 999999))\n",
     "import secrets\ntoken = str(secrets.randbelow(1000000))\n"),

    # ── Python · XXE (CWE-611) ────────────────────────────────────────────────
    ("py-xxe", "python", "CWE-611",
     "from lxml import etree\ndoc = etree.fromstring(data)\n",
     "from lxml import etree\nparser = etree.XMLParser(resolve_entities=False)\n"
     "doc = etree.fromstring(data, parser)\n"),

    # ── Python · path traversal from direct user input (CWE-22) ───────────────
    ("py-path-traversal", "python", "CWE-22",
     "def read(req):\n    return open(req.args.get('f')).read()\n",
     "import os\ndef read(req):\n    name = os.path.basename(req.args.get('f'))\n"
     "    return open(os.path.join(SAFE_DIR, name)).read()\n"),

    # ── JavaScript / TypeScript ───────────────────────────────────────────────
    ("js-eval", "javascript", "CWE-95",
     "app.get('/x', (req, res) => {\n  const out = eval(req.query.code);\n});\n",
     "app.get('/x', (req, res) => {\n  const out = JSON.parse(req.query.code);\n});\n"),
    ("js-command", "javascript", "CWE-78",
     "const cp = require('child_process');\ncp.exec(`ls ${req.query.dir}`);\n",
     "const cp = require('child_process');\ncp.execFile('ls', [req.query.dir]);\n"),
    ("js-innerhtml", "javascript", "CWE-79",
     "el.innerHTML = `<b>${userName}</b>`;\n",
     "el.textContent = userName;\n"),
    ("js-md5", "javascript", "CWE-327",
     "const h = crypto.createHash('md5').update(data).digest('hex');\n",
     "const h = crypto.createHash('sha256').update(data).digest('hex');\n"),
    ("js-tls", "javascript", "CWE-295",
     "const agent = new https.Agent({ rejectUnauthorized: false });\n",
     "const agent = new https.Agent({ rejectUnauthorized: true });\n"),

    # ── Go ────────────────────────────────────────────────────────────────────
    ("go-weak-hash", "go", "CWE-327",
     "import \"crypto/md5\"\nfunc sum(b []byte) { h := md5.New(); h.Write(b) }\n",
     "import \"crypto/sha256\"\nfunc sum(b []byte) { h := sha256.New(); h.Write(b) }\n"),
    ("go-tls", "go", "CWE-295",
     "cfg := &tls.Config{InsecureSkipVerify: true}\n",
     "cfg := &tls.Config{InsecureSkipVerify: false}\n"),
    ("go-command", "go", "CWE-78",
     "out, _ := exec.Command(\"sh\", \"-c\", \"ls \"+dir).Output()\n",
     "out, _ := exec.Command(\"ls\", dir).Output()\n"),
    ("go-sql", "go", "CWE-89",
     "rows, _ := db.Query(\"SELECT * FROM u WHERE id = \" + id)\n",
     "rows, _ := db.Query(\"SELECT * FROM u WHERE id = $1\", id)\n"),

    # ── Java ──────────────────────────────────────────────────────────────────
    ("java-weak-hash", "java", "CWE-327",
     "MessageDigest md = MessageDigest.getInstance(\"MD5\");\n",
     "MessageDigest md = MessageDigest.getInstance(\"SHA-256\");\n"),
    ("java-command", "java", "CWE-78",
     "Process p = Runtime.getRuntime().exec(\"ping \" + host);\n",
     "Process p = new ProcessBuilder(\"ping\", host).start();\n"),
    ("java-sql", "java", "CWE-89",
     "ResultSet rs = stmt.executeQuery(\"SELECT * FROM u WHERE id = \" + id);\n",
     "PreparedStatement ps = conn.prepareStatement(\"SELECT * FROM u WHERE id = ?\");\n"),
    ("java-deser", "java", "CWE-502",
     "ObjectInputStream ois = new ObjectInputStream(in);\nObject o = ois.readObject();\n",
     "Foo o = mapper.readValue(in, Foo.class);\n"),
    ("java-weak-random", "java", "CWE-330",
     "String token = String.valueOf(new Random().nextInt());\n",
     "String token = String.valueOf(new SecureRandom().nextInt());\n"),

    # ── PHP ───────────────────────────────────────────────────────────────────
    ("php-md5", "php", "CWE-327",
     "<?php\n$hash = md5($password);\n",
     "<?php\n$hash = password_hash($password, PASSWORD_DEFAULT);\n"),
    ("php-command", "php", "CWE-78",
     "<?php\nsystem('ping ' . $host);\n",
     "<?php\nsystem(escapeshellcmd('ping'));\n"),
    ("php-sql", "php", "CWE-89",
     "<?php\n$db->query(\"SELECT * FROM users WHERE id = $id\");\n",
     "<?php\n$stmt = $db->prepare(\"SELECT * FROM users WHERE id = ?\");\n"),
    ("php-unserialize", "php", "CWE-502",
     "<?php\n$obj = unserialize($_GET['data']);\n",
     "<?php\n$obj = json_decode($_GET['data'], true);\n"),
    ("php-eval", "php", "CWE-95",
     "<?php\neval($_GET['code']);\n",
     "<?php\n$result = $registry[$_GET['code']]();\n"),

    # ── Ruby ──────────────────────────────────────────────────────────────────
    ("rb-md5", "ruby", "CWE-327",
     "digest = Digest::MD5.hexdigest(data)\n",
     "digest = Digest::SHA256.hexdigest(data)\n"),
    ("rb-command", "ruby", "CWE-78",
     "system(\"ls #{params[:dir]}\")\n",
     "system(\"ls\", params[:dir])\n"),
    ("rb-sql", "ruby", "CWE-89",
     "User.where(\"name = '#{params[:name]}'\")\n",
     "User.where(\"name = ?\", params[:name])\n"),
    ("rb-marshal", "ruby", "CWE-502",
     "obj = Marshal.load(untrusted)\n",
     "obj = JSON.parse(untrusted)\n"),
    ("rb-eval", "ruby", "CWE-95",
     "eval(params[:expr])\n",
     "result = REGISTRY.fetch(params[:expr]).call\n"),

    # ── C# ────────────────────────────────────────────────────────────────────
    ("cs-md5", "csharp", "CWE-327",
     "var hash = MD5.Create().ComputeHash(data);\n",
     "var hash = SHA256.Create().ComputeHash(data);\n"),
    ("cs-command", "csharp", "CWE-78",
     "Process.Start(\"ping \" + host);\n",
     "Process.Start(\"ping\", host);\n"),
    ("cs-sql", "csharp", "CWE-89",
     "var cmd = new SqlCommand(\"SELECT * FROM u WHERE id = \" + id, conn);\n",
     "var cmd = new SqlCommand(\"SELECT * FROM u WHERE id = @id\", conn);\n"),
    ("cs-binaryformatter", "csharp", "CWE-502",
     "var obj = new BinaryFormatter().Deserialize(stream);\n",
     "var obj = JsonSerializer.Deserialize<Foo>(stream);\n"),

    # ── Kotlin ────────────────────────────────────────────────────────────────
    ("kt-weak-hash", "kotlin", "CWE-327",
     "val md = MessageDigest.getInstance(\"MD5\")\n",
     "val md = MessageDigest.getInstance(\"SHA-256\")\n"),
    ("kt-command", "kotlin", "CWE-78",
     "Runtime.getRuntime().exec(\"ping \" + host)\n",
     "ProcessBuilder(\"ping\", host).start()\n"),
    ("kt-sql", "kotlin", "CWE-89",
     "stmt.executeQuery(\"SELECT * FROM u WHERE id = $id\")\n",
     "conn.prepareStatement(\"SELECT * FROM u WHERE id = ?\")\n"),
    ("kt-deser", "kotlin", "CWE-502",
     "val ois = ObjectInputStream(input)\n",
     "val o = mapper.readValue(input, Foo::class.java)\n"),

    # ── Rust ──────────────────────────────────────────────────────────────────
    ("rs-weak-hash", "rust", "CWE-327",
     "let mut hasher = Md5::new();\n",
     "let mut hasher = Sha256::new();\n"),
    ("rs-command", "rust", "CWE-78",
     "Command::new(\"sh\").arg(\"-c\").arg(format!(\"ls {}\", dir)).output();\n",
     "Command::new(\"ls\").arg(dir).output();\n"),
    ("rs-sql", "rust", "CWE-89",
     "sqlx::query(&format!(\"SELECT * FROM u WHERE id = {}\", id)).fetch_one(&pool);\n",
     "sqlx::query(\"SELECT * FROM u WHERE id = $1\").bind(id).fetch_one(&pool);\n"),

    # ── C / C++ ───────────────────────────────────────────────────────────────
    ("cpp-dangerous", "cpp", "CWE-676",
     "strcpy(dst, src);\n",
     "strncpy(dst, src, sizeof(dst) - 1);\n"),
    ("cpp-command", "cpp", "CWE-78",
     "system((\"rm \" + path).c_str());\n",
     "execvp(\"rm\", args);\n"),
    ("cpp-crypto", "cpp", "CWE-327",
     "MD5_Init(&ctx);\n",
     "SHA256_Init(&ctx);\n"),

    # ── SQL tainted across a function boundary within one module ──────────────
    ("py-crossfunc-sql", "python", "CWE-89",
     "def query(cur, sql):\n    cur.execute(sql)\n"
     "def handler(cur, uid):\n    query(cur, f\"SELECT * FROM u WHERE id = {uid}\")\n",
     "def query(cur, sql, args):\n    cur.execute(sql, args)\n"
     "def handler(cur, uid):\n    query(cur, \"SELECT * FROM u WHERE id = ?\", (uid,))\n"),
]

# Classes the *rule-based* engine intentionally does NOT model. These require
# inter-procedural data-flow (taint) tracking, which is the Pro CPG engine's
# job. They are listed here so the scorecard reports an honest overall recall
# and names its own blind spots rather than hiding them. The "secure" side must
# still never produce a false positive.
COVERAGE_GAPS = [
    # SSRF — a guarded call and an unguarded call look identical to a rule.
    ("gap-ssrf", "python", "CWE-918",
     "import requests\ndef fetch(req):\n    return requests.get(req.args.get('url')).text\n",
     "import requests\ndef fetch(req):\n    if not allowed(req.args.get('url')):\n"
     "        raise ValueError('blocked')\n    return requests.get(req.args.get('url')).text\n"),
    # Second-order SQL — tainted value flows through a data store, then is
    # executed on a later read. Needs cross-request / stored-taint tracking.
    ("gap-second-order-sql", "python", "CWE-89",
     "def run(cur):\n    row = cur.execute('SELECT payload FROM jobs').fetchone()\n    cur.execute(row[0])\n",
     "def run(cur):\n    row = cur.execute('SELECT payload FROM jobs').fetchone()\n    dispatch(row[0])\n"),
    # Open redirect — destination validation is a semantic property.
    ("gap-open-redirect", "python", "CWE-601",
     "from flask import redirect, request\ndef go():\n    return redirect(request.args.get('next'))\n",
     "from flask import redirect, request\ndef go():\n    nxt = request.args.get('next')\n"
     "    return redirect(nxt if is_local(nxt) else '/')\n"),
]

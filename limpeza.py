"""Limpeza dos seguindo do Instagram, em ritmo humano.
  python limpeza.py login      -> abre janela, você faz login (com 2FA); sessao fica no perfil
  python limpeza.py lote       -> 1 lote (cota do dia / 5), com pausas aleatorias
  python limpeza.py lote --n 3 -> teste com N unfollows
  python limpeza.py status
Usa a API web do proprio Instagram dentro da sessao logada. Para sozinho em bloqueio."""
import argparse, datetime as dt, json, os, pathlib, random, sys, time
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).parent
PERFIL = BASE / "perfil-chrome"          # sessao logada (nao vai para lugar nenhum)
ESTADO = BASE / "estado.json"
TRAVA = BASE / "BLOQUEADO.txt"           # existe = nao roda mais até você apagar
LOG = BASE / "log.txt"
APP_ID = "936619743392459"
LOTES_DIA = 5

def log(msg):
    linha = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linha); LOG.open("a", encoding="utf-8").write(linha + "\n")

def avisar(texto):
    # opcional: defina NOTIFY_WEBHOOK (Discord, Slack, ntfy.sh...) para receber alertas
    url = os.environ.get("NOTIFY_WEBHOOK")
    if not url: return
    try:
        import urllib.request
        msg = "Limpeza Instagram\n" + texto
        corpo = json.dumps({"content": msg, "text": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(url, corpo, {"Content-Type": "application/json"}), timeout=15)
    except Exception as e:
        log(f"aviso falhou: {e}")

def estado():
    e = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    e.setdefault("inicio", str(dt.date.today())); e.setdefault("total", 0); e.setdefault("dias", {})
    return e

def cota_dia(e):
    # aquecimento conta dias que RODARAM de fato (PC desligado não conta)
    dias_rodados = sum(1 for d, n in e["dias"].items() if n > 0 and d != str(dt.date.today()))
    return 40 if dias_rodados < 3 else 110

def abrir(p, headless):
    return p.chromium.launch_persistent_context(str(PERFIL), headless=headless, channel="chrome",
        locale="pt-BR", viewport={"width": 1280, "height": 860},
        args=["--disable-blink-features=AutomationControlled"])

def api(page, metodo, url):
    return page.evaluate("""async ([metodo, url, app]) => {
        const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
        const r = await fetch(url, {method: metodo, credentials: 'include',
            headers: {'x-csrftoken': csrf, 'x-ig-app-id': app, 'x-requested-with': 'XMLHttpRequest',
                      'content-type': 'application/x-www-form-urlencoded'}});
        let corpo = null; try { corpo = await r.json(); } catch (e) {}
        return {status: r.status, corpo};
    }""", [metodo, url, APP_ID])

BLOQUEIO = ["Tente novamente mais tarde", "Try Again Later", "restringimos", "bloquead", "Action Blocked"]

def deixar_de_seguir(page, user):
    page.goto(f"https://www.instagram.com/{user}/", wait_until="domcontentloaded"); time.sleep(random.uniform(4, 8))
    b = page.locator("header button:has-text('Seguindo'), header button:has-text('Solicitado')").first
    if b.count() == 0: return True, "já não seguia"
    b.click(); time.sleep(random.uniform(1.5, 3))
    m = page.get_by_text("Deixar de seguir", exact=True).last
    if m.count() == 0: return False, "menu Deixar de seguir não apareceu"
    m.click(); time.sleep(random.uniform(3, 5))
    corpo = page.inner_text("body")
    if any(x.lower() in corpo.lower() for x in BLOQUEIO): return False, "Instagram mostrou aviso de bloqueio"
    if page.locator("header button:has-text('Seguindo')").count(): return False, "continuou Seguindo"
    return True, ""

def login():
    with sync_playwright() as p:
        ctx = abrir(p, False); page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.instagram.com/accounts/login/")
        print("Faça o login na janela (inclusive o 2FA). Espero até 10 min...")
        for _ in range(300):
            if any(c["name"] == "sessionid" for c in ctx.cookies("https://www.instagram.com")):
                print("Login OK, sessão salva."); time.sleep(5); ctx.close(); return
            time.sleep(2)
        ctx.close(); sys.exit("Tempo esgotado sem login.")

def lote(n=None):
    if TRAVA.exists(): log("travado (BLOQUEADO.txt existe), não rodo"); return
    e = estado(); hoje = str(dt.date.today()); feitos_hoje = e["dias"].get(hoje, 0)
    cota = cota_dia(e)
    alvo = n if n else min(cota // LOTES_DIA + random.randint(-3, 3), cota - feitos_hoje)
    if alvo <= 0: log(f"cota do dia batida ({feitos_hoje}/{cota})"); return
    with sync_playwright() as p:
        ctx = abrir(p, True); page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded"); time.sleep(random.uniform(4, 8))
        uid = next((c["value"] for c in ctx.cookies("https://www.instagram.com") if c["name"] == "ds_user_id"), None)
        if not uid:
            log("sessão caiu, precisa de login"); avisar("A sessão caiu. Rode: python limpeza.py login"); ctx.close(); return
        r = api(page, "GET", f"https://www.instagram.com/api/v1/friendships/{uid}/following/?count=50")
        if r["status"] != 200:
            log(f"falha ao listar: {r}"); ctx.close(); return
        usuarios = (r["corpo"] or {}).get("users", [])
        if not usuarios: log("seguindo zerado, limpeza concluída"); avisar(f"Concluída! Total: {e['total']}"); ctx.close(); return
        random.shuffle(usuarios); feitos = 0
        for u in usuarios[:alvo]:
            ok, msg = deixar_de_seguir(page, u["username"])
            if not ok:
                msg = f"PARADO em @{u['username']}: {msg}"
                log(msg); TRAVA.write_text(f"{dt.datetime.now()}\n{msg}\n", encoding="utf-8")
                avisar(f"Parei por segurança.\n{msg[:200]}\nEspere 48h e apague BLOQUEADO.txt para voltar.")
                break
            feitos += 1; log(f"deixei de seguir @{u['username']}")
            time.sleep(random.uniform(20, 60))
        e["total"] += feitos; e["dias"][hoje] = feitos_hoje + feitos
        ESTADO.write_text(json.dumps(e, indent=1), encoding="utf-8")
        log(f"lote fim: {feitos} agora, {e['dias'][hoje]}/{cota} hoje, {e['total']} no total")
        ctx.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["login", "lote", "status"]); ap.add_argument("--n", type=int)
    a = ap.parse_args()
    if a.cmd == "login": login()
    elif a.cmd == "lote": lote(a.n)
    else: print(json.dumps(estado(), indent=1), "| travado" if TRAVA.exists() else "")

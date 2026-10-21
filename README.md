# instagram-limpeza

Deixa de seguir as contas que você segue no Instagram **em ritmo humano**, rodando no seu próprio PC, com a sua sessão logada. Não pede senha nem token e não manda nada para servidor de terceiros.

## Como funciona

- Abre um Chrome (Playwright) com um perfil próprio, que fica em `perfil-chrome/`. Você faz o login uma vez, com 2FA, e a sessão continua salva.
- Cada lote pega as contas que você segue e deixa de seguir pelo botão do perfil, como você faria na mão, com pausa aleatória de 20 a 60 s entre uma e outra.
- **Cota diária com aquecimento:** 40 por dia nos 3 primeiros dias rodados, depois 110 por dia, divididos em 5 lotes.
- **Para sozinho:** se o Instagram mostrar aviso de bloqueio ou o botão não responder, cria `BLOQUEADO.txt` e não roda mais até você apagar esse arquivo (espere umas 48 h).

## Instalação

```bash
git clone https://github.com/heitormotti/instagram-limpeza
cd instagram-limpeza
pip install -r requirements.txt
python limpeza.py rodar
```

Na primeira vez, o navegador abre para você entrar na sua conta (com 2FA). Depois disso o script fica rodando: a cada 2h30 a 3h30 faz um lote e, quando a cota do dia acaba, espera até as 9h do dia seguinte. Deixe a janela aberta enquanto o PC estiver ligado. Se fechar, é só rodar de novo: ele continua de onde parou.

Outros comandos:

```bash
python limpeza.py lote --n 3   # teste com 3 contas
python limpeza.py status       # quanto já foi
python limpeza.py login        # refazer o login
```

Precisa do Google Chrome instalado, porque o script usa `channel="chrome"`.

### Alternativa: tarefa agendada (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File agendar.ps1
```

Em vez de deixar a janela aberta, cria 5 tarefas por dia (09:30, 12:30, 15:30, 18:30, 21:30), cada uma com atraso aleatório de até 40 min. No Mac ou no Linux, use `cron` com `python limpeza.py lote`.

### Alertas (opcional)

Defina a variável `NOTIFY_WEBHOOK` com um webhook do Discord, do Slack ou do ntfy.sh e você recebe um aviso quando a sessão cair, quando o script parar por bloqueio ou quando terminar.

## Atenção

- **O script tira TODO mundo que você segue**, sem lista de exceções. Se quiser manter alguma conta, siga de novo depois.
- Automatizar ações vai contra os Termos de Uso do Instagram. O ritmo é conservador, mas o risco de bloqueio temporário é seu.
- **Nunca suba a pasta `perfil-chrome/`**, porque ela tem a sua sessão logada. O `.gitignore` já deixa ela de fora.

## Licença

MIT

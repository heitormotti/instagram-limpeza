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
python limpeza.py login        # abre a janela; faça login (com 2FA)
python limpeza.py lote --n 3   # teste com 3 contas
python limpeza.py status
```

Precisa do Google Chrome instalado, porque o script usa `channel="chrome"`.

### Rodar sozinho (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File agendar.ps1
```

Cria 5 tarefas por dia (09:30, 12:30, 15:30, 18:30, 21:30), cada uma com atraso aleatório de até 40 min. No Mac ou no Linux, use `cron` com `python limpeza.py lote`.

### Alertas (opcional)

Defina a variável `NOTIFY_WEBHOOK` com um webhook do Discord, do Slack ou do ntfy.sh e você recebe um aviso quando a sessão cair, quando o script parar por bloqueio ou quando terminar.

## Atenção

- **O script tira TODO mundo que você segue**, sem lista de exceções. Se quiser manter alguma conta, siga de novo depois.
- Automatizar ações vai contra os Termos de Uso do Instagram. O ritmo é conservador, mas o risco de bloqueio temporário é seu.
- **Nunca suba a pasta `perfil-chrome/`**, porque ela tem a sua sessão logada. O `.gitignore` já deixa ela de fora.

## Licença

MIT

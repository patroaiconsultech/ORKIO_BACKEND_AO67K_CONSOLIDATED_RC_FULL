# GO/NO-GO Checklist

## GO se

- Backend sobe.
- `/api/health` retorna 200.
- `/api/threads` retorna 200.
- `/api/messages` retorna 200.
- `/api/chat/stream` retorna 200.
- Um `trace_id` gera no máximo uma resposta assistant.
- `done` é emitido.
- Input é liberado.
- Orkio não mistura roadmap com produção.

## NO-GO se

- Crash determinístico.
- Duplicação de assistant.
- Mensagem de usuário perdida.
- Terminal Guard V7 preso.
- Capability inventada.
- Autoexecução sem aprovação humana.

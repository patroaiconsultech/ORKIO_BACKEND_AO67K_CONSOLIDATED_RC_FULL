# ORKIO OS 1.0 — Architecture Blueprint

## Decisão central

Separar definitivamente:

- Runtime: transporte, SSE, persistência, encerramento.
- Kernel: decisão cognitiva e composição de resposta.
- Knowledge Fabric: conhecimento governado.
- Governance: políticas, aprovação humana e limites.
- Observability: rastreabilidade por trace_id, thread_id e message_id.

## Fluxo-alvo

request → runtime → executive kernel → truth engine → response builder → persist once → done → unlock

## Regra

O Runtime não inventa conteúdo.  
O Kernel não persiste.  
O Knowledge Fabric não injeta documentos brutos.  
A Governança bloqueia autoexecução sem aprovação humana.

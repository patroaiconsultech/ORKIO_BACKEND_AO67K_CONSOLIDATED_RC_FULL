# PATCH FINAL R4 — Correção Definitiva do Roteamento Executivo

## Diagnóstico Confirmado pelos Logs de Produção

O log de produção revelou a **causa raiz definitiva**:

| Item | Produção (atual) | GitHub (correto) |
|------|-------------------|-------------------|
| SHA do main.py | `93b6edf4...` | `5916ffe8...` |
| Linhas do main.py | ~47.202 | 52.078 |
| Classificação do Cenário 1 | `quantitative_business_math` | `executive_strategy_mode` |

O guard EOS06-AO85-HF2 **existe** em produção, mas é uma **versão antiga** que classifica incorretamente a mensagem do CEO como "cálculo financeiro" por causa dos números presentes (50 funcionários, R$12M/ano).

A versão corrigida no GitHub tem a precedência certa: `_looks_like_executive_strategy_request()` é verificada ANTES de `_looks_like_financial_math_request()`, e a função de math retorna `False` se strategy for detectada.

## Arquivos Incluídos (9 arquivos)

| Arquivo | Função |
|---------|--------|
| `main.py` | Servidor principal com patch R3.2 + diagnóstico |
| `runtime/orkio_executive_guard.py` | Classificador executivo corrigido |
| `runtime/orkio_stream_precedence.py` | Gate de entrada do stream |
| `runtime/orkio_backend_cta_guard.py` | Supressão de CTA no backend |
| `runtime/orkio_kernel/classifier.py` | Classificador de intenções |
| `runtime/orkio_kernel/executive_reasoning.py` | Raciocínio executivo |
| `runtime/orkio_kernel/response_builder.py` | Construtor de respostas |
| `tests/manus_ux_r3_router_and_cta_regression_smoke.py` | Smoke test R3 |
| `tests/manus_ux_r3_1_stream_integration_contract_test.py` | Teste contratual |

## Instruções de Deploy

1. **Extraia o ZIP** na raiz do repositório `ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL`
2. **Substitua os arquivos** existentes (o main.py é o mais crítico)
3. **Commit + Push** para a branch principal
4. **FORCE REBUILD** no Railway: vá em Settings > Deploy > clique "Redeploy" ou use "Clear build cache + Redeploy"
5. **Verifique nos logs** a string `MANUS_UX_R3_2_BOOT_OK` — se aparecer, o código novo está rodando
6. **Verifique o SHA** nos logs: deve ser `5916ffe8a9194b651485c964d4e8c0f30ec759859b56791cf4f26ae1eab028fe`

## Validação Pós-Deploy

Após o deploy, o cenário 1 deve retornar:
- `EOS06_AO85_HF2_TURN_OWNERSHIP category=executive_strategy_mode` (em vez de `quantitative_business_math`)
- Resposta sobre riscos estratégicos (em vez de pedir dados para cálculo)

## Alerta Importante

O main.py tem **52.078 linhas** e **~1.7 MB**. O GitHub pode rejeitar upload via interface web para arquivos desse tamanho. Se isso acontecer, use o Git CLI:

```bash
git add main.py runtime/ tests/
git commit -m "fix: patch R4 - corrige classificador executivo e supressão de CTA"
git push origin main
```

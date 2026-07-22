# ORKIO ORION PREMIUM 2 — instalação

## Arquivos
Copie os arquivos deste pacote para os mesmos caminhos no backend implantado.

## Variáveis iniciais
Use primeiro:

```env
ORKIO_VISION_PIPELINE_ENABLED=false
OPENAI_VISION_MODEL=gpt-4o-mini
OPENAI_VISION_TIMEOUT=45
```

Com a visão desativada, imagens não entram mais no extrator textual e falham de forma segura.

Após validar a chave e o modelo multimodal em staging:

```env
ORKIO_VISION_PIPELINE_ENABLED=true
```

O gateway usa `OPENAI_API_KEY` já existente no backend.

## Validação
```bash
python -m py_compile services/file_upload_indexing_service.py services/orion_premium/*.py
pytest -q tests/orion_premium/test_vision_gateway.py tests/orion_premium/test_evolution_hub.py tests/orion_premium/test_evidence_guard.py
```

## Teste funcional
1. Envie JPG/PNG.
2. Confirme nos logs `media_route=vision`.
3. Com visão desativada: `extracted_chars=0`, `chunks_created=0`.
4. Com visão ativada: `engine=vision:<modelo>` e evidência visual indexada.
5. Pergunte pelo conteúdo da imagem e confirme que a resposta usa apenas evidência visual.

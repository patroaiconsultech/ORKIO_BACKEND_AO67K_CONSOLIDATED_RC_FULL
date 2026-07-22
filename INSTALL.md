# Instalação do Delta

1. Criar branch:
   `git checkout -b feature/orion-premium-phase1`

2. Fazer backup do `main.py`.

3. Copiar o conteúdo deste pacote para a raiz do backend, preservando caminhos.

4. Configurar inicialmente:
   `ORION_PREMIUM_SHADOW_MODE=true`

5. Validar sintaxe:
   `python -m py_compile main.py services/orion_premium/*.py`

6. Executar testes:
   `pytest -q tests/orion_premium`

7. Executar a suíte existente relevante para chat, documentos e stream.

8. Publicar apenas em staging.

O arquivo `main.py` é o único arquivo existente substituído. Os demais são novos.

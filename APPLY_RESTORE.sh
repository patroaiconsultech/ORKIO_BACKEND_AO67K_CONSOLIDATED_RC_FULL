# Apply from repository root
cp -R app/agent_evolution_map ./agent_evolution_map

# Validate
python -m compileall -q agent_evolution_map
PYTHONPATH="$(pwd)/.." python -c "import app.agent_evolution_map.router; print('AGENT_EVOLUTION_MAP_IMPORT_OK')"
PYTHONPATH="$(pwd)/.." python -c "import app.main; print('ORKIO_MAIN_IMPORT_OK')"

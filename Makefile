up:        ; docker compose up -d neo4j kb-api streamlit-ui
load:      ; docker compose run --rm loader
			 docker compose build loader
			 docker compose build --no-cache loader

			 docker compose run --rm loader python -m scripts.run_ingest --notetaker-only --no-seed
			 
			 docker compose run --rm loader python -m scripts.run_schema
			 docker compose --profile local-db up -d neo4j
			 docker compose run --rm kb-api python -m scripts.run_schema
			 docker compose run --rm kb-api python -m scripts.run_ingest
			 docker compose run --rm kb-api python -m scripts.run_ingest --no-seed
			

			docker compose up -d --build --force-recreate kb-api streamlit-ui
docker compose ps

docker compose run --rm loader python -m scripts.run_schema
docker compose run --rm loader python -m scripts.run_ingest --notetaker-only --no-seed --force
docker compose run --rm loader python -m scripts.run_ingest --notetaker-only --no-seed 
docker compose up -d --build kb-api streamlit-ui

cek log: ; docker compose logs kb-api -f		
builder klasik: ; docker-compose up -d
membuat kontainer baru dari awal: ;
			 docker compose up -d --force-recreate
remove dlu: ; 
			docker compose down --remove-orphans
			docker compose --profile local-db down --remove-orphans

hapus plugin korup: ; Remove-Item -Force "$env:USERPROFILE\.docker\cli-plugins\docker-buildx.exe" -ErrorAction SilentlyContinue
seed docker: ; docker compose run --rm kb-api python -m scripts.generate_seed_qa

cek log : ; docker compose logs --tail 50 kb-api
seed:      ; python -m scripts.generate_seed_qa
schema:    ; python -m scripts.run_schema
ingest:    ; python -m scripts.run_ingest
test:      ; python -m pytest -q tests
reset:     ; docker compose down -v
stop:      ; docker compose stop

streamlit:  ; streamlit run ui/app.py

jika Error response from daemon: failed to set up container networking: 
docker rm -f arcana-neo4j
docker network prune -f

docker compose restart streamlit-ui
docker compose restart kb-api
docker compose up -d --force-recreate kb-api

docker compose build streamlit-ui
docker compose up -d

wsl --shutdown

MATCH (n) DETACH DELETE n;

wsl 
cd ~/kb
ls
top


localhost gk terbuka : hostname -I | awk '{print $1}'
example : 172.28.45.133
maka : http://172.28.45.133:8501/


. Cek apakah API aktif: curl -i --max-time 10 http://localhost:8001/kb/health
Cek status container Docker : docker compose ps
docker compose logs --tail=100 kb-api
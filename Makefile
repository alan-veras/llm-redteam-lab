.PHONY: lab lab-local attack test payloads stop clean

lab:            ## start the vulnerable target via docker compose
	docker compose up --build

lab-local:      ## start the target in a local venv (no docker)
	cd target && pip install -r requirements.txt && \
	LAB_MODE=$${LAB_MODE:-insecure} LAB_BACKEND=$${LAB_BACKEND:-mock} \
	python -m uvicorn app.main:app --port 8000

attack:         ## run the attack harness against a running target
	python attacks/harness.py --base http://localhost:8000 --out results/run

test:           ## fast deterministic checks (no server) used by CI
	python -m pytest attacks/test_attacks.py -q
	LAB_MODE=insecure python attacks/harness.py --in-process --out results/insecure
	LAB_MODE=secure   python attacks/harness.py --in-process --out results/secure

payloads:       ## generate indirect-injection payloads
	python attacks/indirect/make_payloads.py

stop:           ## stop docker compose
	docker compose down

clean:
	rm -rf results/run attacks/indirect/payloads __pycache__ */__pycache__

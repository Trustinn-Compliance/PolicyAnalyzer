SHELL=/bin/bash -o pipefail

run:
	unset https_proxy &&  fastapi run --port 9191
serve:
	unset https_proxy &&  nohup uvicorn main:app --host 0.0.0.0 --port 9191 > /tmp/policy_analyzer.log 2>&1 &
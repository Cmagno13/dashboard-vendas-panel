FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 5006

# --allow-websocket-origin=* deixa o app acessível fora do localhost (ex.: em deploy).
CMD ["panel", "serve", "app.py", \
     "--address", "0.0.0.0", "--port", "5006", \
     "--allow-websocket-origin", "*"]

#!/usr/bin/env bash
# Atualiza o código (git pull) e (re)inicia os serviços do site no Docker (PostgreSQL + Django).
# Uso: ./build.sh
set -euo pipefail

# Tudo dentro de main() para que o bash leia o script inteiro antes de executar:
# o git pull pode alterar este próprio arquivo.
main() {
    cd "$(dirname "$0")"

    if [ ! -f .env ]; then
        echo "Arquivo .env não encontrado. Copie .env.example para .env e preencha as variáveis." >&2
        exit 1
    fi

    echo "==> Atualizando o código (git pull)"
    git pull --ff-only

    # COMPOSE_PROFILES=postgres no .env decide se o container do PostgreSQL sobe.
    if docker compose config --services | grep -qx db; then
        echo "==> Container do PostgreSQL: ativado"
    else
        echo "==> Container do PostgreSQL: desativado (usando $(grep -E '^POSTGRES_HOST=' .env | cut -d= -f2-))"
        if grep -qE '^POSTGRES_HOST=(db)?$' .env || ! grep -qE '^POSTGRES_HOST=' .env; then
            echo "Defina POSTGRES_HOST no .env com o endereço do PostgreSQL externo." >&2
            exit 1
        fi
        # Remove o container de um deploy anterior; o volume com os dados é preservado.
        docker compose --profile postgres rm -sf db
    fi

    echo "==> Construindo a imagem e iniciando os serviços"
    docker compose up -d --build --remove-orphans

    echo "==> Aguardando as migrations"
    local tentativas=60
    until docker compose exec -T web python manage.py migrate --check >/dev/null 2>&1; do
        tentativas=$((tentativas - 1))
        if [ "$tentativas" -le 0 ]; then
            echo "O site não ficou pronto a tempo. Últimos logs:" >&2
            docker compose logs --tail=80 web >&2
            exit 1
        fi
        sleep 2
    done

    docker image prune -f >/dev/null
    docker compose ps
    echo "==> Pronto: http://localhost:$(grep -E '^TECAB_PORT=' .env | cut -d= -f2 || echo 8090)"
}

main "$@"
exit

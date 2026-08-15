#!/usr/bin/env python3
"""Smoke test manual para a API HU-Speaker.

Sobe um JWT válido (mesmo segredo compartilhado do NovoSGA) e exercita o fluxo
completo: síntese -> download do WAV -> validação do áudio -> status. Roda
contra o container local na porta 8082, sem precisar subir o NovoSGA.

Uso:
    docker compose up -d
    python scripts/integration_test.py
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

# Reutiliza o gerador de token do script irmão (mesmos claims do NovoSGA).
sys.path.insert(0, os.path.dirname(__file__))
from generate_jwt_token import generate_token  # noqa: E402

BASE_URL = "http://localhost:8082"


def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def test_api():
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO - HU-SPEAKER API")
    print("=" * 60)

    # JWT curto (5 min) só para este teste — mesmos claims que o NovoSGA envia.
    token = generate_token(expires_in_minutes=5)
    auth_header = f'-H "Authorization: Bearer {token}"'

    # 1. POST /speak/synthesize
    print("\n1. Enviando solicitação de síntese...")
    curl_cmd = f"""curl -sS -X POST {BASE_URL}/speak/synthesize \
      {auth_header} \
      -H "Content-Type: application/json" \
      -d '{{"text":"Teste de integração da API","language":"pt_BR","length_scale":1.6}}'"""

    output, code = run_command(curl_cmd)
    if code != 0:
        print(f"❌ ERRO ao chamar API: {output}")
        return False

    try:
        response = json.loads(output)
        synthesis_id = response.get("id")
        print(f"✅ Resposta recebida: {response}")
        print(f"   ID: {synthesis_id}")
    except json.JSONDecodeError:
        print(f"❌ Resposta inválida (não é JSON): {output}")
        return False

    if not synthesis_id:
        print("❌ Resposta sem campo 'id' (contrato do NovoSGA quebrado)")
        return False

    # 2. GET /speak/download/{id}
    print("\n2. Baixando arquivo de áudio...")
    download_cmd = (
        f"curl -s {auth_header} -o /tmp/integration_test.wav "
        f"{BASE_URL}/speak/download/{synthesis_id}"
    )
    output, code = run_command(download_cmd)

    wav_path = Path("/tmp/integration_test.wav")
    if not wav_path.exists():
        print("❌ Arquivo não foi baixado")
        return False

    # 3. Validar arquivo WAV
    print("\n3. Validando arquivo WAV...")
    size_bytes = wav_path.stat().st_size
    print(f"   Tamanho: {size_bytes} bytes")

    if size_bytes <= 44:
        print("❌ Arquivo muito pequeno (apenas header, sem áudio)")
        return False

    try:
        with wave.open(str(wav_path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            frames = wav.getnframes()
            duration = frames / frame_rate

            print(f"   Canais: {channels}")
            print(f"   Bits por amostra: {sample_width * 8}")
            print(f"   Taxa de amostragem: {frame_rate} Hz")
            print(f"   Frames: {frames}")
            print(f"   Duração: {duration:.2f} segundos")

            if frames == 0:
                print("❌ Arquivo WAV sem frames de áudio")
                return False

            print("✅ Arquivo WAV válido e contém áudio")

    except Exception as e:
        print(f"❌ Erro ao validar WAV: {e}")
        return False

    # 4. Testar status endpoint
    print("\n4. Verificando status da síntese...")
    status_cmd = f"curl -sS {auth_header} {BASE_URL}/speak/status/{synthesis_id}"
    output, code = run_command(status_cmd)

    try:
        status = json.loads(output)
        print(f"✅ Status recebido: {status}")
    except json.JSONDecodeError:
        print(f"⚠️  Não conseguiu validar status (resposta: {output})")

    # 5. Testar fallback ?token= no download (usado pelo <audio> do navegador)
    print("\n5. Testando download via ?token= (fallback do navegador)...")
    qs_cmd = (
        f"curl -s -o /tmp/integration_test_qs.wav "
        f'"{BASE_URL}/speak/download/{synthesis_id}?token={token}"'
    )
    run_command(qs_cmd)
    qs_path = Path("/tmp/integration_test_qs.wav")
    if qs_path.exists() and qs_path.stat().st_size > 44:
        print("✅ Fallback ?token= funcionando")
    else:
        print("❌ Fallback ?token= falhou (contrato do navegador quebrado)")
        return False

    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

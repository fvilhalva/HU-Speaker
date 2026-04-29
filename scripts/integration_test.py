#!/usr/bin/env python3
"""Manual integration test for the HU-Speaker API"""
import json
import subprocess
import sys
import wave
from pathlib import Path

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def test_api():
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO - HU-SPEAKER API")
    print("=" * 60)
    
    # 1. POST /speak/synthesize
    print("\n1. Enviando solicitação de síntese...")
    curl_cmd = """curl -sS -X POST http://localhost:8082/speak/synthesize \
      -H "Content-Type: application/json" \
      -d '{"text":"Teste de integração da API","language":"pt_BR"}'"""
    
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
    
    # 2. GET /speak/download/{id}
    print("\n2. Baixando arquivo de áudio...")
    download_cmd = f"curl -s -o /tmp/integration_test.wav http://localhost:8082/speak/download/{synthesis_id}"
    output, code = run_command(download_cmd)
    
    wav_path = Path("/tmp/integration_test.wav")
    if not wav_path.exists():
        print(f"❌ Arquivo não foi baixado")
        return False
    
    # 3. Validar arquivo WAV
    print("\n3. Validando arquivo WAV...")
    size_bytes = wav_path.stat().st_size
    print(f"   Tamanho: {size_bytes} bytes")
    
    if size_bytes <= 44:
        print(f"❌ Arquivo muito pequeno (apenas header, sem áudio)")
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
                print(f"❌ Arquivo WAV sem frames de áudio")
                return False
            
            print(f"✅ Arquivo WAV válido e contém áudio")
    
    except Exception as e:
        print(f"❌ Erro ao validar WAV: {e}")
        return False
    
    # 4. Testar status endpoint
    print("\n4. Verificando status da síntese...")
    status_cmd = f"curl -sS http://localhost:8082/speak/status/{synthesis_id}"
    output, code = run_command(status_cmd)
    
    try:
        status = json.loads(output)
        print(f"✅ Status recebido: {status}")
    except json.JSONDecodeError:
        print(f"⚠️  Não conseguiu validar status (resposta: {output})")
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

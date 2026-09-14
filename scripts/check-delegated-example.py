#!/usr/bin/env python3
"""Check the published example's signatures and cross-hop consistency.

Uses Python's standard library and the openssl executable. This checks
fixtures, not a server implementation or full protocol conformance.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
B64 = lambda raw: base64.urlsafe_b64encode(raw).decode().rstrip('=')
DEC = lambda value: base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))
CANON = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def der(tag, value):
    size = len(value)
    length = bytes([size]) if size < 128 else bytes([0x81, size])
    return bytes([tag]) + length + value


def integer(value):
    value = value.lstrip(b'\0') or b'\0'
    return der(2, (b'\0' if value[0] & 128 else b'') + value)


def tlv(value, start=0):
    length = value[start + 1]
    pos = start + 2
    if length & 128:
        count = length & 127
        length = int.from_bytes(value[pos:pos + count], 'big')
        pos += count
    return value[pos:pos + length], pos + length


def openssl(*args, data=None):
    return subprocess.run(['openssl', *args], input=data, capture_output=True, check=True).stdout


def check():
    fixture = json.loads((ROOT / 'docs/delegated-example.json').read_text())
    tokens, cfg = fixture['tokens'], fixture['configuration']
    payloads, headers = {}, {}
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        for role, key in fixture['public_keys'].items():
            pem = directory / (role + '.pem')
            pem.write_text(key['pem'])
            jwk = key['jwk']
            assert not {'d', 'p', 'q', 'dp', 'dq', 'qi'} & jwk.keys()
            if jwk['kty'] == 'RSA':
                encoded = openssl('rsa', '-pubin', '-in', str(pem), '-RSAPublicKey_out', '-outform', 'DER')
                sequence, _ = tlv(encoded)
                n, pos = tlv(sequence)
                e, _ = tlv(sequence, pos)
                assert DEC(jwk['n']) == n.lstrip(b'\0') and DEC(jwk['e']) == e.lstrip(b'\0')
            else:
                encoded = openssl('pkey', '-pubin', '-in', str(pem), '-pubout', '-outform', 'DER')
                assert encoded[-65:] == b'\x04' + DEC(jwk['x']) + DEC(jwk['y'])
        for name, token in tokens.items():
            header, payload, signature = token.split('.')
            headers[name], payloads[name] = json.loads(DEC(header)), json.loads(DEC(payload))
            raw = DEC(signature)
            if headers[name]['alg'] == 'ES256':
                assert len(raw) == 64
                raw = der(0x30, integer(raw[:32]) + integer(raw[32:]))
                assert headers[name]['jwk'] == fixture['public_keys']['dpop']['jwk']
            else:
                assert headers[name]['alg'] == 'RS256'
            signature_file = directory / 'signature.bin'
            signature_file.write_bytes(raw)
            command = ['openssl', 'dgst', '-sha256', '-verify', str(directory / (fixture['signers'][name] + '.pem')), '-signature', str(signature_file)]
            signing_input = (header + '.' + payload).encode()
            subprocess.run(command, input=signing_input, check=True, capture_output=True)
            assert subprocess.run(command, input=signing_input + b'x', capture_output=True).returncode != 0
            claims = payloads[name]
            assert claims['iat'] <= fixture['evaluation_time']
            if 'exp' in claims:
                assert fixture['evaluation_time'] < claims['exp']

    user, actor, grant, access = (payloads[k] for k in ['user_id_token', 'platform_actor', 'id_jag', 'access_token'])
    jkt = B64(hashlib.sha256(CANON(fixture['public_keys']['dpop']['jwk'])).digest())
    assert {k: actor[k] for k in ['iss', 'sub']} == cfg['external_actor']
    assert actor['aud'] == cfg['idp_issuer'] and actor['sub'] != grant['act']['sub']
    assert user['iss'] == grant['iss'] == grant['act']['iss'] == cfg['idp_issuer']
    assert user['aud'] == cfg['idp_client']
    assert grant['sub'] == cfg['user_mapping']['idp_sub'] == user['sub']
    assert access['sub'] == cfg['user_mapping']['ras_sub']
    assert {k: grant['act'][k] for k in ['iss', 'sub']} == cfg['governed_actor']
    assert access['act'] == grant['act'] and 'act' not in grant['act']
    assert grant['aud'] == access['iss'] == cfg['ras_issuer']
    assert grant['resource'] == access['aud'] == cfg['resource']
    assert grant['cnf']['jkt'] == access['cnf']['jkt'] == jkt
    assert grant['client_id'] == access['client_id'] == cfg['ras_client']
    assert grant['exp'] <= min(actor['exp'], user['exp'])
    assert headers['id_jag']['typ'] == 'oauth-id-jag+jwt' and headers['access_token']['typ'] == 'at+jwt'
    issue, redeem = fixture['issuance_request'], fixture['redemption_request']
    assert issue['form']['subject_token'] == tokens['user_id_token'] and issue['form']['actor_token'] == tokens['platform_actor']
    assert redeem['form']['assertion'] == tokens['id_jag'] and redeem['form']['resource'] == cfg['resource']
    for req, role, proof in [(issue, 'idp_client', 'issuance_proof'), (redeem, 'ras_client', 'redemption_proof')]:
        assertion = payloads[role + '_assertion']
        assert assertion['iss'] == assertion['sub'] == cfg[role]
        assert assertion['aud'] == req['url'] == payloads[proof]['htu']
        assert payloads[proof]['htm'] == 'POST' and req['headers']['DPoP'] == tokens[proof]
        assert req['form']['client_assertion'] == tokens[role + '_assertion']
    assert set(access['scope'].split()) <= set(grant['scope'].split()) <= set(issue['form']['scope'].split())
    assert fixture['issuance_response']['access_token'] == tokens['id_jag'] and fixture['issuance_response']['token_type'] == 'N_A'
    assert fixture['redemption_response']['access_token'] == tokens['access_token'] and fixture['redemption_response']['token_type'] == 'DPoP'
    api = fixture['api_request']
    assert api['url'] in cfg['api_policy']['required_profile_paths']
    assert access['act']['iss'] in cfg['api_policy']['actor_namespaces_by_token_issuer'][access['iss']]
    assert all(isinstance(access['act'][name], str) and access['act'][name] for name in ['iss', 'sub'])
    assert 'act' not in access['act'] and isinstance(access['scope'], str) and access['scope'].split()
    assert api['headers']['Authorization'] == 'DPoP ' + tokens['access_token']
    assert api['url'] == payloads['api_proof']['htu'] == cfg['resource']
    assert payloads['api_proof']['ath'] == B64(hashlib.sha256(tokens['access_token'].encode()).digest())
    assert len({payloads[k]['jti'] for k in ['issuance_proof', 'redemption_proof', 'api_proof']}) == 3
    print('PASS: 9 JWT signatures, tamper rejection, public-key consistency, identity mapping, audiences, client bindings, scope ceilings, API profile configuration and actor namespace, DPoP continuity and access-token hash.')


if __name__ == '__main__':
    check()

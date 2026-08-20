#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""生成森空岛登录接口需要的数美设备 ID。"""

import base64
import gzip
import hashlib
import json
import time
import uuid

import requests

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers.algorithms import AES
    try:
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
    except ImportError:
        from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
    from cryptography.hazmat.primitives.ciphers.modes import CBC, ECB
    CRYPTO_IMPORT_ERROR = None
except ImportError as exc:
    serialization = None
    padding = None
    Cipher = None
    AES = None
    TripleDES = None
    CBC = None
    ECB = None
    CRYPTO_IMPORT_ERROR = exc


SM_CONFIG = {
    'organization': 'UWXspnCCJN4sfYlNfqps',
    'appId': 'default',
    'publicKey': (
        'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmxMNr7n8ZeT0tE1R9j/'
        'mPixoinPkeM+k4VGIn/s0k7N5rJAfnZ0eMER+QhwFvshzo0LNmeUkpR8uIlU/'
        'GEVr8mN28sKmwd2gpygqj0ePnBmOW4v0ZVwbSYK+izkhVFk2V/doLoMbWy6b+'
        'UnA8mkjvg0iYWRByfRsK2gdl7llqCwIDAQAB'
    ),
    'apiHost': 'fp-it.portal101.cn'
}

DES_RULE = {
    'appId': {'is_encrypt': True, 'key': 'uy7mzc4h', 'name': 'xx'},
    'box': {'is_encrypt': False, 'name': 'jf'},
    'canvas': {'is_encrypt': True, 'key': 'snrn887t', 'name': 'yk'},
    'clientSize': {'is_encrypt': True, 'key': 'cpmjjgsu', 'name': 'zx'},
    'organization': {'is_encrypt': True, 'key': '78moqjfc', 'name': 'dp'},
    'os': {'is_encrypt': True, 'key': 'je6vk6t4', 'name': 'pj'},
    'platform': {'is_encrypt': True, 'key': 'pakxhcd2', 'name': 'gm'},
    'plugins': {'is_encrypt': True, 'key': 'v51m3pzl', 'name': 'kq'},
    'pmf': {'is_encrypt': True, 'key': '2mdeslu3', 'name': 'vw'},
    'protocol': {'is_encrypt': False, 'name': 'protocol'},
    'referer': {'is_encrypt': True, 'key': 'y7bmrjlc', 'name': 'ab'},
    'res': {'is_encrypt': True, 'key': 'whxqm2a7', 'name': 'hf'},
    'rtype': {'is_encrypt': True, 'key': 'x8o2h2bl', 'name': 'lo'},
    'sdkver': {'is_encrypt': True, 'key': '9q3dcxp2', 'name': 'sc'},
    'status': {'is_encrypt': True, 'key': '2jbrxxw4', 'name': 'an'},
    'subVersion': {'is_encrypt': True, 'key': 'eo3i2puh', 'name': 'ns'},
    'svm': {'is_encrypt': True, 'key': 'fzj3kaeh', 'name': 'qr'},
    'time': {'is_encrypt': True, 'key': 'q2t3odsk', 'name': 'nb'},
    'timezone': {'is_encrypt': True, 'key': '1uv05lj5', 'name': 'as'},
    'tn': {'is_encrypt': True, 'key': 'x9nzj1bp', 'name': 'py'},
    'trees': {'is_encrypt': True, 'key': 'acfs0xo4', 'name': 'pi'},
    'ua': {'is_encrypt': True, 'key': 'k92crp1t', 'name': 'bj'},
    'url': {'is_encrypt': True, 'key': 'y95hjkoo', 'name': 'cf'},
    'version': {'is_encrypt': False, 'name': 'version'},
    'vpw': {'is_encrypt': True, 'key': 'r9924ab5', 'name': 'ca'}
}

BROWSER_ENV = {
    'plugins': (
        'MicrosoftEdgePDFPluginPortableDocumentFormatinternal-pdf-viewer1,'
        'MicrosoftEdgePDFViewermhjfbmdgcfjbbpaeojofohoefgiehjai1'
    ),
    'ua': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 '
        'Safari/537.36 Edg/129.0.0.0'
    ),
    'canvas': '259ffe69',
    'timezone': -480,
    'platform': 'Win32',
    'url': 'https://www.skland.com/',
    'referer': '',
    'res': '1920_1080_24_1.25',
    'clientSize': '0_0_1080_1920_1920_1080_1920_1080',
    'status': '0011'
}

_device_id_cache = ''


def _encrypt_des_fields(values: dict):
    result = {}
    for field, value in values.items():
        rule = DES_RULE.get(field)
        if not rule:
            result[field] = value
            continue

        output_name = rule['name']
        if not rule['is_encrypt']:
            result[output_name] = value
            continue

        key = rule['key'].encode('utf-8') * 3
        cipher = Cipher(TripleDES(key), ECB())
        raw = str(value).encode('utf-8')
        raw += b'\x00' * (8 - len(raw) % 8)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(raw) + encryptor.finalize()
        result[output_name] = base64.b64encode(encrypted).decode('utf-8')

    return result


def _encrypt_aes(data: bytes, key: bytes):
    cipher = Cipher(AES(key), CBC(b'0102030405060708'))
    data += b'\x00' * (16 - len(data) % 16)
    encryptor = cipher.encryptor()
    return (encryptor.update(data) + encryptor.finalize()).hex()


def _gzip_json(values: dict):
    raw = json.dumps(values, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return base64.b64encode(gzip.compress(raw, compresslevel=2, mtime=0))


def _join_fingerprint_values(values: dict):
    parts = []
    for field in sorted(values):
        value = values[field]
        if isinstance(value, (int, float)):
            parts.append(str(int(value * 10000)))
        elif isinstance(value, dict):
            parts.append(_join_fingerprint_values(value))
        else:
            parts.append(str(value))
    return ''.join(parts)


def _make_smid():
    now = time.localtime()
    timestamp = time.strftime('%Y%m%d%H%M%S', now)
    random_hash = hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()
    base = timestamp + random_hash + '00'
    suffix = hashlib.md5(('smsk_web_' + base).encode('utf-8')).hexdigest()[:14]
    return base + suffix + '0'


def _generate_device_id():
    if CRYPTO_IMPORT_ERROR is not None:
        raise RuntimeError(
            '自动生成设备ID需要cryptography依赖，请先执行: pip install cryptography'
        ) from CRYPTO_IMPORT_ERROR

    uid = str(uuid.uuid4()).encode('utf-8')
    private_id = hashlib.md5(uid).hexdigest()[:16]
    public_key = serialization.load_der_public_key(
        base64.b64decode(SM_CONFIG['publicKey'])
    )
    encrypted_uid = public_key.encrypt(uid, padding.PKCS1v15())

    now_ms = int(time.time() * 1000)
    browser = BROWSER_ENV.copy()
    browser.update({
        'vpw': str(uuid.uuid4()),
        'svm': now_ms,
        'trees': str(uuid.uuid4()),
        'pmf': now_ms
    })
    fingerprint = {
        **browser,
        'protocol': 102,
        'organization': SM_CONFIG['organization'],
        'appId': SM_CONFIG['appId'],
        'os': 'web',
        'version': '3.0.0',
        'sdkver': '3.0.0',
        'box': '',
        'rtype': 'all',
        'smid': _make_smid(),
        'subVersion': '1.0.0',
        'time': 0
    }
    fingerprint['tn'] = hashlib.md5(
        _join_fingerprint_values(fingerprint).encode('utf-8')
    ).hexdigest()

    encrypted_data = _encrypt_aes(
        _gzip_json(_encrypt_des_fields(fingerprint)),
        private_id.encode('utf-8')
    )
    response = requests.post(
        f"https://{SM_CONFIG['apiHost']}/deviceprofile/v4",
        json={
            'appId': SM_CONFIG['appId'],
            'compress': 2,
            'data': encrypted_data,
            'encode': 5,
            'ep': base64.b64encode(encrypted_uid).decode('utf-8'),
            'organization': SM_CONFIG['organization'],
            'os': 'web'
        },
        timeout=20
    )
    response.raise_for_status()
    result = response.json()
    device_id = (result.get('detail') or {}).get('deviceId')
    if result.get('code') != 1100 or not device_id:
        raise RuntimeError(f'设备ID生成失败: {result}')
    return 'B' + device_id


def get_device_id(configured_device_id=''):
    """返回配置的或自动生成的有效 dId，并在当前进程内复用。"""
    global _device_id_cache

    configured_device_id = (configured_device_id or '').strip()
    if configured_device_id:
        if not configured_device_id.startswith('B'):
            raise ValueError(
                'SKYLAND_DID不是有效的森空岛设备ID；有效值应由设备指纹服务签发并以B开头'
            )
        return configured_device_id

    if not _device_id_cache:
        _device_id_cache = _generate_device_id()
    return _device_id_cache


def clear_device_id_cache():
    """丢弃当前进程缓存的设备 ID，使下次调用重新随机生成。"""
    global _device_id_cache
    _device_id_cache = ''

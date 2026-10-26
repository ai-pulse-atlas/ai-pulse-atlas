#!/usr/bin/env python3
"""扫描待发布文本；自检样本仅在内存构造，不回显敏感内容。"""
import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
# 名称、正则、内存中的正例。拆分字面量避免扫描器命中自身。
RULES = [
    ('store-id', r'store' + r'-[0-9a-f]{8}-[0-9a-f]{4}-', 'store' + '-12345678-abcd-'),
    *[(f'private-marker-{i}', re.escape(a + b), a + b) for i, (a, b) in enumerate([
        ('cursor.com/', 'canvas'), ('canvas', '_id'), ('Write', 'Canvas'),
        ('source.', 'canvas'), ('grok/', 'canvas'), ('/home/', 'box'),
        ('/Users', '/'), ('local', 'host'), ('127.0.', '0.1'), ('grok', 'bot')])],
    ('email', r'[A-Z0-9.!#$%&\x27*+/=?^_`{|}~-]+@' + r'[A-Z0-9-]+(?:\.[A-Z0-9-]+)+', 'test' + '@' + 'example.org'),
    ('github-token', re.escape('ghp' + '_'), 'ghp' + '_' + 'a' * 36),
    ('github-pat', re.escape('github' + '_pat_'), 'github' + '_pat_' + 'a' * 40),
    ('api-key', r'sk' + r'-[A-Za-z0-9_-]{20,}', 'sk' + '-' + 'a' * 32),
    ('aws-key', r'AK' + r'IA[A-Z0-9]{16}', 'AK' + 'IA' + 'A' * 16),
    ('private-key', r'-----BE' + r'GIN [^\r\n]*PRIVATE KEY-----', '-----BE' + 'GIN RSA PRIVATE KEY-----'),
]
PATTERNS = [(name, re.compile(pattern, re.I), sample) for name, pattern, sample in RULES]
EXCLUDED = {'.git', 'node_modules', '.venv', '__pycache__'}
EXCLUDED_PATHS = {'build', 'site/dist', 'site/.astro'}


def excluded(path):
    return any(p in EXCLUDED for p in path.parts) or any(path.as_posix() == p or path.as_posix().startswith(p + '/') for p in EXCLUDED_PATHS)


def self_test():
    for name, pattern, sample in PATTERNS:
        assert pattern.search(sample), name
    for safe in ['Grok', 'token', 'https://docs.x.ai/', '模型参数 token']:
        assert not any(p.search(safe) for _, p, _ in PATTERNS), safe
    print(f'自检通过：{len(PATTERNS)} 个模式，4 个合法反例')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    paths = set()
    failures = 0
    for directory, dirs, files in os.walk(ROOT, followlinks=False):
        rel = Path(directory).relative_to(ROOT)
        if 'page' in dirs:
            print(f'{(rel / "page").as_posix()}:1: 禁止的目录')
            failures += 1
        dirs[:] = [d for d in dirs if not excluded(rel / d)]
        paths.update(rel / f for f in files if not excluded(rel / f))
    tracked = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout
    paths.update(Path(s.decode()) for s in tracked.split(b'\0') if s and not excluded(Path(s.decode())))
    count = 0
    for path in sorted(paths):
        full = ROOT / path
        if not full.is_file() or full.is_symlink():
            continue
        raw = full.read_bytes()
        if b'\0' in raw:
            continue
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        count += 1
        for line_number, line in enumerate(content.splitlines(), 1):
            for name, pattern, _ in PATTERNS:
                if pattern.search(line):
                    print(f'{path.as_posix()}:{line_number}: {name}')
                    failures += 1
    print(f'扫描 {count} 个文本文件；命中 {failures}')
    return int(failures > 0)


if __name__ == '__main__':
    raise SystemExit(main())

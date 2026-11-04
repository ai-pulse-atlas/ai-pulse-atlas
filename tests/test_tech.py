"""技术模块测试；所有记录均为样例，仅写入临时目录，不作为线上数据。"""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import common
import validate
import build

# 样例数据，不是真实事件。
SAMPLE = {
    'id': '2026-01-01-example', 'event_date': '2026-01-01',
    'title': '测试样例', 'summary': '仅供单元测试的虚构记录。',
    'tech_category': 'release', 'impact': 'B', 'impact_reason': '样例理由',
    'orgs': ['OpenAI'], 'verified': 'official',
    'sources': [{'url': 'https://example.com/sample', 'publisher': '样例', 'type': 'official'}],
    'created_at': '2026-01-01T12:00:00+08:00', 'updated_at': '2026-01-01T12:00:00+08:00',
}


class TechTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        (self.root / 'data/manifest.json').write_text('{}')
        self.ev = copy.deepcopy(SAMPLE)
        self.patcher = patch.object(common, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def write(self, track, records):
        directory = self.root / 'data' / track
        directory.mkdir(exist_ok=True)
        (directory / '2026-01.jsonl').write_text('\n'.join(json.dumps(e) for e in records))

    def check(self, track='tech'):
        # 配置和 schema 用仓库版本，数据从隔离临时目录读取。
        with patch.object(validate, 'load_taxonomy', lambda: __import__('yaml').safe_load((ROOT / 'data/taxonomy.yaml').read_text())), patch.object(validate, 'load_entities', lambda: __import__('yaml').safe_load((ROOT / 'data/entities.yaml').read_text())):
            return validate.validate_track(track)

    def test_valid_and_categories(self):
        schema = json.loads((ROOT / 'schema/tech-event.schema.json').read_text())
        for category in schema['properties']['tech_category']['enum']:
            self.ev['tech_category'] = category
            self.write('tech', [self.ev])
            self.assertEqual(self.check(), ([], [], 1))

    def test_invalid_records(self):
        cases = [('tech_category', None), ('tech_category', 'unknown'),
                 ('created_at', '2026-01-01T12:00+08:00'),
                 ('updated_at', '2026-01-01T12:00+08:00'),
                 ('created_at', '2026-01-01T04:00:00Z'),
                 ('updated_at', '2026-01-01T04:00:00Z'),
                 ('updated_at', '2026-01-01T12:00:00+09:00'),
                 ('sources', [{'url': 'http://example.com/sample', 'publisher': '样例', 'type': 'official'}])]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                ev = copy.deepcopy(SAMPLE)
                if value is None:
                    del ev[field]
                else:
                    ev[field] = value
                self.write('tech', [ev])
                self.assertTrue(self.check()[0])

    def test_tracks_reject_wrong_schema(self):
        self.write('events', [self.ev])
        self.assertTrue(self.check('events')[0])
        del self.ev['tech_category']
        self.ev.update(category='模型', subcategory='开源权重')
        self.write('tech', [self.ev])
        self.assertTrue(self.check()[0])

    def test_ids_urls_and_references_are_isolated(self):
        ai = copy.deepcopy(self.ev)
        del ai['tech_category']
        ai.update(category='模型', subcategory='开源权重')
        self.write('events', [ai])
        self.write('tech', [self.ev])
        self.assertEqual(self.check(), ([], [], 1))
        self.assertEqual(self.check('events'), ([], [], 1))
        ai['id'] = '2026-01-01-ai-only'
        self.write('events', [ai])
        self.ev['related_ids'] = [ai['id']]
        self.write('tech', [self.ev])
        self.assertTrue(any('related_ids' in e for e in self.check()[0]))
        ai['related_ids'] = [self.ev['id']]
        self.write('events', [ai])
        self.assertTrue(any('related_ids' in e for e in self.check('events')[0]))

    def test_empty_and_populated_build(self):
        self.assertEqual(self.check(), ([], [], 0))
        with patch.object(build, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            build.build_tech()
            self.assertEqual(json.loads((self.root / 'build/tech.json').read_text()), [])
            self.assertEqual(json.loads((self.root / 'build/manifest.json').read_text())['tech'], {'event_count': 0, 'months': {}})
            self.write('tech', [self.ev])
            self.write('events', [dict(self.ev, id='2026-01-01-ai-only')])
            build.build_tech()
            self.assertEqual(json.loads((self.root / 'build/tech.json').read_text()), [self.ev])
            self.assertEqual(json.loads((self.root / 'build/manifest.json').read_text())['tech'], {'event_count': 1, 'months': {'2026-01': 1}})
            self.assertEqual(len(list(common.iter_events())), 1)
            self.assertEqual(list(common.iter_events())[0][2]['id'], '2026-01-01-ai-only')


if __name__ == '__main__':
    unittest.main()

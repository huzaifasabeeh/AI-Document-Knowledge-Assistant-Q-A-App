import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("sync", Path(__file__).parents[1] / "scripts/sync_notion.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SOURCE = "11111111-1111-1111-1111-111111111111"
PAGE = "22222222-2222-2222-2222-222222222222"

class SyncTests(unittest.TestCase):
    def task(self, managed=True):
        return {"page_id": PAGE, "name": "Test", "status": "Completed", "managed": managed}
    def api(self, calls, status="Planned", source=SOURCE):
        def call(token, page_id, payload=None):
            calls.append(payload)
            return {"parent": {"data_source_id": source},
                    "properties": {"Status": {"type": "status", "status": {
                        "name": payload["properties"]["Status"]["status"]["name"] if payload else status}}}}
        return call
    def test_changed_status_updates(self):
        calls=[]
        self.assertEqual(module.sync(SOURCE,[self.task()],"test",self.api(calls)),1)
        self.assertEqual(calls[-1],{"properties":{"Status":{"status":{"name":"Completed"}}}})
    def test_identical_is_noop(self):
        calls=[]
        self.assertEqual(module.sync(SOURCE,[self.task()],"test",self.api(calls,"Completed")),0)
        self.assertEqual(calls,[None])
    def test_manual_tasks_untouched(self):
        calls=[]
        self.assertEqual(module.sync(SOURCE,[self.task(False)],"test",self.api(calls)),0)
        self.assertEqual(calls,[])
    def test_wrong_parent_aborts_before_write(self):
        calls=[]
        with self.assertRaises(ValueError):
            module.sync(SOURCE,[self.task()],"test",self.api(calls,source=PAGE))
        self.assertEqual(calls,[None])
if __name__ == "__main__":
    unittest.main()

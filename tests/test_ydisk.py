import unittest
import ydisk
from os import path

class TestYDiskClient(unittest.TestCase):
    def setUp(self) -> None:

        token_file_path = "ydisk_token.txt"
        if not path.exists(token_file_path):
            with open(token_file_path, 'tw', encoding='utf-8') as f:
                f.write('Put here your YandexDisk access-token')

        with open(token_file_path, encoding='utf-8') as tokenfile:
            self.access_token = tokenfile.read().strip()

        self.ydisk_client = ydisk.YDiskClient(self.access_token)
        self.dir_path = 'YDisk client - Create Dir Test'

    def test_ydisk_auth(self):
        ydisk_client = ydisk.YDiskClient('')
        self.assertRaises(ydisk.YDiskUnauthorizedError, ydisk_client.create_dir, self.dir_path)

    def test_ydisk_create_new_dir(self):

        if self.ydisk_client.path_exists(self.dir_path):
            self.ydisk_client.delete_file(self.dir_path)
        self.assertEqual(self.ydisk_client.path_exists(self.dir_path), False)
        self.ydisk_client.create_dir(self.dir_path)
        self.assertEqual(self.ydisk_client.path_exists(self.dir_path), True)

    def test_ydisk_create_dir_exists(self):
        if not self.ydisk_client.path_exists(self.dir_path):
            self.ydisk_client.create_dir(self.dir_path)

        self.assertEqual(self.ydisk_client.path_exists(self.dir_path), True)
        self.assertRaises(ydisk.YDiskError, self.ydisk_client.create_dir, self.dir_path)

if __name__ == '__main__':
    unittest.main()

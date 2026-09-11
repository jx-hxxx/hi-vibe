"""3D 큐브가 전달받은 테마 조명을 실제 장면에 사용하는지 검증한다."""
import os
import unittest


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CubeThemeTest(unittest.TestCase):
    def test_ambient_light_uses_theme_value(self):
        path = os.path.join(REPO, "docs", "cube", "cube.js")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        self.assertIn("new THREE.AmbientLight(AMBIENT, 0.5)", source)
        self.assertNotIn("new THREE.AmbientLight(0x8898d0, 0.5)", source)

    def test_cube_script_is_cache_busted(self):
        path = os.path.join(REPO, "docs", "index.html")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        self.assertIn('src="cube/cube.js?v=52.1"', html)


if __name__ == "__main__":
    unittest.main()

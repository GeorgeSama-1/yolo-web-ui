import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding='utf-8')


class UIInformationArchitectureTests(unittest.TestCase):
    def test_main_layout_uses_task_oriented_panel_titles(self):
        source = read_text('web_ui_vite/src/layouts/MainLayout.vue')

        self.assertIn('记录中心', source)
        self.assertIn('任务面板', source)

    def test_sidebar_history_prioritizes_filters_and_compact_management(self):
        source = read_text('web_ui_vite/src/components/SidebarHistory.vue')

        self.assertIn('筛选与定位', source)
        self.assertIn('记录管理', source)
        self.assertLess(source.index('筛选与定位'), source.index('记录管理'))

    def test_sidebar_controls_exposes_runtime_and_result_sections(self):
        source = read_text('web_ui_vite/src/components/SidebarControls.vue')

        self.assertIn('流程链路', source)
        self.assertIn('运行模式', source)
        self.assertIn('检测模型', source)
        self.assertIn('绝缘子框', source)
        self.assertIn('分类模型', source)
        self.assertIn('normal / abnormal', source)
        self.assertIn('状态指示', source)
        self.assertIn('当前结果', source)
        self.assertIn('操作台', source)
        self.assertIn('两阶段检测+分类', source)

    def test_canvas_viewer_uses_workspace_oriented_labels(self):
        source = read_text('web_ui_vite/src/components/CanvasViewer.vue')

        self.assertIn('流程总线', source)
        self.assertIn('阶段 1 检测', source)
        self.assertIn('阶段 2 分类', source)
        self.assertIn('未启用分类', source)
        self.assertIn('当前选中', source)
        self.assertIn('一阶段数量', source)
        self.assertIn('二阶段异常', source)
        self.assertIn('主工作台', source)


if __name__ == '__main__':
    unittest.main()

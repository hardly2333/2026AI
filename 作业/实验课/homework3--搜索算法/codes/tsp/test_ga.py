import unittest
import numpy as np
from main import GeneticAlgTSP  # 替换成你保存代码的文件名

class TestGeneticAlgTSP(unittest.TestCase):

    def setUp(self):
        """每个测试用例执行前的初始化"""
        self.filename = "test.tsp"
        self.ga = GeneticAlgTSP(self.filename)

    def test_data_loading(self):
        """检查数据读取是否正确"""
        self.assertEqual(self.ga.num_cities, 4)
        self.assertEqual(len(self.ga.cities), 4)
        # 检查第一个城市坐标是否为 [0.0, 0.0]
        np.testing.assert_array_almost_equal(self.ga.cities[0], [0.0, 0.0])

    # def test_distance_calculation(self):
    #     """检查距离计算逻辑"""
    #     # 测试一个已知的正方形路径 [0, 1, 2, 3] -> (0,0)-(0,3)-(4,3)-(4,0)-back
    #     test_route = [0, 1, 2, 3]
    #     expected_dist = 3.0 + 4.0 + 3.0 + 4.0  # 14.0
    #     actual_dist = self.ga._calculate_dist(test_route)
    #     self.assertAlmostEqual(actual_dist, expected_dist)

    # def test_population_initialization(self):
    #     """检查种群初始化"""
    #     self.assertEqual(len(self.ga.population), self.ga.pop_size)
    #     for ind in self.ga.population:
    #         # 检查每个个体是否包含了所有城市且没有重复
    #         self.assertEqual(len(set(ind)), self.ga.num_cities)
    #         self.assertEqual(len(ind), self.ga.num_cities)

    # def test_crossover_validity(self):
    #     """检查交叉算子：子代是否合法"""
    #     p1 = [0, 1, 2, 3]
    #     p2 = [3, 2, 1, 0]
    #     child = self.ga._crossover(p1, p2)
        
    #     # 核心检查：子代必须包含所有城市，不多不少
    #     self.assertEqual(len(set(child)), self.ga.num_cities)
    #     self.assertEqual(len(child), self.ga.num_cities)
    #     # 检查是否都是有效的城市索引
    #     for city in child:
    #         self.assertTrue(0 <= city < self.ga.num_cities)

    # def test_mutation_validity(self):
    #     """检查变异算子：变异后是否依然合法"""
    #     ind = [0, 1, 2, 3]
    #     # 强制设置高变异率确保触发变异
    #     self.ga.mutation_rate = 1.0
    #     mutated = self.ga._mutate(ind.copy())
        
    #     # 检查变异后城市是否依然完整
    #     self.assertEqual(len(set(mutated)), self.ga.num_cities)
    #     self.assertEqual(len(mutated), self.ga.num_cities)
    #     # 虽然是随机的，但变异后的列表应该和原列表不同（极大概率）
    #     # 如果城市很少，可能会交换回原样，但在测试中我们可以接受
    #     self.assertCountEqual(ind, mutated) # 检查元素是否一致，不计顺序

    # def test_selection_returns_individual(self):
    #     """检查选择逻辑是否返回一个有效的个体"""
    #     parent = self.ga._select_parent()
    #     self.assertIn(list(parent), [list(i) for i in self.ga.population])

    # def test_iterate_output_format(self):
    #     """检查最终输出格式是否符合作业要求(1-n排列)"""
    #     result = self.ga.iterate(5)
    #     self.assertIsInstance(result, list)
    #     self.assertEqual(len(result), self.ga.num_cities)
    #     # 检查是否是从 1 开始编号
    #     self.assertTrue(all(1 <= x <= self.ga.num_cities for x in result))
    #     self.assertEqual(len(set(result)), self.ga.num_cities)

if __name__ == '__main__':
    unittest.main()
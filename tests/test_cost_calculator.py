"""Unit tests for cost_calculator module."""

import unittest

from tokensage.cost_calculator import CostCalculator
from tokensage.exceptions import ModelNotFoundError


class TestCostCalculator(unittest.TestCase):
    """Tests for the CostCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = CostCalculator()

    def test_list_models(self):
        """Test listing available models."""
        models = self.calculator.list_models()
        self.assertGreater(len(models), 0)
        # Should have models from multiple providers
        providers = set(m["provider"] for m in models)
        self.assertGreater(len(providers), 1)

    def test_list_providers(self):
        """Test listing providers."""
        providers = self.calculator.list_providers()
        self.assertIn("openai", providers)
        self.assertIn("anthropic", providers)

    def test_get_model_info(self):
        """Test getting model info."""
        info = self.calculator.get_model_info("gpt-4o")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "gpt-4o")
        self.assertEqual(info["provider"], "openai")
        self.assertGreater(info["input_price_per_1k"], 0)

    def test_get_model_info_not_found(self):
        """Test getting info for non-existent model."""
        info = self.calculator.get_model_info("nonexistent-model-xyz")
        self.assertIsNone(info)

    def test_calculate_cost(self):
        """Test basic cost calculation."""
        result = self.calculator.calculate_cost(
            "Hello, world!", "gpt-4o", estimated_output_tokens=100
        )
        self.assertGreater(result["input_tokens"], 0)
        self.assertEqual(result["output_tokens"], 100)
        self.assertGreater(result["total_cost"], 0)
        self.assertGreater(result["input_cost"], 0)
        self.assertGreater(result["output_cost"], 0)

    def test_calculate_cost_model_not_found(self):
        """Test cost calculation with unknown model."""
        with self.assertRaises(ModelNotFoundError):
            self.calculator.calculate_cost("Hello", "nonexistent-model")

    def test_calculate_savings(self):
        """Test savings calculation."""
        original = "The quick brown fox jumps over the lazy dog. " * 20
        compressed = "Quick fox jumps over lazy dog. " * 5
        result = self.calculator.calculate_savings(
            original, compressed, "gpt-4o", estimated_output_tokens=100
        )
        self.assertGreater(result["original_input_tokens"], 0)
        self.assertGreater(result["compressed_input_tokens"], 0)
        self.assertGreater(result["tokens_saved"], 0)
        self.assertGreater(result["savings"], 0)
        self.assertGreater(result["savings_percent"], 0)

    def test_calculate_savings_no_savings(self):
        """Test savings when original equals compressed."""
        text = "Hello"
        result = self.calculator.calculate_savings(text, text, "gpt-4o")
        self.assertEqual(result["tokens_saved"], 0)
        self.assertEqual(result["savings"], 0)

    def test_compare_models(self):
        """Test model comparison."""
        text = "Hello, world! This is a test."
        comparisons = self.calculator.compare_models(text, estimated_output_tokens=50)
        self.assertGreater(len(comparisons), 0)
        # Should be sorted by cost
        costs = [c["total_cost"] for c in comparisons]
        self.assertEqual(costs, sorted(costs))

    def test_compare_models_with_provider_filter(self):
        """Test model comparison with provider filter."""
        text = "Hello, world!"
        comparisons = self.calculator.compare_models(
            text, provider_filter="openai"
        )
        for comp in comparisons:
            self.assertEqual(comp["provider"], "openai")

    def test_batch_cost(self):
        """Test batch cost calculation."""
        requests = [
            {"text": "Hello", "output_tokens": 10},
            {"text": "World", "output_tokens": 20},
            {"text": "Test", "output_tokens": 30},
        ]
        result = self.calculator.calculate_batch_cost(requests, "gpt-4o")
        self.assertEqual(result["total_requests"], 3)
        self.assertGreater(result["total_cost"], 0)
        self.assertGreater(result["average_cost_per_request"], 0)
        self.assertEqual(len(result["requests"]), 3)

    def test_batch_cost_empty(self):
        """Test batch cost with empty requests."""
        result = self.calculator.calculate_batch_cost([], "gpt-4o")
        self.assertEqual(result["total_requests"], 0)
        self.assertEqual(result["total_cost"], 0)

    def test_custom_pricing(self):
        """Test adding custom pricing model."""
        calc = CostCalculator(custom_pricing={
            "my-model": {"input_price": 1.0, "output_price": 2.0}
        })
        info = calc.get_model_info("my-model")
        self.assertIsNotNone(info)
        self.assertEqual(info["input_price_per_1k"], 1.0)
        self.assertEqual(info["output_price_per_1k"], 2.0)

    def test_custom_pricing_cost_calculation(self):
        """Test cost calculation with custom pricing."""
        calc = CostCalculator(custom_pricing={
            "my-model": {"input_price": 1.0, "output_price": 2.0}
        })
        result = calc.calculate_cost("Hello", "my-model", estimated_output_tokens=10)
        self.assertGreater(result["total_cost"], 0)

    def test_multiple_providers(self):
        """Test that models from expected providers exist."""
        models = self.calculator.list_models()
        provider_names = [m["provider"] for m in models]
        self.assertIn("openai", provider_names)
        self.assertIn("anthropic", provider_names)
        self.assertIn("google", provider_names)
        self.assertIn("deepseek", provider_names)

    def test_minimum_model_count(self):
        """Test that we have at least 10 models."""
        models = self.calculator.list_models()
        self.assertGreaterEqual(len(models), 10)


if __name__ == "__main__":
    unittest.main()

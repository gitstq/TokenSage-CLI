"""Unit tests for CLI module."""

import json
import os
import tempfile
import unittest

from tokensage.cli import create_parser, main


class TestCLIParser(unittest.TestCase):
    """Tests for the CLI argument parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_no_args(self):
        """Test parser with no arguments."""
        args = self.parser.parse_args([])
        self.assertIsNone(args.command)

    def test_version(self):
        """Test version flag."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--version"])

    def test_compress_text(self):
        """Test compress with text argument."""
        args = self.parser.parse_args(["compress", "Hello world"])
        self.assertEqual(args.command, "compress")
        self.assertEqual(args.text, "Hello world")

    def test_compress_file(self):
        """Test compress with file flag."""
        args = self.parser.parse_args(["compress", "-f", "test.json"])
        self.assertEqual(args.command, "compress")
        self.assertEqual(args.file, "test.json")

    def test_compress_level(self):
        """Test compress with level."""
        args = self.parser.parse_args(["compress", "test", "-l", "aggressive"])
        self.assertEqual(args.level, "aggressive")

    def test_compress_type(self):
        """Test compress with content type."""
        args = self.parser.parse_args(["compress", "test", "-t", "json"])
        self.assertEqual(args.type, "json")

    def test_compress_output(self):
        """Test compress with output file."""
        args = self.parser.parse_args(["compress", "test", "-o", "output.txt"])
        self.assertEqual(args.output, "output.txt")

    def test_compress_json_output(self):
        """Test compress with JSON output."""
        args = self.parser.parse_args(["compress", "test", "--json"])
        self.assertTrue(args.output_json)

    def test_count_text(self):
        """Test count with text argument."""
        args = self.parser.parse_args(["count", "Hello world"])
        self.assertEqual(args.command, "count")
        self.assertEqual(args.text, "Hello world")

    def test_count_strategy(self):
        """Test count with strategy."""
        args = self.parser.parse_args(["count", "test", "-s", "bpe_approx"])
        self.assertEqual(args.strategy, "bpe_approx")

    def test_count_compare(self):
        """Test count with compare flag."""
        args = self.parser.parse_args(["count", "test", "--compare"])
        self.assertTrue(args.compare)

    def test_cost_model(self):
        """Test cost with model."""
        args = self.parser.parse_args(["cost", "test", "-m", "gpt-4o"])
        self.assertEqual(args.model, "gpt-4o")

    def test_cost_output_tokens(self):
        """Test cost with output tokens."""
        args = self.parser.parse_args(["cost", "test", "--output-tokens", "100"])
        self.assertEqual(args.output_tokens, 100)

    def test_cost_compare_models(self):
        """Test cost with model comparison."""
        args = self.parser.parse_args(["cost", "test", "--compare-models"])
        self.assertTrue(args.compare_models)

    def test_proxy_port(self):
        """Test proxy with port."""
        args = self.parser.parse_args(["proxy", "--port", "9090"])
        self.assertEqual(args.port, 9090)

    def test_proxy_host(self):
        """Test proxy with host."""
        args = self.parser.parse_args(["proxy", "--host", "0.0.0.0"])
        self.assertEqual(args.host, "0.0.0.0")

    def test_dashboard(self):
        """Test dashboard command."""
        args = self.parser.parse_args(["dashboard"])
        self.assertEqual(args.command, "dashboard")

    def test_config_generate(self):
        """Test config generate."""
        args = self.parser.parse_args(["config", "--generate"])
        self.assertTrue(args.generate)

    def test_config_show(self):
        """Test config show."""
        args = self.parser.parse_args(["config", "--show"])
        self.assertTrue(args.show)

    def test_config_set(self):
        """Test config set."""
        args = self.parser.parse_args(["config", "--set", "key", "value"])
        self.assertEqual(args.set, ["key", "value"])

    def test_benchmark(self):
        """Test benchmark command."""
        args = self.parser.parse_args(["benchmark", "--iterations", "5"])
        self.assertEqual(args.command, "benchmark")
        self.assertEqual(args.iterations, 5)

    def test_history(self):
        """Test history command."""
        args = self.parser.parse_args(["history", "--limit", "10"])
        self.assertEqual(args.command, "history")
        self.assertEqual(args.limit, 10)

    def test_history_stats(self):
        """Test history stats."""
        args = self.parser.parse_args(["history", "--stats"])
        self.assertTrue(args.stats)

    def test_history_clear(self):
        """Test history clear."""
        args = self.parser.parse_args(["history", "--clear"])
        self.assertTrue(args.clear)


class TestCLIMain(unittest.TestCase):
    """Tests for the CLI main function."""

    def test_main_no_args(self):
        """Test main with no arguments returns 0."""
        exit_code = main([])
        self.assertEqual(exit_code, 0)

    def test_main_compress_text(self):
        """Test main with compress command."""
        exit_code = main(["compress", "Hello, world! This is a test text for compression."])
        self.assertEqual(exit_code, 0)

    def test_main_count_text(self):
        """Test main with count command."""
        exit_code = main(["count", "Hello, world!"])
        self.assertEqual(exit_code, 0)

    def test_main_count_compare(self):
        """Test main with count compare."""
        exit_code = main(["count", "Hello, world!", "--compare"])
        self.assertEqual(exit_code, 0)

    def test_main_cost(self):
        """Test main with cost command."""
        exit_code = main(["cost", "Hello, world!", "-m", "gpt-4o"])
        self.assertEqual(exit_code, 0)

    def test_main_cost_compare_models(self):
        """Test main with cost model comparison."""
        exit_code = main(["cost", "Hello", "--compare-models"])
        self.assertEqual(exit_code, 0)

    def test_main_savings(self):
        """Test main with savings command."""
        text = "The quick brown fox jumps over the lazy dog. " * 10
        exit_code = main(["savings", text])
        self.assertEqual(exit_code, 0)

    def test_main_benchmark(self):
        """Test main with benchmark command."""
        exit_code = main(["benchmark", "--iterations", "3", "--text-size", "200"])
        self.assertEqual(exit_code, 0)

    def test_main_history(self):
        """Test main with history command."""
        exit_code = main(["history", "--limit", "5"])
        self.assertEqual(exit_code, 0)

    def test_main_config_list_models(self):
        """Test main with config list models."""
        exit_code = main(["config", "--list-models"])
        self.assertEqual(exit_code, 0)

    def test_main_config_list_providers(self):
        """Test main with config list providers."""
        exit_code = main(["config", "--list-providers"])
        self.assertEqual(exit_code, 0)

    def test_main_compress_file(self):
        """Test main with compress file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"name": "test", "value": 42, "items": [1, 2, 3]}, f)
            f.flush()
            path = f.name

        try:
            exit_code = main(["compress", "-f", path, "--json"])
            self.assertEqual(exit_code, 0)
        finally:
            os.unlink(path)

    def test_main_compress_json_output(self):
        """Test main with JSON output."""
        exit_code = main(["compress", "Hello world", "--json"])
        self.assertEqual(exit_code, 0)

    def test_main_count_json_output(self):
        """Test main with count JSON output."""
        exit_code = main(["count", "Hello world", "--json"])
        self.assertEqual(exit_code, 0)

    def test_main_unknown_command(self):
        """Test main with unknown command."""
        with self.assertRaises(SystemExit):
            main(["nonexistent_command"])


if __name__ == "__main__":
    unittest.main()

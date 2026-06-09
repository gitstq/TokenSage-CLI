"""CLI entry point for TokenSage-CLI.

Provides the command-line interface with subcommands for compression,
token counting, cost calculation, proxy mode, dashboard, and more.
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from tokensage import __version__
from tokensage.compressor import Compressor
from tokensage.config_manager import ConfigManager
from tokensage.cost_calculator import CostCalculator
from tokensage.exceptions import (
    CompressionError,
    ConfigurationError,
    CostCalculationError,
    ModelNotFoundError,
    TokenSageError,
    TokenCountError,
)
from tokensage.history import HistoryManager, HistoryRecord
from tokensage.models.compression import CompressionConfig, CompressionLevel, ContentType
from tokensage.token_counter import TokenCounter, TokenStrategy
from tokensage.tui_dashboard import get_dashboard
from tokensage.utils import (
    detect_content_type,
    detect_language,
    format_cost,
    format_number,
    read_file_safe,
    write_file_safe,
)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="tokensage",
        description="TokenSage-CLI: Lightweight Terminal AI Token Compression & Cost Optimization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tokensage compress "Hello world, this is a test text"
  tokensage compress -f input.json --level aggressive
  tokensage count -f document.md
  tokensage cost -f prompt.txt --model gpt-4o --output-tokens 1000
  tokensage proxy --port 8080
  tokensage dashboard
  tokensage benchmark -f test_data.json
  tokensage history --limit 10
  tokensage config --generate
        """,
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # compress subcommand
    compress_parser = subparsers.add_parser(
        "compress", help="Compress text or file content"
    )
    compress_parser.add_argument(
        "text", nargs="?", help="Text to compress (omit if using -f)"
    )
    compress_parser.add_argument(
        "-f", "--file", help="Read input from file"
    )
    compress_parser.add_argument(
        "-o", "--output", help="Write compressed output to file"
    )
    compress_parser.add_argument(
        "-l", "--level",
        choices=["mild", "medium", "aggressive"],
        default=None,
        help="Compression level (default: from config or medium)",
    )
    compress_parser.add_argument(
        "-t", "--type",
        choices=["auto", "json", "code", "markdown", "text"],
        default="auto",
        help="Content type (default: auto-detect)",
    )
    compress_parser.add_argument(
        "-s", "--strategy",
        choices=["auto", "json", "code", "markdown", "text", "cn_optimize"],
        default="auto",
        help="Compression strategy (default: auto)",
    )
    compress_parser.add_argument(
        "--max-tokens", type=int, default=None, help="Maximum output tokens"
    )
    compress_parser.add_argument(
        "--no-save-history", action="store_true", help="Do not save to history"
    )
    compress_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    # count subcommand
    count_parser = subparsers.add_parser(
        "count", help="Count tokens in text or file"
    )
    count_parser.add_argument(
        "text", nargs="?", help="Text to count tokens for (omit if using -f)"
    )
    count_parser.add_argument(
        "-f", "--file", help="Read input from file"
    )
    count_parser.add_argument(
        "-s", "--strategy",
        choices=["bpe_approx", "char_level", "hybrid"],
        default="hybrid",
        help="Token counting strategy (default: hybrid)",
    )
    count_parser.add_argument(
        "--compare", action="store_true", help="Compare all strategies"
    )
    count_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    # cost subcommand
    cost_parser = subparsers.add_parser(
        "cost", help="Calculate LLM API costs"
    )
    cost_parser.add_argument(
        "text", nargs="?", help="Text to calculate cost for (omit if using -f)"
    )
    cost_parser.add_argument(
        "-f", "--file", help="Read input from file"
    )
    cost_parser.add_argument(
        "-m", "--model", default=None, help="LLM model name (default: gpt-4o)"
    )
    cost_parser.add_argument(
        "--output-tokens", type=int, default=0, help="Estimated output tokens"
    )
    cost_parser.add_argument(
        "--compare-models", action="store_true", help="Compare costs across models"
    )
    cost_parser.add_argument(
        "--provider", default=None, help="Filter by provider for comparison"
    )
    cost_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    # savings subcommand
    savings_parser = subparsers.add_parser(
        "savings", help="Calculate cost savings from compression"
    )
    savings_parser.add_argument(
        "text", nargs="?", help="Text to analyze (omit if using -f)"
    )
    savings_parser.add_argument(
        "-f", "--file", help="Read input from file"
    )
    savings_parser.add_argument(
        "-m", "--model", default="gpt-4o", help="LLM model name"
    )
    savings_parser.add_argument(
        "-l", "--level",
        choices=["mild", "medium", "aggressive"],
        default="medium",
        help="Compression level",
    )
    savings_parser.add_argument(
        "--output-tokens", type=int, default=0, help="Estimated output tokens"
    )
    savings_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    # proxy subcommand
    proxy_parser = subparsers.add_parser(
        "proxy", help="Start HTTP proxy mode"
    )
    proxy_parser.add_argument(
        "--host", default="127.0.0.1", help="Proxy bind address (default: 127.0.0.1)"
    )
    proxy_parser.add_argument(
        "--port", type=int, default=None, help="Proxy port (default: from config or 8080)"
    )
    proxy_parser.add_argument(
        "--target-host", default=None, help="Target API host"
    )
    proxy_parser.add_argument(
        "--target-port", type=int, default=None, help="Target API port"
    )
    proxy_parser.add_argument(
        "-l", "--level",
        choices=["mild", "medium", "aggressive"],
        default=None,
        help="Compression level for proxy",
    )

    # dashboard subcommand
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Open TUI dashboard"
    )
    dashboard_parser.add_argument(
        "--history-limit", type=int, default=20, help="History records to show"
    )

    # config subcommand
    config_parser = subparsers.add_parser(
        "config", help="Manage configuration"
    )
    config_parser.add_argument(
        "--generate", action="store_true", help="Generate default config file"
    )
    config_parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )
    config_parser.add_argument(
        "--path", action="store_true", help="Show config file path"
    )
    config_parser.add_argument(
        "--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a config value"
    )
    config_parser.add_argument(
        "--get", metavar="KEY", help="Get a config value"
    )
    config_parser.add_argument(
        "--add-pricing", nargs=4, metavar=("MODEL", "INPUT_PRICE", "OUTPUT_PRICE", "PROVIDER"),
        help="Add custom model pricing"
    )
    config_parser.add_argument(
        "--list-models", action="store_true", help="List all available models"
    )
    config_parser.add_argument(
        "--list-providers", action="store_true", help="List all providers"
    )

    # benchmark subcommand
    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Run compression benchmarks"
    )
    benchmark_parser.add_argument(
        "-f", "--file", help="File to benchmark against"
    )
    benchmark_parser.add_argument(
        "--text-size", type=int, default=1000, help="Generate test text of N characters"
    )
    benchmark_parser.add_argument(
        "--iterations", type=int, default=10, help="Number of iterations"
    )
    benchmark_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    # history subcommand
    history_parser = subparsers.add_parser(
        "history", help="View compression history"
    )
    history_parser.add_argument(
        "--limit", type=int, default=20, help="Number of records to show"
    )
    history_parser.add_argument(
        "--stats", action="store_true", help="Show aggregate statistics"
    )
    history_parser.add_argument(
        "--clear", action="store_true", help="Clear all history"
    )
    history_parser.add_argument(
        "--json", action="store_true", dest="output_json", help="Output as JSON"
    )

    return parser


def get_input_text(args: argparse.Namespace) -> str:
    """Get input text from command line arguments or file.

    Args:
        args: Parsed command line arguments.

    Returns:
        Input text string.

    Raises:
        TokenSageError: If no input is provided.
    """
    if args.file:
        try:
            return read_file_safe(args.file)
        except FileNotFoundError:
            raise TokenSageError(f"File not found: {args.file}")
        except IOError as e:
            raise TokenSageError(f"Failed to read file: {e}")

    if hasattr(args, "text") and args.text:
        return args.text

    # Try reading from stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    raise TokenSageError("No input provided. Use text argument, -f file, or pipe from stdin.")


def cmd_compress(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the compress subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        text = get_input_text(args)

        # Build compression config
        level_str = args.level or config.get("compression.default_level", "medium")
        strategy_str = args.strategy if args.strategy != "auto" else None

        comp_config = CompressionConfig(
            level=CompressionLevel(level_str),
            content_type=ContentType(args.type),
            max_output_tokens=args.max_tokens,
        )

        compressor = Compressor(comp_config)
        result = compressor.compress(text)

        # Save to history
        if not args.no_save_history and config.get("history.enabled", True):
            history = HistoryManager()
            record = HistoryRecord(
                operation="compress",
                input_text_preview=text[:200],
                original_tokens=result.original_tokens,
                compressed_tokens=result.compressed_tokens,
                strategy=result.strategy,
                level=result.level.value,
                content_type=result.content_type.value,
                savings_percent=result.compression_ratio,
            )
            history.add_record(record)

        # Output
        if args.output_json:
            output = result.to_dict()
            output["compressed_text"] = result.compressed_text
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            dashboard = get_dashboard()
            output = dashboard.show_compression_result(result.to_dict())
            if output:
                print(output)

        # Write to file if requested
        if args.output:
            write_file_safe(args.output, result.compressed_text)
            print(f"\nCompressed output written to: {args.output}")

        return 0

    except TokenSageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_count(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the count subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        text = get_input_text(args)

        strategy = TokenStrategy(args.strategy)
        counter = TokenCounter(strategy=strategy)

        if args.compare:
            report = counter.count_with_report(text)
            if args.output_json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"\nToken Count Report")
                print(f"{'=' * 40}")
                print(f"  Text Length:     {format_number(len(text))} characters")
                print(f"  Line Count:      {report['line_count']}")
                print(f"  Content Type:    {report['content_type']}")
                print(f"")
                print(f"  BPE Approximate: {format_number(report['bpe_approx_tokens'])} tokens")
                print(f"  Char Level:      {format_number(report['char_level_tokens'])} tokens")
                print(f"  Hybrid:          {format_number(report['hybrid_tokens'])} tokens")
                print(f"")
                print(f"  Recommended:     {format_number(report['recommended_estimate'])} tokens")
        else:
            count = counter.count(text)
            report = counter.count_with_report(text)
            if args.output_json:
                print(json.dumps({
                    "tokens": count,
                    "strategy": args.strategy,
                    "text_length": len(text),
                    "content_type": report["content_type"],
                }, indent=2))
            else:
                print(f"\nToken Count: {format_number(count)}")
                print(f"  Strategy:     {args.strategy}")
                print(f"  Text Length:  {format_number(len(text))} characters")
                print(f"  Content Type: {report['content_type']}")

        return 0

    except TokenSageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_cost(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the cost subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        model_name = args.model or config.get("cost_calculator.default_model", "gpt-4o")
        custom_pricing = config.get_custom_pricing()
        calculator = CostCalculator(custom_pricing=custom_pricing)

        if args.compare_models:
            text = get_input_text(args) if (hasattr(args, 'text') and args.text) or args.file else "Hello world"
            if args.file:
                text = read_file_safe(args.file)
            comparisons = calculator.compare_models(
                text, args.output_tokens, args.provider
            )
            if args.output_json:
                print(json.dumps(comparisons, indent=2))
            else:
                dashboard = get_dashboard()
                output = dashboard.show_model_comparison(comparisons)
                if output:
                    print(output)
        else:
            text = get_input_text(args)
            result = calculator.calculate_cost(
                text, model_name, args.output_tokens
            )
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\nCost Analysis for {model_name}")
                print(f"{'=' * 40}")
                print(f"  Input Tokens:   {format_number(result['input_tokens'])}")
                print(f"  Output Tokens:  {format_number(result['output_tokens'])}")
                print(f"  Input Cost:     {format_cost(result['input_cost'])}")
                print(f"  Output Cost:    {format_cost(result['output_cost'])}")
                print(f"  Total Cost:     {format_cost(result['total_cost'])}")
                print(f"  Context Usage:  {result['context_usage_percent']:.1f}%")

        return 0

    except ModelNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except TokenSageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_savings(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the savings subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        text = get_input_text(args)
        custom_pricing = config.get_custom_pricing()
        calculator = CostCalculator(custom_pricing=custom_pricing)

        comp_config = CompressionConfig(level=CompressionLevel(args.level))
        compressor = Compressor(comp_config)
        result = compressor.compress(text)

        savings = calculator.calculate_savings(
            result.original_text,
            result.compressed_text,
            args.model,
            args.output_tokens,
        )

        if args.output_json:
            print(json.dumps(savings, indent=2))
        else:
            dashboard = get_dashboard()
            output = dashboard.show_cost_analysis(savings)
            if output:
                print(output)

        return 0

    except TokenSageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_proxy(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the proxy subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    from tokensage.proxy_mode import ProxyServer

    try:
        port = args.port or config.get("proxy.port", 8080)
        level = args.level or config.get("proxy.compression_level", "medium")

        server = ProxyServer(
            host=args.host,
            port=port,
            target_host=args.target_host or config.get("proxy.target_host"),
            target_port=args.target_port or config.get("proxy.target_port"),
            compression_level=level,
        )
        server.start(blocking=True)
        return 0

    except KeyboardInterrupt:
        print("\nProxy stopped.")
        return 0
    except ProxyError as e:
        print(f"Proxy error: {e}", file=sys.stderr)
        return 1


def cmd_dashboard(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the dashboard subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        dashboard = get_dashboard()
        history = HistoryManager()

        # Show welcome
        output = dashboard.show_welcome()
        if output:
            print(output)

        # Show stats
        stats = history.get_stats()
        output = dashboard.show_stats(stats)
        if output:
            print(output)

        # Show recent history
        records = history.get_records(limit=args.history_limit)
        output = dashboard.show_history(records, limit=args.history_limit)
        if output:
            print(output)

        # Show savings chart if there's data
        if len(history) > 0:
            all_records = history.get_records(limit=100)
            output = dashboard.show_savings_chart(all_records)
            if output:
                print(output)

        return 0

    except Exception as e:
        print(f"Dashboard error: {e}", file=sys.stderr)
        return 1


def cmd_config(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the config subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        if args.generate:
            path = config.generate_default_config()
            print(f"Default configuration generated: {path}")
            return 0

        if args.path:
            print(config.config_path)
            return 0

        if args.show:
            print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.set:
            key, value = args.set
            # Try to parse value as JSON
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value
            config.set(key, parsed_value)
            config.save()
            print(f"Set {key} = {parsed_value}")
            return 0

        if args.get:
            value = config.get(args.get)
            print(json.dumps(value, indent=2, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value))
            return 0

        if args.add_pricing:
            model, input_price, output_price, provider = args.add_pricing
            config.add_custom_pricing(model, float(input_price), float(output_price))
            config.save()
            print(f"Added custom pricing for {model} (provider: {provider})")
            return 0

        if args.list_models:
            calculator = CostCalculator(custom_pricing=config.get_custom_pricing())
            models = calculator.list_models()
            for m in models:
                print(f"  {m['name']:<25} {m['provider']:<12} "
                      f"in:${m['input_price_per_1k']:<8.4f} out:${m['output_price_per_1k']:<8.4f}")
            return 0

        if args.list_providers:
            calculator = CostCalculator(custom_pricing=config.get_custom_pricing())
            providers = calculator.list_providers()
            for p in providers:
                print(f"  {p}")
            return 0

        # Default: show config
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
        return 0

    except (ConfigurationError, TokenSageError) as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 1


def cmd_benchmark(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the benchmark subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        # Get or generate test text
        if args.file:
            text = read_file_safe(args.file)
        else:
            # Generate test text
            text = "This is a sample text for benchmarking token compression. " * (args.text_size // 60)
            text = text[:args.text_size]

        results = []
        levels = ["mild", "medium", "aggressive"]

        print(f"\nBenchmark: {len(text)} characters, {args.iterations} iterations")
        print(f"{'=' * 60}")

        for level in levels:
            comp_config = CompressionConfig(level=CompressionLevel(level))
            compressor = Compressor(comp_config)

            # Warm-up
            compressor.compress(text)

            # Benchmark
            start_time = time.time()
            for _ in range(args.iterations):
                result = compressor.compress(text)
            elapsed = time.time() - start_time

            avg_time = elapsed / args.iterations
            results.append({
                "level": level,
                "original_tokens": result.original_tokens,
                "compressed_tokens": result.compressed_tokens,
                "tokens_saved": result.tokens_saved,
                "compression_ratio": result.compression_ratio,
                "total_time": elapsed,
                "avg_time": avg_time,
                "iterations": args.iterations,
            })

            print(f"  {level:<12} | {result.original_tokens:>6} -> {result.compressed_tokens:>6} tokens "
                  f"| saved {result.compression_ratio:>5.1f}% | {avg_time*1000:>6.1f}ms/op")

        if args.output_json:
            print("\n" + json.dumps(results, indent=2))

        return 0

    except TokenSageError as e:
        print(f"Benchmark error: {e}", file=sys.stderr)
        return 1


def cmd_history(args: argparse.Namespace, config: ConfigManager) -> int:
    """Handle the history subcommand.

    Args:
        args: Parsed command line arguments.
        config: Configuration manager.

    Returns:
        Exit code.
    """
    try:
        history = HistoryManager()

        if args.clear:
            count = history.clear()
            print(f"Cleared {count} history records.")
            return 0

        if args.stats:
            stats = history.get_stats()
            if args.output_json:
                print(json.dumps(stats, indent=2))
            else:
                dashboard = get_dashboard()
                output = dashboard.show_stats(stats)
                if output:
                    print(output)
            return 0

        records = history.get_records(limit=args.limit)
        if args.output_json:
            print(json.dumps([r.to_dict() for r in records], indent=2, ensure_ascii=False))
        else:
            dashboard = get_dashboard()
            output = dashboard.show_history(records, limit=args.limit)
            if output:
                print(output)

        return 0

    except Exception as e:
        print(f"History error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv).

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # Load configuration
    try:
        config = ConfigManager()
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    # Dispatch to command handler
    handlers = {
        "compress": cmd_compress,
        "count": cmd_count,
        "cost": cmd_cost,
        "savings": cmd_savings,
        "proxy": cmd_proxy,
        "dashboard": cmd_dashboard,
        "config": cmd_config,
        "benchmark": cmd_benchmark,
        "history": cmd_history,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

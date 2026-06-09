"""Cost calculation engine for TokenSage-CLI.

Calculates LLM API costs based on token usage and model pricing.
Supports built-in pricing for major LLM providers and custom pricing.
"""

from typing import Any, Dict, List, Optional, Tuple

from tokensage.exceptions import CostCalculationError, ModelNotFoundError
from tokensage.models.pricing import PricingDatabase, PricingModel, get_builtin_pricing
from tokensage.token_counter import TokenCounter


class CostCalculator:
    """LLM API cost calculation engine.

    Provides cost estimation for LLM API calls based on token counts
    and model pricing. Supports batch calculations and savings analysis.
    """

    def __init__(self, custom_pricing: Optional[Dict[str, Dict]] = None):
        """Initialize the cost calculator.

        Args:
            custom_pricing: Optional dictionary of custom model pricing.
                Format: {"model_name": {"input_price": float, "output_price": float}}
        """
        self._pricing_db = get_builtin_pricing()
        self._counter = TokenCounter()

        # Add custom pricing
        if custom_pricing:
            for model_name, pricing in custom_pricing.items():
                self.add_custom_model(
                    model_name=model_name,
                    input_price=pricing.get("input_price", 0),
                    output_price=pricing.get("output_price", 0),
                    context_window=pricing.get("context_window", 8192),
                )

    def add_custom_model(
        self,
        model_name: str,
        input_price: float,
        output_price: float,
        context_window: int = 8192,
        max_output: int = 4096,
        provider: str = "custom",
        description: str = "",
    ) -> None:
        """Add a custom pricing model.

        Args:
            model_name: Name for the custom model.
            input_price: Price per 1K input tokens in USD.
            output_price: Price per 1K output tokens in USD.
            context_window: Maximum context window in tokens.
            max_output: Maximum output tokens.
            provider: Provider name.
            description: Model description.
        """
        model = PricingModel(
            name=model_name,
            provider=provider,
            input_price_per_1k=input_price,
            output_price_per_1k=output_price,
            context_window=context_window,
            max_output=max_output,
            description=description or f"Custom model: {model_name}",
        )
        self._pricing_db.add_model(model)

    def calculate_cost(
        self,
        text: str,
        model_name: str,
        estimated_output_tokens: int = 0,
        is_input: bool = True,
    ) -> Dict[str, Any]:
        """Calculate the cost for processing text with a specific model.

        Args:
            text: The text to process.
            model_name: The LLM model name.
            estimated_output_tokens: Estimated output tokens.
            is_input: Whether the text is input (prompt) text.

        Returns:
            Dictionary with cost details.

        Raises:
            ModelNotFoundError: If the model is not found.
        """
        model = self._pricing_db.get_model(model_name)
        if not model:
            raise ModelNotFoundError(
                f"Model '{model_name}' not found. "
                f"Use list_models() to see available models."
            )

        input_tokens = self._counter.count(text) if is_input else 0
        output_tokens = estimated_output_tokens

        input_cost = (input_tokens / 1000.0) * model.input_price_per_1k
        output_cost = (output_tokens / 1000.0) * model.output_price_per_1k
        total_cost = input_cost + output_cost

        return {
            "model": model_name,
            "provider": model.provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "context_window": model.context_window,
            "context_usage_percent": (
                input_tokens / model.context_window * 100
                if model.context_window > 0
                else 0
            ),
        }

    def calculate_savings(
        self,
        original_text: str,
        compressed_text: str,
        model_name: str,
        estimated_output_tokens: int = 0,
    ) -> Dict[str, Any]:
        """Calculate cost savings from text compression.

        Args:
            original_text: Original uncompressed text.
            compressed_text: Compressed text.
            model_name: The LLM model name.
            estimated_output_tokens: Estimated output tokens.

        Returns:
            Dictionary with savings details.

        Raises:
            ModelNotFoundError: If the model is not found.
        """
        model = self._pricing_db.get_model(model_name)
        if not model:
            raise ModelNotFoundError(f"Model '{model_name}' not found.")

        original_input_tokens = self._counter.count(original_text)
        compressed_input_tokens = self._counter.count(compressed_text)

        original_cost = model.calculate_cost(original_input_tokens, estimated_output_tokens)
        compressed_cost = model.calculate_cost(compressed_input_tokens, estimated_output_tokens)

        savings = original_cost - compressed_cost
        savings_percent = (savings / original_cost * 100) if original_cost > 0 else 0

        return {
            "model": model_name,
            "provider": model.provider,
            "original_input_tokens": original_input_tokens,
            "compressed_input_tokens": compressed_input_tokens,
            "tokens_saved": original_input_tokens - compressed_input_tokens,
            "token_savings_percent": (
                (original_input_tokens - compressed_input_tokens)
                / original_input_tokens
                * 100
                if original_input_tokens > 0
                else 0
            ),
            "output_tokens": estimated_output_tokens,
            "original_cost": original_cost,
            "compressed_cost": compressed_cost,
            "savings": savings,
            "savings_percent": savings_percent,
        }

    def calculate_batch_cost(
        self,
        requests: List[Dict[str, Any]],
        model_name: str,
    ) -> Dict[str, Any]:
        """Calculate total cost for a batch of requests.

        Args:
            requests: List of request dicts with 'text' and optional 'output_tokens'.
            model_name: The LLM model name.

        Returns:
            Dictionary with batch cost details.

        Raises:
            ModelNotFoundError: If the model is not found.
        """
        model = self._pricing_db.get_model(model_name)
        if not model:
            raise ModelNotFoundError(f"Model '{model_name}' not found.")

        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        request_costs = []

        for i, req in enumerate(requests):
            text = req.get("text", "")
            output_tokens = req.get("output_tokens", 0)

            input_tokens = self._counter.count(text)
            cost = model.calculate_cost(input_tokens, output_tokens)

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost += cost

            request_costs.append({
                "request_index": i,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            })

        return {
            "model": model_name,
            "provider": model.provider,
            "total_requests": len(requests),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost": total_cost,
            "average_cost_per_request": total_cost / len(requests) if requests else 0,
            "requests": request_costs,
        }

    def compare_models(
        self,
        text: str,
        estimated_output_tokens: int = 0,
        provider_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Compare costs across all (or filtered) models.

        Args:
            text: The text to process.
            estimated_output_tokens: Estimated output tokens.
            provider_filter: Optional provider name to filter by.

        Returns:
            List of cost comparison dictionaries, sorted by total cost.
        """
        models = self._pricing_db.list_models(provider=provider_filter)
        input_tokens = self._counter.count(text)

        comparisons = []
        for model in models:
            cost = model.calculate_cost(input_tokens, estimated_output_tokens)
            comparisons.append({
                "model": model.name,
                "provider": model.provider,
                "input_tokens": input_tokens,
                "output_tokens": estimated_output_tokens,
                "input_cost": (input_tokens / 1000.0) * model.input_price_per_1k,
                "output_cost": (estimated_output_tokens / 1000.0) * model.output_price_per_1k,
                "total_cost": cost,
                "description": model.description,
            })

        comparisons.sort(key=lambda x: x["total_cost"])
        return comparisons

    def list_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available pricing models.

        Args:
            provider: Optional provider filter.

        Returns:
            List of model information dictionaries.
        """
        models = self._pricing_db.list_models(provider=provider)
        return [
            {
                "name": m.name,
                "provider": m.provider,
                "input_price_per_1k": m.input_price_per_1k,
                "output_price_per_1k": m.output_price_per_1k,
                "context_window": m.context_window,
                "max_output": m.max_output,
                "description": m.description,
            }
            for m in models
        ]

    def list_providers(self) -> List[str]:
        """List all available providers.

        Returns:
            List of provider names.
        """
        return self._pricing_db.list_providers()

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model.

        Args:
            model_name: The model name to look up.

        Returns:
            Model information dictionary, or None if not found.
        """
        model = self._pricing_db.get_model(model_name)
        if not model:
            return None
        return {
            "name": model.name,
            "provider": model.provider,
            "input_price_per_1k": model.input_price_per_1k,
            "output_price_per_1k": model.output_price_per_1k,
            "context_window": model.context_window,
            "max_output": model.max_output,
            "description": model.description,
        }

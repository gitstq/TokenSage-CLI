"""Data models for pricing information."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PricingModel:
    """Pricing information for a specific LLM model.

    Attributes:
        name: Display name of the model.
        provider: The service provider (e.g., 'openai', 'anthropic').
        input_price_per_1k: Price per 1,000 input tokens in USD.
        output_price_per_1k: Price per 1,000 output tokens in USD.
        context_window: Maximum context window size in tokens.
        max_output: Maximum output tokens.
        description: Brief description of the model.
    """

    name: str
    provider: str
    input_price_per_1k: float
    output_price_per_1k: float
    context_window: int = 8192
    max_output: int = 4096
    description: str = ""

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the total cost for a given number of tokens.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Total cost in USD.
        """
        input_cost = (input_tokens / 1000.0) * self.input_price_per_1k
        output_cost = (output_tokens / 1000.0) * self.output_price_per_1k
        return input_cost + output_cost

    def calculate_savings(
        self,
        original_input_tokens: int,
        compressed_input_tokens: int,
        output_tokens: int = 0,
    ) -> Dict[str, float]:
        """Calculate cost savings from compression.

        Args:
            original_input_tokens: Original number of input tokens.
            compressed_input_tokens: Number of tokens after compression.
            output_tokens: Number of output tokens (unchanged by compression).

        Returns:
            Dictionary with original_cost, compressed_cost, savings,
            savings_percent, and tokens_saved.
        """
        original_cost = self.calculate_cost(original_input_tokens, output_tokens)
        compressed_cost = self.calculate_cost(compressed_input_tokens, output_tokens)
        savings = original_cost - compressed_cost
        savings_percent = (
            (savings / original_cost * 100.0) if original_cost > 0 else 0.0
        )
        tokens_saved = original_input_tokens - compressed_input_tokens
        return {
            "original_cost": original_cost,
            "compressed_cost": compressed_cost,
            "savings": savings,
            "savings_percent": savings_percent,
            "tokens_saved": tokens_saved,
        }


@dataclass
class PricingDatabase:
    """Database of LLM pricing models.

    Provides access to built-in pricing data and supports adding
    custom models.
    """

    models: Dict[str, PricingModel] = field(default_factory=dict)

    def add_model(self, model: PricingModel) -> None:
        """Add or update a pricing model.

        Args:
            model: The PricingModel to add.
        """
        self.models[model.name.lower()] = model

    def get_model(self, name: str) -> Optional[PricingModel]:
        """Get a pricing model by name (case-insensitive).

        Args:
            name: The model name to look up.

        Returns:
            The PricingModel if found, None otherwise.
        """
        return self.models.get(name.lower())

    def list_models(self, provider: Optional[str] = None) -> list:
        """List all models, optionally filtered by provider.

        Args:
            provider: If specified, only return models from this provider.

        Returns:
            List of PricingModel objects.
        """
        if provider:
            return [
                m for m in self.models.values() if m.provider.lower() == provider.lower()
            ]
        return list(self.models.values())

    def list_providers(self) -> list:
        """List all unique providers.

        Returns:
            List of provider name strings.
        """
        providers = set(m.provider for m in self.models.values())
        return sorted(providers)


def get_builtin_pricing() -> PricingDatabase:
    """Get the built-in pricing database with popular LLM models.

    Returns:
        A PricingDatabase populated with current pricing data.
    """
    db = PricingDatabase()

    # OpenAI Models
    db.add_model(
        PricingModel(
            name="gpt-4o",
            provider="openai",
            input_price_per_1k=2.50,
            output_price_per_1k=10.00,
            context_window=128000,
            max_output=16384,
            description="GPT-4o multimodal flagship model",
        )
    )
    db.add_model(
        PricingModel(
            name="gpt-4o-mini",
            provider="openai",
            input_price_per_1k=0.15,
            output_price_per_1k=0.60,
            context_window=128000,
            max_output=16384,
            description="GPT-4o-mini cost-effective model",
        )
    )
    db.add_model(
        PricingModel(
            name="gpt-4-turbo",
            provider="openai",
            input_price_per_1k=10.00,
            output_price_per_1k=30.00,
            context_window=128000,
            max_output=4096,
            description="GPT-4 Turbo with vision",
        )
    )
    db.add_model(
        PricingModel(
            name="gpt-3.5-turbo",
            provider="openai",
            input_price_per_1k=0.50,
            output_price_per_1k=1.50,
            context_window=16385,
            max_output=4096,
            description="GPT-3.5 Turbo legacy model",
        )
    )

    # Anthropic Models
    db.add_model(
        PricingModel(
            name="claude-3.5-sonnet",
            provider="anthropic",
            input_price_per_1k=3.00,
            output_price_per_1k=15.00,
            context_window=200000,
            max_output=8192,
            description="Claude 3.5 Sonnet balanced model",
        )
    )
    db.add_model(
        PricingModel(
            name="claude-3-haiku",
            provider="anthropic",
            input_price_per_1k=0.25,
            output_price_per_1k=1.25,
            context_window=200000,
            max_output=4096,
            description="Claude 3 Haiku fast model",
        )
    )
    db.add_model(
        PricingModel(
            name="claude-3-opus",
            provider="anthropic",
            input_price_per_1k=15.00,
            output_price_per_1k=75.00,
            context_window=200000,
            max_output=4096,
            description="Claude 3 Opus powerful model",
        )
    )

    # Google Models
    db.add_model(
        PricingModel(
            name="gemini-1.5-pro",
            provider="google",
            input_price_per_1k=3.50,
            output_price_per_1k=10.50,
            context_window=2097152,
            max_output=8192,
            description="Gemini 1.5 Pro large context model",
        )
    )
    db.add_model(
        PricingModel(
            name="gemini-1.5-flash",
            provider="google",
            input_price_per_1k=0.075,
            output_price_per_1k=0.30,
            context_window=1048576,
            max_output=8192,
            description="Gemini 1.5 Flash fast model",
        )
    )

    # DeepSeek Models
    db.add_model(
        PricingModel(
            name="deepseek-v3",
            provider="deepseek",
            input_price_per_1k=0.27,
            output_price_per_1k=1.10,
            context_window=65536,
            max_output=8192,
            description="DeepSeek V3 open-source model",
        )
    )
    db.add_model(
        PricingModel(
            name="deepseek-chat",
            provider="deepseek",
            input_price_per_1k=0.14,
            output_price_per_1k=0.28,
            context_window=32768,
            max_output=4096,
            description="DeepSeek Chat model",
        )
    )

    # Zhipu AI Models
    db.add_model(
        PricingModel(
            name="glm-4",
            provider="zhipu",
            input_price_per_1k=0.10,
            output_price_per_1k=0.10,
            context_window=128000,
            max_output=4096,
            description="GLM-4 bilingual model by Zhipu AI",
        )
    )
    db.add_model(
        PricingModel(
            name="glm-4-flash",
            provider="zhipu",
            input_price_per_1k=0.001,
            output_price_per_1k=0.001,
            context_window=128000,
            max_output=4096,
            description="GLM-4 Flash free tier model",
        )
    )

    # Alibaba Qwen Models
    db.add_model(
        PricingModel(
            name="qwen-max",
            provider="alibaba",
            input_price_per_1k=0.40,
            output_price_per_1k=1.20,
            context_window=32768,
            max_output=8192,
            description="Qwen Max flagship model",
        )
    )
    db.add_model(
        PricingModel(
            name="qwen-plus",
            provider="alibaba",
            input_price_per_1k=0.16,
            output_price_per_1k=0.48,
            context_window=131072,
            max_output=8192,
            description="Qwen Plus balanced model",
        )
    )
    db.add_model(
        PricingModel(
            name="qwen-turbo",
            provider="alibaba",
            input_price_per_1k=0.04,
            output_price_per_1k=0.12,
            context_window=131072,
            max_output=8192,
            description="Qwen Turbo fast model",
        )
    )

    # ByteDance Doubao Models
    db.add_model(
        PricingModel(
            name="doubao-pro-32k",
            provider="bytedance",
            input_price_per_1k=0.008,
            output_price_per_1k=0.008,
            context_window=32768,
            max_output=4096,
            description="Doubao Pro 32K model",
        )
    )

    # Moonshot Models
    db.add_model(
        PricingModel(
            name="moonshot-v1",
            provider="moonshot",
            input_price_per_1k=0.12,
            output_price_per_1k=0.12,
            context_window=32768,
            max_output=4096,
            description="Moonshot V1 by Kimi",
        )
    )

    # Mistral Models
    db.add_model(
        PricingModel(
            name="mistral-large",
            provider="mistral",
            input_price_per_1k=4.00,
            output_price_per_1k=12.00,
            context_window=128000,
            max_output=4096,
            description="Mistral Large flagship model",
        )
    )

    return db

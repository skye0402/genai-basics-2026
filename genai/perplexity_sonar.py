"""Perplexity Sonar and Sonar Pro Integration for SAP Generative AI Hub

This module provides a dedicated client for accessing Perplexity's Sonar and Sonar Pro
models through SAP Generative AI Hub using the SDK's deployment selection mechanism.

Models supported:
- sonar: Perplexity Sonar (base model)
- sonar-pro: Perplexity Sonar Pro (advanced model with enhanced capabilities)

These models are "online" models that can perform web searches and access real-time information.
"""

import os
from typing import Literal, Optional, List, Dict, Any

from gen_ai_hub.proxy.native.openai.clients import OpenAI
from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubProxyClient, Deployment


class PerplexitySonarClient:
    """Client for Perplexity Sonar and Sonar Pro models via SAP Generative AI Hub.
    
    This client uses the SAP AI SDK's OpenAI proxy to access Perplexity models
    that are deployed in Generative AI Hub but not yet listed in the SDK's
    "Supported Models" table.
    
    Args:
        model_name: Either "sonar" or "sonar-pro"
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        deployment_id: Optional explicit deployment ID to use
        top_p: Optional nucleus sampling parameter
    """
    
    def __init__(
        self,
        model_name: Literal["sonar", "sonar-pro"] = "sonar-pro",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        deployment_id: Optional[str] = None,
        top_p: Optional[float] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.deployment_id = deployment_id
        self.top_p = top_p
        
        # Initialize the OpenAI proxy client (uses env vars for AI Core credentials)
        self.client = OpenAI()
        
        # Verify deployment is accessible
        self._verify_deployment()
    
    def _verify_deployment(self):
        """Verify that the Perplexity deployment is accessible.
        
        Raises:
            ValueError: If no deployment can be found for the model
        """
        try:
            proxy_client: GenAIHubProxyClient = self.client.proxy_client
            
            # Try to select deployment by model_name or deployment_id
            deployment: Deployment
            if self.deployment_id:
                deployment = proxy_client.select_deployment(deployment_id=self.deployment_id)
            else:
                deployment = proxy_client.select_deployment(model_name=self.model_name)
            
            print(f"[OK] Found Perplexity deployment: {deployment.deployment_id}")
            print(f"     Model: {deployment.model_name}")
            print(f"     Config: {deployment.config_name}")
            
        except ValueError as e:
            error_msg = (
                f"Could not find Perplexity deployment for model '{self.model_name}'. "
                f"Please ensure:\n"
                f"1. A Perplexity deployment with model_name='{self.model_name}' exists in GenAI Hub\n"
                f"2. The deployment status is RUNNING\n"
                f"3. Your AI Core credentials are correct\n"
                f"4. Optionally set PERPLEXITY_DEPLOYMENT_ID to pin to a specific deployment\n"
                f"Original error: {str(e)}"
            )
            raise ValueError(error_msg) from e
    
    def invoke(self, prompt: str, stream: bool = False) -> str:
        """Send a simple prompt to Perplexity and get a response.
        
        Args:
            prompt: The user prompt/question
            stream: Whether to stream the response (not yet implemented)
            
        Returns:
            The model's response as a string
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages=messages, stream=stream)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> str:
        """Send a chat conversation to Perplexity and get a response.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "What is AI?"}]
            stream: Whether to stream the response (not yet implemented)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            The model's response as a string
        """
        # Prepare API call parameters
        call_params: Dict[str, Any] = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        # Add optional parameters
        if self.top_p is not None:
            call_params["top_p"] = self.top_p
        
        # Select deployment using model_name or deployment_id
        if self.deployment_id:
            call_params["deployment_id"] = self.deployment_id
        else:
            call_params["model_name"] = self.model_name
        
        # Make the API call
        if stream:
            # TODO: Implement streaming support
            raise NotImplementedError("Streaming is not yet implemented for Perplexity Sonar")
        
        response = self.client.chat.completions.create(**call_params)
        
        # Extract and return the response text
        return response.choices[0].message.content


def create_perplexity_client(
    model: str = "perplexity--sonar-pro",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    deployment_id: Optional[str] = None,
) -> PerplexitySonarClient:
    """Factory function to create a Perplexity client from environment variables.
    
    This is a convenience function that maps the PERPLEXITY_MODEL env var format
    to the actual model_name format expected by GenAI Hub.
    
    Args:
        model: Model identifier in format "perplexity--sonar" or "perplexity--sonar-pro"
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        deployment_id: Optional explicit deployment ID
        
    Returns:
        Configured PerplexitySonarClient instance
    """
    # Map the PERPLEXITY_MODEL format to actual model_name
    if "sonar-pro" in model.lower():
        model_name = "sonar-pro"
    elif "sonar" in model.lower():
        model_name = "sonar"
    else:
        raise ValueError(
            f"Unsupported Perplexity model: {model}. "
            f"Expected 'perplexity--sonar' or 'perplexity--sonar-pro'"
        )
    
    return PerplexitySonarClient(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        deployment_id=deployment_id,
    )

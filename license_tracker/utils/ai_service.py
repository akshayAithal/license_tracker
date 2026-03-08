#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI service layer - abstracted to support OpenAI and local LLM models.

Usage:
    from license_tracker.utils.ai_service import get_ai_service
    service = get_ai_service()
    result = service.analyze_document(text, prompt)
"""

import os
from license_tracker.logger import logger
from license_tracker.models.app_settings import AppSettings


class AIServiceBase(object):
    """Base class for AI services."""

    def analyze_document(self, document_text, prompt):
        """Send document text + prompt to the AI model and return the response.
        Returns dict with 'success', 'response', and optionally 'error'.
        """
        raise NotImplementedError

    def test_connection(self):
        """Test connectivity to the AI service.
        Returns dict with 'success' and 'message' or 'error'.
        """
        raise NotImplementedError


class OpenAIService(AIServiceBase):
    """OpenAI API integration (GPT-4o, GPT-3.5, etc.)."""

    def __init__(self, api_key, model='gpt-4o-mini'):
        self.api_key = api_key
        self.model = model

    def analyze_document(self, document_text, prompt):
        try:
            import requests
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Content-Type': 'application/json',
            }
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are a license cost analysis assistant. Analyze documents and extract license cost information. Always respond with structured data when possible.'},
                    {'role': 'user', 'content': prompt + '\n\n--- DOCUMENT ---\n' + document_text[:15000]},
                ],
                'temperature': 0.2,
                'max_tokens': 2000,
            }
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return {'success': True, 'response': content}
            else:
                error_msg = resp.json().get('error', {}).get('message', resp.text)
                logger.error('OpenAI API error: %s', error_msg)
                return {'success': False, 'error': error_msg}
        except Exception as e:
            logger.error('OpenAI service error: %s', str(e))
            return {'success': False, 'error': str(e)}

    def test_connection(self):
        try:
            import requests
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Content-Type': 'application/json',
            }
            payload = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': 'Say "connected" in one word.'}],
                'max_tokens': 10,
            }
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15,
            )
            if resp.status_code == 200:
                return {'success': True, 'message': 'OpenAI connection successful (model: ' + self.model + ')'}
            else:
                error_msg = resp.json().get('error', {}).get('message', resp.text)
                return {'success': False, 'error': error_msg}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LocalModelService(AIServiceBase):
    """Local LLM service (Ollama, vLLM, text-generation-inference, etc.).
    Expects an OpenAI-compatible API at the configured URL.
    """

    def __init__(self, base_url, model='default', api_key=None):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_key = api_key  # some local servers need a token

    def analyze_document(self, document_text, prompt):
        try:
            import requests
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = 'Bearer ' + self.api_key

            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are a license cost analysis assistant. Analyze documents and extract license cost information.'},
                    {'role': 'user', 'content': prompt + '\n\n--- DOCUMENT ---\n' + document_text[:15000]},
                ],
                'temperature': 0.2,
                'max_tokens': 2000,
            }
            resp = requests.post(
                self.base_url + '/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return {'success': True, 'response': content}
            else:
                return {'success': False, 'error': 'Local model error: ' + resp.text[:500]}
        except Exception as e:
            logger.error('Local model service error: %s', str(e))
            return {'success': False, 'error': str(e)}

    def test_connection(self):
        try:
            import requests
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = 'Bearer ' + self.api_key

            # Try the models endpoint first (works for Ollama, vLLM, etc.)
            try:
                resp = requests.get(self.base_url + '/v1/models', headers=headers, timeout=10)
                if resp.status_code == 200:
                    return {'success': True, 'message': 'Local model connected at ' + self.base_url}
            except Exception:
                pass

            # Fallback: try a simple completion
            payload = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': 'ping'}],
                'max_tokens': 5,
            }
            resp = requests.post(
                self.base_url + '/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15,
            )
            if resp.status_code == 200:
                return {'success': True, 'message': 'Local model connected (model: ' + self.model + ')'}
            else:
                return {'success': False, 'error': 'HTTP ' + str(resp.status_code) + ': ' + resp.text[:200]}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_ai_service():
    """Factory: return the configured AI service instance.
    Checks app_settings for provider preference, falls back to env vars.
    Returns (service_instance, error_string_or_None).
    """
    provider = AppSettings.get_setting('ai_provider', 'openai')

    if provider == 'local':
        url = AppSettings.get_setting('local_model_url', '')
        model = AppSettings.get_setting('local_model_name', 'default')
        api_key = AppSettings.get_setting('local_model_api_key', '')
        if not url:
            return None, 'Local model URL not configured'
        return LocalModelService(url, model, api_key or None), None

    # Default: OpenAI
    api_key = AppSettings.get_setting('openai_api_key', '') or os.environ.get('OPENAI_API_KEY', '')
    model = AppSettings.get_setting('openai_model', 'gpt-4o-mini')
    if not api_key:
        return None, 'OpenAI API key not configured'
    return OpenAIService(api_key, model), None

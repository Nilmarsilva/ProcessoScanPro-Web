"""
Serviços de integração com APIs externas
"""
from .pipedrive import PipedriveAPI
from .assertiva import AssertiveAPI
from .invertexto import InvertextoAPI

__all__ = ['PipedriveAPI', 'AssertiveAPI', 'InvertextoAPI']

# Templates package
# Contains prompt templates for various API calls

from .action_analysis_template import ACTION_ANALYSIS_TEMPLATE
from .click_location_template import CLICK_LOCATION_TEMPLATE
from .task_execution_template import TASK_EXECUTION_TEMPLATE

__all__ = [
    'ACTION_ANALYSIS_TEMPLATE', 
    'CLICK_LOCATION_TEMPLATE', 
    'TASK_EXECUTION_TEMPLATE'
] 
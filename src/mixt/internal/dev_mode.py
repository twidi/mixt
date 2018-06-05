"""Function to get/activate dev-mode."""

from .proptypes import BasePropTypes


__all__ = ["set_dev_mode", "unset_dev_mode", "override_dev_mode", "in_dev_mode"]

set_dev_mode = BasePropTypes.__set_dev_mode__
unset_dev_mode = BasePropTypes.__unset_dev_mode__
override_dev_mode = BasePropTypes.__override_dev_mode__
in_dev_mode = BasePropTypes.__in_dev_mode__

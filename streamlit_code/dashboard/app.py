
import streamlit as st
import pandas as pd
from utility.logger_config import setup_logging
setup_logging()
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})


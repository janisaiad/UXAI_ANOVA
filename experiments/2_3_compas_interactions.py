""" Find feature interactions in COMPAS """
# %%
import os, sys
import numpy as np
import matplotlib.pyplot as plt

# Local imports
from utils import setup_data_trees, custom_train_test_split, setup_pyplot_font
from utils import load_trees, plot_interaction, interactions_heatmap

setup_pyplot_font(20)

sys.path.append(os.path.abspath(".."))
from src.anova import interventional_taylor_treeshap

# %%
# Load data and model
X, y, features, task = setup_data_trees("compas")
x_train, x_test, y_train, y_test = custom_train_test_split(X, y, task)
# Load models
model_name = "rf"
model, perf = load_trees("compas", model_name, 0)

# %%
# Uniform Background
background = x_train[:500]
Phis, _ = interventional_taylor_treeshap(model, background, background)

# %%
interactions_heatmap(Phis, features)
plt.savefig(os.path.join("Images", "compas", f"Interactions_{model_name}.pdf"), 
                                                            bbox_inches='tight')
plt.show()

# %% AGE vs PRIORS
plot_interaction(3, 4, background, Phis, features)
plt.show()

# %% AGE vs RACE
plot_interaction(4, 1, background, Phis, features)
plt.show()

# %% PRIORS vs RACE
plot_interaction(3, 1, background, Phis, features)
plt.show()

# %% [markdown]
# The strongest interactions involve features 
# AGE and PRIORS RACE. These two features will 
# be used when fitting a FDTree.
# %%

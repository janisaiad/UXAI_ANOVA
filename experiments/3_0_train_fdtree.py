
import os, sys
import numpy as np

# Local imports
from utils import setup_data_trees, custom_train_test_split, get_background
from utils import load_trees, save_FDTree, Data_Config, TreeEnsembleHP
from data_utils import INTERACTIONS_MAPPING

sys.path.append(os.path.abspath(".."))
from src.anova_tree import Partition, PARTITION_CLASSES
from src.anova import get_ANOVA_1_tree


if __name__ == "__main__":
    from simple_parsing import ArgumentParser
    
    # Parse arguments
    parser = ArgumentParser()
    parser.add_arguments(Data_Config, "data")
    parser.add_arguments(Partition, "partition")
    parser.add_arguments(TreeEnsembleHP, "ensemble")
    parser.add_argument("--model_name", type=str, default="gbt",
                       help="Type of tree ensemble either gbt or rf")
    parser.add_argument("--background_size", type=int, default=600,
                       help="Size of the background data")
    parser.add_argument("--save", action='store_true', help="Save model locally")
    args, unknown = parser.parse_known_args()
    print(args)

    # Load data and model
    X, y, features, task = setup_data_trees(args.data.name)
    x_train, x_test, y_train, y_test = custom_train_test_split(X, y, task)
    # Load models
    model, perfs = load_trees(args.data.name, args.model_name, args.ensemble.random_state)

    # Make folder for dataset models
    path = os.path.join("models", args.data.name, args.model_name + "_" + str(args.ensemble.random_state))

    # Background data
    background = get_background(x_train, args.background_size, args.ensemble.random_state)

    # Only use interacting features when fitting the FDTree
    interactions = INTERACTIONS_MAPPING[args.data.name]
    subset_features = features.select(interactions)

    # Compute the A matrix only once
    use_logit = args.model_name == "gbt"
    if not os.path.exists(os.path.join(path, f"A_global_N_{args.background_size}.npy")):
        H = get_ANOVA_1_tree(background, model, task=task, logit=use_logit)
        np.save(os.path.join(path, f"A_global_N_{args.background_size}.npy"), H)
    else:
        H = np.load(os.path.join(path, f"A_global_N_{args.background_size}.npy"))
    
    # Modify A if needed for the method
    if args.partition.type == "gadget-pdp":
        H = H[..., [0]+[i+1 for i in interactions]]
    elif args.partition.type in ["random", "l2coe"]:
        H = H.sum(-1)
    elif args.partition.type == "cart":
        H = H[0, :, 0]

    # Use the partitioning tree
    Tree = PARTITION_CLASSES[args.partition.type]

    for max_depth in [1, 2, 3]:

        # Reproducability
        np.random.seed(args.ensemble.random_state)

        # Fit the tree
        tree = Tree(subset_features, max_depth=max_depth,
                    save_losses=args.partition.save_losses,
                    negligible_impurity=args.partition.negligible_impurity,
                    relative_decrease=args.partition.relative_decrease,
                    samples_leaf=args.partition.samples_leaf)
        tree.fit(background[:, interactions], H)
        print(f"Final Loss : {tree.total_impurity}")
        tree.print(verbose=True)
        groups, rules = tree.predict(X)
        print(rules)

        if args.save:
            print("Saving Results")
            save_FDTree(tree, args.data.name, args.model_name, args.ensemble.random_state,
                        args.partition.type, args.background_size)


# # %%
# # Plot the objective values w.r.t the split candidates
# plt.figure()
# for i in range(3):
#     splits = tree.root.splits[i]
#     objectives = tree.root.objectives[i]
#     plt.plot(splits, objectives, '-o', label=features.names[i])
# plt.ylim(0, y.var())
# plt.xlabel(f"Split value")
# plt.ylabel(r"$L_2$ Cost of Exclusion")
# plt.legend()
# plt.show()
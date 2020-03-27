seed0=41
seed1=95
seed2=12
seed3=35
code=main_SBMs_node_classification.py 
tmux new -s benchmark_SBMs_node_classification -d
tmux send-keys "source activate benchmark_gnn" C-m
dataset=SBM_CLUSTER
tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed0 --config 'configs/SBMs_node_clustering_GCN_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed1 --config 'configs/SBMs_node_clustering_GCN_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed2 --config 'configs/SBMs_node_clustering_GCN_CLUSTER.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed3 --config 'configs/SBMs_node_clustering_GCN_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed0 --config 'configs/SBMs_node_clustering_GraphSage_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed1 --config 'configs/SBMs_node_clustering_GraphSage_CLUSTER.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed2 --config 'configs/SBMs_node_clustering_GraphSage_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed3 --config 'configs/SBMs_node_clustering_GraphSage_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed0 --config 'configs/SBMs_node_clustering_GAT_CLUSTER.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed1 --config 'configs/SBMs_node_clustering_GAT_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed2 --config 'configs/SBMs_node_clustering_GAT_CLUSTER.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed3 --config 'configs/SBMs_node_clustering_GAT_CLUSTER.json' &
wait" C-m


############
# SBM_PATTERN - 4 RUNS 
############


dataset=SBM_PATTERN

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed0 --config 'configs/SBMs_node_clustering_GCN_PATTERN.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed1 --config 'configs/SBMs_node_clustering_GCN_PATTERN.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed2 --config 'configs/SBMs_node_clustering_GCN_PATTERN.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed3 --config 'configs/SBMs_node_clustering_GCN_PATTERN.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed0 --config 'configs/SBMs_node_clustering_GraphSage_PATTERN.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed1 --config 'configs/SBMs_node_clustering_GraphSage_PATTERN.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed2 --config 'configs/SBMs_node_clustering_GraphSage_PATTERN.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed3 --config 'configs/SBMs_node_clustering_GraphSage_PATTERN.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed0 --config 'configs/SBMs_node_clustering_GAT_PATTERN.json' &
wait" C-m

tmux send-keys "
python $code --dataset $dataset --gpu_id 0 --seed $seed1 --config 'configs/SBMs_node_clustering_GAT_PATTERN.json' &
python $code --dataset $dataset --gpu_id 1 --seed $seed2 --config 'configs/SBMs_node_clustering_GAT_PATTERN.json' &
python $code --dataset $dataset --gpu_id 2 --seed $seed3 --config 'configs/SBMs_node_clustering_GAT_PATTERN.json' &
wait" C-m

tmux send-keys "tmux kill-session -t benchmark_SBMs_node_classification" C-m

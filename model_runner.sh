# Step 1: Download + extract dataset
docker volume create codeqa
docker compose -f docker-compose-data.yaml up -d
docker run --rm -it -v codeqa:/mnt alpine ls -l /mnt

# Step 2: Launch training shell
docker compose run trainer 

# Step 3: Start Ray head node
export HOST_IP=$(curl --silent http://169.254.169.254/latest/meta-data/public-ipv4 )
docker compose -f docker-compose-ray-1-gpu.yaml up -d

# if got 2 gpu:
# run on node-mltrain
docker exec -it ray-worker-0 nvidia-smi --list-gpus

# # run on node-mltrain
# docker exec -it ray-worker-1 nvidia-smi --list-gpus


## start jupyter container
# run on node-mltrain
docker build -t jupyter-ray -f Dockerfile.jupyter-ray .
Run

# run on node-mltrain
HOST_IP=$(curl --silent http://169.254.169.254/latest/meta-data/public-ipv4 )
docker run  -d --rm  -p 8888:8888 \
    -v ~/workspace_ray:/home/jovyan/work/ \
    -e RAY_ADDRESS=http://${HOST_IP}:8265/ \
    --name jupyter \
    jupyter-ray

# then run
docker logs jupyter
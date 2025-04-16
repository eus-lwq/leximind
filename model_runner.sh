# Step 1: Download + extract dataset
docker compose run dataset

# Step 2: Launch training shell
docker compose run trainer ### still working on it

# Step 3: Start Ray head node
docker compose run ray-head

# Step 4: Start Ray worker node (optional, if needed)
docker compose run ray-worker
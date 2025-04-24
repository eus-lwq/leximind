# Create the directory structure in llama-factory
mkdir -p /root/llama-factory/data/codeqa

# Copy the train and test files from the mounted volume
cp /mnt/codeqa/train.json /root/llama-factory/data/codeqa/
cp /mnt/codeqa/test.json /root/llama-factory/data/codeqa/

# Create the dataset_info.json file
cat > /root/llama-factory/data/codeqa/dataset_info.json << 'EOF'
{
  "dataset_name": "codeqa",
  "train_file": "train.json",
  "val_file": "test.json",
  "formatting_func": "alpaca"
}
EOF
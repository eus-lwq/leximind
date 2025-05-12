import json

# Input and output file paths
input_file = "sample.json"
output_file = "batch_input.jsonl"

# Model name to use in the output
model_name = "/home/cc/model/whole_model"

def convert_sample_to_batch_input(input_file, output_file):
    """
    Convert data from sample.json (JSON array) to the format of batch_input.jsonl.
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        # Load the JSON array from the input file
        samples = json.load(infile)
        
        for idx, sample in enumerate(samples):
            # Create the batch input format
            batch_entry = {
                "custom_id": f"request-{idx + 1}",
                "method": "POST",
                "url": "/v1/score",
                "body": {
                    "model": model_name,
                    "text_1": sample["instruction"],
                    "text_2": [sample["input"]]
                }
            }
            
            # Write the converted entry to the output file
            outfile.write(json.dumps(batch_entry) + "\n")

if __name__ == "__main__":
    convert_sample_to_batch_input(input_file, output_file)
    print(f"Converted data has been saved to {output_file}")
# Triton Inference Server

Our Triton Inference Server (`triton`) service is responsible for the tokenizing/embedding of string queries. 

The following commands will clone a Lefebvre Dalloz Services [Github repo](https://github.com/ELS-RD/transformer-deploy) (Apache License 2.0) within this `triton/` directory. It will then create the Triton model repository with a TensorRT engine `transformer_tensorrt_model` for model inference and a Python tokenizer `transformer_tensorrt_tokenize` to tokenize text input. Finally, it will ensemble them within `transformer_tensorrt_inference`, generating a config file to instruct Triton Server.

```bash
# To be run from AWS instance
cd triton
git clone https://github.com/ELS-RD/transformer-deploy.git
cd transformer-deploy
git checkout tags/v0.4.0
docker pull ghcr.io/els-rd/transformer-deploy:0.4.0 
```
Convert the model using the Docker container. The `512 512 512` at the end of the command corresponds to the minimum, optimal,
and maximum sequence length for the TensorRT engine. These are all set to 512 tokens. Keeping the values all the same should
make the engine faster.

Also need to set batch size minimum, optimal and maximum length.

Refer to https://github.com/ELS-RD/transformer-deploy/blob/main/docs/run.md

```bash
docker run -it --rm --gpus all -v $PWD:/project ghcr.io/els-rd/transformer-deploy:0.4.0 bash -c "cd /project && convert_model -m \"intfloat/e5-large-unsupervised\" --backend tensorrt --task embedding --seq-len 512 512 512 --batch-size 1 1 16"
```
Since we generated the model with fixed input dimensions for performance, we'll have to modify the tokenizer.
In `python_tokenizer.py`, we pad and truncate all queries so that they become 512 tokens in length, corresponding to the max sequence length of the `intfloat/e5-large-unsupervised` model. 
This means a very long input query will be cut off after a certain point, and shorter queries will be padded with a `padding_token` to make sure they are 512 tokens long.

Copy our modified tokenizer backend into the newly generated Triton config.

```bash
# To be run from AWS instance
sudo cp ../python_tokenizer.py triton_models/transformer_tensorrt_tokenize/1/model.py
```

```bash
cd ..
# MUST RUN SCRIPTS FROM THIS DIRECTORY

# Build image
bash build_image.sh

cd ..
```

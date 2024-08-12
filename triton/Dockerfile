FROM nvcr.io/nvidia/tritonserver:22.01-py3@sha256:bb4c71b62bf206c8d6b0db57b66c18e86b471f6549676849508de2afe9f435c0

# copy model files separately to make for smaller layers
COPY transformer-deploy/triton_models/transformer_tensorrt_inference/ /models/transformer_tensorrt_inference/
COPY transformer-deploy/triton_models/transformer_tensorrt_model/ /models/transformer_tensorrt_model/
COPY transformer-deploy/triton_models/transformer_tensorrt_tokenize/ /models/transformer_tensorrt_tokenize/
COPY transformer-deploy/triton_models/model-original.onnx /models/
COPY transformer-deploy/triton_models/model.plan /models/

RUN pip3 install transformers==4.26.0
CMD ["tritonserver", "--model-repository", "/models"]